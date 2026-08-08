#!/usr/bin/env python
"""
E2 LoRA-SFT trainer (runs ON the GPU box via job dispatch).

Fine-tunes Qwen3-VL-8B-Instruct with LoRA on one E2 arm + seed. Reads the arm's
train.jsonl (records: images[5], question, target) and trains the model to produce
`target` given images+question. Saves the LoRA adapter + a train log.

Usage (on box):
  python train_e2_lora.py --arm V1 --seed 0 --data-dir ./data --out ./out_V1_s0 \
      --epochs 3 --lr 1e-4 --grad-accum 8 --max-steps 0

Design for a single 32GB 5090:
  - 4-bit QLoRA (bitsandbytes nf4) to fit the 8B VLM + 5 images/example.
  - gradient checkpointing, bf16, LoRA on attention+MLP proj layers.
  - images downsized to keep visual-token count bounded (min_pixels/max_pixels).
  - per-arm: B1/B2/V1 differ ONLY in the target string (built into the jsonl).
"""
import argparse, json, os, random, time
import torch


def set_seed(s):
    random.seed(s); torch.manual_seed(s); torch.cuda.manual_seed_all(s)


def load_examples(path, arm, data_dir):
    """Load an arm's examples, re-resolving image paths to <data_dir>/renders/<split>/<basename>.

    The jsonl stores absolute build-machine paths; on the training box we resolve each
    image by its basename under the local renders tree, so the data is path-portable.
    """
    rows = [json.loads(l) for l in open(path)]
    out = []
    for r in rows:
        if r["arm"] != arm:
            continue
        split = r.get("split", "train")
        r["images"] = [os.path.join(data_dir, "renders", split, os.path.basename(p))
                       for p in r["images"]]
        out.append(r)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=["B1", "B2", "V1", "V1b"])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--data-dir", default="./data")
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="Qwen/Qwen3-VL-8B-Instruct")
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--grad-accum", type=int, default=8)
    ap.add_argument("--max-steps", type=int, default=0)
    ap.add_argument("--max-pixels", type=int, default=200704)  # ~448x448 per image
    args = ap.parse_args()
    set_seed(args.seed)
    os.makedirs(args.out, exist_ok=True)
    log = {"arm": args.arm, "seed": args.seed, "model": args.model, "steps": []}

    from transformers import (AutoProcessor, BitsAndBytesConfig,
                              Qwen3VLForConditionalGeneration)
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

    proc = AutoProcessor.from_pretrained(args.model, max_pixels=args.max_pixels)
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                             bnb_4bit_compute_dtype=torch.bfloat16,
                             bnb_4bit_use_double_quant=True)
    model = Qwen3VLForConditionalGeneration.from_pretrained(
        args.model, quantization_config=bnb, torch_dtype=torch.bfloat16,
        device_map="auto", attn_implementation="sdpa")
    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)
    lora = LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, bias="none",
                      task_type="CAUSAL_LM",
                      target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                                      "gate_proj", "up_proj", "down_proj"])
    model = get_peft_model(model, lora)
    model.print_trainable_parameters()

    examples = load_examples(os.path.join(args.data_dir, "train.jsonl"), args.arm, args.data_dir)
    print(f"[train] arm={args.arm} seed={args.seed} n_examples={len(examples)}")

    def build_inputs(ex):
        from PIL import Image
        content = [{"type": "image", "image": Image.open(p).convert("RGB")} for p in ex["images"]]
        content.append({"type": "text", "text": ex["question"]})
        messages = [{"role": "user", "content": content},
                    {"role": "assistant", "content": [{"type": "text", "text": ex["target"]}]}]
        text = proc.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
        imgs = [Image.open(p).convert("RGB") for p in ex["images"]]
        batch = proc(text=[text], images=[imgs], return_tensors="pt", padding=True)
        # mask labels: only supervise the assistant target tokens
        labels = batch["input_ids"].clone()
        # find the target span by tokenizing the prompt-only prefix
        prompt_messages = [{"role": "user", "content": content}]
        prompt_text = proc.apply_chat_template(prompt_messages, tokenize=False, add_generation_prompt=True)
        pbatch = proc(text=[prompt_text], images=[imgs], return_tensors="pt", padding=True)
        plen = pbatch["input_ids"].shape[1]
        labels[:, :plen] = -100
        batch["labels"] = labels
        return {k: v.to(model.device) for k, v in batch.items()}

    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=args.lr)
    model.train()
    t0 = time.time(); step = 0; accum_loss = 0.0
    for epoch in range(args.epochs):
        random.shuffle(examples)
        for i, ex in enumerate(examples):
            try:
                inp = build_inputs(ex)
                out = model(**inp)
                loss = out.loss / args.grad_accum
                loss.backward()
                accum_loss += float(out.loss)
                if (i + 1) % args.grad_accum == 0:
                    opt.step(); opt.zero_grad(); step += 1
                    avg = accum_loss / args.grad_accum; accum_loss = 0.0
                    if step % 5 == 0:
                        print(f"  ep{epoch} step{step} loss={avg:.4f} ({time.time()-t0:.0f}s)")
                    log["steps"].append({"step": step, "epoch": epoch, "loss": avg})
                    if args.max_steps and step >= args.max_steps:
                        break
            except torch.cuda.OutOfMemoryError:
                print(f"  OOM on example {i}, skipping"); torch.cuda.empty_cache(); opt.zero_grad()
        if args.max_steps and step >= args.max_steps:
            break

    model.save_pretrained(args.out)
    log["elapsed_sec"] = round(time.time() - t0, 1); log["final_step"] = step
    json.dump(log, open(os.path.join(args.out, "train_log.json"), "w"), indent=1)
    print(f"[train] done arm={args.arm} seed={args.seed} steps={step} "
          f"{log['elapsed_sec']}s -> {args.out}")


if __name__ == "__main__":
    main()

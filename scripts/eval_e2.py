#!/usr/bin/env python
"""
E2 evaluation (runs ON the GPU box).

Loads a trained LoRA adapter, generates predictions on the test split for its arm, and
scores:
  - crystal_system accuracy (micro + macro over 7 systems), the primary E2 metric
  - V1 only: per-step chain accuracy (does the [SYSTEM/BRAVAIS], [SYMMETRY] step name the
    right system / space-group number that the model itself then answers with)
Outputs one JSON per adapter: eval_<arm>_s<seed>.json with per-structure predictions +
aggregates. The property task (band_gap MAE / formation energy) is scored separately
(scripts/eval_e2_property.py) since it needs a regression head; here we focus on the
symmetry perception the arms differ on.

Deterministic decoding (do_sample=False) so eval is reproducible.
"""
import argparse, json, os, re
import torch


CS = ["triclinic", "monoclinic", "orthorhombic", "tetragonal", "trigonal", "hexagonal", "cubic"]


def parse_answer(text):
    """Extract the predicted crystal system from the model output (ANSWER: line, else last CS mention)."""
    m = list(re.finditer(r"ANSWER[:\]]\s*([a-z]+)", text, re.IGNORECASE))
    if m:
        cand = m[-1].group(1).lower()
        if cand in CS:
            return cand
    # fallback: last crystal-system word mentioned
    found = [(text.lower().rfind(s), s) for s in CS if s in text.lower()]
    found = [(i, s) for i, s in found if i >= 0]
    return max(found)[1] if found else None


def load_examples(path, arm, data_dir):
    rows = [json.loads(l) for l in open(path)]
    out = []
    for r in rows:
        if r["arm"] != arm:
            continue
        split = r.get("split", "test")
        r["images"] = [os.path.join(data_dir, "renders", split, os.path.basename(p)) for p in r["images"]]
        out.append(r)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True)
    ap.add_argument("--eval-arm", default=None,
                    help="dataset arm whose test PROMPTS to load (defaults to --arm). "
                         "GRPO arms (B3/V2a/V2b) have no dataset rows; eval them on V1 prompts.")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--adapter", required=True)
    ap.add_argument("--data-dir", default="data/e2")
    ap.add_argument("--model", default="Qwen/Qwen3-VL-8B-Instruct")
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-pixels", type=int, default=200704)
    ap.add_argument("--max-new-tokens", type=int, default=400)
    args = ap.parse_args()

    from transformers import AutoProcessor, BitsAndBytesConfig, Qwen3VLForConditionalGeneration
    from peft import PeftModel
    from PIL import Image

    proc = AutoProcessor.from_pretrained(args.model, max_pixels=args.max_pixels)
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                             bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True)
    base = Qwen3VLForConditionalGeneration.from_pretrained(
        args.model, quantization_config=bnb, torch_dtype=torch.bfloat16,
        device_map="auto", attn_implementation="sdpa")
    model = PeftModel.from_pretrained(base, args.adapter)
    model.eval()

    prompt_arm = args.eval_arm or args.arm
    examples = load_examples(os.path.join(args.data_dir, "test.jsonl"), prompt_arm, args.data_dir)
    results = []
    for ex in examples:
        imgs = [Image.open(p).convert("RGB") for p in ex["images"]]
        content = [{"type": "image", "image": im} for im in imgs]
        content.append({"type": "text", "text": ex["question"]})
        messages = [{"role": "user", "content": content}]
        text = proc.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inp = proc(text=[text], images=[imgs], return_tensors="pt", padding=True).to(model.device)
        with torch.no_grad():
            gen = model.generate(**inp, max_new_tokens=args.max_new_tokens, do_sample=False)
        out_text = proc.batch_decode(gen[:, inp["input_ids"].shape[1]:], skip_special_tokens=True)[0]
        pred = parse_answer(out_text)
        results.append({"material_id": ex["material_id"], "truth": ex["crystal_system"],
                        "pred": pred, "correct": pred == ex["crystal_system"],
                        "space_group": ex.get("space_group"), "text": out_text[:600]})

    # aggregates
    n = len(results); ncorr = sum(r["correct"] for r in results)
    micro = ncorr / n if n else 0.0
    # macro over systems present in test
    from collections import defaultdict
    by_sys = defaultdict(list)
    for r in results:
        by_sys[r["truth"]].append(r["correct"])
    macro = sum(sum(v) / len(v) for v in by_sys.values()) / len(by_sys) if by_sys else 0.0
    per_system = {s: {"n": len(v), "acc": sum(v) / len(v)} for s, v in by_sys.items()}

    out = {"arm": args.arm, "seed": args.seed, "n_test": n,
           "micro_acc": micro, "macro_acc": macro, "n_correct": ncorr,
           "per_system": per_system, "predictions": results}
    json.dump(out, open(args.out, "w"), indent=1)
    print(f"[eval] {args.arm} s{args.seed}: micro={micro:.3f} macro={macro:.3f} ({ncorr}/{n})")


if __name__ == "__main__":
    main()

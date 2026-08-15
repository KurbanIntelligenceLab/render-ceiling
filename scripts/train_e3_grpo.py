#!/usr/bin/env python
"""
E3 GRPO trainer (runs ON the GPU box) — the flagship process-vs-outcome comparison.

Three matched arms from the same V1 SFT checkpoint. All arms carry a COMMON format term;
the only manipulated variable is what per-step verification the base reward aggregates:
  B3   outcome-only     -> base = final crystal-system correct (CrystalReasoner-style)
  V2a  dense step-level -> base = mean(per-step verifiable rewards), final EXCLUDED
  V2b  dense step-level -> base = mean(per-step verifiable rewards + final)
                           (StepGRPO-style: R1-VL arXiv 2503.12937)

NOTE ON NAMING (verified against the primary source): this is NOT per-step / token-level
credit assignment, and neither is StepGRPO. StepGRPO also folds its dense rule-based step
rewards (StepRAR key-step matching + StepRVR structure/logic) into a SCALAR path-level
reward and then group-normalizes it — "the advantage of each reasoning trajectory" is
estimated "by normalizing its reward relative to the group". So describe these arms as
"dense step-level rewards" / "StepGRPO-style", never "step-wise credit assignment" or
"per-step advantage attribution". True per-step credit (token/segment-level advantages,
rollout step-value estimation) remains UNTESTED future work / an optional E3 extension arm.

DIFFERENTIATION from StepGRPO: StepGRPO's key steps are GPT-4-extracted (the paper prompts
GPT-4 to extract key steps from the reasoning path), i.e. model-generated supervision.
CoCr's step targets are DETERMINISTIC from the source CIF via spglib/pymatgen — no model
in the loop, so every step reward is programmatically verifiable rather than LLM-judged.

Uses TRL GRPOTrainer with a custom reward_funcs callable backed by cocr.reward
(the CIF-grounded reward server). LoRA on the V1 adapter, 4-bit base, group size 8,
vLLM sampling. Reward parsing is validated against the live chat template BEFORE any
optimization (the plan's mandate) via --smoke.

Usage:
  python train_e3_grpo.py --arm {B3,V2a,V2b} --seed 0 --sft-adapter adapters/V1_s0 \
      --data-dir data/e2 --out adapters_e3/V2a_s0 [--smoke] [--max-steps N]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time

import torch
from PIL import Image

sys.path.insert(0, "src")
from cocr.reward import score_chain, score_outcome  # noqa: E402

CRYSTAL_SYSTEMS = ["triclinic", "monoclinic", "orthorhombic", "tetragonal",
                   "trigonal", "hexagonal", "cubic"]


def load_examples(path, arm_for_prompt, data_dir):
    """GRPO trains on the (image, question) PROMPT; the target is not shown.

    We load the V1 rows (they carry the full label context we need for reward lookup),
    resolve images by basename under data_dir/renders, and attach the label dict so the
    reward function can score each rollout against ground truth.
    """
    rows = [json.loads(l) for l in open(path)]
    # E2 jsonl has multiple arms/structure (filter to V1); E3 jsonl is one row/structure
    # with no 'arm' field — use all rows in that case.
    if rows and "arm" in rows[0]:
        rows = [r for r in rows if r["arm"] == "V1"]
    # labels come from the precomputed pipeline sidecar (jsonl rows carry only metadata)
    sidecar = json.load(open(os.path.join(data_dir, "labels_sidecar.json")))
    base = os.path.basename(path)
    split = "train" if "train" in base else ("eval" if "eval" in base else ("val" if "val" in base else "test"))
    out = []
    for r in rows:
        imgs = [os.path.join(data_dir, "renders", split, os.path.basename(p)) for p in r["images"]]
        lab = sidecar.get(r["material_id"])
        if lab is None:
            continue
        out.append({"material_id": r["material_id"], "images": imgs,
                    "question": r["question"], "label": lab})
    return out


def build_reward_fn(arm):
    """Return a TRL-compatible reward_funcs callable for the chosen arm.

    TRL calls reward_fn(prompts, completions, **extra) where extra carries any dataset
    columns we passed through (here: 'label'). Returns a list[float] of scalar rewards.
    Both process arms aggregate the dense per-step reward vector into ONE scalar per
    completion, which GRPO then group-normalizes — i.e. dense step-level REWARDING with a
    path-level advantage, the same structure as StepGRPO. This is deliberately NOT per-step
    credit assignment; token/segment-level advantage attribution is untested future work.
    """
    def reward_fn(prompts=None, completions=None, label=None, **kw):
        # MATRIX DESIGN (process_reward pre-registration item 2): the FORMAT term is COMMON to all
        # three arms, so the ONLY manipulated variable is what per-step verification the
        # base reward aggregates:
        #   B3  = final-answer reward           + 0.25*format   (outcome-only)
        #   V2a = mean(per-step rewards)        + 0.25*format   (per-step verification,
        #                                                        NOT including final)
        #   V2b = mean(per-step rewards + final)+ 0.25*format   (per-step + final credit)
        # NOTE: V2a and V2b both AVERAGE (not a raw scalar sum); the V2a-vs-V2b contrast is
        # "per-step only" vs "per-step + final in the averaged set".
        # (The pilot ran B3 WITHOUT the format term — a confound now fixed.)
        FMT_W = 0.25
        rewards = []
        for comp, lab in zip(completions, label):
            text = comp if isinstance(comp, str) else comp[-1]["content"]
            sc = score_chain(text, lab)          # always parse for the common format term
            fmt = sc["format_reward"]
            if arm == "B3":
                base = score_outcome(text, lab)["final_reward"]
            elif arm == "V2a":
                steps = list(sc["per_step"].values())
                base = sum(steps) / len(steps)                       # mean of per-step
            else:  # V2b
                steps = list(sc["per_step"].values()) + [sc["final_reward"]]
                base = sum(steps) / len(steps)                       # mean of per-step + final
            rewards.append(max(0.0, base + FMT_W * fmt))
        return rewards
    return reward_fn


def smoke_test_reward_parse(model, proc, examples, arm, n=4):
    """Plan mandate: validate reward parsing against the LIVE chat template before RL.

    Generate a few completions with the actual model+template, run them through the
    reward function, and print the parse so we can confirm the reward server reads real
    generations (not just synthetic gold traces).
    """
    reward_fn = build_reward_fn(arm)
    print(f"[smoke] validating reward parse on {n} live generations, arm={arm}")
    for ex in examples[:n]:
        imgs = [Image.open(p).convert("RGB") for p in ex["images"]]
        content = [{"type": "image", "image": im} for im in imgs] + [{"type": "text", "text": ex["question"]}]
        text = proc.apply_chat_template([{"role": "user", "content": content}],
                                        tokenize=False, add_generation_prompt=True)
        inp = proc(text=[text], images=[imgs], return_tensors="pt", padding=True).to(model.device)
        with torch.no_grad():
            gen = model.generate(**inp, max_new_tokens=400, do_sample=False)
        out = proc.batch_decode(gen[:, inp["input_ids"].shape[1]:], skip_special_tokens=True)[0]
        r = reward_fn(completions=[out], label=[ex["label"]])[0]
        sc = score_chain(out, ex["label"])
        print(f"  {ex['material_id']}: reward={r:.3f} fmt={sc['format_reward']} "
              f"final={sc['final_reward']} steps={ {k:round(v,2) for k,v in sc['per_step'].items()} }")
        print(f"    gen head: {out[:80]!r}")
    print("[smoke] if rewards are non-degenerate and parse matches the generations, GRPO can proceed.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=["B3", "V2a", "V2b"])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--sft-adapter", required=True)
    ap.add_argument("--data-dir", default="data/e2")
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="Qwen/Qwen3-VL-8B-Instruct")
    ap.add_argument("--group-size", type=int, default=8)
    ap.add_argument("--max-steps", type=int, default=200)
    ap.add_argument("--lr", type=float, default=1e-6)
    ap.add_argument("--beta", type=float, default=0.04, help="KL coeff to SFT reference (calibration knob)")
    ap.add_argument("--train-file", default="train.jsonl", help="jsonl under data-dir for prompts")
    ap.add_argument("--max-pixels", type=int, default=200704)
    ap.add_argument("--smoke", action="store_true", help="validate reward parse then exit")
    args = ap.parse_args()

    from transformers import AutoProcessor, BitsAndBytesConfig, Qwen3VLForConditionalGeneration
    from peft import PeftModel

    proc = AutoProcessor.from_pretrained(args.model, max_pixels=args.max_pixels)
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                             bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True)
    base = Qwen3VLForConditionalGeneration.from_pretrained(
        args.model, quantization_config=bnb, torch_dtype=torch.bfloat16,
        device_map="auto", attn_implementation="sdpa")
    # start GRPO from the V1 SFT checkpoint (continue training the same LoRA)
    model = PeftModel.from_pretrained(base, args.sft_adapter, is_trainable=True)

    examples = load_examples(os.path.join(args.data_dir, args.train_file), "V1", args.data_dir)

    if args.smoke:
        model.eval()
        smoke_test_reward_parse(model, proc, examples, args.arm)
        return

    # ---- full GRPO (smoke-validated: reward parse correct, gradient signal present) ----
    from trl import GRPOConfig, GRPOTrainer

    # GRPO trains on the PROMPT (image+question); the reward function scores rollouts.
    # TRL passes through extra dataset columns to the reward fn, so we carry 'label'.
    #
    # CRITICAL: pass a PLAIN LIST of dicts, NOT a datasets.Dataset. Arrow schema
    # unification across the content list forces every part to share one schema, so
    # image parts gain a null 'text' key AND the text part gains a null 'image' key —
    # the stray 'image': None on the text part is counted as a 6th image placeholder
    # while only 5 real images exist, and the template's replacement iterator runs dry
    # (StopIteration in get_text_with_replacements). A plain list keeps each part's
    # dict exactly as written. Absolute image paths (resolved in load_examples).
    def to_prompt(ex):
        imgs = [os.path.abspath(p) for p in ex["images"]]
        content = ([{"type": "image", "image": p} for p in imgs]
                   + [{"type": "text", "text": ex["question"]}])
        return {"prompt": [{"role": "user", "content": content}], "label": ex["label"]}

    ds = [to_prompt(e) for e in examples]

    cfg = GRPOConfig(
        output_dir=args.out,
        num_generations=args.group_size,          # group size for advantage estimation
        max_completion_length=350,                # hard cap — starves the MOTIF repetition trap
        temperature=1.0, top_p=0.95,              # sampling regime validated to give reward variance
        beta=args.beta,                           # KL to the SFT reference (calibration knob)
        learning_rate=args.lr,
        per_device_train_batch_size=args.group_size,
        gradient_accumulation_steps=1,
        max_steps=args.max_steps,
        loss_type="grpo", scale_rewards=True,
        logging_steps=1, save_steps=args.max_steps,
        bf16=True, gradient_checkpointing=True,
        seed=args.seed, use_vllm=False,           # vLLM off on 32GB (HF generate); revisit for full runs
        report_to=[],
    )

    reward_fn = build_reward_fn(args.arm)
    reward_fn.__name__ = f"cocr_reward_{args.arm}"

    trainer = GRPOTrainer(
        model=model,                              # already a trainable PeftModel from the V1 SFT ckpt
        reward_funcs=reward_fn,
        args=cfg,
        train_dataset=ds,
        processing_class=proc,
    )
    t0 = time.time()
    trainer.train()
    trainer.save_model(args.out)
    log = {"arm": args.arm, "seed": args.seed, "max_steps": args.max_steps,
           "elapsed_sec": round(time.time() - t0, 1),
           "log_history": trainer.state.log_history[-5:]}
    json.dump(log, open(os.path.join(args.out, "grpo_log.json"), "w"), indent=1)
    print(f"[train] done arm={args.arm} seed={args.seed} -> {args.out} ({log['elapsed_sec']}s)")


if __name__ == "__main__":
    main()

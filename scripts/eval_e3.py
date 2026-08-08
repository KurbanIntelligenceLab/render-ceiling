#!/usr/bin/env python
"""
E3 matrix evaluation (runs ON the GPU box) — the Gate-2 measurement.

Loads a GRPO'd LoRA adapter and evaluates on the composition-exclusion eval split
(data/e3/eval.jsonl) with SAMPLED / MAJORITY-VOTE decoding (frozen-config requirement:
measure trained behavior, not the greedy MOTIF trap). Per structure: sample K chains at
temperature, take the modal crystal-system answer. Reports micro + macro-F1 and chain
faithfulness (mean per-step reward vs the CIF label), plus per-prediction rows.
"""
import argparse
import json
import os
import sys
from collections import Counter, defaultdict

import torch

sys.path.insert(0, "src")
from cocr.reward import score_chain  # noqa: E402

CS = ["triclinic", "monoclinic", "orthorhombic", "tetragonal", "trigonal", "hexagonal", "cubic"]


def parse_answer(text):
    import re
    m = re.search(r"\[ANSWER\][^\n]*?(triclinic|monoclinic|orthorhombic|tetragonal|"
                  r"trigonal|hexagonal|cubic)", text, re.I)
    if m:
        return m.group(1).lower()
    # fallback: last crystal-system word mentioned
    hits = re.findall(r"(triclinic|monoclinic|orthorhombic|tetragonal|trigonal|hexagonal|cubic)",
                      text.lower())
    return hits[-1] if hits else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--adapter", required=True)
    ap.add_argument("--data-dir", default="data/e3")
    ap.add_argument("--eval-file", default="eval.jsonl")
    ap.add_argument("--model", default="Qwen/Qwen3-VL-8B-Instruct")
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-pixels", type=int, default=200704)
    ap.add_argument("--max-new-tokens", type=int, default=900)
    ap.add_argument("--samples", type=int, default=5, help="K sampled chains / structure (majority vote)")
    ap.add_argument("--temperature", type=float, default=0.7)
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

    rows = [json.loads(l) for l in open(os.path.join(args.data_dir, args.eval_file))]
    sidecar = json.load(open(os.path.join(args.data_dir, "labels_sidecar.json")))
    split = "eval"

    results = []
    for ex in rows:
        imgs = [Image.open(os.path.join(args.data_dir, "renders", split, os.path.basename(p))).convert("RGB")
                for p in ex["images"]]
        content = [{"type": "image", "image": im} for im in imgs]
        content.append({"type": "text", "text": ex["question"]})
        messages = [{"role": "user", "content": content}]
        text = proc.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inp = proc(text=[text], images=[imgs], return_tensors="pt", padding=True).to(model.device)
        votes = []
        sample_faiths = []
        one_text = ""
        lab = sidecar.get(ex["material_id"])
        for _k in range(args.samples):
            with torch.no_grad():
                gen = model.generate(**inp, max_new_tokens=args.max_new_tokens,
                                     do_sample=True, temperature=args.temperature, top_p=0.95)
            ot = proc.batch_decode(gen[:, inp["input_ids"].shape[1]:], skip_special_tokens=True)[0]
            p = parse_answer(ot)
            if p:
                votes.append(p)
            if lab is not None:
                sc = score_chain(ot, lab)
                sample_faiths.append(sum(sc["per_step"].values()) / len(sc["per_step"]))
            one_text = ot
        pred = Counter(votes).most_common(1)[0][0] if votes else None
        # faithfulness = MEAN per-step reward over ALL sampled chains (fair, consistent across arms)
        faith_mean_struct = (sum(sample_faiths) / len(sample_faiths)) if sample_faiths else None
        results.append({"material_id": ex["material_id"], "truth": ex["crystal_system"],
                        "pred": pred, "correct": pred == ex["crystal_system"],
                        "faith": round(faith_mean_struct, 3) if faith_mean_struct is not None else None,
                        "votes": dict(Counter(votes)), "text": one_text[:400]})

    n = len(results)
    ncorr = sum(r["correct"] for r in results)
    micro = ncorr / n if n else 0.0
    by_sys = defaultdict(list)
    for r in results:
        by_sys[r["truth"]].append(r["correct"])
    macro = sum(sum(v) / len(v) for v in by_sys.values()) / len(by_sys) if by_sys else 0.0
    faiths = [r["faith"] for r in results if r["faith"] is not None]
    faith_mean = sum(faiths) / len(faiths) if faiths else None
    per_system = {s: {"n": len(v), "acc": sum(v) / len(v)} for s, v in by_sys.items()}

    out = {"arm": args.arm, "seed": args.seed, "n_eval": n, "samples": args.samples,
           "temperature": args.temperature, "decode": "majority_vote",
           "micro_acc": micro, "macro_acc": macro, "faithfulness": faith_mean,
           "per_system": per_system, "predictions": results}
    json.dump(out, open(args.out, "w"), indent=1)
    print(f"[eval-e3] {args.arm} s{args.seed}: micro={micro:.3f} macro={macro:.3f} "
          f"faith={faith_mean:.3f} ({ncorr}/{n})")


if __name__ == "__main__":
    main()

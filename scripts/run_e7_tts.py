#!/usr/bin/env python
"""
E7 / test_time_scaling — test-time scaling with the CIF-grounded checker (runs ON the GPU box).

Generates K samples per structure ONCE, then scores every selection rule offline from those
same samples. This matters: it means every row (deployable and oracle) sees IDENTICAL
generations, so differences are the selection rule and never sampling luck.

HARD PARTITION (see ledger/test_time_scaling/prereg.md) — a row is one or the other:
  DEPLOYABLE (no ground truth at inference time)
    D1  majority vote over K
    D2  internal step-consistency: do the model's OWN emitted lattice relations imply the
        system it claims? No CIF, no sidecar — purely self-consistency.
    D3  tool-coupled: parse the coordinates/lattice the model EMITS, run spglib on them, and
        prefer samples whose claimed system matches spglib's verdict on their own numbers.
  ORACLE (consults truth; an upper bound, never a deployable claim)
    O1  rerank by the pipeline-truth geometry-step score (the calibration AUC 0.81 signal)
    O2  best-of-K by final correctness (absolute ceiling)

Eval runs at max_pixels=200704 (416x416 effective) — MATCHED TO TRAINING, per resolution_audit's
demonstrated train/test mismatch artifact. effective_resolution is logged in the output.

Usage:
  python scripts/run_e7_tts.py --arm V2b --seed 0 --adapter adapters_e3m/V2b_s0 \
    --data-dir data/e3 --k 8 --out e7/gen_V2b_s0.json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter

SYSTEMS = ["cubic", "hexagonal", "monoclinic", "orthorhombic",
           "tetragonal", "triclinic", "trigonal"]
SYS_RE = re.compile(r"\b(" + "|".join(SYSTEMS) + r")\b", re.I)


def parse_answer(text: str) -> str | None:
    """The system the sample CLAIMS: prefer the [ANSWER] line, else last mention."""
    m = re.search(r"\[ANSWER\][^\n]*", text, re.I)
    seg = m.group(0) if m else text
    hits = SYS_RE.findall(seg)
    if not hits and m:
        hits = SYS_RE.findall(text)
    return hits[-1].lower() if hits else None


def parse_emitted_lattice(text: str) -> dict | None:
    """Pull the a,b,c / angles the model EMITTED. Used by D2 and D3 — never the truth."""
    m = re.search(
        r"a\s*=\s*([\d.]+)\s*,\s*b\s*=\s*([\d.]+)\s*,\s*c\s*=\s*([\d.]+)"
        r"[^;\n]*;\s*alpha\s*=\s*([\d.]+)\s*,\s*beta\s*=\s*([\d.]+)\s*,\s*gamma\s*=\s*([\d.]+)",
        text, re.I)
    if not m:
        return None
    a, b, c, al, be, ga = (float(x) for x in m.groups())
    return {"a": a, "b": b, "c": c, "alpha": al, "beta": be, "gamma": ga}


def system_from_metric(lat: dict, atol_ang: float = 1.0, rtol_len: float = 0.02) -> str | None:
    """Which crystal system do THESE emitted numbers imply? (D2/D3 core — no ground truth.)"""
    if not lat:
        return None
    a, b, c = lat["a"], lat["b"], lat["c"]
    al, be, ga = lat["alpha"], lat["beta"], lat["gamma"]

    def is90(x):
        return abs(x - 90) < atol_ang

    def eq(p, q):
        return abs(p - q) / max(p, q) < rtol_len

    n90 = sum(1 for x in (al, be, ga) if is90(x))
    if is90(al) and is90(be) and abs(ga - 120) < atol_ang:
        return "hexagonal"
    if n90 == 3:
        if eq(a, b) and eq(b, c):
            return "cubic"
        if eq(a, b) or eq(b, c) or eq(a, c):
            return "tetragonal"
        return "orthorhombic"
    if eq(al, be) and eq(be, ga) and not is90(al):
        return "trigonal"
    if n90 == 2:
        return "monoclinic"
    return "triclinic"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-VL-8B-Instruct")
    ap.add_argument("--arm", required=True)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--adapter", required=True)
    ap.add_argument("--data-dir", default="data/e3")
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--max-new-tokens", type=int, default=512)
    ap.add_argument("--max-pixels", type=int, default=200704,
                    help="416x416 effective — MATCHED TO TRAINING per resolution_audit")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    import torch
    from peft import PeftModel
    from PIL import Image
    from transformers import (AutoProcessor, BitsAndBytesConfig,
                              Qwen3VLForConditionalGeneration)

    sys.path.insert(0, "src")

    proc = AutoProcessor.from_pretrained(args.model, max_pixels=args.max_pixels)
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16,
                             bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True)
    base = Qwen3VLForConditionalGeneration.from_pretrained(
        args.model, quantization_config=bnb, dtype=torch.bfloat16, device_map="auto")
    model = PeftModel.from_pretrained(base, args.adapter)
    model.eval()

    rows = [json.loads(line) for line in open(os.path.join(args.data_dir, "eval.jsonl"))]
    torch.manual_seed(args.seed)

    # record the effective resolution FROM the live processor, never by formula
    probe = Image.open(os.path.join(args.data_dir, "renders", "eval",
                                    os.path.basename(rows[0]["images"][0]))).convert("RGB")
    g = proc.image_processor(images=[probe], return_tensors="pt")["image_grid_thw"][0].tolist()
    ps = getattr(proc.image_processor, "patch_size", 16)
    ms = getattr(proc.image_processor, "merge_size", 2)
    eff = {"max_pixels": args.max_pixels, "grid_thw": g, "patch_size": ps, "merge_size": ms,
           "effective_px": [g[1] * ps, g[2] * ps],
           "visual_tokens_per_view": g[1] * g[2] // (ms * ms),
           "n_views": len(rows[0]["images"])}
    print(f"[res] {eff}", flush=True)

    out = []
    for i, ex in enumerate(rows):
        imgs = [Image.open(os.path.join(args.data_dir, "renders", "eval",
                                        os.path.basename(p))).convert("RGB")
                for p in ex["images"]]
        msg = [{"role": "user", "content": [{"type": "image"} for _ in imgs]
                + [{"type": "text", "text": ex["question"]}]}]
        prompt = proc.apply_chat_template(msg, tokenize=False, add_generation_prompt=True)
        inp = proc(text=[prompt], images=imgs, return_tensors="pt").to(model.device)

        samples = []
        for _k in range(args.k):
            with torch.no_grad():
                gen = model.generate(**inp, do_sample=True, temperature=args.temperature,
                                     top_p=0.95, max_new_tokens=args.max_new_tokens)
            txt = proc.decode(gen[0][inp["input_ids"].shape[1]:], skip_special_tokens=True)
            lat = parse_emitted_lattice(txt)
            samples.append({
                "claim": parse_answer(txt),
                "emitted_lattice": lat,
                "metric_implies": system_from_metric(lat) if lat else None,
                "text": txt,           # FULL text stored (calibration logged truncation as a debt)
            })
        out.append({"material_id": ex["material_id"], "truth": ex["crystal_system"],
                    "samples": samples})
        if (i + 1) % 25 == 0:
            print(f"[gen] {i+1}/{len(rows)}", flush=True)

    json.dump({"arm": args.arm, "seed": args.seed, "k": args.k,
               "temperature": args.temperature, "max_new_tokens": args.max_new_tokens,
               "effective_resolution": eff, "records": out},
              open(args.out, "w"))
    print(f"[done] wrote {args.out} ({len(out)} structures x {args.k} samples)", flush=True)


if __name__ == "__main__":
    main()

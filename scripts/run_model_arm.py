#!/usr/bin/env python
"""Unified model-arm runner for the remaining open experiments (G3, G4, G5, G6).

One code path for every arm so the new results are comparable to the released ones:
same frozen prompt text, same K=3 majority vote, same per-structure scoring, same
output schema as release/predictions/*.json.

Arms
  r4       images -> crystal system            (the frozen main_zeroshot prompt)
  r3       coordinates-as-text -> crystal system (no images)

Prompt variants (G6) paraphrase ONLY the task wording; the answer format line is held
fixed, because changing it would confound prompt sensitivity with parse failure.

Reasoning budgets (G4) are passed through as OpenRouter's `reasoning` field. Every
previously released arm sent no such field and therefore ran at the provider default;
the `default` setting here reproduces that, and is the control.

Renders are regenerated from local CIFs under the frozen protocol (conventional cell,
2x2x2 supercell, px=768, radii=0.5), which reproduces the stored detector measurements
exactly (see results/detector_characterisation).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request
import warnings
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "src"))
ROOT = os.path.dirname(HERE)

from pymatgen.core import Structure

from cocr.render import conventional_cell, render_views, VIEW_ORDER
from cocr.zeroshot import _img_block, score_crystal_system, OPENROUTER_URL

SYSTEMS = ["triclinic", "monoclinic", "orthorhombic", "tetragonal",
           "trigonal", "hexagonal", "cubic"]

# The frozen prompt, verbatim from release/frozen_prompts.json (id: main_zeroshot),
# plus two paraphrases for the G6 sensitivity sweep. The ANSWER-format line is
# identical in all three by design.
_ANSWER = ("Reason briefly, then end with a line exactly of the form:\n"
           "ANSWER: <one crystal system>")

PROMPTS = {
    "frozen": (
        "You are shown {n} ball-and-stick rendering(s) of the SAME crystal structure's "
        "conventional unit cell, viewed from different fixed camera angles. Unit-cell "
        "edges are drawn. Atom colors distinguish chemical elements. Use only what you "
        "can see in the images.\n\n"
        "Identify the CRYSTAL SYSTEM of this structure. Choose exactly one of: "
        "triclinic, monoclinic, orthorhombic, tetragonal, trigonal, hexagonal, cubic.\n"
        + _ANSWER),
    "para1": (
        "The {n} image(s) below show one crystal structure's conventional unit cell, each "
        "rendered from a different fixed viewpoint in ball-and-stick style. The cell edges "
        "are drawn and element identity is encoded by atom colour. Base your answer only "
        "on the images.\n\n"
        "Which of the seven crystal systems does this structure belong to? The options are "
        "triclinic, monoclinic, orthorhombic, tetragonal, trigonal, hexagonal and cubic.\n"
        + _ANSWER),
    "para2": (
        "Below are {n} view(s) of a single crystal's conventional unit cell, drawn as balls "
        "and sticks with the cell edges marked; colours indicate chemical elements. Judge "
        "from the rendered geometry alone.\n\n"
        "Determine the crystal system. Pick exactly one: triclinic, monoclinic, "
        "orthorhombic, tetragonal, trigonal, hexagonal, cubic.\n"
        + _ANSWER),
}

R3_PROMPT = (
    "Below are the atomic positions of a crystal structure's conventional unit cell, "
    "given as element symbols with fractional coordinates, together with the cell "
    "parameters. No images are provided.\n\n{payload}\n\n"
    "Identify the CRYSTAL SYSTEM. Choose exactly one of: triclinic, monoclinic, "
    "orthorhombic, tetragonal, trigonal, hexagonal, cubic.\n" + _ANSWER)


def coords_as_text(conv: Structure, max_atoms: int = 200) -> str:
    lat = conv.lattice
    head = (f"a={lat.a:.4f} b={lat.b:.4f} c={lat.c:.4f} "
            f"alpha={lat.alpha:.3f} beta={lat.beta:.3f} gamma={lat.gamma:.3f}")
    lines = [f"{s.specie} {s.frac_coords[0]:.4f} {s.frac_coords[1]:.4f} {s.frac_coords[2]:.4f}"
             for s in conv[:max_atoms]]
    return head + "\n" + "\n".join(lines)


def call(model, messages, reasoning=None, max_tokens=900, temperature=0.7,
         retries=4, timeout=180):
    """One OpenRouter chat call. `reasoning=None` sends NO reasoning field, which is
    what every previously released arm did."""
    key = os.environ["OPENROUTER_API_KEY"]
    payload = {"model": model, "messages": messages,
               "max_tokens": max_tokens, "temperature": temperature}
    if reasoning is not None:
        payload["reasoning"] = reasoning
    body = json.dumps(payload).encode()
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                OPENROUTER_URL, data=body,
                headers={"Authorization": f"Bearer {key}",
                         "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                d = json.load(r)
            ch = d["choices"][0]["message"]
            txt = ch.get("content") or ""
            u = d.get("usage", {})
            if not txt:
                last = "empty_content"
            else:
                return {"text": txt, "ok": True,
                        "in": u.get("prompt_tokens", 0), "out": u.get("completion_tokens", 0),
                        "cost": u.get("cost", 0.0)}
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:120]}"
        time.sleep(3 * (attempt + 1))
    return {"text": "", "ok": False, "error": last, "in": 0, "out": 0, "cost": 0.0}


def parse_system(text: str) -> str | None:
    for line in reversed((text or "").strip().splitlines()):
        s = line.strip().lower()
        if s.startswith("answer:"):
            s = s.split(":", 1)[1].strip()
            for sysname in SYSTEMS:
                if sysname in s:
                    return sysname
    low = (text or "").lower()
    hits = [s for s in SYSTEMS if s in low]
    return hits[-1] if len(set(hits)) == 1 else None


def one_structure(args):
    mid, cif, truth, model, arm, variant, K, reasoning, rdir = args
    try:
        conv = conventional_cell(Structure.from_str(cif, fmt="cif"))
    except Exception as e:
        return {"material_id": mid, "truth": truth, "pred": None,
                "error": f"{type(e).__name__}: {e}"}

    if arm == "r4":
        d = os.path.join(rdir, mid)
        os.makedirs(d, exist_ok=True)
        paths = render_views(conv, d, f"MP_{mid}", supercell=(2, 2, 2))
        imgs = [paths[v] for v in VIEW_ORDER]
        text = PROMPTS[variant].format(n=len(imgs))
        content = [{"type": "text", "text": text}] + [_img_block(p) for p in imgs]
    else:
        text = R3_PROMPT.format(payload=coords_as_text(conv))
        content = [{"type": "text", "text": text}]
        d = None

    votes, toks_in, toks_out, cost, errs = [], 0, 0, 0.0, []
    for _ in range(K):
        r = call(model, [{"role": "user", "content": content}], reasoning=reasoning)
        toks_in += r["in"]; toks_out += r["out"]; cost += r.get("cost", 0.0)
        if r["ok"]:
            votes.append(parse_system(r["text"]))
        else:
            errs.append(r.get("error"))

    if d:
        for f in os.listdir(d):
            os.remove(os.path.join(d, f))
        os.rmdir(d)

    good = [v for v in votes if v]
    pred = Counter(good).most_common(1)[0][0] if good else None
    return {"material_id": mid, "truth": truth, "pred": pred,
            "votes": votes, "correct": bool(pred == truth),
            "tokens_in": toks_in, "tokens_out": toks_out, "cost_usd": round(cost, 6),
            "errors": errs or None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--arm", choices=["r4", "r3"], default="r4")
    ap.add_argument("--variant", choices=list(PROMPTS), default="frozen")
    ap.add_argument("--K", type=int, default=3)
    ap.add_argument("--reasoning", default="", help="JSON for OpenRouter's reasoning field; empty = send none")
    ap.add_argument("--ids", required=True, help="JSON list of material_ids")
    ap.add_argument("--structures", required=True)
    ap.add_argument("--labels", required=True, help="labels sidecar or eval.jsonl")
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    ids = json.load(open(args.ids))
    if args.limit:
        ids = ids[:args.limit]
    S = json.load(open(args.structures))

    if args.labels.endswith(".jsonl"):
        truth = {json.loads(l)["material_id"]: json.loads(l)["crystal_system"]
                 for l in open(args.labels)}
    else:
        truth = {m: r["crystal_system"] for m, r in json.load(open(args.labels)).items()}

    reasoning = json.loads(args.reasoning) if args.reasoning else None
    rdir = f"/tmp/rc_arm_{os.getpid()}"
    os.makedirs(rdir, exist_ok=True)

    jobs = [(m, S[m]["cif"], truth[m], args.model, args.arm, args.variant,
             args.K, reasoning, rdir) for m in ids if m in S and m in truth]
    print(f"{args.model} | arm={args.arm} variant={args.variant} K={args.K} "
          f"reasoning={reasoning} | {len(jobs)} structures", flush=True)

    preds, t0 = [], time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        for i, r in enumerate(ex.map(one_structure, jobs), 1):
            preds.append(r)
            if i % 25 == 0:
                k = sum(1 for p in preds if p.get("correct"))
                c = sum(p.get("cost_usd", 0) for p in preds)
                print(f"  {i}/{len(jobs)}  acc {k/i:.4f}  ${c:.2f}  {time.time()-t0:.0f}s", flush=True)

    scored = [p for p in preds if p.get("pred") is not None]
    k = sum(1 for p in preds if p.get("correct"))
    out = {
        "model": args.model, "arm": args.arm, "prompt_variant": args.variant,
        "K": args.K, "reasoning": reasoning,
        "n": len(preds), "k": k, "micro": round(k / max(len(preds), 1), 4),
        "n_parsed": len(scored), "unanswered": len(preds) - len(scored),
        "tokens_in": sum(p.get("tokens_in", 0) for p in preds),
        "tokens_out": sum(p.get("tokens_out", 0) for p in preds),
        "cost_usd": round(sum(p.get("cost_usd", 0) for p in preds), 4),
        "elapsed_s": round(time.time() - t0, 1),
        "scored": True,
        "predictions": preds,
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    json.dump(out, open(args.out, "w"))
    print(f"DONE {args.model} {args.arm}/{args.variant}: {k}/{len(preds)} = {out['micro']} "
          f"| ${out['cost_usd']} | {out['elapsed_s']}s -> {args.out}", flush=True)


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""
E0 — Pipeline validation driver -> ledger/pipeline/

Runs the four E0 checks (label correctness, tolerance flip rate, metadata-leakage
guard, human-solvability subset) on a stratified sample drawn from BOTH sources
(Materials Project + JARVIS-DFT), and writes:
    ledger/pipeline/results.json     — full audit table + summary
    ledger/pipeline/samples/         — a stratified render subset for human/vision check
    ledger/pipeline/run.txt          — provenance
The finding.md is written after inspecting results (pass condition >98% agreement).
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import warnings
warnings.filterwarnings("ignore")

from cocr.data import fetch_mp_stratified, fetch_jarvis_stratified
from cocr.audit import audit_sample

LEDGER = os.path.join(os.path.dirname(__file__), "..", "ledger", "pipeline")
RENDER_ROOT = os.path.join(os.path.dirname(__file__), "..", "data", "renders", "e0")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-system", type=int, default=7,
                    help="structures per crystal system per source (7*7*2 ~= 98)")
    ap.add_argument("--min-sites", type=int, default=2)
    ap.add_argument("--max-sites", type=int, default=16)
    ap.add_argument("--no-render", action="store_true",
                    help="labels-only run (for CI extension); skips rendering + leakage")
    ap.add_argument("--out", default="results.json", help="results filename in ledger dir")
    args = ap.parse_args()

    t0 = time.time()
    print(f"[E0] fetching MP stratified ({args.per_system}/system)...")
    mp = fetch_mp_stratified(args.per_system, num_elements=(2, 4),
                             num_sites=(args.min_sites, args.max_sites))
    print(f"[E0] MP: {len(mp)} structures")

    print(f"[E0] fetching JARVIS stratified ({args.per_system}/system)...")
    jv = fetch_jarvis_stratified(args.per_system, min_sites=args.min_sites,
                                 max_sites=args.max_sites)
    print(f"[E0] JARVIS: {len(jv)} structures")

    records = mp + jv
    mode = "label-only" if args.no_render else "label + render + leakage"
    print(f"[E0] auditing {len(records)} structures ({mode})...")
    res = audit_sample(records, RENDER_ROOT, render_supercell=(2, 2, 2),
                       do_render=not args.no_render)

    os.makedirs(LEDGER, exist_ok=True)
    res["meta"] = {
        "per_system": args.per_system,
        "min_sites": args.min_sites,
        "max_sites": args.max_sites,
        "n_mp": len(mp),
        "n_jarvis": len(jv),
        "elapsed_sec": round(time.time() - t0, 1),
    }
    with open(os.path.join(LEDGER, args.out), "w") as f:
        json.dump(res, f, indent=1)

    s = res["summary"]
    print("\n===== E0 SUMMARY =====")
    print(json.dumps(s, indent=1))
    print("======================")

    with open(os.path.join(LEDGER, "run.txt"), "w") as f:
        f.write(f"E0 pipeline validation\n")
        f.write(f"sources: MP ({len(mp)}) + JARVIS ({len(jv)})\n")
        f.write(f"per_system={args.per_system} sites={args.min_sites}-{args.max_sites}\n")
        f.write(f"elapsed={res['meta']['elapsed_sec']}s\n")


if __name__ == "__main__":
    main()

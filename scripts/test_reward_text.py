#!/usr/bin/env python
"""
Adversarial + gold regression test for the A4 text reward scorer.

Every case here corresponds to a defect that was ACTUALLY FOUND during development, before
any training run. The reward function decides what the process arms optimize, so a hole in
it manufactures a fake result. Run this before any A4 training job.

  python scripts/test_reward_text.py --data data/a4_text/train.jsonl
"""
from __future__ import annotations

import argparse, json, os, sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from cocr.reward_text import score_chain, score_outcome, safe_eval, _to_frac  # noqa: E402

LAB = {"question": "Natalia sold clips to 48 friends in April, and then she sold half as "
                   "many clips in May. How many clips did she sell altogether?",
       "answer": "72"}

# (name, chain, label, predicate on mean per-step reward, why this case exists)
CASES = [
    ("gold_wellformed",
     "[PLAN] Find May sales then total.\n[STEP] 48 / 2 = 24\n[STEP] 48 + 24 = 72\n[ANSWER] 72",
     LAB, lambda m: m == 1.0,
     "legitimate reasoning must earn FULL credit; an early grounding rule gave it 0.625"),
    ("longer_gold",
     "[PLAN] Compute weekly then subtract.\n[STEP] 15 * 4 = 60\n[STEP] 60 - 12 = 48\n"
     "[STEP] 48 / 2 = 24\n[ANSWER] 24",
     {"question": "15 items cost 4 each, 12 returned, halve it", "answer": "24"},
     lambda m: m == 1.0, "multi-step chaining on own results must earn full credit"),
    ("HACK_step_spam_grounded",
     "[PLAN] x\n" + "[STEP] 48 - 48 = 0\n" * 5 + "[ANSWER] 5",
     LAB, lambda m: m == 0.0,
     "THE ORIGINAL EXPLOIT: scored a PERFECT 1.000 on a wrong answer. Self-cancellation "
     "repeated five times. Would have let the process arms farm dense reward."),
    ("HACK_trivial_true_steps",
     "[PLAN] x\n[STEP] 1 + 1 = 2\n[STEP] 2 + 2 = 4\n[STEP] 3 + 3 = 6\n[ANSWER] 5",
     LAB, lambda m: m <= 0.25,
     "free-constant identities that touch no problem quantity; a later fix regressed this "
     "to 0.500 because a step's own result bootstrapped its grounding"),
    ("HACK_repeat_valid_step",
     "[PLAN] x\n" + "[STEP] 48 / 2 = 24\n" * 3 + "[ANSWER] 5",
     LAB, lambda m: m <= 0.34, "a real step repeated earns credit once, not three times"),
    ("never_terminates", "[PLAN] x\n" + "[STEP] 48 / 2 = 24\n" * 3,
     LAB, lambda m: True, "format must be -1 (the repetition trap)"),
    ("injection_attempt",
     "[PLAN] x\n[STEP] __import__('os').system('ls') = 1\n[ANSWER] 72",
     LAB, lambda m: m == 0.0, "scorer must never execute model text"),
    ("div_by_zero", "[PLAN] x\n[STEP] 48 / 0 = 0\n[ANSWER] 72",
     LAB, lambda m: m == 0.0, "must be unscoreable, not an exception"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/a4_text/train.jsonl")
    ap.add_argument("--n-gold", type=int, default=2000)
    ap.add_argument("--min-gold-faith", type=float, default=0.85,
                    help="human gold chains must score at least this on average")
    args = ap.parse_args()

    failures = []

    print("=== adversarial cases ===")
    for name, chain, lab, pred, why in CASES:
        sc = score_chain(chain, lab)
        ps = sc["per_step"]
        m = sum(ps) / len(ps) if ps else 0.0
        ok = pred(m)
        print(f"  {'PASS' if ok else 'FAIL'}  {name:28s} mean_step={m:.3f} fmt={sc['format_reward']:+.0f}")
        if not ok:
            failures.append(f"{name}: mean_step={m:.3f} — {why}")

    # format-specific assertions
    if score_chain(CASES[5][1], LAB)["format_reward"] != -1.0:
        failures.append("never_terminates: format reward must be -1.0")
    if safe_eval("__import__('os').system('ls')") is not None:
        failures.append("safe_eval executed non-arithmetic input")
    if safe_eval("0.1 + 0.2") != _to_frac("0.3"):
        failures.append("safe_eval is not exact (float contamination)")

    print("\n=== human gold chain regression ===")
    rows = [json.loads(l) for l in open(args.data)][: args.n_gold]
    faith, aud, nsteps = [], Counter(), 0
    for r in rows:
        sc = score_chain(r["gold_chain"], r)
        ps = sc["per_step"]
        faith.append(sum(ps) / len(ps) if ps else 0.0)
        if sc["final_reward"] != 1.0:
            aud["gold_final_wrong"] += 1
        for lg in sc["log"]["steps"]:
            nsteps += 1
            if lg["reward"] == 1.0:
                aud["full"] += 1
            elif lg.get("verdict"):
                aud[lg["verdict"]] += 1
            elif lg.get("trivial"):
                aud["trivial"] += 1
            elif not lg.get("novel"):
                aud["repeat"] += 1
            elif not lg.get("grounded"):
                aud["ungrounded"] += 1
            else:
                aud["arith_false"] += 1
    mean_gold = sum(faith) / len(faith)
    print(f"  n={len(rows)} chains, {nsteps} steps, mean step-faithfulness {mean_gold:.4f}")
    for k, v in aud.most_common():
        print(f"    {k:18s} {v:6d}  {v/nsteps:6.1%}")
    if mean_gold < args.min_gold_faith:
        failures.append(f"gold faithfulness {mean_gold:.4f} < {args.min_gold_faith}")

    print()
    if failures:
        print("FAILURES:")
        for f in failures:
            print("  -", f)
        sys.exit(1)
    print(f"ALL PASS (gold={mean_gold:.4f})")


if __name__ == "__main__":
    main()

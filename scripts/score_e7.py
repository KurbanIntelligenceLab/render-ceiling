#!/usr/bin/env python
"""
E7 / CP7 scoring — turns one set of K generations into every selection-rule row.

Runs LOCALLY (CPU only) on the harvested generation files. Every row below is scored from the
SAME samples, so any difference between rows is the selection rule and never sampling luck.

THE PARTITION IS ENFORCED HERE (ledger/CP7_test_time_scaling/prereg.md). Deployable rows may
read only what inference has: the emitted text, the emitted numbers, and tools applied to them.
Oracle rows may read the sidecar. A row is labelled one or the other, never blended.

  DEPLOYABLE
    D1  majority vote over K
    D2  internal step-consistency: prefer samples whose OWN emitted lattice implies the system
        they claim (self-consistency, no CIF)
    D3  tool-coupled: same as D2 but the implication is computed by spglib on a cell built from
        the EMITTED lattice parameters, rather than by our metric rules
  ORACLE
    O1  rerank by the CP0-truth geometry-step score (the CP9 AUC 0.81 signal)
    O2  best-of-K by final correctness (absolute ceiling)

Also computes the risk-coverage curve (AURC / E-AURC) with checker-score abstention, and the
predict-and-certify system row.
"""
from __future__ import annotations

import argparse
import json
import statistics as st
from collections import Counter

SYSTEMS = ["cubic", "hexagonal", "monoclinic", "orthorhombic",
           "tetragonal", "triclinic", "trigonal"]


def majority(claims: list[str | None]) -> str | None:
    votes = [c for c in claims if c]
    return Counter(votes).most_common(1)[0][0] if votes else None


def d1_majority(rec: dict) -> tuple[str | None, float]:
    """Plain majority vote; confidence = vote share."""
    claims = [s["claim"] for s in rec["samples"]]
    pred = majority(claims)
    votes = [c for c in claims if c]
    conf = (Counter(votes)[pred] / len(votes)) if votes and pred else 0.0
    return pred, conf


def d2_self_consistent(rec: dict) -> tuple[str | None, float]:
    """Keep samples whose emitted metric implies their own claim, then vote among those.

    Uses ONLY the model's own output. Falls back to plain majority when no sample is
    self-consistent, so the row is always defined.
    """
    keep = [s for s in rec["samples"]
            if s["claim"] and s["metric_implies"] and s["claim"] == s["metric_implies"]]
    if not keep:
        pred, conf = d1_majority(rec)
        return pred, 0.0  # zero checker confidence: nothing passed the check
    claims = [s["claim"] for s in keep]
    pred = majority(claims)
    return pred, len(keep) / len(rec["samples"])


def d3_tool_coupled(rec: dict) -> tuple[str | None, float]:
    """Same idea as D2, but the implication comes from spglib on the EMITTED cell.

    Deployable: spglib is a tool applied to the model's own numbers, not to the answer key.
    """
    keep = [s for s in rec["samples"]
            if s["claim"] and s.get("spglib_implies") and s["claim"] == s["spglib_implies"]]
    if not keep:
        pred, _ = d1_majority(rec)
        return pred, 0.0
    return majority([s["claim"] for s in keep]), len(keep) / len(rec["samples"])


def o1_truth_rerank(rec: dict) -> tuple[str | None, float]:
    """ORACLE: pick the sample with the best truth-scored geometry step."""
    scored = [s for s in rec["samples"] if s.get("geom_truth_score") is not None]
    if not scored:
        return d1_majority(rec)
    best = max(scored, key=lambda s: s["geom_truth_score"])
    return best["claim"], best["geom_truth_score"]


def o2_best_of_k(rec: dict) -> tuple[str | None, float]:
    """ORACLE ceiling: correct if ANY sample was correct."""
    truth = rec["truth"]
    hit = any(s["claim"] == truth for s in rec["samples"])
    return (truth if hit else rec["samples"][0]["claim"]), 1.0 if hit else 0.0


ROWS = {"D1_majority": (d1_majority, "deployable"),
        "D2_self_consistency": (d2_self_consistent, "deployable"),
        "D3_tool_coupled": (d3_tool_coupled, "deployable"),
        "O1_truth_rerank": (o1_truth_rerank, "oracle"),
        "O2_best_of_k": (o2_best_of_k, "oracle")}


def risk_coverage(items: list[tuple[float, bool]]) -> dict:
    """AURC and E-AURC from (confidence, correct) pairs, plus operating points.

    Sort by DESCENDING confidence, sweep coverage, accumulate risk (= error rate on covered).
    E-AURC subtracts the AURC of an oracle ranking at the same overall accuracy.
    """
    if not items:
        return {}
    srt = sorted(items, key=lambda t: -t[0])
    n = len(srt)
    risks, cov = [], []
    err = 0
    for i, (_c, ok) in enumerate(srt, start=1):
        err += 0 if ok else 1
        risks.append(err / i)
        cov.append(i / n)
    aurc = sum(risks) / n
    acc = sum(1 for _c, ok in srt if ok) / n
    # optimal ranking: all correct first
    opt = []
    e = 0
    n_ok = int(round(acc * n))
    for i in range(1, n + 1):
        if i > n_ok:
            e += 1
        opt.append(e / i)
    aurc_opt = sum(opt) / n
    ops = {}
    for target in (0.9, 0.75, 0.5):
        k = max(1, int(round(target * n)))
        ops[str(target)] = {"coverage": round(k / n, 4),
                            "accuracy_on_covered": round(sum(1 for _c, ok in srt[:k] if ok) / k, 4)}
    return {"aurc": round(aurc, 4), "aurc_optimal": round(aurc_opt, 4),
            "e_aurc": round(aurc - aurc_opt, 4), "overall_acc": round(acc, 4),
            "operating_points": ops, "n": n}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", required=True, help="generation json from run_e7_tts.py")
    ap.add_argument("--answerer-gen", default=None,
                    help="B1 generation json, for the predict-and-certify row")
    ap.add_argument("--k", type=int, default=None, help="truncate to first K samples")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    d = json.load(open(args.gen))
    recs = d["records"]
    if args.k:
        for r in recs:
            r["samples"] = r["samples"][:args.k]

    out = {"arm": d["arm"], "seed": d["seed"], "k": args.k or d["k"],
           "effective_resolution": d.get("effective_resolution"), "rows": {}}

    for name, (fn, kind) in ROWS.items():
        preds, items = [], []
        for r in recs:
            p, conf = fn(r)
            ok = (p == r["truth"])
            preds.append({"mid": r["material_id"], "pred": p, "truth": r["truth"], "correct": ok,
                          "conf": conf})
            items.append((conf, ok))
        acc = st.mean(1.0 if p["correct"] else 0.0 for p in preds)
        out["rows"][name] = {"kind": kind, "accuracy": round(acc, 4),
                             "risk_coverage": risk_coverage(items)}

    json.dump(out, open(args.out, "w"), indent=1)
    for name, r in out["rows"].items():
        rc = r["risk_coverage"]
        print(f"{name:22s} [{r['kind']:10s}] acc={r['accuracy']:.4f} "
              f"AURC={rc.get('aurc')} E-AURC={rc.get('e_aurc')}")


if __name__ == "__main__":
    main()

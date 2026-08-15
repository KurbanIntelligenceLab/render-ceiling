#!/usr/bin/env python
"""
expert_study expert-study scorer. Scores one or more returned response sheets against ANSWER_KEY.json,
applies the pre-registered authenticity screen (S1-S4), and reports the hierarchical levels.

Usage: python score_expert.py --key ANSWER_KEY.json --sheets r1.csv r2.csv r3.csv --out results.json
"""
import argparse, csv, json, math, collections

SYS = ["cubic","hexagonal","monoclinic","orthorhombic","tetragonal","triclinic","trigonal"]
CHANCE = 1/7


def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k/n; d = 1+z*z/n; c = p+z*z/(2*n)
    m = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))
    return ((c-m)/d, (c+m)/d)


def screen(rows, key):
    """Pre-registered authenticity screen. Returns (admit: bool, flags: dict)."""
    n = len(rows)
    ok = [r["crystal_system"].strip().lower() == key[r["item_id"]]["truth_crystal_system"] for r in rows]
    acc = sum(ok)/n
    lo, _ = wilson(sum(ok), n)
    s1 = lo > CHANCE                                    # beats chance at the CI lower bound

    byc = collections.defaultdict(lambda: [0, 0])
    for r, o in zip(rows, ok):
        try:
            c = int(r["confidence_1_to_5"])
        except (ValueError, KeyError):
            continue
        byc[c][1] += 1; byc[c][0] += o
    levels = sorted(byc)
    accs = [byc[c][0]/byc[c][1] for c in levels]
    # positive association: higher confidence -> higher accuracy
    s2 = len(levels) < 2 or (accs[-1] >= accs[0])

    mismatch = 0
    for r in rows:
        nt = r.get("notes", "").lower()
        ans = r["crystal_system"].strip().lower()
        named = [s for s in SYS if s in nt]
        if named and ans not in named:
            mismatch += 1
    # uniformly self-consistent notes AT chance accuracy is the confabulation signature
    s3 = not (mismatch == 0 and acc < CHANCE*1.5)

    try:
        secs = [int(r["seconds_spent"]) for r in rows]
        s4 = not (all(s % 5 == 0 for s in secs) and len(set(secs)) <= n/4)
    except (ValueError, KeyError):
        s4 = True

    flags = {"S1_beats_chance": s1, "S2_confidence_tracks_correctness": s2,
             "S3_notes_not_uniformly_selfconsistent_at_chance": s3,
             "S4_timing_not_on_grid": s4,
             "accuracy": round(acc, 4), "wilson_lo": round(lo, 4),
             "confidence_profile": {str(c): round(byc[c][0]/byc[c][1], 3) for c in levels}}
    admit = s1 and (s2 and s3 and s4)
    return admit, flags


def score_sheet(rows, key):
    n = len(rows)
    l1 = sum(1 for r in rows
             if r["crystal_system"].strip().lower() == key[r["item_id"]]["truth_crystal_system"])
    per = collections.defaultdict(lambda: [0, 0])
    confus = collections.Counter()
    for r in rows:
        t = key[r["item_id"]]["truth_crystal_system"]
        g = r["crystal_system"].strip().lower()
        per[t][1] += 1; per[t][0] += (g == t)
        if g != t:
            confus[f"{t}->{g}"] += 1
    blanks = sum(1 for r in rows if not r.get("point_group_or_blank", "").strip())
    lo, hi = wilson(l1, n)
    return {"n": n, "L1_correct": l1, "L1_accuracy": round(l1/n, 4),
            "L1_wilson95": [round(lo, 4), round(hi, 4)],
            "per_system": {s: f"{per[s][0]}/{per[s][1]}" for s in SYS},
            "confusions": dict(confus.most_common(10)),
            "L3_blank_rate": round(blanks/n, 4)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", required=True)
    ap.add_argument("--sheets", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    key = {m["item_id"]: m for m in json.load(open(a.key))}
    out = {"chance": round(CHANCE, 4), "sheets": {}, "admitted": [], "excluded": []}
    for path in a.sheets:
        rows = list(csv.DictReader(open(path)))
        admit, flags = screen(rows, key)
        res = score_sheet(rows, key)
        res["screen"] = flags; res["admitted"] = admit
        out["sheets"][path] = res
        (out["admitted"] if admit else out["excluded"]).append(path)
        print(f"{path}: L1={res['L1_accuracy']:.3f} CI{res['L1_wilson95']} "
              f"{'ADMITTED' if admit else 'EXCLUDED'} {'' if admit else flags}")
    if len(out["admitted"]) >= 3:
        accs = [out["sheets"][p]["L1_accuracy"] for p in out["admitted"]]
        out["human_row"] = {"n_raters": len(accs), "mean": round(sum(accs)/len(accs), 4),
                            "per_rater": accs}
        print(f"\nHUMAN ROW: {out['human_row']}")
    else:
        out["human_row"] = None
        print(f"\nNO HUMAN ROW: only {len(out['admitted'])} admitted sheet(s); protocol requires >=3")
    json.dump(out, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""
E0.5 human-expert study packet builder -> ledger/identifiability/expert_packet/

Assembles a turnkey blind study for crystallographers to close Gate 0:
  renders/          50 structures x 4 blind views (frozen view set), blinded IDs
  answer_sheet.csv  one row per structure: expert fills crystal_system, point_group,
                    space_group, confidence (1-5); NO symmetry hints present
  scoring_rubric.md hierarchical scoring with coarse-credit rules
  answer_key.csv    ground truth (kept separate; for scoring AFTER responses)
  manifest.json     blind_id -> {source, material_id} provenance (sealed)

Blinding: structures are shuffled and assigned opaque IDs (S01..S50). Render
filenames are <blind_id>_v0..v3.png — index only, no view name, no material_id, no
symmetry. The view index->name map is fixed and identical for every structure, so it
carries no information.
"""
import argparse, csv, json, os, random, sys, warnings
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
warnings.filterwarnings("ignore")

from cocr.data import fetch_mp_stratified, fetch_jarvis_stratified
from cocr.render import render_views, conventional_cell, VIEW_ORDER
from cocr.labels import make_labels

LEDGER = os.path.join(os.path.dirname(__file__), "..", "ledger", "identifiability")
PACKET = os.path.join(LEDGER, "expert_packet")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()
    random.seed(args.seed)

    # ~7-8 per system across 7 systems from both sources; stratified for balance.
    per_sys = max(1, args.n // 7 // 2 + 1)
    mp = fetch_mp_stratified(per_sys, num_elements=(2, 4), num_sites=(2, 30))
    jv = fetch_jarvis_stratified(per_sys, min_sites=2, max_sites=30)
    pool = mp + jv
    random.shuffle(pool)

    # keep a stratified 50: cap per system so no system dominates
    by_sys = {}
    chosen = []
    for rc in pool:
        try:
            lab = make_labels(rc["structure"], rc["material_id"], rc["source"])
        except Exception:
            continue
        s = lab["crystal_system"]
        by_sys.setdefault(s, 0)
        if by_sys[s] >= (args.n // 7 + 2):
            continue
        by_sys[s] += 1
        chosen.append((rc, lab))
        if len(chosen) >= args.n:
            break

    os.makedirs(os.path.join(PACKET, "renders"), exist_ok=True)
    manifest, answer_key, sheet = [], [], []
    for i, (rc, lab) in enumerate(chosen, 1):
        bid = f"S{i:02d}"
        conv = conventional_cell(rc["structure"])
        paths = render_views(conv, os.path.join(PACKET, "renders"), bid,
                             supercell=(2, 2, 2))
        # rename to blind index-only names
        for idx, view in enumerate(VIEW_ORDER):
            src = paths[view]
            dst = os.path.join(PACKET, "renders", f"{bid}_v{idx}.png")
            if os.path.abspath(src) != os.path.abspath(dst):
                os.replace(src, dst)
        manifest.append({"blind_id": bid, "source": rc["source"],
                         "material_id": rc["material_id"]})
        answer_key.append({"blind_id": bid, "crystal_system": lab["crystal_system"],
                           "point_group": lab["point_group"],
                           "space_group_number": lab["space_group"]["number"],
                           "space_group_symbol": lab["space_group"]["symbol"]})
        sheet.append({"blind_id": bid, "crystal_system": "", "point_group": "",
                      "space_group_number": "", "space_group_symbol": "",
                      "confidence_1to5": "", "notes": ""})

    # view index->name legend (fixed, information-free)
    legend = {f"v{idx}": view for idx, view in enumerate(VIEW_ORDER)}

    with open(os.path.join(PACKET, "answer_sheet.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(sheet[0].keys())); w.writeheader(); w.writerows(sheet)
    with open(os.path.join(PACKET, "answer_key.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(answer_key[0].keys())); w.writeheader(); w.writerows(answer_key)
    with open(os.path.join(PACKET, "manifest.json"), "w") as f:
        json.dump({"legend": legend, "n": len(chosen), "seed": args.seed,
                   "structures": manifest}, f, indent=1)
    # per-system count for the record
    from collections import Counter
    dist = Counter(a["crystal_system"] for a in answer_key)
    print(f"packet: {len(chosen)} structures, {len(chosen)*4} renders")
    print("system distribution:", dict(dist))


if __name__ == "__main__":
    main()

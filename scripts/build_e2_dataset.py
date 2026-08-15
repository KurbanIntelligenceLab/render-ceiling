#!/usr/bin/env python
"""
E2 dataset builder -> data/e2/

Builds the SFT dataset for the three arms (B1 direct / B2 free-CoT / V1 CoCr chain) on a
stratified held-out sample, DISJOINT from the E0.5/E1 samples (no train/eval leakage). For
each structure: render the frozen 5-view set (conventional cell, 2x2x2 supercell), compute the
pipeline label, and emit one training record per arm sharing the same images+question.

Outputs:
  data/e2/renders/<split>/<stem>_view{0..4}.png
  data/e2/train.jsonl / val.jsonl / test.jsonl   (records: {stem, material_id, source,
     crystal_system, space_group, band_gap, formation_energy_per_atom, images[5], arm,
     question, target})   -- one row per (structure, arm)
  data/e2/manifest.json   (split sizes, per-system counts, provenance, seed, disjointness proof)

Property targets (band_gap, formation_energy_per_atom) are attached for the E2 property task;
they are MP-sourced and carried through even for JARVIS rows (None where unavailable).
"""
import argparse, json, os, sys, time, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import warnings; warnings.filterwarnings("ignore")

from cocr.labels import make_labels
from cocr.render import conventional_cell, render_views, VIEW_SWEEP, VIEWS
from cocr.traces import make_example
from cocr.data import fetch_mp_stratified, fetch_jarvis_stratified

ROOT = os.path.join(os.path.dirname(__file__), "..")
E2 = os.path.join(ROOT, "data", "e2")
ARMS = ["B1", "B2", "V1"]


def _prior_ids():
    """material_ids already used in E0.5 (identifiability) and E1 samples -> exclude for disjointness."""
    used = set()
    for p in ["ledger/identifiability/results.json", "ledger/zeroshot/sample.json"]:
        fp = os.path.join(ROOT, p)
        if not os.path.exists(fp):
            continue
        d = json.load(open(fp))
        rows = d.get("rows") or d.get("structures") or (d.get("summary", {}) or {}).get("rows", [])
        for r in (rows or []):
            mid = r.get("material_id")
            if mid:
                used.add(str(mid))
    return used


def build(args):
    t0 = time.time()
    os.makedirs(E2, exist_ok=True)
    exclude = _prior_ids()
    print(f"[E2] excluding {len(exclude)} material_ids used in identifiability/zeroshot (disjointness)")

    # oversample then filter out prior ids, keep per_system balance across both sources
    mp = fetch_mp_stratified(args.per_system * 3, num_elements=(2, 4), num_sites=(2, args.max_sites))
    jv = fetch_jarvis_stratified(args.per_system * 3, min_sites=2, max_sites=args.max_sites)
    pool = [r for r in (mp + jv) if str(r["material_id"]) not in exclude]
    print(f"[E2] pool after exclusion: {len(pool)} ({sum(r['source']=='MP' for r in pool)} MP, "
          f"{sum(r['source']=='JARVIS' for r in pool)} JARVIS)")

    # rebalance to per_system per source, cap
    from collections import defaultdict
    buckets = defaultdict(list)
    for r in pool:
        buckets[(r["source"], r.get("queried_system", "?"))].append(r)
    chosen = []
    for (src, sysn), rs in buckets.items():
        chosen.extend(rs[:args.per_system])
    print(f"[E2] chosen {len(chosen)} structures")

    # deterministic split by hash(material_id): 70/15/15 train/val/test
    def split_of(mid):
        h = int(hashlib.md5(mid.encode()).hexdigest(), 16) % 100
        return "train" if h < 70 else ("val" if h < 85 else "test")

    records = {"train": [], "val": [], "test": []}
    persys = defaultdict(lambda: defaultdict(int))
    n_ok = 0
    for i, rc in enumerate(chosen):
        try:
            conv = conventional_cell(rc["structure"])
            lab = make_labels(rc["structure"], str(rc["material_id"]), rc["source"])
            if not lab["label_policy"]["keep_for_training"]:
                continue  # honor pipeline frozen quarantine policy
            split = split_of(str(rc["material_id"]))
            stem = f"{rc['source']}_{rc['material_id']}".replace("/", "_")
            rdir = os.path.join(E2, "renders", split)
            paths = render_views(conv, rdir, stem, supercell=(2, 2, 2),
                                 view_names=VIEW_SWEEP[5], view_map=VIEWS)
            img_list = [paths[v] for v in VIEW_SWEEP[5]]
            for arm in ARMS:
                ex = make_example(lab, img_list, arm)
                ex["split"] = split
                ex["space_group"] = lab["space_group"]["number"]
                ex["band_gap"] = rc.get("band_gap")
                ex["formation_energy_per_atom"] = rc.get("formation_energy_per_atom")
                records[split].append(ex)
            persys[split][lab["crystal_system"]] += 1
            n_ok += 1
        except Exception as e:
            print(f"  skip {rc['material_id']}: {type(e).__name__}: {e}")

    for split in ["train", "val", "test"]:
        with open(os.path.join(E2, f"{split}.jsonl"), "w") as f:
            for r in records[split]:
                f.write(json.dumps(r) + "\n")

    manifest = {
        "n_structures": n_ok, "arms": ARMS, "seed": args.seed,
        "split_sizes_structures": {s: len(records[s]) // len(ARMS) for s in records},
        "split_sizes_examples": {s: len(records[s]) for s in records},
        "per_system": {s: dict(persys[s]) for s in persys},
        "excluded_prior_ids": len(exclude),
        "disjoint_from": ["identifiability", "zeroshot"],
        "render": {"views": VIEW_SWEEP[5], "supercell": "2x2x2", "cell": "conventional_standard"},
        "property_targets": ["band_gap", "formation_energy_per_atom"],
        "elapsed_sec": round(time.time() - t0, 1),
    }
    json.dump(manifest, open(os.path.join(E2, "manifest.json"), "w"), indent=1)
    print(f"[E2] wrote {n_ok} structures x {len(ARMS)} arms; splits "
          f"{manifest['split_sizes_structures']}; {manifest['elapsed_sec']}s")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-system", type=int, default=12)
    ap.add_argument("--max-sites", type=int, default=20)
    ap.add_argument("--seed", type=int, default=23)
    build(ap.parse_args())

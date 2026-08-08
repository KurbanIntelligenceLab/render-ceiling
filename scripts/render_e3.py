#!/usr/bin/env python
"""
Render the E3 matrix dataset (data/e3/) with the FROZEN view set.

Structures come from the split manifests + a fetched-by-ID pool. Uses the exact
render config frozen at E0.5: conventional standard cell, 2x2x2 supercell, the 4-view
set, index-only filenames (leakage guard). Writes data/e3/renders/<split>/<stem>_view{0..3}.png
and appends the resolved image paths + question into the split jsonl rows.
"""
import json
import os
import sys
import warnings

warnings.filterwarnings("ignore")
sys.path.insert(0, "src")
from cocr.render import conventional_cell, render_views, VIEW_ORDER  # noqa: E402
from cocr.traces import QUESTION  # noqa: E402

E3 = "data/e3"


def main():
    import argparse
    from mp_api.client import MPRester
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", required=True, choices=["train", "eval"])
    args = ap.parse_args()

    rows = [json.loads(l) for l in open(f"{E3}/{args.split}.jsonl")]
    ids = [r["material_id"] for r in rows]
    # fetch structures by ID (MP)
    struct = {}
    with MPRester(os.environ["MP_API_KEY"]) as m:
        docs = m.materials.summary.search(material_ids=ids, fields=["material_id", "structure"])
        for d in docs:
            struct[str(d.material_id)] = d.structure

    rdir = os.path.join(E3, "renders", args.split)
    out = []
    for i, r in enumerate(rows):
        st = struct.get(r["material_id"])
        if st is None:
            continue
        conv = conventional_cell(st)
        stem = f"{r['source']}_{r['material_id']}"
        paths = render_views(conv, rdir, stem, supercell=(2, 2, 2))
        r["images"] = [paths[v] for v in VIEW_ORDER]  # frozen 5-view order (matches E2/V1 training)
        r["question"] = QUESTION
        out.append(r)
        if (i + 1) % 100 == 0:
            print(f"[render {args.split}] {i+1}/{len(rows)}", flush=True)

    with open(f"{E3}/{args.split}.jsonl", "w") as f:
        for r in out:
            f.write(json.dumps(r) + "\n")
    print(f"[render {args.split}] done: {len(out)} structures, {len(out)*4} renders")


if __name__ == "__main__":
    main()

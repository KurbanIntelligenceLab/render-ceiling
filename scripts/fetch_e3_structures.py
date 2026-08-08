#!/usr/bin/env python
"""
Re-fetch the atomic structures for the E3 dataset by material_id, and VERIFY that our
spglib labels reproduce the sidecar exactly (the CP0 audit method).

This unblocks two things that both need coordinates, which data/e3/*.jsonl does not carry:
  - item 5: the structure-PROTOTYPE-exclusion split (needs structure matching / prototypes)
  - item 7: E8 external baselines (ALIGNN / CGCNN consume the structure graph)

Writes data/e3/structures.json  {material_id: {"cif": ..., "source": ...}}
Writes data/e3/structure_label_audit.json  the reproduce-the-sidecar audit.

Usage:
  MP_API_KEY=... PYTHONPATH=src python scripts/fetch_e3_structures.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

DATA = Path("data/e3")


def load_ids() -> dict[str, str]:
    ids: dict[str, str] = {}
    for sp in ("train", "eval"):
        for line in open(DATA / f"{sp}.jsonl"):
            r = json.loads(line)
            ids[r["material_id"]] = r["source"]
    return ids


def fetch_mp(mids: list[str]) -> dict[str, str]:
    """Fetch conventional-cell CIFs from Materials Project in batches."""
    from mp_api.client import MPRester

    out: dict[str, str] = {}
    key = os.environ.get("MP_API_KEY")
    if not key:
        sys.exit("MP_API_KEY not set")
    with MPRester(key) as mpr:
        B = 200
        for i in range(0, len(mids), B):
            batch = mids[i : i + B]
            docs = mpr.materials.search(
                material_ids=batch, fields=["material_id", "structure"]
            )
            for d in docs:
                out[str(d.material_id)] = d.structure.to(fmt="cif")
            print(f"  fetched {min(i+B, len(mids))}/{len(mids)}", flush=True)
    return out


def audit(structs: dict[str, str], sidecar: dict) -> dict:
    """Recompute labels from the fetched structures and compare with the sidecar.

    This is the CP0 audit method: the fetched structure must reproduce the SAME
    crystal_system / space_group / bravais_lattice the sidecar recorded, at the same
    frozen tolerance. A mismatch means the structure we are about to hand the GNN
    baselines is not the structure the VLM was labelled against.
    """
    sys.path.insert(0, "src")
    from pymatgen.core import Structure

    from cocr.labels import make_labels

    res = {"n": 0, "match": 0, "mismatch": [], "missing": []}
    for mid, side in sidecar.items():
        cif = structs.get(mid)
        if cif is None:
            res["missing"].append(mid)
            continue
        st = Structure.from_str(cif, fmt="cif")
        lab = make_labels(st, mid, side.get("source", "MP"))
        res["n"] += 1
        same = (
            lab["crystal_system"] == side["crystal_system"]
            and lab["space_group"]["number"] == side["space_group"]["number"]
        )
        if same:
            res["match"] += 1
        else:
            res["mismatch"].append(
                {
                    "material_id": mid,
                    "sidecar": [side["crystal_system"], side["space_group"]["number"]],
                    "refetched": [
                        lab["crystal_system"],
                        lab["space_group"]["number"],
                    ],
                }
            )
    res["match_rate"] = round(res["match"] / res["n"], 5) if res["n"] else None
    res["n_mismatch"] = len(res["mismatch"])
    res["n_missing"] = len(res["missing"])
    res["mismatch"] = res["mismatch"][:50]  # cap the record
    res["missing"] = res["missing"][:50]
    return res


def main() -> None:
    ids = load_ids()
    mp_ids = sorted([k for k, v in ids.items() if v == "MP"])
    other = sorted([k for k, v in ids.items() if v != "MP"])
    print(f"ids: {len(ids)} (MP {len(mp_ids)}, other {len(other)})")
    if other:
        print(f"  NOTE non-MP ids present and NOT fetched by this script: {other[:5]}")

    out_path = DATA / "structures.json"
    if out_path.exists():
        structs = json.load(open(out_path))
        print(f"reusing cached {out_path} ({len(structs)} entries)")
    else:
        structs = {mid: {"cif": c, "source": "MP"} for mid, c in fetch_mp(mp_ids).items()}
        json.dump(structs, open(out_path, "w"))
        print(f"wrote {out_path} ({len(structs)} entries)")

    sidecar = json.load(open(DATA / "labels_sidecar.json"))
    a = audit({k: v["cif"] for k, v in structs.items()}, sidecar)
    json.dump(a, open(DATA / "structure_label_audit.json", "w"), indent=1)
    print(
        f"\nLABEL AUDIT: {a['match']}/{a['n']} reproduce the sidecar "
        f"(rate {a['match_rate']}), mismatches {a['n_mismatch']}, missing {a['n_missing']}"
    )
    if a["n_mismatch"]:
        print("first mismatches:", json.dumps(a["mismatch"][:5], indent=1))


if __name__ == "__main__":
    main()

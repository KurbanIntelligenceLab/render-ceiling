#!/usr/bin/env python
"""
E7 enrichment — add the two fields the scoring rows need, computed from the SAVED generations.

run_e7_tts.py deliberately only records what generation itself produces (the claim, the emitted
lattice, and our metric-rule implication). Two rows need more:

  D3 (DEPLOYABLE, tool-coupled) needs `spglib_implies`: build a cell from the lattice parameters
     the model EMITTED and ask spglib what system it is. This is a tool applied to the model's
     own numbers — no ground truth — so it stays deployable.
  O1 (ORACLE) needs `geom_truth_score`: the per-step geometry reward scored against pipeline truth.
     This reads the sidecar and is therefore oracle-only.

Doing this as a post-pass (rather than inside generation) means the expensive GPU step never has
to be repeated when a scoring rule changes, and it keeps the oracle/deployable computation in one
auditable place.

Usage (on the box, where spglib + the reward module live):
  python scripts/enrich_e7.py --gen e7/gen_V2b_s0_k8.json --data-dir data/e3 \
      --out e7/gen_V2b_s0_k8_enriched.json
"""
from __future__ import annotations

import argparse
import json
import sys

SYSTEMS = ["cubic", "hexagonal", "monoclinic", "orthorhombic",
           "tetragonal", "triclinic", "trigonal"]


def spglib_system_from_emitted(lat: dict, symprec: float = 0.1) -> str | None:
    """Crystal system that spglib assigns to a cell built from the EMITTED parameters.

    We only have lattice PARAMETERS from the chain (not coordinates), so we build a single-atom
    cell with that lattice. That is enough to determine the lattice-metric symmetry, which is
    what the chain's geometry step claims to establish. A looser symprec (0.1) is used because
    the emitted numbers are rounded to ~3 decimals by the chain format.
    """
    if not lat:
        return None
    try:
        import numpy as np
        import spglib
        from pymatgen.core import Lattice

        L = Lattice.from_parameters(lat["a"], lat["b"], lat["c"],
                                    lat["alpha"], lat["beta"], lat["gamma"])
        cell = (L.matrix, np.array([[0.0, 0.0, 0.0]]), [1])
        ds = spglib.get_symmetry_dataset(cell, symprec=symprec)
        if ds is None:
            return None
        num = ds["number"] if isinstance(ds, dict) else ds.number
        from pymatgen.symmetry.groups import SpaceGroup
        return SpaceGroup.from_int_number(num).crystal_system.lower()
    except Exception:
        return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", required=True)
    ap.add_argument("--data-dir", default="data/e3")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    sys.path.insert(0, "src")
    from cocr.reward import score_chain

    sidecar = json.load(open(f"{args.data_dir}/labels_sidecar.json"))
    d = json.load(open(args.gen))

    n_spg = n_geom = 0
    for rec in d["records"]:
        lab = sidecar.get(rec["material_id"])
        for s in rec["samples"]:
            # DEPLOYABLE: spglib on the model's own emitted lattice
            s["spglib_implies"] = spglib_system_from_emitted(s.get("emitted_lattice"))
            if s["spglib_implies"]:
                n_spg += 1
            # ORACLE: truth-scored geometry step
            if lab is not None:
                ps = score_chain(s.get("text", ""), lab).get("per_step", {})
                s["geom_truth_score"] = ps.get("geometry")
                if s["geom_truth_score"] is not None:
                    n_geom += 1
            else:
                s["geom_truth_score"] = None

    tot = sum(len(r["samples"]) for r in d["records"])
    d["enrichment"] = {"n_samples": tot, "spglib_resolved": n_spg, "geom_scored": n_geom,
                       "spglib_symprec": 0.1,
                       "note": ("spglib_implies is DEPLOYABLE (tool on emitted numbers); "
                                "geom_truth_score is ORACLE (reads the sidecar)")}
    json.dump(d, open(args.out, "w"))
    print(f"[enrich] samples={tot} spglib_resolved={n_spg} geom_scored={n_geom} -> {args.out}")


if __name__ == "__main__":
    main()

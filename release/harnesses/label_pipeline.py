"""
CoCr step-label pipeline.

Generates per-structure crystallographic ground truth from a pymatgen Structure
using spglib/pymatgen, serialized to a canonical JSON schema (schema_version below).
The same labels feed SFT trace synthesis and RL step scoring, so the schema is the
single source of truth for both.

Label fields (per the experiment plan's "Step labels" section):
  crystal_system, bravais_lattice, point_group, space_group (symbol + number),
  wyckoff (occupation), coordination (per-site environments), bond_lengths.

A symprec / angle-tolerance sweep runs per structure; structures whose space-group
number flips across the sweep are flagged (`tolerance_robust=False`) so downstream
code can exclude them or take the tolerance-robust label.
"""
from __future__ import annotations

import math
import warnings
from collections import Counter
from typing import Any

import numpy as np

# CrystalNN emits benign radius/deprecation warnings per site; silence to keep
# batch stdout clean. Numerical behavior is unchanged.
warnings.filterwarnings("ignore", module="pymatgen.analysis.local_env")
from pymatgen.core import Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from pymatgen.analysis.local_env import CrystalNN

SCHEMA_VERSION = "cocr-labels-2"  # v2: lattice reported on conventional standard cell (was input/primitive cell)

# Space-group-number -> crystal system boundaries (ITA).
_CRYSTAL_SYSTEM_RANGES = [
    (1, 2, "triclinic"),
    (3, 15, "monoclinic"),
    (16, 74, "orthorhombic"),
    (75, 142, "tetragonal"),
    (143, 167, "trigonal"),
    (168, 194, "hexagonal"),
    (195, 230, "cubic"),
]

# Default sweep: (symprec, angle_tolerance). First entry is the canonical label.
DEFAULT_SWEEP = [
    (0.01, 5.0),
    (0.001, 5.0),
    (0.05, 5.0),
    (0.1, 5.0),
    (0.01, 1.0),
    (0.01, 10.0),
]

# Canonical (production) tolerance.
CANONICAL_SETTING = (0.01, 5.0)

# Production neighborhood: sweep settings near the production tolerance, EXCLUDING
# the two extremes (tightest symprec=0.001, loosest symprec=0.1). Empirically
# (CP0 verification, all 16 n=224 flip cases) space-group assignment is stable
# across this neighborhood for 15/16 flip structures; the flips occur only at the
# tolerance extremes. A label constant across this neighborhood is the production
# label the model would be trained/evaluated at, so neighborhood stability — not
# whole-sweep stability — is the correct exclusion criterion.
PRODUCTION_NEIGHBORHOOD = {(0.01, 5.0), (0.05, 5.0), (0.01, 1.0), (0.01, 10.0)}


def crystal_system_from_number(sg_number: int) -> str:
    for lo, hi, name in _CRYSTAL_SYSTEM_RANGES:
        if lo <= sg_number <= hi:
            return name
    raise ValueError(f"space-group number out of range: {sg_number}")


def bravais_lattice(sga: SpacegroupAnalyzer) -> str:
    """Return the 6-Bravais-family label + centering, e.g. 'cF' (cubic F-centered)."""
    sg_number = sga.get_space_group_number()
    system = crystal_system_from_number(sg_number)
    symbol = sga.get_space_group_symbol()
    centering = symbol[0]  # P/I/F/C/A/B/R
    system_letter = {
        "triclinic": "a",
        "monoclinic": "m",
        "orthorhombic": "o",
        "tetragonal": "t",
        "trigonal": "h",  # trigonal grouped with hexagonal lattice families
        "hexagonal": "h",
        "cubic": "c",
    }[system]
    return f"{system_letter}{centering}"


def _wyckoff_occupation(structure: Structure, symprec: float, angle_tol: float) -> tuple[list[dict[str, Any]], int]:
    """Return occupied Wyckoff positions referenced to the CONVENTIONAL standard cell.

    Wyckoff multiplicities are only well-defined (and only sum to the cell atom
    count) in the conventional ITA setting. Databases often serve a primitive cell,
    where get_symmetrized_structure reports primitive-cell multiplicities that are
    smaller than the ITA values by the centering factor (F=4, I/C/A/B=2, R=3) and
    do NOT sum to the atom count. We standardize to the conventional cell first so
    the E7 reward check "Wyckoff multiplicities sum to the implied atom count" holds.

    Returns (wyckoff_list, conventional_cell_n_atoms).
    """
    sga = SpacegroupAnalyzer(structure, symprec=symprec, angle_tolerance=angle_tol)
    conv = sga.get_conventional_standard_structure()
    sga_conv = SpacegroupAnalyzer(conv, symprec=symprec, angle_tolerance=angle_tol)
    sym = sga_conv.get_symmetrized_structure()
    out = []
    for sites, wyck in zip(sym.equivalent_sites, sym.wyckoff_symbols):
        # wyck like '4a'; split multiplicity from letter
        mult = int("".join(c for c in wyck if c.isdigit()))
        letter = "".join(c for c in wyck if c.isalpha())
        elem = sites[0].specie.symbol if hasattr(sites[0], "specie") else str(sites[0].species)
        out.append(
            {
                "element": elem,
                "wyckoff_letter": letter,
                "multiplicity": mult,
                "site_symmetry": None,
            }
        )
    return out, len(conv)


def _coordination(structure: Structure, max_sites: int = 24) -> list[dict[str, Any]]:
    """Per-site coordination number and neighbor elements via CrystalNN.

    Capped at max_sites sites to bound cost on large cells; reports the primitive
    (symmetry-reduced) site set when available.
    """
    cnn = CrystalNN()
    out = []
    n = min(len(structure), max_sites)
    for i in range(n):
        try:
            nn = cnn.get_nn_info(structure, i)
        except Exception:
            out.append({"site_index": i, "element": structure[i].specie.symbol,
                        "coordination_number": None, "neighbor_elements": None})
            continue
        neigh = Counter(x["site"].specie.symbol for x in nn)
        out.append(
            {
                "site_index": i,
                "element": structure[i].specie.symbol,
                "coordination_number": len(nn),
                "neighbor_elements": dict(neigh),
            }
        )
    return out


def _bond_lengths(structure: Structure, cutoff: float = 3.5, max_pairs: int = 40) -> list[dict[str, Any]]:
    """Nearest-neighbor bond lengths (unique element pairs, min distance) up to cutoff."""
    pairs: dict[tuple[str, str], float] = {}
    center_indices, point_indices, _, distances = structure.get_neighbor_list(cutoff)
    for ci, pi, d in zip(center_indices, point_indices, distances):
        a = structure[int(ci)].specie.symbol
        b = structure[int(pi)].specie.symbol
        key = tuple(sorted((a, b)))
        if key not in pairs or d < pairs[key]:
            pairs[key] = float(d)
    out = [{"pair": f"{k[0]}-{k[1]}", "min_distance_ang": round(v, 4)}
           for k, v in sorted(pairs.items(), key=lambda kv: kv[1])]
    return out[:max_pairs]


def symprec_sweep(structure: Structure, sweep=DEFAULT_SWEEP) -> dict[str, Any]:
    """Run the tolerance sweep; report space-group number at each setting and flip status."""
    results = []
    for symprec, angle_tol in sweep:
        try:
            sga = SpacegroupAnalyzer(structure, symprec=symprec, angle_tolerance=angle_tol)
            results.append(
                {
                    "symprec": symprec,
                    "angle_tolerance": angle_tol,
                    "space_group_number": sga.get_space_group_number(),
                    "space_group_symbol": sga.get_space_group_symbol(),
                }
            )
        except Exception as e:
            results.append(
                {"symprec": symprec, "angle_tolerance": angle_tol,
                 "space_group_number": None, "error": f"{type(e).__name__}: {e}"}
            )
    sg_numbers = [r["space_group_number"] for r in results if r["space_group_number"] is not None]
    unique = sorted(set(sg_numbers))
    # Most common SG across the sweep = tolerance-robust label.
    robust_sg = Counter(sg_numbers).most_common(1)[0][0] if sg_numbers else None

    # Production-neighborhood stability (the FROZEN CP0 labeling policy).
    neigh_sgs = set(r["space_group_number"] for r in results
                    if (r["symprec"], r["angle_tolerance"]) in PRODUCTION_NEIGHBORHOOD
                    and r["space_group_number"] is not None)
    neighborhood_stable = (len(neigh_sgs) == 1)
    return {
        "sweep": results,
        "unique_space_groups": unique,
        "flipped": len(unique) > 1,               # any flip across the full sweep (diagnostic)
        "neighborhood_stable": neighborhood_stable,  # flip WITHIN production neighborhood (policy)
        "robust_space_group_number": robust_sg,
    }


def make_labels(
    structure: Structure,
    material_id: str,
    source: str,
    canonical_symprec: float = 0.01,
    canonical_angle_tol: float = 5.0,
    include_coordination: bool = True,
    source_space_group_number: int | None = None,
) -> dict[str, Any]:
    """Build the canonical label record for one structure."""
    sga = SpacegroupAnalyzer(structure, symprec=canonical_symprec,
                             angle_tolerance=canonical_angle_tol)
    sg_number = sga.get_space_group_number()
    sg_symbol = sga.get_space_group_symbol()
    point_group = sga.get_point_group_symbol()
    system = crystal_system_from_number(sg_number)

    sweep = symprec_sweep(structure)
    # Lattice parameters MUST be reported on the CONVENTIONAL standard cell: only there do
    # the metric constraints match the crystal system (cubic -> 90/90/90 & a=b=c, etc.).
    # The raw input cell is often primitive (e.g. MP), whose angles do NOT match the system
    # (an orthorhombic primitive cell can have gamma=155 deg). This is the same
    # primitive-vs-conventional issue fixed for Wyckoff; here it governs the lattice block
    # that the E2 V1 chain's [GEOMETRY] step reads. The rendered cell is also conventional,
    # so the label lattice now matches what the images show.
    conv_struct = sga.get_conventional_standard_structure()
    lat = conv_struct.lattice
    prim_lat = structure.lattice  # retained for provenance

    wyckoff, conv_n_atoms = _wyckoff_occupation(structure, canonical_symprec, canonical_angle_tol)
    wyckoff_mult_sum = sum(w["multiplicity"] for w in wyckoff)

    rec: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "material_id": material_id,
        "source": source,
        "formula_pretty": structure.composition.reduced_formula,
        "n_sites": len(structure),
        "conventional_n_atoms": conv_n_atoms,
        "lattice": {
            "a": round(lat.a, 5), "b": round(lat.b, 5), "c": round(lat.c, 5),
            "alpha": round(lat.alpha, 4), "beta": round(lat.beta, 4), "gamma": round(lat.gamma, 4),
            "volume": round(lat.volume, 5),
            "cell_setting": "conventional_standard",
        },
        "lattice_input_cell": {
            "a": round(prim_lat.a, 5), "b": round(prim_lat.b, 5), "c": round(prim_lat.c, 5),
            "alpha": round(prim_lat.alpha, 4), "beta": round(prim_lat.beta, 4),
            "gamma": round(prim_lat.gamma, 4), "n_sites": len(structure),
        },
        "crystal_system": system,
        "bravais_lattice": bravais_lattice(sga),
        "point_group": point_group,
        "space_group": {"symbol": sg_symbol, "number": sg_number},
        "wyckoff": wyckoff,
        "wyckoff_multiplicity_sum": wyckoff_mult_sum,
        # Self-consistency invariant used by the E7 reward server: Wyckoff
        # multiplicities (conventional ITA cell) must sum to the conventional
        # atom count. Recorded so downstream code can assert it cheaply.
        "wyckoff_sum_consistent": (wyckoff_mult_sum == conv_n_atoms),
        "bond_lengths": _bond_lengths(structure),
        "tolerance": {
            "canonical_symprec": canonical_symprec,
            "canonical_angle_tolerance": canonical_angle_tol,
            **sweep,
            "tolerance_robust": (not sweep["flipped"]),  # whole-sweep (diagnostic)
        },
    }
    # --- FROZEN CP0 LABELING POLICY (decided at CP0, do not re-litigate downstream) ---
    # Carry the production-tolerance (canonical) label; KEEP a structure iff BOTH:
    #   (i)  neighborhood_stable — label constant across the production tolerance
    #        neighborhood (flips, if any, occur only at the tolerance extremes), AND
    #   (ii) source_agrees — canonical label matches the source database's reported
    #        space group (when a source SG is provided).
    # Rationale: blunt whole-sweep exclusion drops ~7% of structures concentrated in
    # the low-symmetry strata (triclinic 15.6%, trigonal 12.5%) — where the model is
    # weakest — even though 15/16 such flips are neighborhood-stable and flip only at
    # the tolerance extremes. Neighborhood-stability alone preserves those strata but
    # would admit the 3 triclinic P1/P-1 cases where our production label (P1) differs
    # from MP's looser-default label (P-1) — a genuine near-inversion-boundary
    # ambiguity. Requiring source agreement quarantines exactly those contested labels
    # while still keeping the tolerance-extreme-only flips. This both preserves the
    # low-symmetry strata AND keeps the kept-set label certificate clean.
    source_agrees = (source_space_group_number is None
                     or int(source_space_group_number) == sg_number)
    keep = bool(sweep["neighborhood_stable"] and source_agrees)
    rec["label_policy"] = {
        "policy": "keep-if-neighborhood-stable-and-source-agrees",
        "neighborhood_stable": sweep["neighborhood_stable"],
        "source_agrees": source_agrees,
        "keep_for_training": keep,
        "production_label_space_group_number": sg_number,
    }
    return rec
    if include_coordination:
        rec["coordination"] = _coordination(structure)
    return rec

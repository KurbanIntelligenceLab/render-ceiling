"""
CoCr data layer: fetch structures from Materials Project and JARVIS-DFT.

Both sources return a normalized record:
  {source, material_id, structure (pymatgen), source_symmetry_number, source_symmetry_symbol}

source_symmetry_* is the database's own reported space group, used ONLY for the
E0 label-correctness audit (agreement between our spglib labels and the source).
"""
from __future__ import annotations

import os
from typing import Any, Iterator

from pymatgen.core import Structure


def fetch_mp(
    n: int,
    num_elements: tuple[int, int] = (2, 4),
    num_sites: tuple[int, int] = (2, 20),
    api_key: str | None = None,
    seed: int = 0,
) -> list[dict[str, Any]]:
    """Fetch n structures from Materials Project with source-reported symmetry."""
    from mp_api.client import MPRester

    key = api_key or os.environ["MP_API_KEY"]
    out = []
    with MPRester(key) as m:
        docs = m.materials.summary.search(
            num_elements=num_elements,
            num_sites=num_sites,
            fields=["material_id", "formula_pretty", "symmetry", "structure"],
            num_chunks=1,
            chunk_size=n,
        )
    for d in docs[:n]:
        out.append(
            {
                "source": "MP",
                "material_id": str(d.material_id),
                "formula_pretty": d.formula_pretty,
                "structure": d.structure,
                "source_symmetry_number": int(d.symmetry.number),
                "source_symmetry_symbol": d.symmetry.symbol,
            }
        )
    return out


_CRYSTAL_SYSTEMS = ["Triclinic", "Monoclinic", "Orthorhombic", "Tetragonal",
                    "Trigonal", "Hexagonal", "Cubic"]


def fetch_mp_stratified(
    per_system: int,
    num_elements: tuple[int, int] = (2, 4),
    num_sites: tuple[int, int] = (2, 20),
    api_key: str | None = None,
) -> list[dict[str, Any]]:
    """Fetch ~per_system structures for EACH of the 7 crystal systems, so the
    audit sample spans the full symmetry range instead of an alphabetical slice."""
    from mp_api.client import MPRester

    key = api_key or os.environ["MP_API_KEY"]
    out = []
    with MPRester(key) as m:
        for system in _CRYSTAL_SYSTEMS:
            docs = m.materials.summary.search(
                crystal_system=system,
                num_elements=num_elements,
                num_sites=num_sites,
                fields=["material_id", "formula_pretty", "symmetry", "structure",
                        "band_gap", "formation_energy_per_atom"],
                num_chunks=1,
                chunk_size=per_system,
            )
            for d in docs[:per_system]:
                out.append(
                    {
                        "source": "MP",
                        "material_id": str(d.material_id),
                        "formula_pretty": d.formula_pretty,
                        "structure": d.structure,
                        "source_symmetry_number": int(d.symmetry.number),
                        "source_symmetry_symbol": d.symmetry.symbol,
                        "queried_system": system,
                        # E2 property-task targets (additive; earlier callers ignore these)
                        "band_gap": getattr(d, "band_gap", None),
                        "formation_energy_per_atom": getattr(d, "formation_energy_per_atom", None),
                    }
                )
    return out


def fetch_jarvis(n: int, dataset: str = "dft_3d", store_dir: str | None = None) -> list[dict[str, Any]]:
    """Fetch n structures from JARVIS-DFT (jarvis-tools bundled dataset).

    JARVIS records carry 'spg_number'/'spg_symbol' when symmetry was computed.
    store_dir: where to cache the downloaded figshare dataset (defaults to
    data/jarvis_cache under the repo, kept inside the sandbox grant).
    """
    from jarvis.db.figshare import data as jdata
    from jarvis.core.atoms import Atoms as JAtoms

    if store_dir is None:
        store_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                 "data", "jarvis_cache")
    os.makedirs(store_dir, exist_ok=True)
    recs = jdata(dataset, store_dir=store_dir)
    out = []
    for r in recs:
        if len(out) >= n:
            break
        try:
            jatoms = JAtoms.from_dict(r["atoms"])
            structure = Structure(
                lattice=jatoms.lattice_mat,
                species=jatoms.elements,
                coords=jatoms.frac_coords,
                coords_are_cartesian=False,
            )
        except Exception:
            continue
        spg = r.get("spg_number")
        try:
            spg = int(spg) if spg not in (None, "na", "") else None
        except (ValueError, TypeError):
            spg = None
        out.append(
            {
                "source": "JARVIS",
                "material_id": str(r.get("jid", f"jarvis-{len(out)}")),
                "formula_pretty": r.get("formula", ""),
                "structure": structure,
                "source_symmetry_number": spg,
                "source_symmetry_symbol": r.get("spg_symbol"),
            }
        )
    return out


def _system_of(sg_number):
    if sg_number is None:
        return None
    for lo, hi, name in [(1,2,"Triclinic"),(3,15,"Monoclinic"),(16,74,"Orthorhombic"),
                         (75,142,"Tetragonal"),(143,167,"Trigonal"),(168,194,"Hexagonal"),
                         (195,230,"Cubic")]:
        if lo <= sg_number <= hi:
            return name
    return None


def fetch_jarvis_stratified(
    per_system: int,
    dataset: str = "dft_3d",
    store_dir: str | None = None,
    max_sites: int = 20,
    min_sites: int = 2,
) -> list[dict[str, Any]]:
    """Sample ~per_system JARVIS structures per crystal system (by source spg_number)."""
    from jarvis.db.figshare import data as jdata
    from jarvis.core.atoms import Atoms as JAtoms

    if store_dir is None:
        store_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                 "data", "jarvis_cache")
    os.makedirs(store_dir, exist_ok=True)
    recs = jdata(dataset, store_dir=store_dir)

    buckets: dict[str, list] = {s: [] for s in _CRYSTAL_SYSTEMS}
    for r in recs:
        spg = r.get("spg_number")
        try:
            spg = int(spg) if spg not in (None, "na", "") else None
        except (ValueError, TypeError):
            spg = None
        system = _system_of(spg)
        if system is None or len(buckets[system]) >= per_system:
            continue
        try:
            jatoms = JAtoms.from_dict(r["atoms"])
            if not (min_sites <= len(jatoms.elements) <= max_sites):
                continue
            structure = Structure(lattice=jatoms.lattice_mat, species=jatoms.elements,
                                   coords=jatoms.frac_coords, coords_are_cartesian=False)
        except Exception:
            continue
        buckets[system].append(
            {
                "source": "JARVIS",
                "material_id": str(r.get("jid", "")),
                "formula_pretty": r.get("formula", ""),
                "structure": structure,
                "source_symmetry_number": spg,
                "source_symmetry_symbol": r.get("spg_symbol"),
                "queried_system": system,
            }
        )
        if all(len(b) >= per_system for b in buckets.values()):
            break
    out = []
    for s in _CRYSTAL_SYSTEMS:
        out.extend(buckets[s])
    return out

from __future__ import annotations

import os
from typing import Any


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


_CRYSTAL_SYSTEMS = [
    "Triclinic",
    "Monoclinic",
    "Orthorhombic",
    "Tetragonal",
    "Trigonal",
    "Hexagonal",
    "Cubic",
]


def fetch_mp_stratified(
    per_system: int,
    num_elements: tuple[int, int] = (2, 4),
    num_sites: tuple[int, int] = (2, 20),
    api_key: str | None = None,
) -> list[dict[str, Any]]:


    from mp_api.client import MPRester

    key = api_key or os.environ["MP_API_KEY"]
    out = []
    with MPRester(key) as m:
        for system in _CRYSTAL_SYSTEMS:
            docs = m.materials.summary.search(
                crystal_system=system,
                num_elements=num_elements,
                num_sites=num_sites,
                fields=[
                    "material_id",
                    "formula_pretty",
                    "symmetry",
                    "structure",
                ],
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
                    }
                )
    return out

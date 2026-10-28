"""Crystal-system labels used by the geometric reference and reconstruction."""

_CRYSTAL_SYSTEM_RANGES = [
    (1, 2, "triclinic"),
    (3, 15, "monoclinic"),
    (16, 74, "orthorhombic"),
    (75, 142, "tetragonal"),
    (143, 167, "trigonal"),
    (168, 194, "hexagonal"),
    (195, 230, "cubic"),
]


def crystal_system_from_number(sg_number: int) -> str:
    for lo, hi, name in _CRYSTAL_SYSTEM_RANGES:
        if lo <= sg_number <= hi:
            return name
    raise ValueError(f"space-group number out of range: {sg_number}")

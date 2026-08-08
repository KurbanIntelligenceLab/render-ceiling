"""
CoCr E2 SFT trace synthesis.

Turns a CP0 label record (from cocr.labels.make_labels) into supervised targets for
the three E2 arms, all sharing the same (images, question) input but differing in the
target completion:

  B1  direct     : the bare answer, no reasoning.
  B2  free_cot   : a free-form chain-of-thought then the answer (natural prose, not
                   the enforced schema) — the "reasoning helps" control.
  V1  cocr_chain : the hierarchical CoCr chain with a FIXED step structure:
                   [GEOMETRY] -> [SYSTEM/BRAVAIS] -> [POINT GROUP/SPACE GROUP + symmetry-
                   element justification] -> [WYCKOFF/COORDINATION] -> [ANSWER]
                   Every step is generated deterministically from the label, so each
                   step is programmatically checkable (this is what E3's process reward
                   scores). No step asserts anything not in the label.

The primary task is crystal-system identification (7-way), consistent with E1/CP0b; the
chain still surfaces the finer labels (point/space group, Wyckoff) as intermediate steps
so V1 carries the full hierarchical supervision the schema hypothesis (H1) is about.

Design choices grounded in the CP0 schema (verified against make_labels output):
  - space_group carries {symbol, number}; point_group is the Hermann-Mauguin PG symbol.
  - wyckoff is a list of {element, wyckoff_letter, multiplicity}; multiplicities sum to
    conventional_n_atoms (the wyckoff_sum_consistent invariant).
  - coordination may be EMPTY for some intermetallics (CrystalNN returns nothing); the
    chain SKIPS the coordination clause rather than emit a broken step.
  - bond_lengths is a list of {pair, min_distance_ang}.
"""
from __future__ import annotations

from typing import Any

# Symmetry-element vocabulary keyed by space-group number ranges is unreliable; instead
# we justify the space group from what the label actually exposes (HM symbol glyphs),
# which is faithful and checkable.
_LATTICE_CENTERING = {
    "P": "primitive", "I": "body-centered", "F": "face-centered",
    "C": "base-centered (C)", "A": "base-centered (A)", "B": "base-centered (B)",
    "R": "rhombohedral-centered",
}

_SYSTEM_GEOMETRY = {
    "cubic": "three mutually perpendicular axes of equal length (a=b=c, all angles 90 deg); "
             "the cell projects to a square along each principal axis",
    "tetragonal": "a square base with a distinct height (a=b!=c, all angles 90 deg)",
    "orthorhombic": "three unequal perpendicular axes (a!=b!=c, all angles 90 deg); a rectangular box",
    "hexagonal": "two equal axes at 120 deg plus a distinct c (a=b, gamma=120 deg)",
    "trigonal": "a rhombohedral/hexagonal-family cell (a=b, gamma=120 deg in the hexagonal setting)",
    "monoclinic": "one oblique angle (a!=b!=c, alpha=gamma=90 deg, beta!=90 deg)",
    "triclinic": "no axis or angle constraints (all lengths and angles free); a fully skewed cell",
}


def _fmt_lattice(lat: dict[str, Any]) -> str:
    return (f"a={lat['a']:.3f}, b={lat['b']:.3f}, c={lat['c']:.3f} Ang; "
            f"alpha={lat['alpha']:.1f}, beta={lat['beta']:.1f}, gamma={lat['gamma']:.1f} deg")


def _qualitative_geometry(lat: dict[str, Any]) -> str:
    """View-MEASURABLE qualitative geometry only — NO exact cell parameters.

    Used by the V1b arm (CP2 follow-up item 3). The renders let a viewer judge
    edge-length RELATIONS (equal vs distinct), the angle family (~90 / ~120 / oblique),
    and a COARSE axial-ratio bin (roughly cubic / moderately elongated / very elongated),
    but not exact Angstrom values. Supervising on those exact values (as V1 did) demands a
    measurement the renders cannot support, so V1's geometry step collapses to memorized
    template numbers. V1b tests the schema with a step the images can actually ground.
    """
    a, b, c = lat["a"], lat["b"], lat["c"]
    al, be, ga = lat["alpha"], lat["beta"], lat["gamma"]

    def approx_eq(x, y, tol=0.03):
        return abs(x - y) <= tol * max(x, y)

    # edge-length relation
    if approx_eq(a, b) and approx_eq(b, c):
        edges = "all three edges appear equal (a\u2248b\u2248c)"
    elif approx_eq(a, b) and not approx_eq(a, c):
        edges = "two edges appear equal and one distinct (a\u2248b\u2260c)"
    elif approx_eq(a, c) and not approx_eq(a, b):
        edges = "two edges appear equal and one distinct (a\u2248c\u2260b)"
    elif approx_eq(b, c) and not approx_eq(a, b):
        edges = "two edges appear equal and one distinct (b\u2248c\u2260a)"
    else:
        edges = "all three edges appear distinct (a\u2260b\u2260c)"

    # angle family
    def near(x, t):
        return abs(x - t) <= 2.0
    if near(al, 90) and near(be, 90) and near(ga, 90):
        angles = "all inter-axial angles look like right angles (~90 deg)"
    elif near(al, 90) and near(be, 90) and near(ga, 120):
        angles = "two angles are ~90 deg and one is ~120 deg"
    else:
        oblique = [n for n, v in [("alpha", al), ("beta", be), ("gamma", ga)] if not near(v, 90)]
        angles = f"at least one angle is oblique (not 90 deg): {', '.join(oblique)}"

    # coarse axial ratio (longest/shortest), binned
    r = max(a, b, c) / min(a, b, c)
    if r < 1.15:
        ratio = "the cell is close to isometric (axial ratio near 1)"
    elif r < 2.0:
        ratio = "the cell is moderately anisotropic (one axis noticeably longer)"
    else:
        ratio = "the cell is strongly anisotropic (one axis much longer, a layered/columnar look)"

    return f"{edges}; {angles}; {ratio}"


def _symmetry_justification(space_group: dict, point_group: str, system: str) -> str:
    """Justify the space group from HM-symbol glyphs actually present in the label.

    Reads screw axes (2_1,3_1,...), glide planes (a,b,c,d,n,e), and centering from the
    Hermann-Mauguin symbol — all directly visible in the label, no external table.
    """
    sym = space_group["symbol"]
    parts = []
    centering = sym.replace("-", "")[0] if sym else "P"
    if centering in _LATTICE_CENTERING:
        parts.append(f"the leading '{centering}' marks a {_LATTICE_CENTERING[centering]} lattice")
    if "-" in sym:
        parts.append("the bar (e.g. -3, -1, -4) indicates an inversion/rotoinversion axis")
    # screw axes appear as digit-with-subscript in the full symbol; the summary symbol
    # keeps the rotation order glyphs
    for g, name in [("2", "2-fold"), ("3", "3-fold"), ("4", "4-fold"), ("6", "6-fold")]:
        if g in sym:
            parts.append(f"a {name} rotation")
            break
    for glide in ["d", "n", "c", "b", "a"]:
        if glide in sym[1:]:  # skip centering position
            parts.append(f"a '{glide}' glide plane")
            break
    if "m" in sym[1:]:
        parts.append("a mirror plane (m)")
    just = "; ".join(parts) if parts else "the point-group symmetry alone"
    return (f"The Hermann-Mauguin symbol {sym} (No. {space_group['number']}, point group {point_group}) "
            f"encodes: {just}.")


def _wyckoff_clause(wyckoff: list[dict], conv_n: int | None) -> str:
    if not wyckoff:
        return ""
    items = ", ".join(f"{w['element']} on {w['multiplicity']}{w['wyckoff_letter']}" for w in wyckoff)
    total = sum(w["multiplicity"] for w in wyckoff)
    tail = f" (multiplicities sum to {total}" + (f", matching the {conv_n}-atom conventional cell)" if conv_n else ")")
    return f"Occupied Wyckoff positions: {items}{tail}."


def _coordination_clause(coordination: list[dict]) -> str:
    if not coordination:
        return ""
    # summarize modal CN per element
    by_el: dict[str, list[int]] = {}
    for c in coordination:
        cn = c.get("coordination_number")
        if cn is not None:
            by_el.setdefault(c["element"], []).append(cn)
    if not by_el:
        return ""
    parts = []
    for el, cns in by_el.items():
        modal = max(set(cns), key=cns.count)
        parts.append(f"{el} is {modal}-coordinated")
    return "Coordination environments: " + ", ".join(parts) + "."


QUESTION = ("You are shown standardized multi-view ball-and-stick renders of a crystal "
            "structure (principal-axis and oblique views of the conventional cell). "
            "Identify the crystal system (one of: triclinic, monoclinic, orthorhombic, "
            "tetragonal, trigonal, hexagonal, cubic). Reason from the cell geometry and "
            "atomic arrangement visible in the images.")


def make_target(label: dict[str, Any], arm: str) -> str:
    """Return the SFT target completion for the given arm ('B1','B2','V1')."""
    system = label["crystal_system"]
    if arm == "B1":
        return f"ANSWER: {system}"

    if arm == "B2":
        # free-form CoT: natural reasoning, correct but not enforced schema
        lat = _fmt_lattice(label["lattice"])
        return (
            f"Looking at the renders, the unit cell shows {_SYSTEM_GEOMETRY[system].split(';')[0]}. "
            f"The lattice parameters ({lat}) are consistent with a {system} cell. "
            f"The atomic arrangement and cell shape across the principal-axis views confirm this.\n"
            f"ANSWER: {system}"
        )

    if arm in ("V1", "V1b"):
        sg = label["space_group"]; pg = label["point_group"]
        conv_n = label.get("conventional_n_atoms")
        steps = []
        if arm == "V1":
            lat = _fmt_lattice(label["lattice"])
            steps.append(f"[GEOMETRY] Cell parameters: {lat}. The cell shows "
                         f"{_SYSTEM_GEOMETRY[system]}.")
        else:  # V1b: qualitative, view-measurable geometry only (no exact cell parameters)
            steps.append(f"[GEOMETRY] From the renders: {_qualitative_geometry(label['lattice'])}.")
        steps.append(f"[SYSTEM/BRAVAIS] These metric constraints identify the {system} crystal "
                     f"system, Bravais lattice {label['bravais_lattice']}.")
        steps.append(f"[SYMMETRY] {_symmetry_justification(sg, pg, system)}")
        wy = _wyckoff_clause(label.get("wyckoff", []), conv_n)
        co = _coordination_clause(label.get("coordination", []))
        motif = " ".join(x for x in [wy, co] if x)
        if motif:
            steps.append(f"[MOTIF] {motif}")
        steps.append(f"[ANSWER] {system}")
        return "\n".join(steps)

    raise ValueError(f"unknown arm {arm!r}")


def make_example(label: dict[str, Any], image_paths: list[str], arm: str) -> dict[str, Any]:
    """One SFT example: images + shared question + arm-specific target."""
    return {
        "material_id": label["material_id"],
        "source": label["source"],
        "crystal_system": label["crystal_system"],
        "arm": arm,
        "images": image_paths,
        "question": QUESTION,
        "target": make_target(label, arm),
    }

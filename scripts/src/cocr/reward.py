"""
CoCr reward server (E3/E4/E7 shared infrastructure).

Parses an emitted hierarchical CoCr chain and scores every step against the
pipeline-label ground truth derived from the source CIF (spglib/pymatgen). Returns a
per-step reward vector + a final-answer reward + a format reward, and logs every
decision for the E4 reward-hacking audit. CPU, millisecond-scale.

Chain schema (from traces.py):
  [GEOMETRY]        continuous/qualitative -> edge-relation, angle-family, ratio-bin
  [SYSTEM/BRAVAIS]  discrete hierarchical  -> crystal system (coarse) + Bravais (fine)
  [SYMMETRY]        discrete hierarchical  -> point group + space group
  [MOTIF]           set-match              -> Wyckoff letters (deduped; repetition NOT rewarded)
  [ANSWER] <system> final reward           -> crystal system exact

Design decisions carried over from sft_chain (ledger/sft_chain):
  1. Geometry is scored on QUALITATIVE relations, never exact cell parameters — the
     finite views cannot support exact-value measurement (E0.5/E1), so exact-value
     rewards would reward an unmeasurable target and invite template recitation.
  2. FORMAT reward explicitly requires termination: each tag once, in order, ending
     with a valid [ANSWER]. This directly penalizes the MOTIF repetition trap that
     sank the pure-SFT chains (generation looping in the Wyckoff enumeration, never
     reaching [ANSWER]).
  3. Hierarchical credit: a correct crystal system with a wrong space group earns
     coarse credit only (the plan's rule), so the reward is dense but not gameable by
     nailing only the easy coarse label.
"""

from __future__ import annotations

import re
from typing import Any

SECTIONS = ["GEOMETRY", "SYSTEM/BRAVAIS", "SYMMETRY", "MOTIF", "ANSWER"]
CRYSTAL_SYSTEMS = ["triclinic", "monoclinic", "orthorhombic", "tetragonal",
                   "trigonal", "hexagonal", "cubic"]

# --- geometry: qualitative relations from a lattice (mirror of traces._qualitative_geometry) ---


def lattice_relations(lat: dict[str, float]) -> tuple[str, str, str]:
    """(edge_relation, angle_family, ratio_bin) — the view-measurable qualitative triple."""
    a, b, c = lat["a"], lat["b"], lat["c"]
    al, be, ga = lat["alpha"], lat["beta"], lat["gamma"]

    def aeq(x, y, tol=0.03):
        return abs(x - y) <= tol * max(x, y)

    if aeq(a, b) and aeq(b, c):
        edge = "abc_equal"
    elif aeq(a, b) or aeq(a, c) or aeq(b, c):
        edge = "two_equal"
    else:
        edge = "all_distinct"

    def near(x, t):
        return abs(x - t) <= 2.0

    if near(al, 90) and near(be, 90) and near(ga, 90):
        ang = "all90"
    elif near(ga, 120) and near(al, 90) and near(be, 90):
        ang = "120"
    else:
        ang = "oblique"

    r = max(a, b, c) / min(a, b, c)
    ratio = "iso" if r < 1.15 else ("mod" if r < 2.0 else "strong")
    return (edge, ang, ratio)


def _parse_emitted_relations(geom_text: str) -> tuple[str | None, str | None, str | None]:
    """Extract the qualitative triple from an emitted [GEOMETRY] step.

    Handles both the V1 (exact numbers) and V1b (qualitative phrases) surface forms —
    for V1 we re-derive relations from the emitted numbers; for V1b we read the phrases.
    """
    m = re.search(r"a=([\d.]+), b=([\d.]+), c=([\d.]+) Ang; "
                  r"alpha=([\d.]+), beta=([\d.]+), gamma=([\d.]+)", geom_text)
    if m:
        a, b, c, al, be, ga = map(float, m.groups())
        return lattice_relations({"a": a, "b": b, "c": c, "alpha": al, "beta": be, "gamma": ga})
    # qualitative surface form
    if "a≈b≈c" in geom_text:
        edge = "abc_equal"
    elif any(s in geom_text for s in ["a≈b≠c", "a≈c≠b", "b≈c≠a"]):
        edge = "two_equal"
    elif "a≠b≠c" in geom_text:
        edge = "all_distinct"
    else:
        edge = None
    if "one is ~120" in geom_text:
        ang = "120"
    elif "right angles" in geom_text:
        ang = "all90"
    elif "oblique" in geom_text:
        ang = "oblique"
    else:
        ang = None
    ratio = ("iso" if "isometric" in geom_text
             else "mod" if "moderately" in geom_text
             else "strong" if "strongly" in geom_text else None)
    return (edge, ang, ratio)


# --- chain parsing ---


def parse_chain(text: str) -> dict[str, Any]:
    """Split an emitted chain into its section texts and record structural facts."""
    tags = list(re.finditer(r"\[([A-Z/]+)\]", text))
    sections: dict[str, str] = {}
    order: list[str] = []
    for i, mt in enumerate(tags):
        name = mt.group(1)
        if name not in SECTIONS:
            continue
        order.append(name)
        start = mt.end()
        end = tags[i + 1].start() if i + 1 < len(tags) else len(text)
        # keep only the FIRST occurrence of each tag's content
        if name not in sections:
            sections[name] = text[start:end].strip()
    return {"sections": sections, "tag_order": order}


# --- discrete hierarchical matching ---


def _final_system(text_after_answer: str) -> str | None:
    t = text_after_answer.lower()
    for s in CRYSTAL_SYSTEMS:
        if s in t:
            return s
    return None


def score_chain(text: str, label: dict[str, Any], weights: dict[str, float] | None = None) -> dict[str, Any]:
    """Score an emitted chain against the pipeline label.

    Returns per-step rewards in [0,1], a final-answer reward, a format reward in
    [-1, 1], the format-penalized scalar sum (V2a style), and a full decision log.
    """
    w = weights or {"geometry": 1.0, "system": 1.0, "bravais": 1.0,
                    "point_group": 1.0, "space_group": 1.0, "motif": 1.0}
    parsed = parse_chain(text)
    sec = parsed["sections"]
    order = parsed["tag_order"]
    log: dict[str, Any] = {}
    step: dict[str, float] = {}

    # --- FORMAT: each of the 5 tags exactly once, in canonical order, terminating with ANSWER ---
    first_occurrence = [t for t in order]
    canonical = SECTIONS
    seen_once = all(order.count(t) == 1 for t in canonical if t in order)
    present = [t for t in canonical if t in sec]
    in_order = present == [t for t in first_occurrence if t in canonical][:len(present)]
    terminates = "ANSWER" in sec and _final_system(sec.get("ANSWER", "")) is not None
    all_present = len(present) == len(canonical)
    if all_present and terminates and in_order and seen_once:
        fmt = 1.0
    elif terminates:
        fmt = 0.0            # reached an answer but structure imperfect
    else:
        fmt = -1.0           # never terminated (the MOTIF-trap failure) -> hard penalty
    log["format"] = {"present": present, "terminates": terminates,
                     "seen_once": seen_once, "in_order": in_order, "reward": fmt}

    # --- GEOMETRY (continuous/qualitative): fraction of the relation triple that matches ---
    if "GEOMETRY" in sec:
        em = _parse_emitted_relations(sec["GEOMETRY"])
        tr = lattice_relations(label["lattice"])
        hits = sum(1 for e, t in zip(em, tr) if e is not None and e == t)
        step["geometry"] = hits / 3.0
        log["geometry"] = {"emitted": em, "truth": tr, "reward": step["geometry"]}
    else:
        step["geometry"] = 0.0

    # --- SYSTEM/BRAVAIS (discrete, hierarchical) ---
    sysb = sec.get("SYSTEM/BRAVAIS", "").lower()
    true_sys = label["crystal_system"].lower()
    true_brav = label["bravais_lattice"]
    sys_ok = true_sys in sysb
    step["system"] = 1.0 if sys_ok else 0.0
    # Bravais credited only if system is right (hierarchical)
    brav_ok = sys_ok and (true_brav.lower() in sysb or true_brav in sec.get("SYSTEM/BRAVAIS", ""))
    step["bravais"] = 1.0 if brav_ok else 0.0
    log["system_bravais"] = {"true_system": true_sys, "true_bravais": true_brav,
                             "system_ok": sys_ok, "bravais_ok": brav_ok}

    # --- SYMMETRY (discrete, hierarchical): point group + space group ---
    symt = sec.get("SYMMETRY", "")
    true_pg = str(label["point_group"])
    true_sg_sym = label["space_group"]["symbol"]
    true_sg_num = str(label["space_group"]["number"])
    pg_ok = sys_ok and (true_pg in symt)
    # space group credited only if system right (coarse-credit rule from the plan)
    sg_ok = sys_ok and (true_sg_sym in symt or re.search(rf"\bNo\.?\s*{true_sg_num}\b", symt) is not None)
    step["point_group"] = 1.0 if pg_ok else 0.0
    step["space_group"] = 1.0 if sg_ok else 0.0
    log["symmetry"] = {"true_pg": true_pg, "true_sg": true_sg_sym, "true_sg_num": true_sg_num,
                       "pg_ok": pg_ok, "sg_ok": sg_ok}

    # --- MOTIF (set match, deduped — repetition is NOT rewarded) ---
    motif = sec.get("MOTIF", "")
    emitted_wyck = set(re.findall(r"\b(\d+[a-z])\b", motif))
    true_wyck = set()
    for wy in label.get("wyckoff", []) or []:
        # label stores multiplicity + wyckoff_letter separately; the emitted trace
        # composes them as "<mult><letter>" (e.g. "2i"). Match that combined form.
        if isinstance(wy, dict):
            letter = str(wy.get("wyckoff_letter", wy.get("letter", wy.get("wyckoff", "")))).strip()
            mult = wy.get("multiplicity")
            if mult is not None and re.fullmatch(r"[a-z]", letter):
                true_wyck.add(f"{int(mult)}{letter}")
            else:
                m = re.search(r"(\d+[a-z])", str(wy.get("wyckoff", "")))
                if m:
                    true_wyck.add(m.group(1))
        elif isinstance(wy, str):
            m = re.search(r"(\d+[a-z])", wy)
            if m:
                true_wyck.add(m.group(1))
    if true_wyck:
        inter = emitted_wyck & true_wyck
        union = emitted_wyck | true_wyck
        step["motif"] = len(inter) / len(union) if union else 0.0  # Jaccard
    else:
        step["motif"] = 0.0
    log["motif"] = {"emitted": sorted(emitted_wyck), "truth": sorted(true_wyck),
                    "reward": step["motif"]}

    # --- FINAL answer reward (crystal system exact) ---
    final_sys = _final_system(sec.get("ANSWER", ""))
    final_reward = 1.0 if (final_sys == true_sys) else 0.0
    log["final"] = {"emitted": final_sys, "truth": true_sys, "reward": final_reward}

    # --- aggregate (V2a: scalar sum of per-step verifiable rewards, format-gated) ---
    step_sum = sum(w[k] * step[k] for k in step) / sum(w.values())
    # format penalty folds in: a non-terminating chain (fmt=-1) is heavily discounted
    v2a_scalar = max(0.0, step_sum + 0.25 * fmt)  # fmt in {-1,0,1} nudges +/- 0.25

    return {
        "per_step": step,          # process arms AGGREGATE this vector into one scalar
                                   # (dense step-level rewarding, NOT per-step credit
                                   #  assignment — see train_e3_grpo.py naming note)
        "final_reward": final_reward,
        "format_reward": fmt,
        "v2a_scalar": v2a_scalar,  # scalar-sum arm reward
        "log": log,
    }


# --- outcome-only reward (B3 arm: CrystalReasoner-style, final answer only) ---


def score_outcome(text: str, label: dict[str, Any]) -> dict[str, Any]:
    """B3 arm: reward the final crystal-system answer only, plus a light format gate."""
    parsed = parse_chain(text)
    final_sys = _final_system(parsed["sections"].get("ANSWER", ""))
    if final_sys is None:
        # fall back to last crystal-system word anywhere (outcome reward is answer-only)
        for s in reversed(re.findall(r"(triclinic|monoclinic|orthorhombic|tetragonal|"
                                     r"trigonal|hexagonal|cubic)", text.lower())):
            final_sys = s
            break
    true_sys = label["crystal_system"].lower()
    return {"final_reward": 1.0 if final_sys == true_sys else 0.0,
            "emitted": final_sys, "truth": true_sys}

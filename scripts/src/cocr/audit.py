"""
CoCr E0 pipeline-validation audit.

Runs the four E0 checks over a sample drawn from MP and JARVIS:

  (1) Label correctness  — our spglib space-group number vs the source database's
      reported number, on the tolerance-robust subset. Pass: >98% agreement.
  (2) Tolerance flip rate — fraction of structures whose SG number changes across
      the symprec/angle sweep. Reported (not a hard gate).
  (3) Metadata-leakage guard — verify render filenames + the emitted sidecar carry
      no symmetry label; the index->view map is fixed and structure-independent.
  (4) Human-solvability — a stratified subset is rendered for human/vision check
      that crystal system is identifiable from pixels (surfaced as images, scored
      externally). This module emits the subset manifest.

Writes results.json + a per-structure table; the pipeline finding is written by the
driver script.
"""
from __future__ import annotations

import json
import os
import re
from collections import Counter, defaultdict
from typing import Any

from .labels import make_labels, crystal_system_from_number
from .render import render_views, conventional_cell, VIEW_ORDER


def _cp_lower(k: int, n: int, alpha: float = 0.05) -> float:
    """Exact Clopper-Pearson one-sided lower confidence bound for k/n successes.

    For k == n (all agree), reduces to alpha**(1/n). Uses the Beta quantile in
    the general case.
    """
    if n == 0:
        return 0.0
    if k == n:
        return alpha ** (1.0 / n)
    from scipy.stats import beta
    return float(beta.ppf(alpha, k, n - k + 1))

# Any of these substrings in a render filename would leak the label.
_LEAK_TOKENS = [
    "cubic", "tetragonal", "orthorhombic", "monoclinic", "triclinic",
    "trigonal", "hexagonal", "rhombohedral",
    "fm-3m", "fm3m", "p1", "pmmm", "sg", "spacegroup", "space_group",
    "wyckoff", "pointgroup", "point_group", "bravais",
]


def check_leakage(render_paths: dict[str, str]) -> dict[str, Any]:
    """No render filename may contain a symmetry token, and it must not encode
    the view identity in a symmetry-informative way. Filenames use bare indices."""
    violations = []
    for view, path in render_paths.items():
        fname = os.path.basename(path).lower()
        for tok in _LEAK_TOKENS:
            if re.search(rf"(^|[_\-]){re.escape(tok)}([_\-]|\.|$)", fname):
                violations.append({"view": view, "file": fname, "token": tok})
        # filenames must be <stem>_viewN.png — index only, no view name
        if view in fname:
            violations.append({"view": view, "file": fname, "token": "view-name-in-filename"})
    return {"leak_free": len(violations) == 0, "violations": violations}


def audit_sample(
    records: list[dict[str, Any]],
    render_root: str,
    render_supercell: tuple[int, int, int] = (2, 2, 2),
    do_render: bool = True,
    use_conventional: bool = True,
) -> dict[str, Any]:
    """Run the E0 checks over a list of normalized source records."""
    rows = []
    for rec in records:
        struct = rec["structure"]
        mid = rec["material_id"]
        src = rec["source"]
        row: dict[str, Any] = {"material_id": mid, "source": src,
                               "formula": rec.get("formula_pretty", "")}
        try:
            labels = make_labels(struct, mid, src,
                                 source_space_group_number=rec.get("source_symmetry_number"))
        except Exception as e:
            row["error"] = f"label: {type(e).__name__}: {e}"
            rows.append(row)
            continue

        ours = labels["space_group"]["number"]
        src_sg = rec.get("source_symmetry_number")
        row["our_sg"] = ours
        row["source_sg"] = src_sg
        row["crystal_system"] = labels["crystal_system"]
        row["sg_agree"] = (src_sg is not None and int(src_sg) == ours)
        row["tolerance_robust"] = labels["tolerance"]["tolerance_robust"]
        row["neighborhood_stable"] = labels["tolerance"]["neighborhood_stable"]
        row["keep_for_training"] = labels["label_policy"]["keep_for_training"]
        row["unique_sgs"] = labels["tolerance"]["unique_space_groups"]
        # E7 reward-server invariant: Wyckoff multiplicities (conventional cell)
        # must sum to the conventional atom count.
        row["wyckoff_sum_consistent"] = labels.get("wyckoff_sum_consistent")

        if do_render:
            struct_r = conventional_cell(struct) if use_conventional else struct
            stem = f"{src}_{mid}".replace("/", "_")
            out_dir = os.path.join(render_root, src)
            paths = render_views(struct_r, out_dir, stem, supercell=render_supercell)
            leak = check_leakage(paths)
            row["render_view_files"] = [os.path.basename(paths[v]) for v in VIEW_ORDER]
            row["leak_free"] = leak["leak_free"]
            row["leak_violations"] = leak["violations"]
        rows.append(row)

    # Aggregate
    robust = [r for r in rows if r.get("tolerance_robust") and "error" not in r]
    with_src = [r for r in robust if r.get("source_sg") is not None]
    n_agree = sum(1 for r in with_src if r["sg_agree"])
    flip = [r for r in rows if "error" not in r and not r.get("tolerance_robust", True)]
    n_ok = sum(1 for r in rows if "error" not in r)

    by_system = Counter(r["crystal_system"] for r in rows if "crystal_system" in r)
    leak_fail = [r for r in rows if r.get("leak_free") is False]

    # Per-crystal-system flip breakdown. Tolerance-ambiguity concentrates in
    # pseudosymmetric / low-symmetry systems; quarantining flips can skew the
    # stratified balance toward high-symmetry classes exactly where the model is
    # weakest, so this is tracked at every scale (including the full dataset).
    sys_tot: dict = defaultdict(int)
    sys_flip: dict = defaultdict(int)
    for r in rows:
        if "error" in r or "crystal_system" not in r:
            continue
        sys_tot[r["crystal_system"]] += 1
        if r.get("tolerance_robust") is False:
            sys_flip[r["crystal_system"]] += 1
    per_system_flip = {
        s: {"n": sys_tot[s], "flipped": sys_flip[s],
            "flip_rate": (sys_flip[s] / sys_tot[s]) if sys_tot[s] else None}
        for s in sys_tot
    }

    # Frozen labeling policy: keep neighborhood-stable, quarantine the rest.
    # Report per-system keep/quarantine so the balance impact of the policy is
    # explicit and comparable to the blunt whole-sweep-exclusion alternative.
    sys_quar: dict = defaultdict(int)
    for r in rows:
        if "error" in r or "crystal_system" not in r:
            continue
        if r.get("keep_for_training") is False:
            sys_quar[r["crystal_system"]] += 1
    n_keep = sum(1 for r in rows if r.get("keep_for_training") is True)
    n_quar = sum(1 for r in rows if r.get("keep_for_training") is False)
    per_system_policy = {
        s: {"n": sys_tot[s], "quarantined": sys_quar[s],
            "quarantine_rate": (sys_quar[s] / sys_tot[s]) if sys_tot[s] else None}
        for s in sys_tot
    }
    wy_checked = [r for r in rows if r.get("wyckoff_sum_consistent") is not None]
    wy_ok = [r for r in wy_checked if r["wyckoff_sum_consistent"]]

    summary = {
        "n_records": len(rows),
        "n_labeled_ok": n_ok,
        "n_errors": len(rows) - n_ok,
        "label_correctness": {
            "n_robust_with_source_sg": len(with_src),
            "n_agree": n_agree,
            "agreement_rate": (n_agree / len(with_src)) if with_src else None,
            "point_estimate_ge_98pct": (n_agree / len(with_src) >= 0.98) if with_src else None,
            # Exact Clopper-Pearson one-sided 95% lower confidence bound on the
            # agreement rate. Certifies >98% only if this bound exceeds 0.98.
            "ci95_lower": _cp_lower(n_agree, len(with_src)) if with_src else None,
            "certified_gt_98pct_at_95ci": (
                _cp_lower(n_agree, len(with_src)) > 0.98 if with_src else None),
            # Per-system agreement + per-stratum CP95 lower bound. The pooled
            # certificate above holds under the BALANCED sampling distribution; it
            # transfers to the natural long-tailed production distribution only if
            # label errors are not system-dependent. Per-system bounds (each weak at
            # n~32) make that assumption checkable and are extended by the continuous
            # full-scale audit. Zero observed errors in any stratum keeps the
            # transfer assumption credible.
            "per_system": {
                s: {
                    "n": sum(1 for r in robust if r.get("crystal_system") == s
                             and r.get("source_sg") is not None),
                    "n_agree": sum(1 for r in robust if r.get("crystal_system") == s
                                   and r.get("source_sg") is not None and r["sg_agree"]),
                    "ci95_lower": _cp_lower(
                        sum(1 for r in robust if r.get("crystal_system") == s
                            and r.get("source_sg") is not None and r["sg_agree"]),
                        sum(1 for r in robust if r.get("crystal_system") == s
                            and r.get("source_sg") is not None)),
                }
                for s in sorted(set(r.get("crystal_system") for r in robust
                                    if r.get("crystal_system")))
            },
        },
        "tolerance_flip": {
            "n_flipped": len(flip),
            "flip_rate": (len(flip) / n_ok) if n_ok else None,
            "flipped_ids": [r["material_id"] for r in flip],
            "per_system": per_system_flip,
        },
        "metadata_leakage": {
            "n_checked": sum(1 for r in rows if "leak_free" in r),
            "n_leak_free": sum(1 for r in rows if r.get("leak_free") is True),
            "all_leak_free": len(leak_fail) == 0,
            "violations": [{"material_id": r["material_id"], "v": r["leak_violations"]}
                           for r in leak_fail],
        },
        "label_policy": {
            "policy": "keep-if-neighborhood-stable-and-source-agrees",
            "n_keep": n_keep,
            "n_quarantine": n_quar,
            "quarantine_rate": (n_quar / (n_keep + n_quar)) if (n_keep + n_quar) else None,
            "per_system": per_system_policy,
        },
        "wyckoff_consistency": {
            "n_checked": len(wy_checked),
            "n_consistent": len(wy_ok),
            "all_consistent": len(wy_checked) == len(wy_ok),
            "inconsistent_ids": [r["material_id"] for r in wy_checked
                                 if not r["wyckoff_sum_consistent"]],
        },
        "crystal_system_distribution": dict(by_system),
    }
    return {"summary": summary, "rows": rows}

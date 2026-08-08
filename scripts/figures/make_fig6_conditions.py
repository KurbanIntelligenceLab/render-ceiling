"""Figure 6 — the visibility conditions (CP31).

Reads ledger/CP31_visibility_corrected_oracle/results.json and writes conditions.png.
Usage:  python scripts/figures/make_fig6_conditions.py <ledger_dir> <out.png>
"""
import json, sys
import os as _os
sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from _style import apply_style

LABELS = {"O0": "unconditioned", "O1": "informative occluders removed",
          "O2": "all occluders removed", "O3": "control: random removal"}


def main(ledger, out):
    d = json.load(open(f"{ledger}/CP31_visibility_corrected_oracle/results.json"))
    C = d["conditions"]
    keys = [k for k in ("expansion_4v_O0", "expansion_4v_O1", "expansion_4v_O2", "expansion_4v_O3")
            if k in C]
    short = [k.split("_")[-1] for k in keys]
    vals = [C[k]["micro"] for k in keys]
    cm = [C[k]["count_match"] for k in keys]
    n = C[keys[0]]["n"]
    x = np.arange(len(keys))

    apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 5.2), gridspec_kw={"width_ratios": [1.15, 1]})
    ax = axes[0]
    cols = ["#b9c6d4", "#4a6fa5", "#8a5a2f", "#9aa8b5"]
    ax.bar(x, vals, 0.6, color=cols[:len(x)], edgecolor="#333", lw=0.7, zorder=2)
    ax.axhline(vals[0], color="#2f6b3a", ls="--", lw=1.4, zorder=4,
               label=f"unconditioned ({vals[0]:.4f})")
    for i, v in enumerate(vals):
        ax.text(i, v + 0.012, f"{v:.4f}", ha="center", fontsize=9)
    ax.set_xticks(x); ax.set_xticklabels(short, fontsize=9.5)
    ax.set_ylim(0, 1.32)
    ax.set_ylabel(f"symmetry recovery   (expansion eval, n={n}, 4 views)")
    ax.set_title("Removing informative occluders changes nothing; the control moves",
                 loc="left", fontsize=11, weight="bold")
    ax.legend(loc="upper left", fontsize=8.4)
    ax.grid(axis="y", alpha=0.25); ax.set_axisbelow(True)
    # condition key ABOVE the bars, never over them
    ax.text(0.985, 0.985, "\n".join(f"{k}: {LABELS[k]}" for k in short),
            transform=ax.transAxes, fontsize=7.8, color="#444", va="top", ha="right",
            bbox=dict(boxstyle="round,pad=0.32", fc="white", ec="#ccc", alpha=0.95))

    ax2 = axes[1]
    ax2.bar(x, cm, 0.6, color=cols[:len(x)], edgecolor="#333", lw=0.7, zorder=2)
    for i, v in enumerate(cm):
        ax2.text(i, v + 2.0, str(v), ha="center", fontsize=9)
    ax2.set_xticks(x); ax2.set_xticklabels(short, fontsize=9.5)
    ax2.set_ylim(0, n * 1.30)
    ax2.set_ylabel(f"structures with exact atom-count match (of {n})")
    ax2.set_title("The removals DID reach the reconstructor", loc="left",
                  fontsize=11, weight="bold")
    ax2.text(0.5, 0.995, "atom counts change across conditions, so a flat\n"
             "recovery curve is not a plumbing failure",
             transform=ax2.transAxes, ha="center", va="top", fontsize=8.0, color="#444",
             bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#ccc", alpha=0.95))
    ax2.grid(axis="y", alpha=0.25); ax2.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    print(f"{out}: {len(keys)} conditions, O0 {vals[0]:.4f}, count_match {cm}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

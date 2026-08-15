"""Figure 6 -- the visibility conditions (visibility_corrected_oracle).

Reads results/visibility_corrected_oracle/results.json and writes a
vector PDF. Usage:  python manuscript/codes/make_fig6_conditions.py <results_dir> <out.pdf>

R12: figsize width fixed at the placement width (no rescaling); every font role is
8pt so \\includegraphics[width=\\linewidth] places text at exactly 8pt. The
left panel's y-axis is extended so the condition-key box sits in headroom
above the bars rather than overlapping them.
"""
import json, sys
import os as _os
sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from _style import (apply_style, DDWIDTH_IN, FONT_PT, panel_letter, save_pdf)

LABELS = {"O0": "unconditioned", "O1": "informative occluders removed",
          "O2": "all occluders removed", "O3": "control: random removal"}


def main(ledger, out):
    d = json.load(open(f"{ledger}/visibility_corrected_oracle/results.json"))
    C = d["conditions"]
    keys = [k for k in ("expansion_4v_O0", "expansion_4v_O1", "expansion_4v_O2", "expansion_4v_O3")
            if k in C]
    short = [k.split("_")[-1] for k in keys]
    vals = [C[k]["micro"] for k in keys]
    cm = [C[k]["count_match"] for k in keys]
    n = C[keys[0]]["n"]
    x = np.arange(len(keys))

    apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(DDWIDTH_IN, 4.0),
                              gridspec_kw={"width_ratios": [1.15, 1], "wspace": 0.45})
    ax = axes[0]
    cols = ["#b9c6d4", "#4a6fa5", "#8a5a2f", "#9aa8b5"]
    ax.bar(x, vals, 0.6, color=cols[:len(x)], edgecolor="#333", lw=0.7, zorder=2)
    ax.axhline(vals[0], color="#2f6b3a", ls="--", lw=1.2, zorder=4,
               label=f"unconditioned ({vals[0]:.3f})")
    for i, v in enumerate(vals):
        ax.text(i, v + 0.02, f"{v:.3f}", ha="center", fontsize=FONT_PT)
    ax.set_xticks(x); ax.set_xticklabels(short, fontsize=FONT_PT)
    ax.set_ylim(0, 1.02)
    ax.tick_params(axis="both", labelsize=FONT_PT)
    ax.set_ylabel(f"symmetry recovery (n={n}, 4 views)", fontsize=FONT_PT)
    panel_letter(ax, "a")
    ax.legend(loc="upper left", fontsize=FONT_PT, framealpha=0.95)
    ax.grid(axis="y", alpha=0.25); ax.set_axisbelow(True)
    # condition key ABOVE the bars in the extended headroom, never over them
    # the O0-O3 condition key is spelled out in the figure CAPTION
    assert short == ["O0", "O1", "O2", "O3"]

    ax2 = axes[1]
    ax2.bar(x, cm, 0.6, color=cols[:len(x)], edgecolor="#333", lw=0.7, zorder=2)
    for i, v in enumerate(cm):
        ax2.text(i, v + 3.5, str(v), ha="center", fontsize=FONT_PT)
    ax2.set_xticks(x); ax2.set_xticklabels(short, fontsize=FONT_PT)
    ax2.set_ylim(0, n * 1.10)
    ax2.tick_params(axis="both", labelsize=FONT_PT)
    ax2.set_ylabel(f"exact atom-count match (of {n})", fontsize=FONT_PT)
    panel_letter(ax2, "b")
    ax2.grid(axis="y", alpha=0.25); ax2.set_axisbelow(True)
    # explicit margins, not bbox_inches="tight" -- see make_fig1 for why
    fig.subplots_adjust(left=0.085, right=0.985, top=0.945, bottom=0.09, wspace=0.30)
    save_pdf(fig, out)
    print(f"{out}: {len(keys)} conditions, O0 {vals[0]:.4f}, count_match {cm}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

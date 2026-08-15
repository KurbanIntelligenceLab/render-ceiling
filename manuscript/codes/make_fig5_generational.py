"""Figure 5 -- the generational comparison (generational_comparison).

Reads results/generational_comparison/results.json and writes a vector
PDF. The two panels are the point: raw gains invite one reading,
headroom-normalised gains reverse it.
Usage:  python manuscript/codes/make_fig5_generational.py <results_dir> <out.pdf>

R12: figsize width fixed at the placement width (no rescaling); every font role is
8pt so \\includegraphics[width=\\linewidth] places text at exactly 8pt.
"""
import json, sys
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from _style import (apply_style, CHANCE, SIWIDTH_IN, FONT_PT, panel_letter, save_pdf)


def main(ledger, out):
    R = json.load(open(f"{ledger}/generational_comparison/results.json"))
    S = R["stratified"]; H = R["headroom_normalisation"]
    orc = H["oracle_ceiling"]
    labels = [f"box-sufficient\n(n={S['box_sufficient']['n']})",
              f"box-ambiguous\n(n={S['box_ambiguous']['n']})"]
    g25 = [S["box_sufficient"]["g25"], S["box_ambiguous"]["g25"]]
    g36 = [S["box_sufficient"]["g36"], S["box_ambiguous"]["g36"]]
    sh = [H["sufficient_share_of_headroom"] * 100, H["ambiguous_share_of_headroom"] * 100]
    x = np.arange(2)

    apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(SIWIDTH_IN, 3.95),
                              gridspec_kw={"width_ratios": [1, 1.05], "wspace": 0.4})
    ax = axes[0]
    ax.bar(x - 0.2, g25, 0.38, color="#c9b8a0", edgecolor="#6b5d4a", lw=0.7,
           label="gemini-2.5-flash", zorder=2)
    ax.bar(x + 0.2, g36, 0.38, color="#4a6fa5", edgecolor="#2b3f5a", lw=0.7,
           label="gemini-3.6-flash", zorder=2)
    ax.axhline(orc, color="#2f6b3a", lw=1.2, zorder=3, label=f"oracle ceiling ({orc:.3f})")
    ax.axhline(CHANCE, color="#8a2f2f", ls="--", lw=1.0, zorder=3, label=f"chance ({CHANCE:.3f})")
    for i, (a, b) in enumerate(zip(g25, g36)):
        ax.text(i - 0.2, a + 0.02, f"{a:.2f}", ha="center", fontsize=FONT_PT)
        ax.text(i + 0.2, b + 0.02, f"{b:.2f}", ha="center", fontsize=FONT_PT)
        ax.annotate(f"+{b - a:.2f}", xy=(i, max(a, b) + 0.075), ha="center",
                    fontsize=FONT_PT, weight="bold", color="#2b3f5a")
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=FONT_PT)
    ax.set_ylim(0, 1.38); ax.set_yticks(np.arange(0, 1.01, 0.2))
    ax.tick_params(axis="both", labelsize=FONT_PT)
    ax.set_ylabel("accuracy", fontsize=FONT_PT)
    panel_letter(ax, "a")
    ax.legend(fontsize=FONT_PT, loc="upper left", ncol=1, framealpha=0.92,
              handletextpad=0.4, labelspacing=0.25, borderpad=0.3)
    ax.grid(axis="y", alpha=0.25); ax.set_axisbelow(True)

    ax2 = axes[1]
    ax2.bar(x, sh, 0.5, color=["#7d94b5", "#b5917d"], edgecolor="#333", lw=0.7, zorder=2)
    for i, v in enumerate(sh):
        ax2.text(i, v + 2.0, f"{v:.1f}%", ha="center", fontsize=FONT_PT, weight="bold")
    ax2.set_xticks(x); ax2.set_xticklabels(labels, fontsize=FONT_PT); ax2.set_ylim(0, 90)
    ax2.tick_params(axis="both", labelsize=FONT_PT)
    ax2.set_ylabel("headroom-to-oracle closed (%)", fontsize=FONT_PT)
    panel_letter(ax2, "b")
    # the raw-gain reading is stated in the figure CAPTION, not on the canvas
    assert abs(S["box_ambiguous"]["delta"] - 0.50) < 5e-3
    assert abs(S["box_sufficient"]["delta"] - 0.21) < 5e-3
    ax2.grid(axis="y", alpha=0.25); ax2.set_axisbelow(True)
    # explicit margins, not bbox_inches="tight" -- see make_fig1 for why
    fig.subplots_adjust(left=0.085, right=0.985, top=0.945, bottom=0.115, wspace=0.34)
    save_pdf(fig, out)
    print(f"{out}: raw +{S['box_ambiguous']['delta']:.4f} amb vs "
          f"+{S['box_sufficient']['delta']:.4f} suff; normalised {sh[1]:.1f}% vs {sh[0]:.1f}%")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

"""Figure 5 — the generational comparison (CP36).

Reads ledger/CP36_generational_comparison/results.json and writes generational.png.
The two panels are the point: raw gains invite one reading, headroom-normalised gains reverse it.
Usage:  python scripts/figures/make_fig5_generational.py <ledger_dir> <out.png>
"""
import json, sys
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from _style import apply_style, CHANCE


def main(ledger, out):
    R = json.load(open(f"{ledger}/CP36_generational_comparison/results.json"))
    S = R["stratified"]; H = R["headroom_normalisation"]
    orc = H["oracle_ceiling"]
    labels = [f"box-sufficient\n(n={S['box_sufficient']['n']})",
              f"box-ambiguous\n(n={S['box_ambiguous']['n']})"]
    g25 = [S["box_sufficient"]["g25"], S["box_ambiguous"]["g25"]]
    g36 = [S["box_sufficient"]["g36"], S["box_ambiguous"]["g36"]]
    sh = [H["sufficient_share_of_headroom"] * 100, H["ambiguous_share_of_headroom"] * 100]
    x = np.arange(2)

    apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 5.2), gridspec_kw={"width_ratios": [1, 1.05]})
    ax = axes[0]
    ax.bar(x - 0.2, g25, 0.38, color="#c9b8a0", edgecolor="#6b5d4a", lw=0.7,
           label="gemini-2.5-flash", zorder=2)
    ax.bar(x + 0.2, g36, 0.38, color="#4a6fa5", edgecolor="#2b3f5a", lw=0.7,
           label="gemini-3.6-flash", zorder=2)
    ax.axhline(orc, color="#2f6b3a", lw=1.4, zorder=3, label=f"oracle ceiling ({orc:.4f})")
    ax.axhline(CHANCE, color="#8a2f2f", ls="--", lw=1.2, zorder=3, label=f"chance ({CHANCE:.4f})")
    for i, (a, b) in enumerate(zip(g25, g36)):
        ax.text(i - 0.2, a + 0.012, f"{a:.3f}", ha="center", fontsize=8.5)
        ax.text(i + 0.2, b + 0.012, f"{b:.3f}", ha="center", fontsize=8.5)
        ax.annotate(f"+{b - a:.3f}", xy=(i, max(a, b) + 0.055), ha="center",
                    fontsize=9.5, weight="bold", color="#2b3f5a")
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylim(0, 1.30); ax.set_yticks(np.arange(0, 1.01, 0.2))
    ax.set_ylabel("accuracy   (original eval, n=210, K=3)")
    ax.set_title("One generation, by cue-sufficiency stratum", loc="left",
                 fontsize=10.5, weight="bold", pad=10)
    ax.legend(fontsize=7.6, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.005))
    ax.grid(axis="y", alpha=0.25); ax.set_axisbelow(True)

    ax2 = axes[1]
    ax2.bar(x, sh, 0.5, color=["#7d94b5", "#b5917d"], edgecolor="#333", lw=0.7, zorder=2)
    for i, v in enumerate(sh):
        ax2.text(i, v + 1.6, f"{v:.1f}%", ha="center", fontsize=10.5, weight="bold")
    ax2.set_xticks(x); ax2.set_xticklabels(labels, fontsize=9); ax2.set_ylim(0, 88)
    ax2.set_ylabel("share of headroom-to-oracle closed  (%)")
    ax2.set_title("Normalised, the ambiguous stratum closes LESS", loc="left",
                  fontsize=10.5, weight="bold", pad=10)
    ax2.text(0.5, 0.955,
             f"the larger raw gain on ambiguous "
             f"(+{S['box_ambiguous']['delta']:.3f} vs +{S['box_sufficient']['delta']:.3f})\n"
             "is substantially a low-baseline effect",
             transform=ax2.transAxes, ha="center", va="top", fontsize=8.2, color="#444",
             bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#ccc", alpha=0.95))
    ax2.grid(axis="y", alpha=0.25); ax2.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    print(f"{out}: raw +{S['box_ambiguous']['delta']:.4f} amb vs "
          f"+{S['box_sufficient']['delta']:.4f} suff; normalised {sh[1]:.1f}% vs {sh[0]:.1f}%")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

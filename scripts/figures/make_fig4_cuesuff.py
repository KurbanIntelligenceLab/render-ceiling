"""Figure 4 — the cue-sufficiency contrast (CP35).

Reads ledger/CP35_stratified_frontier_expansion/results.json and writes cuesuff.png.
Usage:  python scripts/figures/make_fig4_cuesuff.py <ledger_dir> <out.png>
"""
import json, sys
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from _style import apply_style

MODELS = ["google/gemini-3.6-flash", "x-ai/grok-4.5", "anthropic/claude-opus-4.8"]


def main(ledger, out):
    R = json.load(open(f"{ledger}/CP35_stratified_frontier_expansion/results.json"))
    res = R["primary_contrast_pixel_minus_rf"]

    apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(11.6, 5.0), sharey=True)
    for ax, sample in zip(axes, ("original", "expansion")):
        gs = [res[m][sample]["sufficient"]["gap"] for m in MODELS]
        ga = [res[m][sample]["ambiguous"]["gap"] for m in MODELS]
        x = np.arange(len(MODELS))
        ax.bar(x - 0.2, gs, 0.38, color="#7d94b5", edgecolor="#2b3f5a", lw=0.7,
               label="box-sufficient", zorder=2)
        ax.bar(x + 0.2, ga, 0.38, color="#b5917d", edgecolor="#6b4a3a", lw=0.7,
               label="box-ambiguous", zorder=2)
        for i, (a, b) in enumerate(zip(gs, ga)):
            ax.text(i - 0.2, a - 0.022, f"{a:.3f}", ha="center", va="top", fontsize=8)
            ax.text(i + 0.2, b - 0.022, f"{b:.3f}", ha="center", va="top", fontsize=8)
        ax.axhline(0, color="#333", lw=1.0, zorder=3)
        ax.set_xticks(x)
        ax.set_xticklabels([m.split("/")[-1] for m in MODELS], fontsize=8.5, rotation=12, ha="right")
        n_s = res[MODELS[0]][sample]["sufficient"]["n"]
        n_a = res[MODELS[0]][sample]["ambiguous"]["n"]
        ax.set_title(f"{sample} eval  (n={n_s}+{n_a}, K=3)", loc="left", fontsize=10, weight="bold")
        ax.grid(axis="y", alpha=0.25); ax.set_axisbelow(True); ax.set_ylim(-0.50, 0.06)
    axes[0].set_ylabel("pixel model minus cell-metric RF\n(negative = pixel model trails)")
    axes[0].legend(fontsize=8.5, loc="lower left")
    fig.suptitle("The pixel-minus-numeric gap widens on cue-ambiguous structures "
                 "\u2014 3 of 3 arms, both samples", fontsize=11.5, weight="bold", y=1.00)
    cf = R["confound_stated"]["ambiguous_is_largely_one_degeneracy"]
    dc = R["de_concentration_check"]
    fig.text(0.5, -0.035,
             f"ambiguous stratum is {cf['original_hex_or_trig']}/{cf['original_n']} and "
             f"{cf['expansion_hex_or_trig']}/{cf['expansion_n']} hexagonal-or-trigonal, so this is close to "
             f"a hex/trig effect; residual n={dc['original_residual_n']} and "
             f"n={dc['expansion_residual_n']} is suggestive only",
             ha="center", fontsize=8.2, color="#555")
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    print(f"{out}: {R['n_arms_widening_both_samples']}/3 arms widen on both samples")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

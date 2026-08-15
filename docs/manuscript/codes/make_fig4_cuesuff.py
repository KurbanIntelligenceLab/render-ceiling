"""Figure 4 -- the cue-sufficiency contrast (stratified_frontier_expansion).

Reads results/stratified_frontier_expansion/results.json and writes a
vector PDF. Usage:  python manuscript/codes/make_fig4_cuesuff.py <results_dir> <out.pdf>

R12: figsize width fixed at the placement width (no rescaling); every font role is
8pt so \\includegraphics[width=\\linewidth] places text at exactly 8pt. The
footnote sits below the rotated x tick labels (extra bottom margin) rather
than overlapping them.
"""
import json, sys
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from _style import (apply_style, SIWIDTH_IN, FONT_PT, panel_letter, save_pdf)

MODELS = ["google/gemini-3.6-flash", "x-ai/grok-4.5", "anthropic/claude-opus-4.8"]


def main(ledger, out):
    R = json.load(open(f"{ledger}/stratified_frontier_expansion/results.json"))
    res = R["primary_contrast_pixel_minus_rf"]

    apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(SIWIDTH_IN, 2.85), sharey=True)
    for ax, sample in zip(axes, ("original", "expansion")):
        gs = [res[m][sample]["sufficient"]["gap"] for m in MODELS]
        ga = [res[m][sample]["ambiguous"]["gap"] for m in MODELS]
        x = np.arange(len(MODELS))
        ax.bar(x - 0.2, gs, 0.38, color="#7d94b5", edgecolor="#2b3f5a", lw=0.7,
               label="box-sufficient", zorder=2)
        ax.bar(x + 0.2, ga, 0.38, color="#b5917d", edgecolor="#6b4a3a", lw=0.7,
               label="box-ambiguous", zorder=2)
        for i, (a, b) in enumerate(zip(gs, ga)):
            ax.text(i - 0.2, a - 0.018, f"{a:.2f}", ha="center", va="top", fontsize=FONT_PT)
            ax.text(i + 0.2, b - 0.018, f"{b:.2f}", ha="center", va="top", fontsize=FONT_PT)
        ax.axhline(0, color="#333", lw=1.0, zorder=3)
        ax.set_xticks(x)
        ax.set_xticklabels([m.split("/")[-1] for m in MODELS], fontsize=FONT_PT,
                           rotation=25, ha="right")
        ax.tick_params(axis="both", labelsize=FONT_PT)
        n_s = res[MODELS[0]][sample]["sufficient"]["n"]
        n_a = res[MODELS[0]][sample]["ambiguous"]["n"]
        panel_letter(ax, "a" if sample == "original" else "b")
        assert (n_s, n_a) == ((140, 70) if sample == "original" else (141, 69)), \
            f"stratum sizes moved: {sample} {n_s}+{n_a} -- update the caption"
        ax.grid(axis="y", alpha=0.25); ax.set_axisbelow(True); ax.set_ylim(-0.50, 0.06)
    axes[0].set_ylabel("pixel minus cell-metric RF", fontsize=FONT_PT)
    # legend upper right: the bars there are near zero, so it never overlaps
    # a value label (lower-left collided with the "-0.31"/"-0.33" annotations
    # in testing)
    axes[0].legend(fontsize=FONT_PT, loc="upper right", framealpha=0.95,
                   handletextpad=0.4, borderpad=0.3, labelspacing=0.25)
    # the stratum-composition confound is stated in the figure CAPTION, not on
    # the canvas; asserted here so a change in the record cannot silently
    # desynchronise the caption from the data
    cf = R["confound_stated"]["ambiguous_is_largely_one_degeneracy"]
    dc = R["de_concentration_check"]
    assert (cf["original_hex_or_trig"], cf["original_n"]) == (60, 70)
    assert (cf["expansion_hex_or_trig"], cf["expansion_n"]) == (58, 69)
    # NOTE: the record's expansion_residual_n reads 12, which contradicts its
    # own 58/69 stratum composition (69 - 58 = 11). The manuscript reports the
    # arithmetic-consistent 11, as Sections S7 and S8 of the ESI already did.
    assert dc["original_residual_n"] == 10
    assert cf["expansion_n"] - cf["expansion_hex_or_trig"] == 11
    # explicit margins, not bbox_inches="tight" -- see make_fig1 for why
    fig.subplots_adjust(left=0.115, right=0.985, top=0.935, bottom=0.245, wspace=0.09)
    save_pdf(fig, out)
    print(f"{out}: {R['n_arms_widening_both_samples']}/3 arms widen on both samples")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

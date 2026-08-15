"""Figure 1 — the zero-shot leaderboard (model_sweep).

Reads results/model_sweep/results.json and writes a vector PDF.
Usage:  python manuscript/codes/make_fig1_leaderboard.py <results_dir> <out.pdf>

R12: figsize width is fixed at the placement width (no rescaling) and every font
role is 8pt, so \\includegraphics[width=\\linewidth] places text at exactly
8pt with no rescaling.

R6: the panel title must NOT assert "every scored model falls below a
baseline that never sees the image" — that is the claim Section 4.3 retires.
The title here is a neutral description of what the panel plots.
Reference lines (confirmed from the draw calls below): the SOLID line is the
shape-free baseline (floor, ~0.5286); the DASHED line is seven-way chance
(CHANCE = 1/7 ~= 0.1429).
"""
import json, sys
import os as _os
sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from _style import (apply_style, CHANCE, DDWIDTH_IN, FONT_PT, save_pdf)


def main(ledger, out):
    d = json.load(open(f"{ledger}/model_sweep/results.json"))
    lb = d["leaderboard_canonical_run_A"]
    floor = d["reference_rows"]["shape_free_regularity_floor"]["micro"]
    spread = d["measurement_provenance"]["run_to_run_spread"]

    order = sorted(lb, key=lambda m: lb[m]["micro"])
    vals = [lb[m]["micro"] for m in order]
    names = [m.split("/")[-1].replace("-instruct", "") for m in order]
    y = np.arange(len(order))

    apply_style()
    fig, ax = plt.subplots(figsize=(DDWIDTH_IN, 4.1))
    ax.barh(y, vals, color="#b9c6d4", edgecolor="#3a4a58", linewidth=0.7, height=0.7, zorder=2)
    # reference lines ON TOP of the bars, or they vanish behind them
    ax.axvline(floor, color="#8a5a2f", ls="-", lw=1.5, zorder=4,
               label=f"shape-free baseline ({floor:.4f})")
    ax.axvline(CHANCE, color="#8a2f2f", ls="--", lw=1.3, zorder=4,
               label=f"7-way chance ({CHANCE:.4f})")
    if spread:
        err = spread["mean_abs_structures"] / 210.0
        ax.errorbar(vals, y, xerr=err, fmt="none", ecolor="#3a4a58", elinewidth=0.9,
                    capsize=2.0, zorder=5)
    ax.set_yticks(y); ax.set_yticklabels(names, fontsize=FONT_PT)
    # widen past the baseline line so the annotation box lands in the
    # whitespace beyond it, clear of every bar (max bar < floor here)
    ax.set_xlim(0, max(max(vals), floor) * 1.34)
    ax.set_xlabel("crystal-system accuracy   (original eval, n=210, K=3)", fontsize=FONT_PT)
    ax.tick_params(axis="both", labelsize=FONT_PT)
    # no on-canvas title and no annotation box: the claim and the error-bar
    # definition are stated once, in the figure caption
    assert abs(spread["mean_abs_structures"] - 5.0) < 0.05
    ax.legend(loc="lower right", fontsize=FONT_PT)
    ax.grid(axis="x", alpha=0.25, zorder=0); ax.set_axisbelow(True)
    # NOTE: explicit margins, not bbox_inches="tight" -- "tight" crops the PDF
    # page to the content box, which would shrink the page below 5.5in and
    # defeat the point of fixing the figsize (LaTeX \linewidth would then
    # rescale placed text away from 8pt).
    fig.subplots_adjust(left=0.22, right=0.985, top=0.985, bottom=0.115)
    save_pdf(fig, out)
    print(f"{out}: {len(order)} models, floor {floor:.4f}, best {max(vals):.4f}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

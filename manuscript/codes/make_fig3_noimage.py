"""Figure 3 -- the no-image control (no_image_control).

Reads results/no_image_control/results.json and writes a vector PDF.
Usage:  python manuscript/codes/make_fig3_noimage.py <results_dir> <out.pdf>

R12: figsize width fixed at the placement width so no rescaling occurs and
every font role is placed at exactly 8pt.

DD: the width is the RSC double-column figure width (17.1 cm = 6.73 in), what
0.92\\textwidth resolves to in the Digital Discovery template; the height is
unchanged from the ICLR draw, so the panel is squarer. Model identifiers are
drawn INSIDE the panel at the end of each bar pair rather than as y-tick
labels, which is why the left margin collapses.
"""
import json, sys
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from _style import (apply_style, CHANCE, DDWIDTH_IN, FONT_PT, save_pdf)


def main(ledger, out):
    d = json.load(open(f"{ledger}/no_image_control/results.json"))
    rex = d["roster_extension"]
    sc = {m: v for m, v in rex["paired"].items() if isinstance(v, dict) and "image" in v}
    nsig = rex["significant"]["n"]

    order = sorted(sc, key=lambda m: -sc[m]["image"])
    img = [sc[m]["image"] for m in order]
    txt = [sc[m]["text"] for m in order]
    names = [m.split("/")[-1].replace("-instruct", "") for m in order]
    y = np.arange(len(order))

    apply_style()
    fig, ax = plt.subplots(figsize=(DDWIDTH_IN, 4.2))
    ax.barh(y - 0.2, img, height=0.38, color="#4a6fa5", edgecolor="#2b3f5a",
            linewidth=0.6, label="with images", zorder=2)
    ax.barh(y + 0.2, txt, height=0.38, color="#c9b8a0", edgecolor="#6b5d4a",
            linewidth=0.6, label="formula only, no images", zorder=2)
    ax.axvline(CHANCE, color="#8a2f2f", ls="--", lw=1.3, zorder=3,
               label=f"7-way chance ({CHANCE:.4f})")
    for i, m in enumerate(order):
        if sc[m].get("p", 1) < 0.05:
            ax.text(img[i] + 0.012, i - 0.2, "*", va="center", fontsize=FONT_PT, color="#2b3f5a")
    # identifiers inside the panel. Default position is just past the longer of
    # each model's two bars (plus the significance star's width where one is
    # drawn). For the two longest bars that position would run under the legend,
    # so those labels are set inside the blue bar instead, right-aligned.
    for i, m in enumerate(order):
        pad = 0.030 if sc[m].get("p", 1) < 0.05 else 0.012
        if max(img[i], txt[i]) + pad > 0.52:
            ax.text(img[i] - 0.012, i - 0.2, names[i], va="center", ha="right",
                    fontsize=FONT_PT, color="white", zorder=4)
        else:
            ax.text(max(img[i], txt[i]) + pad, i, names[i], va="center",
                    ha="left", fontsize=FONT_PT, color="#222", zorder=4)
    ax.set_yticks([])
    ax.invert_yaxis(); ax.set_xlim(0, 0.90)
    ax.tick_params(axis="x", labelsize=FONT_PT)
    ax.set_xlabel("crystal-system accuracy   (original eval, n=210, K=3)", fontsize=FONT_PT)
    # no on-canvas title: the claim is made once, in the figure caption
    # the significance count and the identity of the nulls are stated in the
    # CAPTION, not on the canvas
    assert (nsig, len(sc)) == (10, 13)
    # legend in the empty mid-right band: the top rows are occupied by the two
    # longest bars and their in-bar labels, the bottom right by the note box
    ax.legend(loc="upper right", fontsize=FONT_PT, bbox_to_anchor=(0.999, 0.80))
    ax.grid(axis="x", alpha=0.25, zorder=0); ax.set_axisbelow(True)
    # explicit margins, not bbox_inches="tight" -- "tight" crops the PDF page
    # to the content box, shrinking it below 5.5in and defeating the figsize
    # fix (LaTeX \linewidth would then rescale placed text away from 8pt).
    fig.subplots_adjust(left=0.035, right=0.985, top=0.93, bottom=0.11)
    save_pdf(fig, out)
    print(f"{out}: {len(sc)} models, {nsig} significant")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

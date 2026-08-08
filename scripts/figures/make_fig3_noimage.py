"""Figure 3 — the no-image control (CP41).

Reads ledger/CP41_no_image_control/results.json and writes noimage.png.
Usage:  python scripts/figures/make_fig3_noimage.py <ledger_dir> <out.png>
"""
import json, sys
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from _style import apply_style, CHANCE


def main(ledger, out):
    d = json.load(open(f"{ledger}/CP41_no_image_control/results.json"))
    rex = d["roster_extension"]
    sc = {m: v for m, v in rex["paired"].items() if isinstance(v, dict) and "image" in v}
    nsig = rex["significant"]["n"]

    order = sorted(sc, key=lambda m: -sc[m]["image"])
    img = [sc[m]["image"] for m in order]
    txt = [sc[m]["text"] for m in order]
    names = [m.split("/")[-1].replace("-instruct", "") for m in order]
    y = np.arange(len(order))

    apply_style()
    fig, ax = plt.subplots(figsize=(8.6, 6.2))
    ax.barh(y - 0.2, img, height=0.38, color="#4a6fa5", edgecolor="#2b3f5a",
            linewidth=0.6, label="with images", zorder=2)
    ax.barh(y + 0.2, txt, height=0.38, color="#c9b8a0", edgecolor="#6b5d4a",
            linewidth=0.6, label="formula only, no images", zorder=2)
    ax.axvline(CHANCE, color="#8a2f2f", ls="--", lw=1.3, zorder=3,
               label=f"7-way chance ({CHANCE:.4f})")
    for i, m in enumerate(order):
        if sc[m].get("p", 1) < 0.05:
            ax.text(img[i] + 0.008, i - 0.2, "*", va="center", fontsize=10, color="#2b3f5a")
    ax.set_yticks(y); ax.set_yticklabels(names, fontsize=8.5)
    ax.invert_yaxis(); ax.set_xlim(0, 0.90)
    ax.set_xlabel("crystal-system accuracy   (original eval, n=210, K=3)")
    ax.set_title("Removing the image collapses every model toward chance",
                 loc="left", fontsize=11.5, weight="bold")
    ax.text(0.985, 0.02,
            f"* paired difference significant, {nsig} of {len(sc)} models\n"
            "3 nulls are the 3 weakest models (2 at chance even with images)",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=7.8, color="#444")
    ax.legend(loc="lower right", bbox_to_anchor=(0.985, 0.13), fontsize=8.5)
    ax.grid(axis="x", alpha=0.25, zorder=0); ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    print(f"{out}: {len(sc)} models, {nsig} significant")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

"""Figure 2 — the attribution ladder (CP53, CP25).

Reads ledger/CP53_rung_R3_coords_as_text/results.json and writes ladder.png.
Usage:  python scripts/figures/make_fig2_ladder.py <ledger_dir> <out.png>
"""
import json, sys
import os as _os
sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from _style import apply_style, CHANCE


def main(ledger, out):
    d = json.load(open(f"{ledger}/CP53_rung_R3_coords_as_text/results.json"))
    dec = d["decomposition"]; rows = d["rows"]
    r1 = d["oracle_R1"]
    pf = d["perception_fraction"]
    models = [m for m in dec if isinstance(rows.get(m), dict)]
    models.sort(key=lambda m: rows[m]["pixel"])
    r4 = [rows[m]["pixel"] for m in models]
    r3 = [rows[m]["r3_coords"] for m in models]
    frac = [dec[m]["perception_fraction"] for m in models]
    names = [m.split("/")[-1].replace("-instruct", "") for m in models]
    y = np.arange(len(models))

    apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 6.0), gridspec_kw={"width_ratios": [1.5, 1]})
    ax = axes[0]
    for i in y:
        ax.plot([r4[i], r3[i]], [i, i], color="#9aa8b5", lw=1.6, zorder=2)
    ax.scatter(r4, y, s=42, color="#8a5a2f", edgecolor="#4a3018", zorder=3, label="$R_4$ pixels")
    ax.scatter(r3, y, s=42, color="#3a6a8a", edgecolor="#1f3a4a", zorder=3,
               label="$R_3$ exact geometry as text")
    ax.axvline(r1, color="#2f6b3a", lw=1.6, zorder=4, label=f"$R_1$ solver on truth ({r1})")
    ax.axvline(CHANCE, color="#8a2f2f", ls="--", lw=1.2, zorder=4, label=f"chance ({CHANCE:.4f})")
    ax.set_yticks(y); ax.set_yticklabels(names, fontsize=8.5)
    ax.set_xlim(0, 1.02)
    ax.set_xlabel("crystal-system accuracy   (original eval, n=210, K=3)")
    ax.set_title("Supplying exact geometry does not close the gap to the solver",
                 loc="left", fontsize=11, weight="bold")
    ax.legend(loc="lower right", bbox_to_anchor=(0.88, 0.015), fontsize=8)
    ax.grid(axis="x", alpha=0.25); ax.set_axisbelow(True)

    ax2 = axes[1]
    ax2.scatter(r4, frac, s=52, color="#3a6a8a", edgecolor="#1f3a4a", zorder=3)
    ax2.axhline(pf["median"], color="#8a5a2f", ls="-", lw=1.4, zorder=2,
                label=f"median {pf['median']}")
    ax2.axhline(0.5, color="#666", ls=":", lw=1.1, zorder=2, label="perception = symbolic")
    ax2.set_xlabel("pixel accuracy ($R_4$)")
    ax2.set_ylabel("perception share of the total deficit")
    ax2.set_ylim(0, 1.0)
    ax2.set_title("The bottleneck moves with model strength", loc="left",
                  fontsize=11, weight="bold")
    ax2.text(0.03, 0.955, f"Spearman $\\rho$ = {d['spearman_pixel_vs_perception_share']['rho']}, "
             f"p = {d['spearman_pixel_vs_perception_share']['p']}",
             transform=ax2.transAxes, va="top", fontsize=8.4, color="#333",
             bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#ccc", alpha=0.95))
    ax2.legend(loc="lower right", fontsize=8)
    ax2.grid(alpha=0.25); ax2.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    print(f"{out}: {len(models)} models, median perception share {pf['median']}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

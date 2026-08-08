"""Figure 1 — the zero-shot leaderboard (CP26).

Reads ledger/CP26_model_sweep/results.json and writes leaderboard.png.
Usage:  python scripts/figures/make_fig1_leaderboard.py <ledger_dir> <out.png>
"""
import json, sys
import os as _os
sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from _style import apply_style, CHANCE


def main(ledger, out):
    d = json.load(open(f"{ledger}/CP26_model_sweep/results.json"))
    lb = d["leaderboard_canonical_run_A"]
    floor = d["reference_rows"]["shape_free_regularity_floor"]["micro"]
    spread = d["measurement_provenance"]["run_to_run_spread"]

    order = sorted(lb, key=lambda m: lb[m]["micro"])
    vals = [lb[m]["micro"] for m in order]
    names = [m.split("/")[-1].replace("-instruct", "") for m in order]
    y = np.arange(len(order))

    apply_style()
    fig, ax = plt.subplots(figsize=(8.8, 6.4))
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
    ax.set_yticks(y); ax.set_yticklabels(names, fontsize=8.5)
    ax.set_xlim(0, max(max(vals), floor) * 1.28)
    ax.set_xlabel("crystal-system accuracy   (original eval, n=210, K=3)")
    ax.set_title("Every scored model falls below a baseline that never sees the image",
                 loc="left", fontsize=11.5, weight="bold")
    ax.text(0.985, 0.30,
            "error bars: run-to-run spread, mean "
            f"{spread['mean_abs_structures']:.1f} of 210 structures\n"
            "(two independent sweep executions)",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=7.6, color="#444",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#ccc", alpha=0.95))
    ax.legend(loc="lower right", fontsize=8.5)
    ax.grid(axis="x", alpha=0.25, zorder=0); ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    print(f"{out}: {len(order)} models, floor {floor:.4f}, best {max(vals):.4f}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

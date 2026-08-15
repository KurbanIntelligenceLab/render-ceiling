"""Figure 2 -- the attribution ladder (rung_R3_coords_as_text, oracle_within_sample).

Reads results/rung_R3_coords_as_text/results.json and writes a vector
PDF. Usage:  python manuscript/codes/make_fig2_ladder.py <results_dir> <out.pdf>

R12: figsize width is fixed at the placement width so no rescaling occurs and
every font role is placed at exactly 8pt (no mathtext subscripts, which
matplotlib renders smaller than the base size -- labels use plain
"R1"/"R3"/"R4"). DD: the width is the RSC double-column figure width
(17.1 cm = 6.73 in), which is what 0.92\\textwidth resolves to in the
Digital Discovery template; the height is unchanged from the ICLR draw, so
the two panels are squarer.

DD: model identity is a marker shape + colour pair used in both panels, with
y-axis, and the reference rung is the exact-extraction ceiling R1 = 1.0000
(delta <= tau) that the manuscript's Table 1 and captions quote, not the
released-tolerance reading 0.9524 stored as oracle_R1 in the checkpoint.
Shares, median, CI, the sign test and the Spearman are all recomputed at
that reference: median 0.2901, CI [0.1492, 0.3576], 13/14 residual-limited
(p = 0.0018), rho(share, R4) = -0.1588 (p = 0.5877). The Spearman is
reference-invariant only in sign ordering, so it is recomputed rather than
carried over.

B1: the right panel is regenerated from the per-model vectors in
results/rung_R3_coords_as_text/results.json (14-model roster: the 15
r3coords release files minus qwen/qwen2.5-vl-72b-instruct, which is
unscored). It reports and annotates the SHARE correlation,
Spearman(share, R4) = -0.1588 (p = 0.5877) -- no relationship -- and does
NOT annotate Spearman(R3-R4, R4) = -0.6439 (p = 0.0130), which is the raw
component correlation, not the share, and previously mislabeled the panel.
The median share (0.3092) and its bootstrap 95% CI [0.1668, 0.3787], and the
12-of-14 residual-limited sign test (p = 0.0129), are recomputed here from
the same source rather than read off a stored summary field.
"""
import json, sys
import os as _os
sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import numpy as np
from scipy import stats
from scipy.stats import binomtest
import matplotlib.pyplot as plt
from _style import (apply_style, CHANCE, DDWIDTH_IN, FONT_PT, model_styles,
                    panel_letter, save_pdf, wrap_label)


R1_EXACT = 1.0000  # exact-extraction ceiling, delta <= tau (Table 1 of the article)


def main(ledger, out):
    d = json.load(open(f"{ledger}/rung_R3_coords_as_text/results.json"))
    dec = d["decomposition"]; rows = d["rows"]
    r1 = R1_EXACT
    models = [m for m in dec if isinstance(rows.get(m), dict)]
    models.sort(key=lambda m: rows[m]["pixel"])
    r4 = np.array([rows[m]["pixel"] for m in models])
    r3 = np.array([rows[m]["r3_coords"] for m in models])
    # shares recomputed at the exact-extraction reference rather than read from
    # dec[m]["perception_fraction"], which is stored against 0.9524.
    share = (r3 - r4) / (r1 - r4)
    names = [m.split("/")[-1].replace("-instruct", "") for m in models]
    y = np.arange(len(models))

    # B1: recompute both correlations from the per-model vectors; annotate
    # ONLY the share one (the component correlation is a different quantity
    # and must not be presented as evidence for an ordering in R4).
    rho_share, p_share = stats.spearmanr(share, r4)
    median_share = float(np.median(share))
    rng = np.random.default_rng(0)
    boots = np.array([np.median(share[rng.integers(0, len(share), len(share))])
                       for _ in range(20000)])
    ci_lo, ci_hi = np.percentile(boots, [2.5, 97.5])
    n_resid_limited = int(np.sum(share < 0.5))
    sign_p = binomtest(n_resid_limited, len(share), 0.5).pvalue

    apply_style()

    # DD: per-model identity is a marker SHAPE + COLOUR pair, assigned once and
    # used in both panels, with the roster drawn as a shared two-row key below
    # the panels instead of as y-tick labels or in-panel annotations. Left
    # panel: open marker = R4 (pixels), filled marker = R3 (exact geometry as
    # text), so shape/colour carries the model and fill carries the rung.
    style = model_styles(names)

    fig, axes = plt.subplots(1, 2, figsize=(DDWIDTH_IN, 4.25),
                             gridspec_kw={"width_ratios": [1.18, 1], "wspace": 0.22})
    ax = axes[0]
    for i in y:
        mk, cl = style[names[i]]
        ax.plot([r4[i], r3[i]], [i, i], color="#9aa8b5", lw=1.1, zorder=2)
        ax.plot(r4[i], i, marker=mk, ms=5.2, mfc="white", mec=cl, mew=1.2, zorder=3)
        ax.plot(r3[i], i, marker=mk, ms=5.2, mfc=cl, mec=cl, mew=1.0, zorder=3)
    ax.axvline(r1, color="#2f6b3a", lw=1.2, zorder=4)
    ax.axvline(CHANCE, color="#8a2f2f", ls="--", lw=1.0, zorder=4)
    ax.text(r1 - 0.012, len(models) - 0.55, f"R1 oracle ({r1:.4f})", rotation=90,
            ha="right", va="top", fontsize=FONT_PT, color="#2f6b3a")
    ax.text(CHANCE + 0.012, len(models) - 0.55, f"chance ({CHANCE:.3f})", rotation=90,
            ha="left", va="top", fontsize=FONT_PT, color="#8a2f2f")
    ax.set_yticks([])
    ax.set_ylim(-2.5, len(models) - 0.35)
    ax.set_xlim(0, 1.04)
    ax.tick_params(axis="x", labelsize=FONT_PT)
    ax.set_xlabel("crystal-system accuracy", fontsize=FONT_PT)
    panel_letter(ax, "a")
    rung = [plt.Line2D([], [], marker="o", ls="none", ms=5.2, mfc="white",
                       mec="#444", mew=1.2, label="R4 pixels (open)"),
            plt.Line2D([], [], marker="o", ls="none", ms=5.2, mfc="#444",
                       mec="#444", label="R3 text-geometry (filled)")]
    # the rung key sits in an empty band opened below the lowest model row, so
    # it cannot cover a marker at any x
    ax.legend(handles=rung, loc="lower right", fontsize=FONT_PT, framealpha=0.9,
              handletextpad=0.3, borderpad=0.25, labelspacing=0.2)
    ax.grid(axis="x", alpha=0.25); ax.set_axisbelow(True)

    ax2 = axes[1]
    ax2.axhline(median_share, color="#8a5a2f", ls="-", lw=1.2, zorder=2,
                label=f"median {median_share:.3f}")
    ax2.axhspan(ci_lo, ci_hi, color="#8a5a2f", alpha=0.12, zorder=1)
    ax2.axhline(0.5, color="#666", ls=":", lw=1.0, zorder=2, label="parity")
    for nm, xv, sv in zip(names, r4, share):
        mk, cl = style[nm]
        ax2.plot(xv, sv, marker=mk, ms=5.8, mfc=cl, mec=cl, ls="none", zorder=3)
    ax2.set_xlabel("pixel accuracy (R4)", fontsize=FONT_PT)
    ax2.set_ylabel("perception share of deficit", fontsize=FONT_PT)
    ax2.set_xlim(0.06, 0.82)
    ax2.set_ylim(-0.06, 0.90)
    ax2.tick_params(axis="both", labelsize=FONT_PT)
    panel_letter(ax2, "b")
    # the Spearman and the residual-limited count are stated in the CAPTION,
    # not on the canvas; asserted here so the caption cannot drift from the data
    assert abs(rho_share - (-0.1588)) < 5e-4 and abs(p_share - 0.5877) < 5e-4
    assert (n_resid_limited, len(models)) == (13, 14)
    assert abs(median_share - 0.2901) < 5e-4
    assert abs(ci_lo - 0.1492) < 5e-4 and abs(ci_hi - 0.3576) < 5e-4
    ax2.legend(loc="upper right", fontsize=FONT_PT, framealpha=0.95,
               handletextpad=0.4, borderpad=0.3, labelspacing=0.2)
    ax2.grid(alpha=0.25); ax2.set_axisbelow(True)

    # shared roster key: two rows of seven, below both panels. Identifiers are
    # hyphen-wrapped (nothing abbreviated) so the key fits the column width.
    keys = [plt.Line2D([], [], marker=style[nm][0], ls="none", ms=5.2,
                       mfc=style[nm][1], mec=style[nm][1], label=wrap_label(nm))
            for nm in names]
    fig.legend(handles=keys, loc="lower center", ncol=7, fontsize=FONT_PT,
               frameon=False, handletextpad=0.35, columnspacing=1.1,
               labelspacing=0.6, bbox_to_anchor=(0.5, 0.004))
    # NOTE: explicit margins, not bbox_inches="tight" -- "tight" crops the PDF
    # page to the content box, shrinking it below the target width and
    # defeating the figsize fix (LaTeX would then rescale text off 8pt).
    fig.subplots_adjust(left=0.048, right=0.985, top=0.955, bottom=0.315, wspace=0.22)
    save_pdf(fig, out)
    print(f"{out}: {len(models)} models, median share {median_share:.4f} "
          f"CI [{ci_lo:.4f},{ci_hi:.4f}], rho(share,R4)={rho_share:.4f} p={p_share:.4f}, "
          f"{n_resid_limited}/{len(models)} residual-limited sign p={sign_p:.4f}, R1_ref={R1_EXACT}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

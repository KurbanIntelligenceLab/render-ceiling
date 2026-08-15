# Figure generators for the Digital Discovery submission

Every figure in `../render-ceiling-dd` is produced by one script here, from a
checkpoint record under `../../results`. No figure is hand-edited, and no script
takes any input other than a results directory and an output path.

    python manuscript/codes/<script>.py results manuscript/render-ceiling-dd/figures/<name>.pdf

Run from the repository root.

| Script | Output | Source record | Placement |
|---|---|---|---|
| `make_fig1_leaderboard.py` | `leaderboard.pdf` (Fig. 2) | `model_sweep` | article, `0.92\textwidth` |
| `make_fig2_ladder.py` | `ladder.pdf` (Fig. 3) | `rung_R3_coords_as_text` | article, `0.92\textwidth` |
| `make_fig3_noimage.py` | `noimage.pdf` (Fig. 4) | `no_image_control` | article, `0.92\textwidth` |
| `make_fig6_conditions.py` | `conditions.pdf` (Fig. 5) | `visibility_corrected_oracle` | article, `0.92\textwidth` |
| `make_fig4_cuesuff.py` | `cuesuff.pdf` (Fig. S1) | `stratified_frontier_expansion` | ESI, `\linewidth` |
| `make_fig5_generational.py` | `generational.pdf` (Fig. S2) | `generational_comparison` | ESI, `\linewidth` |

Figure 1 of the article is TikZ, drawn inline in
`../render-ceiling-dd/sections/section_introduction.tex`. Every table is
hand-written LaTeX in the section files; there is no table generator.

## Conventions these scripts encode

`_style.py` holds the shared rules. Read it before changing a figure.

**Width is the placement width, so nothing is rescaled.** `DDWIDTH_IN = 6.7333`
(17.10 cm) is what `0.92\textwidth` resolves to in the RSC two-column template;
`SIWIDTH_IN = 6.5354` is the ESI's `\linewidth`. Drawing at the width the figure
is placed at means LaTeX applies no scale factor, so every glyph lands on the
page at `FONT_PT = 8.0` — the RSC minimum. Change the `\includegraphics` width in
the `.tex` and you must change the constant here to match.

**Save with explicit margins, never `bbox_inches="tight"`.** "Tight" crops the
PDF page to its content box, which shrinks the page below the placement width and
silently reintroduces the rescaling the fixed figsize exists to prevent.

**Multi-panel figures carry `(a)`/`(b)`, not per-panel titles.** Use
`panel_letter(ax, "a")`. The claim a title would have made belongs in the figure
caption, so it is stated once. For the same reason there are no on-canvas
annotation boxes: statistics, condition keys and stratum compositions live in the
caption, and each script `assert`s those values against the record so a caption
cannot drift from the data it describes.

**Model identity is a marker shape plus colour, assigned once.** `model_styles()`
returns the pairing and `wrap_label()` breaks a long identifier at the hyphen that
best evens two lines. A figure with a large roster draws the models as a shared
key below the panels rather than crowding identifiers into the axes.

**Read the reference point before trusting a stored share.** The perception
shares in `rung_R3_coords_as_text` are stored against the released merge tolerance
$R_1^{0.15} = 0.9524$, while the article quotes the exact
$R_1 = 1.0000$ ($\delta \le \tau$). `make_fig2_ladder.py` recomputes every share,
the median, its bootstrap CI, the sign test and the Spearman against
`R1_EXACT = 1.0` for that reason. The two readings give different numbers
(median 0.2901 vs 0.3092; 13/14 vs 12/14 residual-limited), so a figure drawn
from the stored field would contradict the text.

# Finding — option_a_frontier

Consolidated record for the exactness revision. It carries the values the article's Section 3.4 and the
ESI's statistical sections report, and it is the source of record for the figure of the attribution ladder.

## What it establishes

The render ceiling is exact, not merely high. Over the 1950 structures of the scale-up sample, the
phantom set is empty at five views on every structure (0 of
1950 structure-subset pairs nonempty), so the oracle returns
every label and $R_1 = 1.0000$ at any tolerance at or below the symmetry tolerance. Emptiness is a property
of the five-camera protocol rather than of the construction: the same census leaves the phantom set nonempty
on 15.4% of two-view pairs and
1.9% of three-view pairs.

## Why the reference point matters

The ladder decomposition is reported against two ceilings, and they disagree. Against the exact
$R_1 = 1.0000$ the median perception share is 0.2901
(bootstrap 95% CI [0.1492, 0.3576]) and 13 of
14 models are residual-limited (sign test p = 0.0018).
Against the released merge tolerance, $R_1 = 0.9524$, the same data give a median of
0.3092 (CI [0.1667, 0.3787]) and
12 of 14 residual-limited (p = 0.0129).
The manuscript quotes the exact reference throughout, so any figure or table drawn from the stored
per-model `perception_fraction` field — which is computed against 0.9524 — would contradict its own text.
`manuscript/codes/make_fig2_ladder.py` recomputes every share against the exact reference for this reason.

The Spearman correlation of perception share against pixel accuracy is
-0.1588 (p = 0.5877), which is
reference-invariant, so perception dominance does not trend with model strength.

## Scope

No model inference was run for this record; the ladder statistics are recomputed from the stored per-model
accuracies of `rung_R3_coords_as_text`. It has no pre-registration because it consolidates and re-reads
measurements already taken rather than testing a new prediction.

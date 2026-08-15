# Phase 2 results — what the manuscript may and may not claim

Checkpoints: ck_2_1_kappa_prediction.json, ck_2_2_noise10.json, ck_2_3_phantoms1933.json,
ck_2_4_frontier1933.json. Predictions for 2.1 were written and timestamped before any measurement.

## 2.1 / 2.2 kappa prediction test — MIXED

Measured accuracy, mean over 10 seeds, n = 210:

| sigma (A) | 0.0 | 0.001 | 0.003 | 0.01 | 0.02 |
|---|---|---|---|---|---|
| Frozen (kappa 2.7321) | 1.0000 | 1.0000 | 0.9971 | 0.9790 | 0.9152 |
| Off-axis (kappa 8.4258) | 1.0000 | 0.9990 | 0.9986 | 0.9110 | 0.4495 |
| Tiled | 1.0000 | 0.9867 | 0.9695 | 0.8924 | 0.8167 |

Crossing sigma for R1 = 0.95, linear interpolation: frozen 0.0146, off-axis 0.0069, tiled 0.0048.

| Prediction | Outcome |
|---|---|
| kappa orders frozen vs off-axis (identical geometry, cameras only) | HOLDS. Frozen crosses at 2.1x the sigma of off-axis; kappa predicted 3.1x. Paired: 18 vs 3 at sigma = 0.01 (p = 0.0015), 102 vs 2 at sigma = 0.02 (p = 5.4e-28) |
| Three-way ordering frozen > tiled > off-axis | FAILS. Tiled measured last, not second |
| Absolute sigma* = 0.4456 for frozen | FAILS. Observed 0.0146, optimistic by 31x |

The tiled arm was mis-specified in the prediction: tiling is not kappa-preserving, since it
multiplies atoms per cell eightfold and shrinks same-species separations, so it degrades robustness
through density rather than conditioning. That arm cannot score kappa in either direction.

Claimable: kappa predicts RELATIVE noise robustness for protocols differing only in camera
placement. Not claimable: a three-way robustness ordering across protocols that differ in atom
density, or any absolute noise budget from Proposition 2's band.

## 2.3 phantom census at scale (n = 1950) — Phi_0 empty at five views

| Views | Structure-subset pairs | Nonempty Phi_0 | Total phantoms |
|---|---|---|---|
| 5 | 1950 | 0 (0.0) | 0 |
| 3 | 19500 | 365 (0.0187) | 8039 |
| 2 | 19500 | 3007 (0.1542) | 136663 |

The pooled correlation of phantom count against atoms per cell flips sign between two views
(+0.4571) and three (-0.1471). Decomposed: conditional on Phi_0 being nonempty, count rises steeply
with density at both view counts (rho 0.8331 at two views n = 1408; rho 0.8273 at three n = 365),
while the probability of being nonempty at all is flat in density at two views (rho 0.0299,
p = 0.19) and decreasing at three (rho -0.1875, p = 6.9e-17). The three-view negative is a mixture
effect, not evidence that density protects against phantoms. Report the decomposition, never the
single pooled coefficient.

## 2.4 delta frontier at scale (n = 1950)

| delta (A) | 0.005 | 0.01 | 0.05 | 0.1 | 0.15 |
|---|---|---|---|---|---|
| Correct | 1949 | 1950 | 1869 | 1787 | 1713 |
| Accuracy | 0.9995 | 1.0000 | 0.9585 | 0.9164 | 0.8785 |

Both memo endpoints reproduce: 1950/1950 at delta = 0.01 and 1713/1950 at delta = 0.15. Note
delta = 0.005 gives 1949/1950, one below the peak, so the frontier is not monotone in delta at the
tight end; the single loss is a structure where the tighter merge tolerance fails to combine two
triangulations of one atom.

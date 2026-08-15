# Option A revision: what changed and how it was verified

Manuscript: `manuscript/revised_new`. All revisions marked `\textcolor{red}{}` (55 spans). Pre-edit copy at
`/tmp/revised_new_preoptionA`. Source of record for every revised value:
`results/option_a_frontier/results.json`, assembled from the per-task checkpoints in this directory.

## The reframing

The ceiling was reported as 0.9524. That number is set by the merge tolerance delta = 0.15 A hardcoded in
`reconstruct.py`, fifteen times the symmetry tolerance tau = 0.01 A used to score it. At delta <= tau the
phantom set is empty and the oracle recovers every structure on both samples, so identifiability is exact
and the operational ceiling is a frontier in extraction tolerance.

| delta (A) | 0.005 | 0.01 | 0.02 | 0.03 | 0.05 | 0.075 | 0.1 | 0.125 | 0.15 | 0.2 | 0.25 | 0.3 | 0.4 | 0.5 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R1, n=210 | 1.0000 | 1.0000 | 0.9952 | 0.9857 | 0.9810 | 0.9667 | 0.9619 | 0.9619 | 0.9524 | 0.9286 | 0.9143 | 0.9048 | 0.9048 | 0.8857 |

At n = 1933: 1950/1950 at delta = 0.01 and 1713/1950 (0.8785) at delta = 0.15. Positions recover to 3.9e-15 A.

All 10 failures at the shipped tolerance recover the correct atom count, and the closest same-species pair
among them is 1.7251 A, 11.5 times delta: over-merging, not projection coincidence.

## Theorem 1 is exact and non-vacuous

| Views | Structure-subset pairs | Phi_0 nonempty | Phantoms |
|---|---|---|---|
| 5 | 1950 | 0 (0.0) | 0 |
| 3 | 19500 | 365 (0.0187) | 8039 |
| 2 | 19500 | 3007 (0.1542) | 136663 |

Five views empties the phantom set; two and three views do not. The condition Theorem 1 names is met by the
protocol rather than by construction.

## The pre-registered conditioning test: one prediction held, two failed

Predictions were written and timestamped before measurement (`ck_2_1_kappa_prediction.json`).

| sigma (A) | 0.0 | 0.001 | 0.003 | 0.01 | 0.02 | Crossing |
|---|---|---|---|---|---|---|
| Frozen (kappa 2.7321) | 1.0000 | 1.0000 | 0.9971 | 0.9790 | 0.9152 | 0.0146 |
| Off-axis (kappa 8.4258) | 1.0000 | 0.9990 | 0.9986 | 0.9110 | 0.4495 | 0.0069 |
| Tiled | 1.0000 | 0.9867 | 0.9695 | 0.8924 | 0.8167 | 0.0048 |

HELD: the contrast that isolates kappa. Frozen and off-axis differ only in camera placement; frozen
tolerates 2.1x the noise where kappa predicted 3.1x. Paired: 18 against 3 at sigma = 0.01 (p = 0.0015),
102 against 2 at sigma = 0.02 (p = 5.4e-28).

FAILED: the three-way ordering. Tiled was predicted second, measured last. Tiling is not kappa-preserving,
since it multiplies atoms per cell eightfold, so it degrades through density; that arm cannot score kappa
either way.

FAILED: the absolute budget. Predicted sigma* = 0.4456 A for frozen against 0.0146 measured, optimistic by
31x, because the band is sufficient rather than tight.

The manuscript claims only the isolating contrast and reports all three outcomes.

## Retracted, and what replaced each claim

| Retracted | Replaced by |
|---|---|
| Tiling loses 22 structures and gains none (identifiability) | Tiling costs nothing at exact extraction; it degrades through atom density |
| Off-axis cameras raise the ceiling to 0.9952 | Off-axis cameras triple kappa and halve noise tolerance |
| kappa = 1.7689 | kappa = 2.7321; band half-width 0.0902 -> 0.1393 A, conclusion unchanged (1.0951 A clears the band by 7.34x) |
| Ceiling is 0.9524 rather than 1.0, so the gap is separable | R0 = R1 = 1.0000, so the entire deficit is the model's |

## The ladder strengthens

| Statistic | At R1 = 0.9524 | At R1 = 1.0000 |
|---|---|---|
| S(m) > P(m) | 12 of 14, p = 0.0129 | 13 of 14, p = 0.0018 |
| Median perception share | 0.3092, CI [0.1667, 0.3787] | 0.2901, CI [0.1492, 0.3576] |
| Spearman share vs pixels | -0.1588, p = 0.5877 | -0.1588, p = 0.5877 |
| Exceptions | 2 | 1 |

No model inference was re-run; all 14 models' R3 and R4 are stored. The method section's manual R0 -> R1
correction is removed, since the two rungs now coincide.

## Citations added

Tomasi & Kanade, IJCV 9(2):137-154, 1992, DOI 10.1007/BF00129684 (the oracle's methodological ancestor);
Daunhawer et al., ICLR 2023; GaussianCAD, Computers and Electrical Engineering 2026 (PII S0045790626001497,
ISSN-matched). TriaGS is arXiv-only and held back. GaussianCAD's full author list is paywalled and must be
retrieved before camera-ready.

## Verification

Three independent layers, all passing (`ck_3_9_verification.log`):

1. Value and pairing check (`scripts/verify_option_a.py`): every revised number matches its checkpoint,
   with sample size and tolerance correctly paired. This check exists because an earlier draft presented two
   same-delta numbers from different samples as a tolerance step.
2. Repo ledger (`scripts/verify_manuscript_numbers.py`): all seven project documents pass, including
   `INTERNAL_REVIEW_RESOLUTION.md`, which failed before this revision.
3. Final sweep: no retracted claim survives unqualified, every R1 = 1.0000 assertion carries its tolerance
   condition, all three prediction outcomes are reported, and all 35 newly introduced values trace to option_a_frontier.

LaTeX structure was checked separately (`ck_3_10_latex_check.log`): braces, environments, all four table
column counts, 34 references and 20 citations resolve. No LaTeX toolchain is available in this environment,
so the PDF was not rebuilt; `main.pdf` on disk is the pre-revision build.

## Corrections found in project documents

`INTERNAL_REVIEW_RESOLUTION.md` asserted kappa = 1.7689 with empirical amplification 1.7656 and concluded
the bound was tight. Corrected to 2.7321 and 2.7318, with the superseded values retained and labelled. The
same document's median same-species separation of 2.8793 A does not reproduce under any definition tried
(per-structure minimum with or without PBC, per-species pooled, all pairs pooled, or the mean: 2.9006,
2.9858, 3.8988, 4.5390, 3.1505); replaced by 2.9006 with the accounting recorded. The minimum, 1.0951 A,
reproduces exactly and is the value the argument rests on.

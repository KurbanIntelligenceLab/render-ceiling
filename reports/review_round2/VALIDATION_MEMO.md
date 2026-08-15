# Render-ceiling manuscript: reviewer validation and reframing options

Decision memo. Every number below was recomputed from `data/` and `scripts/src/cocr/` in this
repository; nothing is carried over from the manuscript text. Raw outputs are in
`reports/review_round2/validation_all.json`.

## 1. Summary

The reviewer's substantive requests were sensitivity analyses: how does the ceiling move with the
symmetry tolerance tau and the reconstruction merge tolerance delta, and with centroid noise. Running
them found that the manuscript's headline ceiling of 0.9524 is set by the merge tolerance
delta = 0.15 A hardcoded in `reconstruct.py`, not by identifiability. At delta matched to the paper's own
symmetry tolerance tau = 0.01 A, the ceiling is 1.0000 on both evaluation samples, and the phantom set
that Theorem 1 identifies as the oracle's only failure mode is empty.

Three claims do not survive. Two of them are the render-convention consistency checks, which return
with the opposite sign and a different mechanism once conditioning is measured instead of assumed. The
attribution ladder, the fabrication finding, and every control reproduce exactly and strengthen slightly.

## 2. What reproduces exactly

| Quantity | Manuscript | Recomputed | Status |
|---|---|---|---|
| R1, original sample, delta = 0.15 | 200/210 = 0.9524 | 200/210 = 0.9524 | exact |
| Atom drops (n_rec < n_true) | never | 0 of 210 | exact |
| Median perception share | 0.3092 | 0.3092 | exact |
| Bootstrap 95% CI on that median | [0.167, 0.379] | [0.1667, 0.3787] | exact |
| S(m) > P(m) count | 12 of 14 | 12 of 14, p = 0.0129 | exact |
| Spearman share vs pixel accuracy | -0.1588, p = 0.5877 | -0.1588, p = 0.5877 | exact |
| Spearman (R3-R4) vs R4 | -0.6439, p = 0.0130 | -0.6439, p = 0.0130 | exact |
| Decomposition identity P + S = R1 - R4 | asserted | holds for all 14 models | exact |
| View-sweep table (delta = 0.15) | 0.7481 / 0.9152 / 0.9371 / 0.9524 | identical to 4 dp | exact |
| Detector median precision / recall | 0.4278 / 0.4227 | stored values confirmed | exact |
| kappa at 5 degrees separation | approx 16 | 16.2108 | exact |
| Reasoning-budget null | 130/210 both settings, p = 1.0000 | stored values confirmed | exact |

## 3. Finding 1: the ceiling is a frontier in delta, not a single number

`reconstruct_positions()` triangulates and merges at `tol = 0.15` A while `recover_symmetry()` runs
spglib at `symprec = 0.01` A. The merge tolerance is 15x the symmetry tolerance, so the merge step
collapses distinct atoms and displaces the survivors by more than spglib's tolerance. Sweeping delta at
fixed tau = 0.01, correct structures out of 210:

| delta (A) | 0.005 | 0.01 | 0.02 | 0.03 | 0.05 | 0.075 | 0.1 | 0.125 | 0.15 | 0.2 | 0.25 | 0.3 | 0.4 | 0.5 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Frozen protocol | 210 | 210 | 209 | 207 | 206 | 203 | 202 | 202 | 200 | 195 | 192 | 190 | 190 | 186 |
| Off-axis cameras | 210 | 210 | 210 | 210 | 210 | 210 | 209 | 209 | 209 | 208 | 205 | 203 | 195 | 185 |
| 2x2x2 tiled geometry | 210 | 210 | 207 | 204 | 198 | 192 | 187 | 185 | 178 | 170 | 161 | 159 | 154 | 151 |

All 10 failures at delta = 0.15 are over-merging, not coincidence. Each recovers the correct atom count;
the closest same-species pair among the 10 is 1.7251 A, over eleven times delta. Each returns the correct
label once delta is reduced.

Joint (delta, tau) grid, correct of 210:

| delta \\ tau | 0.001 | 0.01 | 0.05 | 0.1 |
|---|---|---|---|---|
| 0.001 | 210 | 210 | 210 | 209 |
| 0.01 | 208 | 210 | 210 | 209 |
| 0.05 | 204 | 206 | 210 | 208 |
| 0.15 | 198 | 200 | 203 | 206 |

The manuscript's operating point (0.15, 0.01) is the second-worst cell in this grid. The frontier is not
new theory: Proposition 2 already states that a centroid-triangulating pipeline with extraction error
epsilon matches the oracle outside a band of width 2 kappa epsilon. delta is that pipeline's tolerance to
epsilon. Tracing the curve is the measurement the proposition asks for and the paper does not report.

## 4. Finding 2: Theorem 1 is exactly satisfied, and non-vacuously

An independently written oracle (all 10 independent view pairs rather than the hardcoded pair, cluster-mean
representatives, acceptance and verification at tau) gives:

| tau (A) | 1e-6 | 1e-4 | 1e-3 | 0.01 | 0.05 | 0.15 |
|---|---|---|---|---|---|---|
| R1 | 210/210 | 210/210 | 210/210 | 210/210 | 208/210 | 193/210 |
| Max reconstruction error (A) | 3.9e-15 | 3.9e-15 | 3.9e-15 | 1.0e-3 | 2.2e-2 | 8.1e-2 |

Phi_0 = empty on all 210 structures at five views, with recovery to machine precision. The scaled sample
agrees: 1950/1950 at delta = 0.01 against 1713/1950 (0.8785) at delta = 0.15.

The phantom set is not empty by construction. Censused directly:

| Views | Structure-subset pairs | With Phi_0 nonempty | Total phantoms |
|---|---|---|---|
| 2 | 2100 | 305 (0.1452) | 6165 |
| 3 | 2100 | 39 (0.0186) | 477 |
| 5 | 210 | 0 (0.0000) | 0 |

Phantoms are real and common at sparse view counts and are eliminated exactly at five views. This is a
stronger theorem-to-measurement link than the current text, which attributes 10 failures to coincidence
when they are tolerance artefacts.

## 5. Finding 3: both render-convention findings reverse

| Leg | delta = 0.15 | delta = 0.01 |
|---|---|---|
| Frozen | 200/210 | 210/210 |
| Off-axis | 209/210 (gained 9, lost 0, p = 0.0039) | 210/210 (gained 0, lost 0) |
| Tiled | 178/210 (gained 0, lost 22, p = 4.8e-7) | 210/210 (gained 0, lost 0) |

At exact extraction the three protocols are identifiability-equivalent. The abstract's 'supplying it the
shipped tiling loses 22 structures and gains none', offered as a consistency check on Corollary 3(b), is a
delta artefact. Corollary 3(b) is itself correct, but with five cameras the remaining views resolve every
lattice-vector ambiguity, so the corollary predicts no loss on this protocol and the check was not testing it.

View-count monotonicity also cleans up: 195 of 22,050 structure-level violations at delta = 0.15 becomes
9 of 11550 at delta = 0.01, all in two-view subsets.

## 6. Finding 4: kappa is misreported, and the corrected value recovers both legs

Proposition 2 defines kappa as the max over enumerated independent view pairs of ||[P_v; P_w]^+||_2. The
manuscript and `run_g1_detector.py` use 1.7689. Computed over all 10 pairs: max = 2.7321
(pair axis_a / oblique2). Per-pair values:

| Pair | 01 | 02 | 03 | 04 | 12 | 13 | 14 | 23 | 24 | 34 |
|---|---|---|---|---|---|---|---|---|---|---|
| kappa | 1.0 | 1.0 | 1.4142 | 2.7321 | 1.0 | 2.0 | 1.1547 | 1.328 | 1.328 | 2.2823 |

1.7689 = 1.33 squared, and 1.328 is the kappa of pairs (2,3) and (2,4), so a squaring slip is the likely
origin. No variant I constructed reproduces it: stacked, transposed, hstacked, Frobenius, or
sigma_max/sigma_min. Random-perturbation amplification confirms 2.7321 empirically (2.7266 over 20,000 draws).

The correction is load-bearing, because kappa is what separates the protocols under noise. The off-axis
perturbation raises kappa from 2.7321 to 8.4258, a factor of 3.1.
Per-view Gaussian centroid jitter of sigma A, delta scaled to the noise, spglib tolerance matched to the
measured reconstruction error, mean accuracy over three seeds:

| sigma (A) | 0.0 | 0.001 | 0.003 | 0.01 | 0.02 |
|---|---|---|---|---|---|
| Frozen (kappa = 2.7321) | 1.0000 | 1.0000 | 0.9968 | 0.9730 | 0.9222 |
| Off-axis (kappa = 8.4258) | 1.0000 | 0.9984 | 0.9984 | 0.9095 | 0.4524 |
| Tiled | 1.0000 | 0.9857 | 0.9683 | 0.9032 | 0.8159 |

The protocols are equivalent at exact extraction and separate under noise in kappa order. The frozen
protocol is therefore not information-suboptimal as the manuscript claims; it is the noise-robust choice,
and the off-axis perturbation buys nothing for a 3.1x conditioning penalty. The direction is predicted in
advance by Proposition 2's kappa rather than retrofitted.

## 7. Effect on the attribution ladder

No model inference is needed; all 14 models' R3 and R4 are stored. Moving the reference from R1 = 0.9524
to R1 = 1.0000 adds 0.0476 to every S(m) and leaves every P(m) unchanged.

| Model | R4 | R3 | P | S at 0.9524 | share | S at 1.0000 | share |
|---|---|---|---|---|---|---|---|
| google/gemini-3.6-flash | 0.7333 | 0.8524 | 0.1191 | 0.1000 | 0.5436 | 0.1476 | 0.4466 |
| x-ai/grok-4.5 | 0.6143 | 0.8524 | 0.2381 | 0.1000 | 0.7042 | 0.1476 | 0.6173 |
| anthropic/claude-opus-4.8 | 0.5810 | 0.6667 | 0.0857 | 0.2857 | 0.2307 | 0.3333 | 0.2045 |
| qwen/qwen3-vl-235b-a22b-instruct | 0.3333 | 0.5429 | 0.2096 | 0.4095 | 0.3386 | 0.4571 | 0.3144 |
| meta-llama/llama-4-scout | 0.2048 | 0.5048 | 0.3000 | 0.4476 | 0.4013 | 0.4952 | 0.3773 |
| meta-llama/llama-4-maverick | 0.4429 | 0.4952 | 0.0523 | 0.4572 | 0.1026 | 0.5048 | 0.0939 |
| amazon/nova-pro-v1 | 0.1810 | 0.4667 | 0.2857 | 0.4857 | 0.3704 | 0.5333 | 0.3488 |
| mistralai/mistral-medium-3.1 | 0.2286 | 0.4524 | 0.2238 | 0.5000 | 0.3092 | 0.5476 | 0.2901 |
| mistralai/mistral-small-2603 | 0.1476 | 0.4524 | 0.3048 | 0.5000 | 0.3787 | 0.5476 | 0.3576 |
| qwen/qwen3-vl-32b-instruct | 0.2286 | 0.4524 | 0.2238 | 0.5000 | 0.3092 | 0.5476 | 0.2901 |
| qwen/qwen3-vl-8b-instruct | 0.3762 | 0.4524 | 0.0762 | 0.5000 | 0.1322 | 0.5476 | 0.1222 |
| z-ai/glm-4.6v | 0.4429 | 0.4476 | 0.0047 | 0.5048 | 0.0092 | 0.5524 | 0.0084 |
| bytedance-seed/seed-1.6 | 0.2571 | 0.4238 | 0.1667 | 0.5286 | 0.2398 | 0.5762 | 0.2244 |
| openai/gpt-4.1-mini | 0.3667 | 0.4143 | 0.0476 | 0.5381 | 0.0813 | 0.5857 | 0.0752 |

| Statistic | At R1 = 0.9524 | At R1 = 1.0000 |
|---|---|---|
| S(m) > P(m) | 12 of 14, p = 0.0129 | 13 of 14, p = 0.0018 |
| Median perception share | 0.3092, CI [0.1667, 0.3787] | 0.2901, CI [0.1492, 0.3576] |
| Spearman share vs pixel | -0.1588, p = 0.5877 | -0.1588, p = 0.5877 |
| Exceptions (P > S) | gemini-3.6-flash, grok-4.5 | grok-4.5 |

The ladder's central claim strengthens: the post-perception residual dominates for 13 of 14 rather than 12
of 14, and the p-value improves by an order of magnitude. The method section's manual R0-to-R1 correction
(which already notes that correcting moves shares down and strengthens the conclusion) becomes unnecessary,
because R0 and R1 coincide at 1.0000. The negative Spearman result is unchanged, so the 'perception
dominance is a property of the top of the roster' framing survives with one exception instead of two.

## 8. Reviewer questions now answered with data

| Question | Answer |
|---|---|
| Sensitivity of R1 to tau, and label flips | 198 to 206 of 210 over symprec 0.001 to 0.1 at delta = 0.15. At the matched delta = 0.01: 208 at symprec 0.001, 210 at 0.01 and 0.05, 209 at 0.1. At delta = 0.001: 210 for symprec up to 0.05. R1 is not flat in tau at any single delta -- reaching 210 requires delta <= tau, and the residual loss at symprec 0.001 with delta = 0.01 is the same over-merging effect one decade down |
| Sensitivity to merge tolerance delta, tied to tau | Full frontier in section 3; delta must be <= tau to avoid over-merging |
| Centroid-noise robustness, kappa to practical brackets | Section 6 table; R1 >= 0.997 to sigma = 0.003 A, 0.973 at 0.01, 0.884 at 0.03 |
| Per-crystal-system confusion for R1 | Diagonal at delta = 0.01 (30 per system, 7 systems, zero off-diagonal); computed at delta = 0.15 as well |
| Tiling: projection coincidence vs phantom density | Answered: neither. Both legs are delta artefacts and vanish at matched tolerance |
| Camera calibration / conditioning predictions | kappa predicts the noise ordering across all three protocols |

Remaining reviewer requests not addressed by this work, unchanged from the manuscript's own limitations:
model arms at n = 1933, a stronger extractor to measure the R2 rung, perspective and shading regimes, and
roster currency.

## 9. Two story options

### Option A: the ceiling is a frontier (recommended)

Headline: renders determine the label exactly, verified at machine precision on 2160 structures with
Phi_0 = empty, and the operational ceiling is a frontier in extraction tolerance whose shape is a protocol
property. The two convention legs return as kappa-predicted conditioning results.

Gains: Theorem 1 goes from approximately confirmed to exactly confirmed and non-vacuous; the design
guidance becomes quantitative (views buy phantom elimination, camera spread costs conditioning, with a
measured exchange rate); the ladder claim strengthens to 13 of 14 at p = 0.0018; the paper answers three
reviewer questions with new measurements rather than caveats.

Costs: abstract, teaser figure, Table 1, the conventions section and the conclusion all change. Two claims
retract as identifiability findings and return as conditioning findings. The framing sentence 'the ceiling
is 0.9524 rather than 1.0, so the gap between the ceiling and a model is separable from the gap between the
ceiling and the label' is lost, since R0 and R1 now coincide.

### Option B: frontier as an added section, 0.9524 retained as the shipped operating point

Keep 0.9524 in the abstract, relabelled as the shipped pipeline's operating point at delta = 0.15 rather
than as the ceiling; add Theorem 1 exactness and the frontier as a new results subsection. The convention
legs still have to retract to conditioning findings, because their delta = 0.15 significance is an artefact
either way.

Gains: teaser figure and Table 1 survive largely intact; smaller diff.

Costs: the abstract still leads with a tolerance-dependent number while the paper's own appendix shows the
tolerance-free value is 1.0000, which a referee who reads the new section will notice. The 'ceiling of
0.9524 rather than 1.0' separability argument is still unavailable.

## 10. What is unaffected under either option

The learned-extractor fabrication finding (median recall 0.0000, 105 of 206 structures with no emitted
atom within tolerance of a real one, against 0.400 for a colour-threshold blob detector); the image-removal
control; the formula-only control pair; the atom-count confound analysis; the detector characterisation and
its factor-of-6.6 localisation failure, which is a tau/2 comparison and does not depend on kappa; the
reasoning-budget null; the cell-metric baseline and its specification-reading range; label certification;
and the composition-exclusion split. The scale-up baseline comparison is unaffected in direction, though
the oracle side of it moves to 1.0000.

## 11. Corrections required regardless of the option chosen

1. kappa: 1.7689 becomes 2.7321 in Proposition 2's discussion, in `run_g1_detector.py`, and in the
   ambiguity-band half-width, which moves from 0.0902 A to 0.1393 A. The band still avoids the closest
   interatomic distance of 1.0951 A, so the conclusion there is unchanged.
2. The relationship between delta and tau must be stated in the main text. The reviewer asked for exactly
   this and the manuscript currently gives delta no numeric value outside the algorithm block.
3. Missing related work, all verified to exist: Tomasi and Kanade 1992 orthographic factorization, the
   direct methodological ancestor of this oracle and currently uncited; GaussianCAD (orthographic CAD
   reconstruction); TriaGS (differentiable triangulation); Daunhawer et al. ICLR 2023 (multi-view
   identifiability).

CHECKPOINT: view_subset_sweep   GAP: Corollary 3(a) proves R1 is non-decreasing in the view
     set at tau = 0. That is a falsifiable prediction of the paper's own theory and it was
     untested. (audit gap G2 / red flag R10)
STATUS: DONE. THE PREDICTION HOLDS IN AGGREGATE AT 103 OF 105 NESTED PAIRS, AND THE TWO
     EXCEPTIONS ARE REAL RATHER THAN NOISE. Reported as measured, with the violation mechanism
     identified. Zero API calls; 5460 reconstructions in 15 s on 10 CPU processes.

WHAT WAS RUN. The ideal-extraction oracle over every view subset of size 2-5 drawn from the
frozen five-camera set (axis_a, axis_b, axis_c, body_diagonal, oblique2) = 26 subsets, on the
210-structure original evaluation sample, symprec 0.01, angle tolerance 5.0, ray tolerance 0.15 A.
Zero structure-level errors.

THE SAMPLE IS THE LOCAL ONE, DELIBERATELY. oracle_view_curve ran an earlier view curve through the live
database query and recorded that 21 of 280 material_ids changed between two runs at the same
seed, because the seed fixes the draw order and not the candidate pool. This sweep reads
data/e3/structures.json, the same 210 structures every other arm in the paper is scored on, so
its numbers are comparable to the ladder rather than to a fresh draw.

=================  THE CURVE  ================================================================
  views   subsets   mean R1    min       max
    2        10     0.7481    0.6762    0.8000
    3        10     0.9152    0.8857    0.9524
    4         5     0.9371    0.9095    0.9524
    5         1     0.9524    0.9524    0.9524

The full frozen five-camera set gives R1 = 200/210 = 0.9524, which REPRODUCES THE PAPER'S
HEADLINE CEILING EXACTLY from an independent code path. The knee is at three views: 2->3 gains
16.7 points, 3->4 gains 2.2, 4->5 gains 1.5. That agrees with oracle_view_curve's 280-structure curve
(0.7429 / 0.9143 / 0.9357 / 0.9393) to within 0.09 to 1.31 percentage points, on a different
sample, which is a reproducibility result in its own right. Per view count the absolute
differences are 0.52, 0.09, 0.14 and 1.31 points; the largest sits at five views, where oracle_view_curve's
0.9393 on 280 structures meets 0.9524 on this 210-structure sample.

Note that the best THREE-view subset (axis_a, body_diagonal, oblique2) already reaches 0.9524.
The fifth camera buys nothing on the crystal-system task; it buys the guarantee below.

=================  THE MONOTONE CHECK, STATED HONESTLY  ======================================
105 nested pairs C subset C'.
  AGGREGATE violations (mean R1 falls when a view is added):  2 of 105
  PER-STRUCTURE violations (correct at C, wrong at C'):     195 of 22050 = 0.884%
  structures showing at least one violation:                 25 of 210

The two aggregate violations share a subset and a direction:
  axis_a|body_diagonal|oblique2 (200/210) -> +axis_b (198/210): gained 3, lost 5
  axis_a|body_diagonal|oblique2 (200/210) -> +axis_c (195/210): gained 4, lost 9

Corollary 3(a) is proved at tau = 0. This sweep runs at tau > 0, where the corollary is
approximate, so these are violations of the approximation and not counterexamples to the
theorem. Reporting them rather than asserting none is the point of the exercise.

=================  MECHANISM: PHANTOMS, NOT LOST ATOMS  ======================================
n_recovered < n_true NEVER occurs, in any of the 5460 cells. The oracle never drops an atom,
which is exactly what Theorem 1 says. Every failure is a PHANTOM: a spurious point that survives
cross-view verification. Mean phantom excess (n_recovered - n_true) falls monotonically with
view count and reaches zero at the full set:

  2 views 4.911 | 3 views 0.480 | 4 views 0.048 | 5 views 0.000

So the fifth camera does not raise mean accuracy much; it eliminates phantoms entirely
(210 of 210 structures recover exactly the true atom count). That is the design consequence
worth stating: extra views buy reconstruction FIDELITY after they stop buying accuracy.

Why a superset can still lose a structure: at the violating cells the subset's reconstruction
carries a mean positional RMSD of 0.1801 A (median exactly 0) while the superset's is 0.0505 A
and NEVER exactly 0. Adding a view removes phantoms but perturbs which candidate survives
deduplication, and spglib at symprec 0.01 can flip a system on a sub-0.06 A perturbation. The
subset was sometimes right for a reason the tolerance made fragile, not because fewer views
carried more information.

=================  THE TEN FIVE-VIEW FAILURES ARE NOT RECONSTRUCTION FAILURES  ===============
At the full camera set, all 210 structures recover the exact true atom count and 89 have RMSD
identically zero. The 10 structures the oracle gets wrong all have exact atom counts. They fail
inside spglib at the production tolerance, not in the inversion. The ceiling at 0.9524 is
therefore a LABEL-TOLERANCE limit on this sample, not a view-geometry limit.

=================  WHAT THIS ADDS TO THE PAPER  ==============================================
A third one-sided-in-aggregate theory check alongside the tiling result (22 lost, 0 gained) and
the camera perturbation (9 gained, 0 lost), at zero API cost, plus an independent reproduction
of R1 = 0.9524 through a separate code path. Unlike those two it is NOT perfectly one-sided, and
the paper should say so.

Reproduce: python scripts/run_viewsweep.py   (rc-analysis env; pymatgen + spglib 2.7.0; CPU only)
Artifacts: raw.json (per-structure x per-subset), summary.json (aggregates).

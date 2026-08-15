CHECKPOINT: rung_R2_detector_oracle   GAP: R1 never touches a pixel — it inverts the cameras from
     GROUND-TRUTH projections. So "perception is the bottleneck" rested on an instrument that assumes
     perception. R2 substitutes a real extractor's detections into the identical inversion. (ICLR rung R2)
STATUS: DONE AND REPORTED UNSCORED BY MY OWN PRE-REGISTERED GATE. The rung does not enter the ladder.

THE GATE, QUOTED FROM THE PRE-REGISTRATION WRITTEN BEFORE THE RUN.
  "If R2 fails to triangulate on >5% of structures, report the failure rate and do NOT score it."
  MEASURED, BOTH SETS: original 40/210 = 19.0%, expansion 47/210 = 22.4% recover ZERO atoms. The gate
  fails by 14 and 17 points respectively, so the verdict is consistent across independently drawn samples.
  So the value R2 produces — 16/210 = 0.0762 on the original set — IS NOT A LADDER RUNG and is not
  plotted as one. It is reported here as a diagnostic only (expansion: 18/210 = 0.0857).

I ALSO PRE-REGISTERED THE EXPECTATION, AND IT HELD.
  "With recall at 0.400 I expect R2 at or BELOW R4 ... a detector that finds two atoms in five cannot
   reconstruct a lattice. If that happens, R2 does NOT separate extraction from reasoning; it only shows
   THIS detector is worse than the models, and I will say so rather than presenting a floor as an
   attribution."
  R2 = 0.0762 against the best model's 0.6905, i.e. 0.6143 BELOW it. None of B1/B2/B3 fires. Saying so.

WHAT THE RUN DOES ESTABLISH, WHICH IS NOT NOTHING.
1. THE PIPELINE IS CORRECT, so the failure is attributable to the detector rather than to my plumbing.
   Zero exceptions across 420 structures (both sets). The pixel-to-projection calibration is EXACT: a least-squares
   affine per view against ground-truth pixels has max residual 0.0000 in projection units. And the same
   inversion reproduces R1 exactly when fed ground-truth projections (visibility_corrected_oracle's O0 gate, 200/210).
2. THE DETECTOR IS THE BINDING LIMIT, and it fails in the way its own measurements predict. Median
   recovered/true atom ratio 0.400, which equals the detector's independently measured median recall of
   0.400 from atom_detection. Atom-count match on 2 of 210.
3. MISSING DETECTIONS DO NOT MERELY SUBTRACT — THEY CORRUPT. 44 of 210 original and 25 of 210 expansion
   structures OVER-triangulate
   (n_recovered > n_true) despite the detector finding FEWER atoms than exist. Dropping a disc in one view
   lets a ray from a different atom pass the cross-view consistency test, manufacturing phantom sites. This
   is worth recording as a mechanism: an extraction stage's errors propagate non-monotonically through
   triangulation, so recall alone does not predict reconstruction quality.

THE MANDATORY CO-REPORTED OPERATING POINT, per the pre-registration, to appear wherever R2 is mentioned:
  median recall 0.400, median precision 0.233, median centroid error 0.717 px on matched atoms.
R2 IS A LOWER BOUND FROM ONE CONCRETE EXTRACTOR. It is not a ceiling for extraction in general, and it does
not license any claim about how much of the R1-to-R4 gap extraction accounts for. That attribution remains
UNMEASURED, and the honest statement is that we bound it from neither side: R1 assumes perfect extraction,
R2 uses an extractor too weak to be informative.

WHAT WOULD MAKE THIS RUNG WORK. A detector at recall >0.9 — a trained detector rather than connected
components on colour thresholds. That is a real experiment and it is NOT in this package. Recorded as the
single most valuable missing measurement, since R2 is the only rung that would attribute the gap between
the oracle and the models to a stage rather than describing it.

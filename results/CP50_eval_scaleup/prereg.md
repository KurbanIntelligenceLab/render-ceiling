PRE-REGISTRATION — CP50 evaluation-set scale-up
Committed BEFORE generation. CPU for data + oracle + classical arms; tiered API for the model arms.

GAP. Every accuracy in this package rests on n=210. "n is too small" is the first reviewer objection and it
is correct: a 210-structure sample gives a minimum detectable paired difference near 0.09, so adjacent
leaderboard rows are not separable and the shape-free floor is a single-sample quantity.

METHOD. Regenerate the evaluation set at n = 2000 under the IDENTICAL rules already frozen:
  - composition-exclusion against the 1610-structure training set, verified to zero overlap
  - the frozen five-camera render protocol at 768 px, 2x2x2 supercell, radii 0.5
  - the canonical labelling tolerance (symprec 0.01, angle_tolerance 5.0) with the tolerance sweep and
    quarantine policy unchanged
  - stratified by crystal system
  - zero overlap with the 280-structure oracle sample
TIERING, because API cost scales with the roster and not with the science:
  FULL 2000  oracle, classical baselines (shape-free floor, 19-feature RF)
  CORE 500   a stratified subset, named in every table that uses it, for the model arms
The existing 210 and 210-expansion sets survive as NAMED HISTORICAL SAMPLES and their results are reported
as replications, not as the headline.

DECISION RULE, fixed now.
  S1  the shape-free floor on 2000 lands within 0.05 of the 210 value (0.5286) -> the floor is a stable
      property of the task and every below-floor claim in the package survives at scale
  S2  the floor MOVES by more than 0.05 -> every below-floor claim is re-scoped to its sample, and the
      abstract's thesis sentence must be rewritten. THIS IS THE OUTCOME THAT COSTS THE MOST TO ABSORB and
      it is why the sentence was already written to survive the floor moving.
  S3  the ORACLE ceiling on 2000 lands within 0.03 of 0.9524 -> the identifiability result generalises
      beyond the original draw; outside that, report the scale-dependence.

WHAT WOULD MAKE A ROW UNINFORMATIVE. Any structure whose space-group number flips across the tolerance
sweep is QUARANTINED as before, and the quarantine rate is reported. If quarantine exceeds 10% the sample
is not comparable to the 210 set and that is stated rather than absorbed.

EXPECTED, STATED FIRST. I expect S1 and S3: both quantities are geometric properties of the structure
distribution rather than of the draw. If the floor moves materially, the most likely cause is a different
composition mix at 2000, and I will check that before reporting a scale effect.

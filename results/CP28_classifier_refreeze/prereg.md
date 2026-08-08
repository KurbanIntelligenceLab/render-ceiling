PRE-REGISTRATION — CP28 classifier refreeze   (ICLR plan, Phase A)
Committed BEFORE any refit or recompute.

GAP. Two cited classifiers cannot be reproduced from the record:
  (a) the random forest on 19 lattice-metric features — three values have circulated (0.8905 original
      run, 0.8857 reproduced, 0.8762 gradient boosting) and the original feature list was never saved;
  (b) the box-sufficiency predicate — CP15 records a 137/73 split whose exact rule is not recoverable.
      CP25 searched 50 tolerance x branch-order combinations; two reproduced the COUNT, none reproduced
      the stratum COMPOSITION, establishing the rule as structurally different from its description.

WHAT I WILL DO.
  1. Refit the RF on the 1610 train structures, evaluate on the 210 original eval, n_estimators=500,
     seed 23. Write to the ledger: the ORDERED feature list, sklearn and numpy versions, the
     hyperparameters, and the per-structure prediction vector.
  2. Adopt CP25's 140/70 predicate (2% length, 1 degree angle, monoclinic branch requiring beta
     genuinely non-90) as CANONICAL and write its exact source. Recompute EVERY stratified row in
     CP15, CP24, CP25 and the paper on that predicate.

DECISION RULE, fixed now.
  - The refrozen RF value becomes the cited value everywhere. 0.8905 goes to a footnote as the
    unreproducible original.
  - If the refit lands OUTSIDE 0.8857 +/- 0.02, report BOTH values and treat the refit as a second
    non-reproduction rather than a repair.
  - Recomputed stratified rows are published even where they CHANGE a significance verdict. A p-value
    that crosses 0.05 under the canonical predicate is reported as such, not suppressed and not
    described as a robustness check.
  - Old 137/73 values are retained in correction notes, never deleted.

WHAT WOULD MAKE THIS UNINFORMATIVE.
  - If the refit's per-structure vector disagrees with the recorded 186/210 by more than 10 structures,
    the feature list I reconstruct is not the one originally used and I will say so rather than
    presenting the refit as a recovery.

SCOPE NOTE. This is bookkeeping, not a new result. No claim in the paper becomes stronger because a
classifier was refrozen; the point is that a reviewer recomputing any stratified row gets the published
number.

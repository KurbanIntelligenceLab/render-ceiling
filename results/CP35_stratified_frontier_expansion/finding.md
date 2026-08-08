CHECKPOINT: CP35_stratified_frontier_expansion   GAP: CP15's stratified mechanism failed to replicate on
              a single arm; does it hold against a CONTROL rather than a moving baseline? (directive Phase D)
STATUS: DONE. BRANCH D1 FIRES, 3 OF 3 ARMS ON BOTH SAMPLES — AND THIS CONTRADICTS THE EXPECTATION I
     RECORDED BEFORE RUNNING. My pre-registration said "I expect D3" and named the existing expansion data
     as pointing away from the claim. It was wrong, and the reversal is the result.

WHAT WAS RUN. gemini-3.6-flash, grok-4.5, claude-opus-4.8 on the 210 expansion structures, frozen 5-view
renders, K=3, temperature 0.7, verbatim CP14 prompt. Zero unparseable, zero API errors on all three arms.
Partition is the CP28 canonical predicate, verified this session to reproduce 140/70 (original) and 141/69
(expansion) with composition identical to the record across all five metric classes.
RF control refit to the FROZEN specification and verified to reproduce 188/210 = 0.8952 exactly.

THE PRIMARY CONTRAST, pixel-minus-RF, negative means the pixel model trails the numeric reader:

  arm                  sample      suff gap   amb gap    widens?   pixel amb-vs-suff Fisher p
  claude-opus-4.8      original     -0.3000   -0.3429      YES        1.04e-01
  claude-opus-4.8      expansion    -0.2695   -0.3623      YES        1.73e-04
  gemini-3.6-flash     original     -0.0857   -0.3143      YES        4.95e-06
  gemini-3.6-flash     expansion    -0.0851   -0.2609      YES        4.00e-08
  grok-4.5             original     -0.2571   -0.3286      YES        5.02e-02
  grok-4.5             expansion    -0.2270   -0.4203      YES        2.31e-07

THREE OF THREE ARMS WIDEN ON THE AMBIGUOUS STRATUM ON BOTH SAMPLES. That is D1: pixel models lose their
advantage over a numeric reader of the same cell specifically where the cell metric is degenerate.

WHY THIS IS NOT THE SAME CLAIM CP15 MADE, AND WHY IT SURVIVES WHERE CP15 DID NOT. CP15 compared a pixel
arm's raw accuracy across strata, which moves with the stratum's intrinsic difficulty. THE RF CONTROL DROPS
TOO (original 0.9214 -> 0.8429, expansion 0.9433 -> 0.7536), so a raw drop proves nothing. The contrast is
what the pre-registration named as primary, and it is what replicates. CP15's withdrawal stands; this is a
weaker and different claim tested against a control.

CONFOUND STATED, NOT BURIED. The ambiguous stratum is LARGELY ONE DEGENERACY: 60 of 70 (original) and 58
of 69 (expansion) are hexagonal-or-trigonal. So "cue-ambiguous" and "hexagonal/trigonal confusion" are
close to the same partition on these samples, and the finding could equally be described as a hex/trig
effect. Both descriptions are reported.
DE-CONCENTRATION CHECK, with n stated as the prereg requires. Removing hex/trig leaves n=10 (original) and
n=12 (expansion). The gap persists on both — original -1.0000 / -0.6000 / -0.6000, expansion -0.5000 /
-0.6667 / -0.5000 — but AT THESE n A SINGLE STRUCTURE MOVES THE VALUE BY 8 TO 10 POINTS. The residual is
SUGGESTIVE ONLY and is not evidence the effect is independent of the hex/trig degeneracy. It is reported
because the prereg required it, not because it settles anything.

WHAT THIS LICENSES. The render convention's cue-sufficiency partition predicts where a pixel reader falls
behind a numeric reader of the same cell, on two independent samples and three frontier models. It is a
property of the partition tested against a control, not an accuracy pattern.
WHAT IT DOES NOT LICENSE. Any claim that the effect is separable from the hexagonal/trigonal confusion; the
residual n is too small. And no mechanism: this measures where the gap widens, not why.

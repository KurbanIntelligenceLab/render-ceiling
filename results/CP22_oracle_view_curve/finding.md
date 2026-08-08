CHECKPOINT: CP22_oracle_view_curve   GAP: how much information does the view SET deliver, as a
                                     function of view count, independent of any model?
                                     (directive Stage 0c)
STATUS: DONE, AND THE SATURATION CLAIM IS WEAKER THAN FIRST STATED. A paired test on the same 280
        structures puts the saturation point at FOUR views, not three, and the 3->4 step is itself
        NOT RESOLVED (7 gained vs 1 lost, exact p = 0.0703). The defensible statement is ONE view of
        slack, not two. See the PAIRED TEST section. This is a protocol finding obtainable with no model and no API spend.

=================  THE CURVE  ================================================================
Ideal-extraction oracle (perfect atom localisation, triangulated from the frozen cameras), n=280:
  views   crystal system   point group   space group    delta (crystal system)
    2         0.7429          0.6464        0.4107           -
    3         0.9143          0.8357        0.7429        +0.1714
    4         0.9357          0.9143        0.9071        +0.0214
    5         0.9393          0.9179        0.9107        +0.0036
THE KNEE IS AT 3 VIEWS for crystal system: 2->3 gains 17 points, 3->4 gains 2, 4->5 gains 0.4.
The frozen protocol ships FIVE views, so it is delivering two views past the point where crystal-
system information saturates. That matches the known model-side result (1->3 views is the large jump,
3->5 flat) and shows the flatness is a property of the INFORMATION, not a model limitation.
SPACE GROUP BEHAVES DIFFERENTLY and this matters for how the finding is stated: it is still climbing
steeply at 3->4 (+0.164) and only flattens by 5. So "past the knee" is true for the crystal-system
task this paper evaluates, and NOT true for the harder space-group task. A protocol recommendation
must name its task.

=================  TWO LIMITS ON THE SWEEP, BOTH GEOMETRIC RATHER THAN CHOSEN  ================
1 VIEW IS IMPOSSIBLE, not merely absent. The oracle triangulates atom positions from multiple
projections; a single projection gives one ray per atom and no depth, so reconstruct_positions raises
on a single camera. The directive asked for 1 view; the honest answer is that the oracle is undefined
there, and any 1-view number would have to come from a different instrument.
8 VIEWS DO NOT EXIST. The frozen protocol defines exactly five cameras (axis_a, axis_b, axis_c,
body_diagonal, oblique2). Extending to 8 would mean adding cameras, which changes the protocol and is
not a free Stage-0 analysis. Reported as out of scope rather than silently omitted.

=================  A SAMPLING NOTE THAT LOOKS LIKE A REPRODUCIBILITY FAILURE AND IS NOT  ======
The rerun's 4-view crystal-system value is 0.9357; the previously recorded value is 0.9321. Both are
exact integer counts on 280 (262 and 261), so one structure differs. Cause, checked rather than
assumed: the two runs drew DIFFERENT SAMPLES — 21 of 280 material_ids differ — despite the same
--seed 0, because the harness samples from a live database query whose result set has changed since
the original run. The seed fixes the draw ORDER, not the candidate pool.
So 0.9321 and 0.9357 are two samples, not a computation discrepancy, and neither is wrong. The curve
above is reported on ONE consistent sample (the rerun) so its shape is internally valid. On the
original sample the 2/3/4 values are 0.7393 / 0.9071 / 0.9321 — THE SAME KNEE, which is the check
that matters.
CONSEQUENCE: the oracle harness is not reproducible against a moving database. Any future oracle
number must ship its material_id list. The original sample's ids are preserved in the prior artifact.

=================  WHAT THIS DOES AND DOES NOT LICENSE  =======================================
LICENSES: "the frozen 5-view protocol delivers crystal-system information that already saturates at
3 views" — a statement about the render protocol, model-free, and directly relevant to anyone
choosing a view count for VLM consumption. It also bounds what view-count optimisation can buy for
this task: at most the 0.4 points between 4 and 5 views, plus whatever a better-CHOSEN 3 views gains
over the current 3.
DOES NOT LICENSE: any claim that reducing to 3 views would leave MODEL accuracy unchanged. The oracle
assumes perfect extraction; a model that reads views imperfectly may still benefit from redundancy
the oracle does not need. That is a separate experiment.

=================  PAIRED TEST ON CONSECUTIVE STEPS — THE CLAIM SHRINKS  ======================
The original reading compared marginal rates. The right test is paired, on the same 280 structures:
  step    gained   lost   exact p    verdict
  2 -> 3      50      2    <1e-4     REAL
  3 -> 4       7      1     0.0703   NOT RESOLVED
  4 -> 5       1      0     1.0000   not resolved
WHAT THIS CHANGES. "Saturates at 3" is NOT supported: the 3->4 step gains 7 structures and loses 1,
which does not reach significance but is not negligible either. "Saturates at 4" is the closest
defensible reading, since 4->5 moves exactly one structure. So the frozen 5-view protocol carries
ONE view of slack, not two.
The directive predicted 3->4 would be 6 gained and 0 lost, giving p = 0.031 and a real step. The
actual discordance is 7-1, which is p = 0.0703 — so by the directive's own decision rule the step is
NOT established, and neither is the 3-view saturation it would have licensed. One view of slack is a
modest but honest free protocol finding; the two-view version is retired.
STATED FOR THE PAPER: crystal-system information delivered by the view set is essentially complete at
FOUR views (the 4->5 step moves one structure of 280); whether three suffice is unresolved at this
sample size. Space group behaves differently and is still climbing at 3->4, so any recommendation must
name its task.

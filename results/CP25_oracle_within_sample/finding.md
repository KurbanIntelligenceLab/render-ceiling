CHECKPOINT: CP25_oracle_within_sample   GAP: is the localization gap real on the SAME structures the
                                        models were scored on, or an artifact of comparing two
                                        disjoint samples? (directive item 1)
STATUS: DONE. BRANCH W1 FIRES ON BOTH EVALUATION SETS. The oracle runs on the evaluation sets with
        ZERO failures, so the gap is now WITHIN-SAMPLE, PER-STRUCTURE and PAIRED. The
        sample-disjointness caveat that qualified every use of CP24's result is REMOVED.

=================  IT RUNS, AND THERE WAS NO BLOCKER  ========================================
The oracle is a deterministic geometric computation: triangulate atom positions from the frozen
cameras at perfect localisation, then spglib. Both evaluation sets have ground-truth structures and the
same cameras, so it runs directly. 210 structures per set, 0 exceptions, 0 unresolved.
  ORACLE, ideal extraction:   original eval 0.9524 (4v) / 0.9524 (5v)
                              expansion eval 0.8952 (4v) / 0.9095 (5v)
NOTE THAT THIS IS CONSERVATIVE FOR CP24, NOT FLATTERING. CP24's cross-sample oracle was 0.9357 on its
own 280-structure sample; the evaluation sets give 0.9524 and 0.8952. The original eval set is HIGHER,
so the cross-sample bracket understated the gap there.

=================  THE PAIRED RESULT — ORIGINAL EVAL SET, n=210  =============================
Oracle at the shipped 5 views vs each arm, McNemar exact on discordant pairs, same named structures:
  arm            arm acc   oracle    delta   oracle-only   arm-only     exact p
  A3_native       0.6905   0.9524   +0.2619       61            6       1.5e-12
  B1_direct       0.6190   0.9524   +0.3333       76            6       1.6e-16
  V2b_chain       0.3810   0.9524   +0.5714      122            2       7.3e-34
  B3_chain        0.2810   0.9524   +0.6714      145            4       5.7e-38
=================  AND ON THE EXPANSION SET, n=210  ==========================================
  B1_direct       0.4524   0.9095   +0.4571      104            8       2.0e-22
  V2b_chain       0.4000   0.9095   +0.5095      118           11       8.6e-24
BOTH SETS, EVERY ARM, p < 1e-11. The discordance is heavily one-sided: on the original set the oracle
is right and the best arm wrong on 61 structures while the reverse holds on 6, a 10.2:1 ratio.
THAT 10:1 IS THE BEST ARM'S AND IS THE WEAKEST OF THE SIX - DO NOT GENERALISE IT. Ratios across every
arm x set combination: A3 original 61:6 = 10.2:1, B1 original 76:6 = 12.7:1, V2b original 122:2 =
61.0:1, B3 original 145:4 = 36.2:1, B1 expansion 104:8 = 13.0:1, V2b expansion 118:11 = 10.7:1. The
range is 10.2:1 to 61.0:1, so quoting "~10:1" as though it characterised all arms understates the
chain arms by up to sixfold. State the range or name the arm. Arm
accuracies reproduce the recorded values exactly (B1 0.6190, V2b 0.3810, A3 0.6905 on the original;
B1 0.4524, V2b 0.4000 on the expansion), which is the check that the per-structure vectors are the
same ones the leaderboard was built from.

=================  WHAT THIS LICENSES, AND IT IS MORE THAN CP24 COULD  ========================
LICENSED NOW, without the cross-sample caveat: on these exact 420 structures, rendered under the frozen
protocol, ideal atom extraction recovers the crystal system on 90-95% while the best model recovers
45-69%, and the difference is per-structure and overwhelmingly one-sided. The information IS present in
these renders; these models do not recover it. That is a localization statement about the model, not
about the render or the data.
STILL NOT LICENSED. Perfect atom localisation is assumed, so this bounds what is unrecovered GIVEN
extraction. It does NOT show a model could have extracted the positions from pixels — the oracle reads
ground-truth coordinates, not the image. The correct reading is that the render CARRIES the
information and the bottleneck is upstream of symmetry reasoning, in perception.

=================  A CAVEAT ON THE STRATIFIED ROWS: CP15's CLASSIFIER IS NOT EXACTLY RECOVERABLE  ===
I could not reproduce CP15's 137/73 box-sufficiency split. CP15 records "tolerances 2% on lengths,
1 deg on angles"; that convention gives me 140/70, and 1%/0.5deg gives 144/66. The composition of the
ambiguous stratum matches on five of six metric classes (60 hexagonal_or_trigonal, 4 tetragonal,
3 cubic, 2 orthorhombic, 1 trigonal_rhombohedral) and differs only in the 3 monoclinic entries, which
my rule places in the sufficient stratum. Inspecting the near-miss structures shows a cluster of
triclinic-truth cells with angles within 1-4 deg of monoclinic, so the recorded split depends on a
tolerance or branch-ordering detail that was never written down.
I THEN SEARCHED FOR IT EXHAUSTIVELY rather than concluding from two attempts: a 50-combination grid over
length tolerance (0.5%, 1%, 2%, 3%, 5%), angle tolerance (0.5, 1, 1.5, 2, 3 deg) and both monoclinic
branch variants. Exactly TWO combinations reproduce the count of 73, both at 3% length / 0.5 deg angle
— and NEITHER reproduces the composition: they give 7 tetragonal and 1 monoclinic against the recorded
4 and 3, with the recorded single trigonal_rhombohedral entry absent. So the count match is a
coincidence of totals, not a recovery, and no tolerance setting of this rule produces CP15's split.
CP15 used a structurally different rule than the one its finding.md describes.
CONSEQUENCE, STATED PRECISELY: the HEADLINE paired result above does NOT depend on the partition and is
unaffected. The stratified breakdown DOES, so it is reported as approximate with the classifier
discrepancy named. This is the SECOND unrecoverable classifier in this package after the random-forest
feature list, and the standing rule now is that any classifier whose output is cited must have its
exact parameters written into the ledger at the time of first use.
The approximate stratified rows (my 140/70 split, original eval set) for completeness:
  arm            box-sufficient delta   p          box-ambiguous delta   p
  A3_native            +0.2639        7.5e-11            +0.2576      1.5e-03
  B1_direct            +0.3056        3.7e-11            +0.3939      2.6e-06
  V2b_chain            +0.6111        6.5e-27            +0.4848      1.9e-08
  B3_chain             +0.7778        1.6e-31            +0.4394      1.3e-07
The gap is large and significant on BOTH strata for every arm, which is the robust reading regardless
of the exact partition: this is not a box-ambiguous-specific deficit.

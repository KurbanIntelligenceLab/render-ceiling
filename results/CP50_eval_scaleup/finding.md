CHECKPOINT: CP50_eval_scaleup   GAP: every accuracy in this package rested on n=210. "n is too small" is
     the first reviewer objection and it was correct. (ICLR directive)
STATUS: DONE, AND BRANCH S2 FIRES. THE SHAPE-FREE FLOOR DOES NOT SURVIVE AT SCALE, WHICH RETIRES THE
     PACKAGE'S MOST-QUOTED CLAIM. A size-matched control separates two causes that moved together and
     shows the oracle's apparent drop is something else entirely.

=====  THE SAMPLE  =====
1995 structures, MP, 2-4 elements, conventional cell <= 80 atoms, stratified EXACTLY 285 per crystal
system. QUARANTINE RATE 3.11% (62 structures), inside the pre-registered 10% gate.
LEAKAGE AUDIT: 0 overlap with the 1610 training set, 0 with the original 210 eval, 0 with the 210
expansion. Composition exclusion enforced against 1198 training compositions.

=====  THE HEADLINE: THE FLOOR MOVES, AND IT IS NOT A SAMPLE-SIZE EFFECT  =====
  quantity                        n=210    n=1995   size-matched (n=721)
  shape-free floor (3 features)   0.5286   0.2090        0.2205
  geometric oracle                0.9524   0.8797        0.9459
  19-feature cell-metric RF       0.8952   0.8697          --

Both moved, so I ran the control the pre-registration demanded before calling anything a scale effect:
restrict the new sample to cells no larger than the 95th percentile of the old one (37 atoms) and
re-stratify. The 1995 sample has a MEDIAN OF 38 ATOMS PER CELL against the original's 14 — 2.7x larger —
because the two draws used different filters.

THE CONTROL SEPARATES THE TWO QUANTITIES CLEANLY.
  THE ORACLE'S DROP IS A CELL-SIZE EFFECT. At matched size it returns to 0.9459, within 0.0065 of the
  original 0.9524. More atoms per cell means more projective coincidence and more correspondence ambiguity,
  which is the mechanism CP20 already established. So S3's apparent failure was a composition difference
  between draws, NOT scale, and the identifiability result generalises once cell size is held fixed.
  THE FLOOR'S DROP IS NOT. At matched size it is 0.2205, still 0.3081 below the original. The floor stays
  near 0.22 whether n is 721 or 1995 and whether cells are large or small, so 0.5286 WAS A PROPERTY OF THE
  ORIGINAL 210 DRAW rather than of the task.

=====  WHAT THIS RETIRES  =====
"All 13 zero-shot models fall below a composition-only baseline" HOLDS ONLY ON THE ORIGINAL 210 SAMPLE.
  best zero-shot 0.4429 vs 210-sample floor 0.5286        BELOW
  best zero-shot 0.4429 vs size-matched floor 0.2205      ABOVE
  best zero-shot 0.4429 vs full-1995 floor 0.2090         ABOVE
The claim is re-scoped to its sample wherever it appears, and it can no longer be stated as a property of
the task. This is the outcome the pre-registration named as the most expensive to absorb, and the reason the
abstract's thesis sentence was written to survive the floor moving: the thesis rests on the
oracle-to-model gap, which SURVIVES (0.9459 against 0.4429 at matched size), not on the below-floor
comparison.

=====  WHY THE ORIGINAL FLOOR WAS SO HIGH, STATED AS A HYPOTHESIS NOT A RESULT  =====
The 3-feature floor reads atom count, density and cell volume. In a 210-structure draw with a median of 14
atoms those three numbers evidently separate the seven systems far better than they do in a broader draw.
I have NOT established the mechanism and am not claiming one; what is established is that the 0.5286 does
not reproduce on an independently drawn, composition-excluded, identically stratified sample at either
cell-size regime.

=====  A DEFECT IN MY OWN AUDIT, AND WHAT IT COST  =====
I FIRST PUBLISHED "quarantine rate 0" AND IT WAS WRONG. The check read a top-level `tolerance_robust` key
that the label schema does not have — the flag is nested under `tolerance` — so `.get()` returned None,
my `if not lab.get("tolerance_robust", True)` defaulted to True for every structure, and the quarantine
NEVER RAN. The generation loop's printed "quarantined 0" was the count of a filter that could not fire.
THE TRUE RATE IS 3.11% (62 of 1995) by the union criterion: space group flips across the
tolerance sweep, OR the canonical neighborhood-stability test fails, OR label policy declines it for
training. That is inside the pre-registered 10% gate, so the sample remains comparable — but the gate was
never actually tested until now.
RESCORING WITHOUT THE 62 CHANGES NOTHING MATERIAL, which is the only reason the conclusions stand:
  quantity            with quarantined (n=1995)   clean (n=1933)   shift
  oracle                      0.8797               0.8774      -0.0023
  shape-free floor            0.2090               0.2054      -0.0036
  19-feature RF               0.8697               0.8738      +0.0041
Largest shift 0.0041, so S2 still fires and the floor still does not survive. THE CLEAN NUMBERS ARE
CANONICAL and the with-quarantined ones are retained here as the superseded values.
Quarantine removes strata unevenly — triclinic loses 39 of 285, cubic loses none — so the clean sample is
no longer exactly uniform, and that is stated rather than smoothed.

A SECOND CHECK THE SAME BUG PROMPTED, WHICH CAME BACK CLEAN. The generation log carried spglib
"ssm_get_exact_positions failed" warnings. A silent fallback to the trivial group would show as an excess of
P1: there are 109 P1 structures, 38.2% of the 285-strong triclinic stratum, across 144 distinct space
groups present. That is a normal distribution for a triclinic-inclusive draw, not a degenerate one, so the
warnings did not corrupt labels.

=====  WHAT IS NOT RUN  =====
The tiered MODEL arms on the 500-structure core subset. The oracle and both classical baselines are
complete on the full 1995 because they are free; the model leg is 500 x 13 x K=3 = 19,500 calls and has not
been spent. Every model number in this package therefore still rests on n=210, and the leaderboard is
reported with that sample named. The oracle-to-model gap at scale is bounded on the oracle side only.

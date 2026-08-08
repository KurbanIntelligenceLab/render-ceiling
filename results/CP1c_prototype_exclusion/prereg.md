# PRE-REGISTRATION — structure-prototype-exclusion split (the arbiter of the B1 memorization headline)
# Written and committed BEFORE any evaluation was run on this split.

## WHY THIS SPLIT EXISTS
CP1b took branch (a): B1-direct held at 0.6143 on the composition-exclusion split (vs IID
0.711), refuting the pre-registered SFT-memorizes/RL-generalizes prediction. CP1b's own
refutation note names the likely reason: composition-exclusion withholds ELEMENTS, not the
lattice geometry the task actually depends on, so it is OOD in chemistry while plausibly IID
in the decisive feature. This split tests that explanation directly.

## THE SPLIT (built and verified; data/e3proto/)
Prototype definition (AFLOW-style, deterministic, no external DB needed — computed from the
existing sidecar): (space group number, anonymized reduced stoichiometry, sorted per-element
Wyckoff (multiplicity, letter) multiset). Element identities are ANONYMIZED so isostructural
compounds (NaCl / KBr) share a prototype — the point is to withhold the ARRANGEMENT.

  structures 1820 -> 883 distinct prototypes (613 singletons = 33.7% of structures)
  train 1610 / eval 210, whole prototype classes assigned to eval
  eval balance: 30 per crystal system, all 7 systems (exactly matching data/e3)
  prototype overlap train n eval = 0        (VERIFIED)
  eval-only elements = 0                    (VERIFIED — chemistry held constant BY DESIGN)
  renders reused from data/e3/renders (identical per material_id, same frozen view set)
  seed 23 (same as the composition-exclusion split)

This is the CONTROLLED COMPLEMENT of data/e3: same sizes, same balance, same renders, same
labels — one withholds chemistry, the other withholds geometry.

## WHAT WILL BE RUN
The full CP1b table on the prototype-exclusion eval set, same protocol as everywhere else
(3-sample majority vote, temp 0.7, 512 max new tokens): B1, SFT-V1, B3, V2a, V2b.
NOTE: these checkpoints were TRAINED on the composition-exclusion train set, which overlaps
the prototype-exclusion TRAIN ids only partially. This is an EVALUATION-ONLY probe of the
existing checkpoints, not a retrained comparison — see the caveat below, which is why the
decision rule is written on B1's DROP rather than on absolute cross-split levels.

## DECISION RULE (pre-registered)
Reference: B1 composition-exclusion 0.6143 +/- 0.0515 (seed SD). Movement threshold 0.05
(the largest observed arm SD), consistent with CP0c.

  (i)  B1 COLLAPSES under prototype exclusion (drops > 0.05, i.e. <= ~0.56) WHILE the chain
       arms hold (within 0.05 of their composition-exclusion values)
       => the memorization story PARTIALLY REVIVES. Report BOTH splits side by side; state
          explicitly that B1's robustness is chemistry-specific and does not extend to unseen
          structural arrangements. The legibility-tax frame then carries a second finding:
          the tax is smaller (or reverses) on geometry-OOD data.
  (ii) B1 HOLDS (within 0.05 of 0.6143)
       => the CP1b robustness finding STRENGTHENS and the legibility-tax frame carries alone.
          The "composition-exclusion is IID in the decisive feature" explanation is then NOT
          sufficient, and we must say so.
  (iii) ALL arms drop together (> 0.05)
       => the split is simply harder for everyone; report as a difficulty shift, NOT as
          evidence about memorization, and compare arm ORDERING rather than levels.

## CAVEAT FIXED IN ADVANCE (so it cannot be reported selectively)
The checkpoints were trained on data/e3's train split. Some prototype-exclusion EVAL
structures were therefore SEEN IN TRAINING (they sit in data/e3 train). That means this probe
UNDERSTATES any prototype-exclusion effect: it is a lower bound on the true geometric-OOD
drop. A clean test requires retraining on data/e3proto/train, which is deferred and explicitly
NOT claimed here. The number of eval ids that appear in data/e3's train split will be counted
and reported alongside the result.

CHECKPOINT: CP1c_prototype_exclusion     GAP: is B1's OOD robustness chemistry-specific?
STATUS: DONE as a no-retrain stratified probe (double-OOD subset). The full retrained
prototype-exclusion comparison is BUILT but NOT RUN (see "what was NOT done").
RESULT: pre-registered BRANCH (ii) — B1 HOLDS. The memorization story does NOT revive.

=================  WHY THIS CHECKPOINT EXISTS  =================
CP1b took branch (a) (B1-direct 0.6143 on composition-exclusion vs 0.711 IID), refuting the
SFT-memorizes/RL-generalizes prediction. CP1b's own refutation note offered the leading
explanation: composition-exclusion withholds ELEMENTS, not the lattice geometry the task
depends on, so it may be OOD in chemistry while IID in the decisive feature. CP1c tests that.

=================  WHAT WAS BUILT  =================
data/e3proto/ — a structure-PROTOTYPE-exclusion split, the controlled complement of data/e3.
Prototype key (AFLOW-style, deterministic, computed from the existing sidecar — no external
database): (space group number, anonymized reduced stoichiometry, sorted per-element Wyckoff
(multiplicity, letter) multiset). Element identities ANONYMIZED so isostructural compounds
(NaCl / KBr) share a prototype; the split therefore withholds the ARRANGEMENT.
  1820 structures -> 883 distinct prototypes (613 singletons = 33.7% of structures)
  train 1610 / eval 210, whole prototype classes assigned to eval
  eval balanced 30 per crystal system, all 7 systems (matching data/e3 exactly)
  prototype overlap train n eval = 0     VERIFIED
  eval-only elements = 0                 VERIFIED (chemistry held constant BY DESIGN)
  renders reused (identical per material_id), seed 23, sidecar reused

Structures were re-fetched by material_id to build this (data/e3/structures.json, 1820 CIFs)
and AUDITED against the sidecar by the CP0 method: 1820/1820 reproduce the recorded
crystal_system AND space-group number (rate 1.0, 0 mismatch, 0 missing). So the structures
used for prototyping are provably the ones the VLM was labelled against.

=================  A BLOCKER FOUND, AND WHY THE PROBE CHANGED SHAPE  =================
Evaluating the EXISTING checkpoints on data/e3proto/eval would be close to meaningless:
189/210 (90.0%) of that eval set sits in data/e3's TRAIN split, i.e. the checkpoints were
trained on it. Only 21/210 were never trained on, and those 21 are severely unbalanced
(1 cubic, 6 hexagonal, 2 monoclinic, 1 orthorhombic, 2 tetragonal, 5 triclinic, 4 trigonal).
Running the CP1b table there would mostly measure memorization of SEEN structures — the
opposite of the intended test. This is logged rather than worked around.

INSTEAD, a valid no-retrain probe exists in the data we already have: of data/e3's 210 eval
structures, 83 have a PROTOTYPE that is also absent from data/e3's train split. Those 83 are
simultaneously composition-OOD (unseen element, by the split's construction) AND
prototype-OOD (unseen arrangement) with respect to what the checkpoints actually trained on.
This "DOUBLE-OOD subset" needs zero new generation — it is a stratified re-scoring of the
CP1b and CP3 predictions already in hand.
  subset per-system: hexagonal 8, monoclinic 17, orthorhombic 9, tetragonal 12,
                     triclinic 21, trigonal 16, cubic 0.
  NOTE: unbalanced and contains NO cubic structures, so it is a STRATIFIED RE-ANALYSIS, not
  a replacement for the balanced split. Cubic is the easiest system, and its absence lowers
  all arms' absolute numbers — which is why only the WITHIN-ARM DELTA is interpreted.

=================  RESULT  =================
Same predictions, same protocol; full 210-structure eval vs the 83-structure double-OOD
subset. Deltas are within-arm, so the subset's imbalance affects all arms identically.

  arm            full 210                        double-OOD (83)                delta
  B1-direct      0.590 / 0.567 / 0.686 = 0.6143  0.518 / 0.615 / 0.542 = 0.5583  -0.0560
  SFT-V1 (s0)    0.3524                          0.2892                         -0.0632
  B3             0.3444                          0.2811                         -0.0633
  V2a            0.3762                          0.2530                         -0.1232
  V2b            0.3857                          0.2570                         -0.1287

BRANCH TAKEN: (ii) — B1 HOLDS. Its drop (-0.0560) is at the pre-registered 0.05 threshold and
INSIDE its own seed SD (0.0515), while both process arms lose more than twice as much
(-0.123, -0.129). B1 still leads the best chain arm by +0.30 on the hardest subset.
B1 drops LEAST, not most.

CONSEQUENCE, stated as the pre-registration requires: the "composition-exclusion is IID in
the decisive feature" explanation offered in CP1b is NOT SUFFICIENT. B1's robustness survives
withholding the structural ARRANGEMENT as well as the chemistry. The memorization story does
not revive, the CP1b robustness finding STRENGTHENS, and the legibility-tax frame carries
alone. We should stop looking for a split that rescues an accuracy headline.

A SECONDARY OBSERVATION (directional, not a claim): the two PROCESS arms degrade roughly 2x
more than the outcome arm and the SFT baseline under geometric OOD. If that survives a
retrained test it would mean dense per-step geometric supervision buys faithfulness at the
cost of geometric generalization — an interesting and reportable tension. It is NOT
established here: n=83, single split, no seeds for SFT-V1, and the contamination structure
differs per arm. Flagged for the retrained run.

=================  WHAT WAS NOT DONE  =================
The clean test of the built split requires RETRAINING on data/e3proto/train and evaluating on
data/e3proto/eval. That is not done and is not claimed. The double-OOD probe is a lower bound
on the geometric-OOD effect for the existing checkpoints; the split is built, audited, and
ready if the retrain is authorized.

REPRODUCE
  split build:   prototype keys from data/e3/labels_sidecar.json (see prereg.md for the key)
  structures:    scripts/fetch_e3_structures.py -> data/e3/structures.json (+ label audit)
  split files:   data/e3proto/{train,eval}.jsonl, split_meta.json, contamination.json,
                 double_ood_subset.json
  scoring:       stratified re-scoring of evals_cp1b/*.json and the harvested e3m_votes.json

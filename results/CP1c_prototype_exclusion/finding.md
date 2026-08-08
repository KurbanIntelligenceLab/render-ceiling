CHECKPOINT: CP1c_prototype_exclusion     GAP: is B1's OOD robustness chemistry-specific?
STATUS: DONE as a no-retrain stratified probe (double-OOD subset). The full retrained
prototype-exclusion comparison is BUILT but NOT RUN (see "what was NOT done").
RESULT: pre-registered BRANCH (iii) — ALL ARMS DROP TOGETHER. This is a DIFFICULTY SHIFT and
the pre-registration FORBIDS reading it as evidence about memorization. The probe therefore
DOES NOT arbitrate the CP1b question; only arm ORDERING may be compared.

[CORRECTION — this record originally claimed BRANCH (ii) "B1 HOLDS" and drew the
 memorization-relevant conclusions that branch (iii) forbids. That was WRONG against my own
 pre-registered rule: branch (ii) required B1 to hold WITHIN 0.05 and B1's drop is 0.0560,
 which EXCEEDS 0.05. All four arms exceed the threshold (B1 -0.0560, B3 -0.0633,
 V2a -0.1232, V2b -0.1287), which is exactly the condition branch (iii) defines. I had noted
 in prose that B1's drop sat "right at the threshold" and then resolved the ambiguity toward
 the conclusion I preferred — the precise failure the pre-registration exists to prevent.
 Pre-correction text preserved in finding_prebranchfix_snapshot.md.]

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

BRANCH TAKEN: (iii) — ALL ARMS DROP TOGETHER. Every arm's magnitude exceeds the pre-registered
0.05 threshold: B1 -0.0560, SFT-V1 -0.0632, B3 -0.0633, V2a -0.1232, V2b -0.1287. Branch (i)
required the chain arms to hold (they do not); branch (ii) required B1 to hold within 0.05
(0.0560 > 0.050, so it does not). Branch (iii) is therefore the rule that applies.

WHAT THE PRE-REGISTRATION PERMITS AND FORBIDS HERE:
  FORBIDDEN: reading this as evidence about memorization in either direction. The subset is
    simply harder for every arm, so it CANNOT distinguish "B1's robustness is chemistry-
    specific" from "B1's robustness is general". CP1b's proposed explanation (composition-
    exclusion may be IID in the decisive feature) is NEITHER confirmed NOR refuted by this
    probe, and this checkpoint does NOT strengthen the CP1b robustness finding.
  PERMITTED: comparing arm ORDERING rather than levels. THE ORDERING DOES NOT SURVIVE INTACT —
    an earlier version of this record wrongly claimed it was "unchanged". Actual orderings:
      full eval (210):  B1 0.6143 > V2b 0.3857 > V2a 0.3762 > SFT-V1 0.3524 > B3 0.3444
      double-OOD (83):  B1 0.5583 > SFT-V1 0.2892 > B3 0.2811 > V2b 0.2570 > V2a 0.2530
    So BOTH PROCESS ARMS FALL BELOW SFT-V1 AND B3 on the harder subset — a rank INVERSION,
    which is the direct consequence of their >2x larger drops noted below (the two statements
    are the same fact; claiming "unchanged ordering" alongside it was self-contradictory).
    What DOES survive: B1 remains first by a wide margin (+0.269 over the next arm on the
    subset; +0.2286 over the best chain arm on the full set). So CP1b's branch (a) — B1 leads
    — is not disturbed. But CP3's Gate-2 ordering (process > outcome) DOES invert here, and
    under branch (iii) that inversion cannot be interpreted as a memorization or
    generalization result; it is confounded with the subset simply being harder.
  ALSO NOTED, without a memorization interpretation: B1's drop is the SMALLEST of the five and
    lies inside its own seed SD (0.0515), while the process arms' drops are >2x larger. Under
    branch (iii) that is a statement about relative difficulty sensitivity, NOT about
    memorization.

CONSEQUENCE: the CP1b question REMAINS OPEN. Arbitrating it requires the clean retrained test
on data/e3proto (built and audited here, not run), or a difficulty-matched geometric-OOD
subset. Do not cite this checkpoint as having settled it.

A SECONDARY OBSERVATION (directional, not a claim; and note branch (iii) means the subset is
harder for everyone, so this is a DIFFERENTIAL SENSITIVITY observation, not a geometric-OOD
mechanism): the two PROCESS arms degrade roughly 2x more than the outcome arm and the SFT
baseline on the harder subset. If that survives a
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

=================  APPENDIX: POST-HOC DIFFICULTY-CONTROLLED ANALYSIS  =================
STATUS OF THIS APPENDIX: EXPLORATORY AND POST-HOC. It is NOT the pre-registered analysis.
I designed it AFTER seeing the pre-registered comparison return branch (iii), specifically to
try to remove the difficulty confound that forced branch (iii). Analyses invented after seeing
a disappointing result, and which happen to point toward a preferred conclusion, are exactly
the kind that must be labelled and not promoted. Recording it because the DESIGN is reusable
and the NULL is informative — not because it settles anything.

MOTIVATION. Branch (iii) fired because the double-OOD subset is harder for every arm. But the
raw subset also has a DIFFERENT SYSTEM COMPOSITION than the full eval (no cubic at all,
triclinic over-represented 21/83 vs 30/210), and crystal systems differ enormously in
difficulty. So part of the uniform drop is system mix, not geometry.

DESIGN. The 210 eval structures split into 83 prototype-OOD + 127 prototype-IID, and BOTH
halves are composition-OOD by the split's construction. So a WITHIN-SYSTEM contrast between
the halves isolates the geometric-OOD effect with chemistry-OOD held constant on both sides.
Six systems have >=5 structures on both sides (hexagonal, monoclinic, orthorhombic,
tetragonal, triclinic, trigonal; cubic has 0 prototype-OOD and is necessarily dropped).
Effect = mean over those 6 systems of (accuracy on prototype-OOD - accuracy on prototype-IID),
equal weight per system.

RESULT (stratified geometric-OOD effect, and its honest error bar):

  arm            effect    sd across systems    SE      t      distinguishable from 0?
  B1            -0.0856          0.1283       0.0524   -1.63   NO
  SFT-V1 (s0)   -0.0126          0.0390       0.0159   -0.79   NO
  B3            -0.0353          0.1017       0.0415   -0.85   NO
  V2a           -0.0253          0.0763       0.0311   -0.81   NO
  V2b           -0.0293          0.0995       0.0406   -0.72   NO
  (B1 per-seed effects: -0.0530 / -0.1253 / -0.0786; seed SD 0.0299)

THE TEMPTING READ, AND WHY IT IS NOT SUPPORTED. On point estimates alone this looks like
pre-registered branch (i): B1 is the ONLY arm whose effect exceeds the 0.05 threshold
(-0.0856), every chain/process arm sits below it (-0.013 to -0.035), and B1's gap to V2b
(0.0563) exceeds B1's own seed SD (0.0299). That pattern would mean B1's robustness IS
chemistry-specific and the memorization story partially revives.
IT DOES NOT SURVIVE ERROR BARS. With only 6 systems, the system-to-system spread (0.04-0.19)
swamps every effect (0.01-0.09); NO arm reaches |t| > 1.8, B1 included (t = -1.63). The
apparent "B1 breaks while the chains hold" structure is not statistically distinguishable from
"nothing is happening to anyone".

CONCLUSION OF THE APPENDIX: an HONEST NULL. The difficulty-controlled analysis is UNDERPOWERED
and does not arbitrate the CP1b question either. It neither rescues branch (i) nor strengthens
branch (iii)'s difficulty explanation. Two independent analyses (the pre-registered raw
comparison and this post-hoc stratified one) both fail to resolve it, which is itself the
useful finding: THIS DATA CANNOT SETTLE THE QUESTION. Settling it requires the clean retrained
test on data/e3proto (built and audited here) — or, cheaper, a geometric-OOD eval set
constructed to be system-balanced on BOTH sides so the contrast is not limited to 6 unbalanced
strata. The prototype-key machinery for building that already exists.

DO NOT cite the -0.0856 vs -0.029 contrast as evidence. It is a point estimate with t = -1.63.

=================  DELIVERABLE FOR THE CLEAN TEST: data/e3geo/  =================
The appendix concluded that this data cannot settle the CP1b question and named what would:
a geometric-OOD eval set system-balanced on BOTH sides. That set is now BUILT and VERIFIED.

data/e3geo/ — structure-prototype exclusion, balanced on both sides:
  train 1610 (230 per system, all 7)   eval 210 (30 per system, all 7)
  eval drawn from 209 whole prototype classes
  prototype overlap train n eval = 0                       VERIFIED (computed, not assumed)
  eval-only elements = 0                                   VERIFIED (chemistry held constant)
  overlap with data/e3proto eval  =  83/210
  overlap with data/e3 (chemistry) eval = 13/210 -> independent of the chemistry split
  renders reused (identical per material_id), sidecar reused, seed 23

WHY IT FIXES THE POWER PROBLEM: the post-hoc analysis was underpowered because the usable
within-system contrast collapsed to 6 unbalanced strata (cubic had 0 prototype-OOD structures),
leaving system-to-system spread (0.04-0.19) larger than every effect (0.01-0.09). Here all 7
systems carry 30 eval / 230 train, so a retrained comparison gets a balanced 7-stratum contrast
instead of 6 lopsided ones.

HARD CONSTRAINT, RECORDED SO IT CANNOT BE MISUSED: 197/210 (93.8%) of this eval set sits in
data/e3's TRAIN split. Scoring the CURRENT adapters on it would reproduce exactly the
contamination that invalidated the data/e3proto probe (90.0%). This split is for a RETRAINED
comparison ONLY. Do not use it to evaluate the existing checkpoints.

COST OF THE CLEAN TEST (for the record, not a recommendation): retrain the arms of interest on
data/e3geo/train, then evaluate on data/e3geo/eval with the standard protocol. At the measured
~2 hr/GRPO run and ~5 min/seed for a B1-style eval, a minimal B1-vs-V2b retrained contrast at
3 seeds is roughly a day of GPU. Given CP1b branch (a) deprioritized accuracy work, this is
listed as available, not urgent.

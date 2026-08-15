CHECKPOINT: merged_retrain    GAP: Q1 (geometric-OOD) + Q2 (native-resolution retrain)
STATUS: CLOSED — SUBSUMED, NOT ABANDONED. The Q2 half was executed and is recorded as sota_push
        (the A3 arm IS this pre-registration's native-resolution retrain). The Q1 half was cancelled
        for a reason recorded in prereg.md itself, not dropped silently.

WHERE THE Q2 HALF WENT. prereg.md asked: was B1's 0.133 accuracy drop at native resolution a genuine
resolution effect or the train/test mismatch resolution_audit could not separate? Answer it by TRAINING at native
resolution and evaluating at native resolution. That is exactly the A3 run in sota_push:
direct arm, max_pixels 589824 (576 visual tokens/view read from the live processor), 3220 examples
(1610 structures x2 with 6-camera augmentation), evaluated on the same frozen 210-structure
composition-exclusion split at matched resolution.
  RESULT: A3 = 0.6619 (139/210) vs the B1 416px reference 0.6143 +/- 0.0515. Branch Q2-(ii): FLAT
  within the 0.05 rule. The pre-registered stopping rule fired against the direction I was leaning
  and no further runs were made. See sota_push/finding.md for the full record.
  CONSEQUENCE for resolution_audit: because native-trained/native-eval is flat, resolution_audit's branch (ii) reading stands
  — resolution is not shown to be a confound, and the 416px effective resolution used throughout the
  program is not a defect that inflated or deflated any reported number.

WHY THE Q1 HALF WAS CANCELLED. Q1 asked whether B1-direct's OOD robustness is chemistry-specific by
retraining on a geometric-OOD split. prereg.md records the reason it became non-load-bearing: exclusion_baselines
branch (a) already REFUTED the pre-registered hypothesis that B1-direct would collapse out of
distribution (it reached 0.6143 on composition-exclusion vs 0.711 IID, only -13.6%), and prototype_exclusion's
no-retrain prototype probe returned an uninterpretable branch (iii) (a difficulty shift affecting all
five arms). With the memorization question already answered in the direction that made the retrain
unnecessary, spending ~8 GPU-hours to re-answer it was not justified.
  The data was built and verified regardless and remains reproducible: data/e3geo_sft/train.jsonl
  = 3220 rows (1610 structures x arms B1, V1), data/e3geo_sft/eval.jsonl = 420 rows, targets
  generated deterministically from labels_sidecar.json via cocr.traces.make_target, all 9100 renders
  verified to resolve with zero train/eval leakage.

WHAT MUST NOT BE CLAIMED FROM THIS CHECKPOINT. A3 is ONE seed. prereg.md is explicit that no branch
may be declared from a single seed where the comparison needs seed SDs, and the flat Q2 reading is
reported as attempted-and-flat rather than as a demonstrated null. The geometric-OOD question is
open, not answered.

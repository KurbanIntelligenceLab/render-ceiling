CHECKPOINT: process_reward     GAP: G2, G3 (process-verified vs outcome-only reward)     STATUS: pilot done (1 seed x 3 arms, 200 steps); FULL pre-registered matrix pending. This is a DE-RISKING pilot, NOT the Gate-2 verdict.

PLAN CONTEXT: E3 is the flagship — the pre-registered test of H1 (process-verified
GRPO beats outcome-only GRPO). The full experiment is 3 matched arms x >=3 seeds with
Gate 2: a process arm confirms H1 iff it beats B3 on the exclusion splits by more than
the pooled seed SD, on BOTH macro-F1 symmetry AND chain faithfulness. This record is
the 1-seed pilot run first (per the user's de-risk-before-full-matrix decision).

METHOD DONE: Built the CIF-grounded REWARD SERVER (src/cocr/reward.py) — the scientific
core and shared infra for E4/E7. It parses an emitted CoCr chain and scores each step
against the pipeline label: geometry (qualitative relations, per the sft_chain lesson — NOT exact
cell parameters), system/Bravais and point/space group (hierarchical, coarse-credit:
wrong system zeros the fine labels), motif (Wyckoff set Jaccard), a final-answer reward,
and a FORMAT reward that hard-penalizes non-termination (targets the sft_chain MOTIF trap).
Validated: gold traces score 1.0 on every step (MP + JARVIS, 167/167 sidecar); a
non-terminating MOTIF-trap chain gets format=-1 while the OUTCOME reward is fooled to
1.0 on the same chain (the process-vs-outcome mechanism, demonstrated); 0.02 ms/chain.

Ran GRPO (TRL 1.9.0 GRPOTrainer, custom reward_funcs, LoRA continued from the V1 SFT
checkpoint, 4-bit base, group size 8, HF-generate sampling, 200 steps) in three arms:
  B3   outcome-only reward
  V2a  scalar-sum of per-step verifiable rewards
  V2b  step-wise credit
on the RTX 5090 (~1.3 hr/arm). Reward-parse validated against the live chat template
before RL (plan mandate). Data: the E2 held-out sample + a precomputed pipeline label sidecar
(data/e2/labels_sidecar.json, 167 structs). Evaluated all three on the V1 test prompts.

RESULT (crystal_system, test n=30):
  arm      micro   macro   faithfulness
  SFT-V1   0.378   0.411   ~0.35          <- pre-GRPO baseline (sft_chain)
  B3       0.333   0.414   0.263
  V2a      0.300   0.348   0.244
  V2b      0.333   0.414   0.263

GATE 2 (pilot): NOT MET at pilot scale. All three arms are statistically
indistinguishable (paired McNemar p=1.0 on every pair, discordant 0-2 of 30), and none
beats the SFT baseline. Faithfulness did not improve either.

DIAGNOSIS (why the null is DIAGNOSTIC, not evidence against H1):
  - KL to the SFT reference stayed ~0.0002 for ALL arms across 200 steps -> at lr 1e-6
    the policy barely moved off the SFT checkpoint. The three arms' prediction
    distributions are near-IDENTICAL (B3 == V2b exactly) and all collapse to
    high-symmetry classes only (never triclinic/monoclinic/orthorhombic, which are
    15/30 of the truth) — i.e. all three are still ~the SFT policy. They are
    indistinguishable BECAUSE GRPO did not diverge them at this step/KL budget.
  - The hypothesized process advantage IS visible in the TRAINING signal: B3's outcome
    reward is sparse — 0.125 of rollout groups had zero reward variance (no gradient) —
    while V2a/V2b (dense per-step reward) had 0.0 wasted groups. Dense reward wastes no
    group; 200 steps just wasn't enough to convert that into held-out gains.
  - EVAL CAVEAT: eval uses greedy decode, where all arms fall back into the MOTIF trap
    (terminate 0/30) and are scored via last-crystal-system fallback. Training was under
    sampling (terminate 8/8). Greedy eval measures the trap, not fully what GRPO trained.

CONSEQUENCES FOR THE FULL RUN (pre-registered before scaling):
  1. MORE STEPS — 200 is too few; V2a reward was still rising at step 200.
  2. LOOSER KL / HIGHER lr — KL ~0.0002 is near-frozen; the policy must actually move.
  3. SAMPLED-decode (or majority-vote) eval — measure trained behavior, not greedy trap.
  4. Constrain the MOTIF format (fixed slots / dedup / length cap) so greedy decode
     also terminates, removing the eval confound.

VERDICT: pilot SUCCESS as de-risking — pipeline validated end to end, Gate 2 is
measurable, the reward server is correct, and the null is fully explained (under-trained
at frozen KL). The full 3-seed matrix should adopt the four config changes above.

REPRODUCE:
  reward: src/cocr/reward.py (score_chain / score_outcome); tests in this dir
  train:  python scripts/train_e3_grpo.py --arm {B3,V2a,V2b} --seed 0 \
            --sft-adapter adapters/V1_s0 --max-steps 200 --group-size 8   (on GPU box)
  eval:   python scripts/eval_e2.py --arm <ARM> --eval-arm V1 --adapter adapters_e3/<ARM>_s0 \
            --max-new-tokens 900
  data:   data/e2/{train,val,test}.jsonl + labels_sidecar.json
  records: pilot_validation.json (pre-flight), pilot_finding.json (this run), results below

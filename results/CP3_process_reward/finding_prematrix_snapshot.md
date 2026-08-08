CHECKPOINT: CP3_process_reward     GAP: G2, G3 (process-verified vs outcome-only reward)     STATUS: pilot done + pre-matrix audit done; FULL pre-registered matrix pending. This is a DE-RISKING pilot, NOT the Gate-2 verdict.

[Pre-matrix audit (verify-then-do checklist). Prior pilot text preserved in
finding_pilot_snapshot.md.
ITEM 1 (wiring audit for "B3==V2b exactly") — RESOLVED, NO BUG. Adapter-weight diff
  (43.6M LoRA params): B3 vs V2b L2=0.0168, max_abs=6.0e-5 — near-identical but NOT
  bit-identical (a save-twice/same-reward bug would give exactly 0). All arms sit
  L2~0.063 from the SFT ckpt (max weight change ~6e-5) = frozen-KL confirmed by weights.
  Inter-arm L2 (~0.016) is 4x smaller than arm-vs-SFT (~0.063): all arms took small,
  distinct steps and landed near each other. "B3==V2b in PREDICTIONS" was greedy-argmax
  collapsing two near-identical policies to identical discrete tokens, not identical
  weights. Reward trajectories DO differ (last-20 mean: B3 0.263, V2a 0.509, V2b 0.497).
  The faithfulness "drop" was a METRIC MISMATCH: SFT-V1 faithfulness on the SAME
  reward-server metric = 0.274 (not the ~0.35 estimate, which came from CP2's different
  geometry-accuracy metric). True picture is flat: SFT 0.274 vs arms 0.244-0.263, within
  n=30 fallback noise. Consistent with frozen-KL; no mechanism puzzle.
ITEM 2 (format reward common to all arms) — CONFOUND CONFIRMED, fixed for matrix. Pilot
  B3 reward = final_reward ONLY (no format term); V2a/V2b carried +0.25*format. So the
  pilot manipulated TWO variables. MATRIX DESIGN (pre-registered): B3 = outcome + format;
  V2a = step-sum + format; V2b = step-credit + format. Only per-step verification varies.
ITEM 3/4 (real eval set + scaled train set) — BUILT & VERIFIED. data/e3/: 1610 train
  (230/system) + 210 eval (30/system), composition-exclusion split (13 reserved elements),
  0 ID leakage (train∩eval=0, both disjoint from 448 prior ids), all 210 eval structures
  carry a train-unseen element, full sidecar coverage, 9100 renders (frozen 5-view set).
ITEM 6 (stack) — DECIDED: stay on TRL 1.9.0 GRPOTrainer; DEVIATION from plan (EasyR1/verl)
  recorded, held for all arms/seeds. Reward server plugs in as a reward_funcs callable.
ITEM 5 (config calibration) — DONE. V2a lr x beta sweep (40 steps x 3 configs). FROZEN:
  lr=1e-5, beta=0.02, group=8 -> KL settles in a deliberate ~0.015 band (75x the pilot's
  frozen 0.0002), entropy stable, gradient present; rejected lr3e-5/b0.005 (KL ~0.08,
  divergence risk). Reward oscillates on fresh 1610-prompt batches (not a decline).
  Eval decode = sampled/majority-vote. calibration.json records the sweep. Caveat: 40
  steps too short to CONFIRM a plateau -> KL/reward is a standing training panel (item 8).]

PLAN CONTEXT: E3 is the flagship — the pre-registered test of H1 (process-verified
GRPO beats outcome-only GRPO). The full experiment is 3 matched arms x >=3 seeds with
Gate 2: a process arm confirms H1 iff it beats B3 on the exclusion splits by more than
the pooled seed SD, on BOTH macro-F1 symmetry AND chain faithfulness. This record is
the 1-seed pilot run first (per the user's de-risk-before-full-matrix decision).

=================  E3 FULL-MATRIX PRE-REGISTRATION (frozen before launch)  =================
[Written after the pre-matrix audit; frozen prior to running the matrix. Items keyed to
the pre-matrix checklist.]

ARMS (item 2 — FORMAT term common to all; only per-step verification is manipulated):
  B3  = outcome(final crystal system) + 0.25*format
  V2a = mean(per-step verifiable rewards) + 0.25*format          [scalar-sum]
  V2b = mean(per-step + final) + 0.25*format                     [step-wise credit]
  format reward = +1 well-formed & terminating / 0 terminating-but-malformed / -1
  non-terminating. Verified on synthetic chains: gold->1.25 all arms; wrong-system->B3
  0.25 vs V2a/V2b 0.54-0.58 (per-step credit isolated); non-terminating penalized in all.

DATA (items 3, 4 — real eval set + scaled train set, built via the CP0 pipeline):
  TRAIN: data/e3/train.jsonl — 1610 structures (230/system x 7), MP, keep-policy filtered.
  EVAL:  data/e3/eval.jsonl  — 210 structures (30/system x 7), COMPOSITION-EXCLUSION split.
  Split: 13 elements reserved for eval only (Cd Ce Hg In Ir La Mn Os Re Ru Tc Ti Tl);
  every eval structure contains >=1 element NEVER in any train structure. Leakage: 0
  (train∩eval ids=0; both disjoint from all 448 prior CP0b/CP1/E2 ids; 0 eval structures
  are fully composed of train-seen elements). Labels: deterministic CP0 sidecar
  data/e3/labels_sidecar.json (1820). Renders: frozen 5-view set (conventional cell,
  2x2x2, index-only filenames). split_meta.json records the full spec.
  Rationale: pilot trained 200 steps over 115 prompts = dozens of epochs (prompt
  overfitting risk); 1610 prompts fixes that. n=210 eval >> pilot n=30 (±9pp binomial
  noise that swamped a seed-SD threshold).

CONFIG (item 5 — ONE frozen config from a calibration sweep; tuning on the calibration
  seed is legitimate, tuning inside the matrix is not). Calibration: short single-seed
  lr x beta sweep; success = KL lands in a deliberate band (NOT ~0.0002 frozen) AND V2a
  training reward PLATEAUS within the step budget.
  FROZEN CONFIG (from the sweep, identical across all arms/seeds, no mid-matrix tuning):
    lr = 1e-5, beta (KL) = 0.02, group_size = 8, max_completion_length = 350, seeds = 0/1/2.
  Sweep: 3 configs x 40 steps; lr1e-5/b0.02 chosen (KL settles ~0.015 = deliberate band,
  75x the pilot's frozen 0.0002; entropy stable ~0.15; gradient present). Rejected
  lr3e-5/b0.005 (KL ~0.08, divergence risk over a long run). Reward oscillates step-to-
  step on the fresh 1610-prompt batches (group 8) — that is batch-mix noise, not a
  decline. CAVEAT: 40 steps is too short to CONFIRM a plateau; the matrix runs longer
  with KL/reward watched as a standing panel (item 8) to catch divergence early.
  Eval decoding: SAMPLED / majority-vote (not greedy) so the measured behavior is what
  GRPO trained, not the greedy MOTIF trap.

STACK (item 6 — frozen): TRL 1.9.0 GRPOTrainer. DEVIATION from plan (EasyR1/verl) recorded
  and held for all arms/seeds; no mid-matrix switch. Justification: pilot-validated on
  this 32GB box, reward server plugs in as a reward_funcs callable, arms share the stack
  so the controlled comparison is unaffected.

GATE 2 (restated against the new eval set): a process arm (V2a or V2b) confirms H1 iff it
  beats B3 on the COMPOSITION-EXCLUSION eval split by more than the pooled across-seed SD,
  on BOTH macro-F1 (symmetry) AND chain faithfulness (mean per-step reward). >=3 seeds/arm.
  A flat/negative result is reported straight with a saturation/decoupling analysis.

HONEST NOTE (item 5): constraining the format so greedy decode also terminates REMOVES the
  format-hacking channel through which the pilot's process arms showed their (training-
  signal) advantage. The matrix therefore tests whether per-step verification helps BEYOND
  termination shaping — a cleaner and HARDER version of H1 than the pilot hinted.

STANDING TRAINING PANEL (item 8): log the zero-reward-variance group fraction per arm
  every step (pilot: B3 0.125 wasted vs V2a/V2b 0.0). This is the training-dynamics
  statistic that may mechanistically explain whatever Gate 2 returns.
============================================================================================

METHOD DONE: Built the CIF-grounded REWARD SERVER (src/cocr/reward.py) — the scientific
core and shared infra for E4/E7. It parses an emitted CoCr chain and scores each step
against the CP0 label: geometry (qualitative relations, per the CP2 lesson — NOT exact
cell parameters), system/Bravais and point/space group (hierarchical, coarse-credit:
wrong system zeros the fine labels), motif (Wyckoff set Jaccard), a final-answer reward,
and a FORMAT reward that hard-penalizes non-termination (targets the CP2 MOTIF trap).
Validated: gold traces score 1.0 on every step (MP + JARVIS, 167/167 sidecar); a
non-terminating MOTIF-trap chain gets format=-1 while the OUTCOME reward is fooled to
1.0 on the same chain (the process-vs-outcome mechanism, demonstrated); 0.02 ms/chain.

Ran GRPO (TRL 1.9.0 GRPOTrainer, custom reward_funcs, LoRA continued from the V1 SFT
checkpoint, 4-bit base, group size 8, HF-generate sampling, 200 steps) in three arms:
  B3   outcome-only reward
  V2a  scalar-sum of per-step verifiable rewards
  V2b  step-wise credit
on the RTX 5090 (~1.3 hr/arm). Reward-parse validated against the live chat template
before RL (plan mandate). Data: the E2 held-out sample + a precomputed CP0 label sidecar
(data/e2/labels_sidecar.json, 167 structs). Evaluated all three on the V1 test prompts.

RESULT (crystal_system, test n=30):
  arm      micro   macro   faithfulness
  SFT-V1   0.378   0.411   ~0.35          <- pre-GRPO baseline (CP2)
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

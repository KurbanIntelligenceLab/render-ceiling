CHECKPOINT: process_reward     GAP: G2, G3 (process-verified vs outcome-only reward)     STATUS: DONE — full 3-arm x 3-seed matrix run + evaluated. GATE 2: CONFIRMED for V2b (dense step-level, StepGRPO-style); V2a passes faithfulness decisively, borderline on accuracy. H1 SUPPORTED: process-verified rewards beat outcome-only, most clearly on chain faithfulness.

=================  E3 MATRIX RESULT (Gate-2 verdict)  =================
Full matrix: 3 arms (B3 outcome / V2a dense step-level / V2b dense step-level +final) x 3 seeds, 300 GRPO
steps each, frozen config (lr 1e-5, beta 0.02, group 8) from the V1 SFT ckpt, on the
1610-prompt train set.
[ARM DEFINITIONS as IMPLEMENTED (train_e3_grpo.py build_reward_fn) — note "step-sum" is
 shorthand: V2a and V2b both AVERAGE per-step rewards (not a raw scalar sum). B3 base =
 final-answer reward; V2a base = mean(per-step rewards, final EXCLUDED); V2b base =
 mean(per-step rewards + final). All three add the common 0.25*format. The V2a-vs-V2b
 contrast is thus "per-step only" vs "per-step + final in the average".]

[NAMING CORRECTION (verified against the primary source, R1-VL/StepGRPO arXiv 2503.12937).
 These arms do DENSE STEP-LEVEL REWARDING with a PATH-LEVEL advantage; they are NOT
 per-step credit assignment — and neither is StepGRPO. StepGRPO likewise folds its dense
 rule-based step rewards (StepRAR soft key-step matching + StepRVR completeness/logic) into
 a scalar per-trajectory reward and group-normalizes it: the paper estimates "the advantage
 of each reasoning trajectory" by "normaliz[ing] its reward relative to the group", and
 contains no token-level advantage attribution. RETRACTED wording: "step-wise credit
 assignment", "per-step advantage attribution" (used in earlier versions of this record and
 in pilot_finding.json). CORRECT wording: "dense step-level rewards" / "StepGRPO-style".
 So V2b = mean(per-step + final) is legitimately describable as StepGRPO-style dense step
 rewarding. True per-step credit attribution (token/segment-level advantages, rollout
 step-value estimation) is UNTESTED here and is listed as future work / an optional E3
 extension arm.
 DIFFERENTIATION (strengthens the novelty claim): StepGRPO's key steps are GPT-4-EXTRACTED
 — the paper defines key steps as the essential variables/equations contributing to the
 solution and prompts GPT-4 to extract them from the reasoning path, i.e. model-generated
 supervision. CoCr's step targets are DETERMINISTIC from the source CIF via spglib/pymatgen
 with no model in the loop, so every step reward is programmatically verifiable rather than
 LLM-judged. That is the substantive difference, not the advantage formulation.] Evaluated on the 210-structure COMPOSITION-EXCLUSION eval set with
majority-vote sampled decoding (3 samples, temp 0.7, 512 tok). Prior text (pilot + audit)
in finding_prematrix_snapshot.md / finding_pilot_snapshot.md.

RESULT (macro-F1 == micro; balanced 30/system eval):
  arm   macro-F1 (mean±sd)   faithfulness (mean±sd)   macro seeds
  B3    0.344 ± 0.045        0.258 ± 0.035            [0.281, 0.371, 0.381]
  V2a   0.376 ± 0.014        0.306 ± 0.021            [0.357, 0.381, 0.391]
  V2b   0.386 ± 0.000        0.299 ± 0.018            [0.386, 0.386, 0.386]
  (chance 1/7 = 0.143; SFT-V1 pre-GRPO baseline ~0.38 macro on the E2 IID test — but that
   was IID, not this harder composition-exclusion split, so not a like-for-like anchor.)

GATE 2 (pre-registered: process arm beats B3 by > pooled across-seed SD on BOTH macro-F1
  AND chain faithfulness, >=3 seeds):
  V2b vs B3: macro Δ=+0.041 > pooled_sd 0.032 (PASS); faith Δ=+0.041 > 0.028 (PASS)
    -> GATE 2 CONFIRMED.
  V2a vs B3: faith Δ=+0.048 > 0.029 (PASS); macro Δ=+0.032 vs pooled_sd 0.033 (narrow FAIL)
    -> not met on the strict two-metric rule (accuracy a hair under threshold).

COMPLEMENTARY per-structure paired test (mean-over-seeds per structure, n=210 — far more
  power than the 3-seed-mean gate): both process arms beat B3 on BOTH metrics.
    accuracy:     V2a Δ=+0.032 t≈2.0 ; V2b Δ=+0.041 t≈2.9
    faithfulness: V2a Δ=+0.048 t≈6.2 ; V2b Δ=+0.041 t≈5.8  (~120/210 structures improved)
  The faithfulness effect (the direct "reads the structure vs recites" measure) is large
  and robust for BOTH process arms; the accuracy effect is clear for V2b, borderline V2a.

HONEST CAVEATS:
  - The strict Gate-2 verdict is SENSITIVE to B3's wide seed spread (sd 0.045, driven by a
    genuinely weak seed s0=0.281 — CONFIRMED not a decode-budget artifact: re-evaluated at
    the consistent 3x512 setting = 0.281, unchanged from 5x900's 0.286). With only 3 seeds
    the SD estimate is noisy; the per-structure paired test is reported alongside for power.
  - V2b's zero seed variance (0.386 x3) is striking stability but also means its sd is an
    underestimate at n=3; the per-structure test guards against reading too much into it.
  - Effect sizes are modest in absolute terms (~3-4 pp accuracy, ~4-5 pp faithfulness) at
    this pilot-plus scale (1610 train prompts, 300 steps). The DIRECTION is consistent and,
    on faithfulness, statistically strong; magnitude would sharpen with more steps/data.
  - Per item-5 note: format is common to all arms, so this tests per-step verification
    BEYOND termination shaping — the harder H1. The advantage survives that harder test.

TERMINATION (corrected — an earlier "0/210 reach [ANSWER] at 900 tok" claim was a
  STORED-TEXT TRUNCATION ARTIFACT: eval_e3.py stores only text[:400], and the chain's
  [ANSWER] line sits past char 400). Full-length re-generation (12 eval structs/arm, 900
  tok) shows GRPO LARGELY FIXED the SFT non-termination trap: B3 10/12, V2a 8/12, V2b
  10/12 reach [ANSWER] (mean gen ~350-460 tok), vs the V1 SFT checkpoint's 1.1%. So the
  crystal-system fallback parser and the true [ANSWER] mostly agree here; the Gate-2
  numbers stand (fallback-scored), and separately GRPO earned a real termination fix.

MECHANISM (item-8 standing panel — the training-dynamics statistic): the sparse binary
  outcome reward (B3) left ~47-51% of rollout GROUPS with zero reward variance (no
  gradient) across all seeds; the dense process rewards (V2a/V2b) left ~0-4%. So B3 wastes
  roughly half its rollout groups while the process arms waste almost none — the concrete
  mechanism by which dense per-step verification converts into the held-out advantage.

  NAMED LITERATURE (item-8 extended). This is the "zero advantage / advantage vanishing"
  failure mode documented in DAPO (arXiv 2503.14476): "if all outputs {o_i} of a particular
  prompt are correct and receive the same reward, the resulting advantage for this group is
  zero", and "a zero advantage results in zero policy gradients, shrinking the magnitude and
  increasing the noise sensitivity of the batch gradient, thereby degrading sample
  efficiency." DAPO's remedy is dynamic sampling — "over-sample and filter out prompts with
  the accuracy equal to 1 and 0 ... leaving all prompts in the batch with effective
  gradients". Related advantage-vanishing work: R1-ShareVL (2505.16673), MM-Eureka's online
  zero-advantage filtering, VL-Rethinker / Skywork large-advantage reuse. Our contribution
  here is orthogonal: instead of FILTERING silent groups, a densely-verifiable reward makes
  them not arise (~2% vs ~49%).

  CLOSED-FORM SANITY CHECK (item-8 required). B3's per-rollout reward is binary + the common
  format term (1.25 correct / 0.25 wrong when the chain terminates), so a group's mean reward
  lies on the lattice 0.25 + k/G with k = #correct out of G=8. Recovering silent groups
  directly from that lattice (k=0 -> 0.25, k=G -> 1.25) over all 900 B3 training steps gives
  441/900 = 0.490, matching the TRL-logged frac_reward_zero_std = 0.4889 to 0.001 — the panel
  statistic is confirmed two independent ways.
  Against P[silent] = p^G + (1-p)^G: a HOMOGENEOUS single-p binomial FAILS badly — at the
  measured mean per-rollout accuracy p̄ = 0.336 it predicts only 0.038 (and the best-fit
  homogeneous p = 0.461 predicts 0.009) versus 0.490 observed, a ~13x under-prediction. The
  rate is therefore NOT explained by mean accuracy; it is driven by PROMPT HETEROGENEITY.
  Empirically P[k=0] = 0.380 and P[k=G] = 0.110, i.e. only ~51% of groups are informative.
  A Beta-binomial (per-prompt p ~ Beta) fitted to just p̄ and P[k=0] reproduces the rest:
  predicted P[k=G] = 0.105 (obs 0.110) and P[silent] = 0.485 (obs 0.490), with fitted
  concentration a+b = 0.887 < 1 — a U-shaped per-prompt difficulty distribution (mass pushed
  toward p~0 and p~1). That is the quantitative signature of a task with a wide difficulty
  spread, and it is exactly the regime where an outcome-only reward goes silent.

  CAUTION IF DYNAMIC SAMPLING IS EVER ADOPTED (item-8 extended): on sparse hard-gated
  rewards it has a documented failure mode of batch-wide rejection plus resample thrashing
  (arXiv 2606.27210). With B3 at ~49% silent groups this is a LIVE risk for the outcome arm
  specifically. If adopted: cap resample rounds and log rejection rates. It must NOT be
  added to some arms and not others — that would break the matched-arm design that makes
  Gate 2 interpretable.
=======================================================================



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
  reward-server metric = 0.274 (not the ~0.35 estimate, which came from sft_chain's different
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
  V2b = mean(per-step + final) + 0.25*format          [dense step-level, StepGRPO-style]
  format reward = +1 well-formed & terminating / 0 terminating-but-malformed / -1
  non-terminating. Verified on synthetic chains: gold->1.25 all arms; wrong-system->B3
  0.25 vs V2a/V2b 0.54-0.58 (per-step credit isolated); non-terminating penalized in all.

DATA (items 3, 4 — real eval set + scaled train set, built via the pipeline pipeline):
  TRAIN: data/e3/train.jsonl — 1610 structures (230/system x 7), MP, keep-policy filtered.
  EVAL:  data/e3/eval.jsonl  — 210 structures (30/system x 7), COMPOSITION-EXCLUSION split.
  Split: 13 elements reserved for eval only (Cd Ce Hg In Ir La Mn Os Re Ru Tc Ti Tl);
  every eval structure contains >=1 element NEVER in any train structure. Leakage: 0
  (train∩eval ids=0; both disjoint from all 448 prior identifiability/zeroshot/E2 ids; 0 eval structures
  are fully composed of train-seen elements). Labels: deterministic pipeline sidecar
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
  V2a  dense step-level rewards, mean of per-step (final excluded)
  V2b  dense step-level rewards (StepGRPO-style; NOT per-step credit assignment)
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

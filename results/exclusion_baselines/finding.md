CHECKPOINT: exclusion_baselines     GAP: does the accuracy story survive OOD chemistry?
STATUS: DONE — B1-direct (3 seeds) AND SFT-V1 (3 seeds) both complete.
BRANCH TAKEN: (a) — B1 HOLDS. THE ACCURACY STORY IS DEAD.
PRE-REGISTERED HYPOTHESIS: REFUTED.

=================  RESULT  =================
210-structure composition-exclusion eval set (every structure contains a train-unseen
element), 3-sample majority vote, temp 0.7, 512 max tokens — the SAME protocol as the
E3 matrix arms.

  arm                        seeds                    mean    SD      faithfulness
  B1-direct (SFT)            0.590 / 0.567 / 0.686    0.614   0.052   0.000 (no chain)
  SFT-V1 (chain, pre-GRPO)   0.3524 / 0.3286 / 0.3286  mean 0.3365 +/- 0.0112   faith 0.2523
    [ALL 3 SEEDS COMPLETE. THE DIRECTION FLIPPED between seed 1 and seed 2, which is why this row
     was held provisional rather than written as a finding: at seed 0 alone SFT-V1 0.3524 was
     ABOVE B3 0.3445; at the final 3-seed mean 0.3365 it is BELOW B3 by 0.0080. That gap is
     smaller than the pooled noise (0.0328, ledger/CONVENTIONS.md), so SFT-V1 and B3 are NOT
     DISTINGUISHABLE in either direction on this metric. Computed final ordering:
       V2b 0.3857 > V2a 0.3762 > B3 0.3445 > SFT-V1 0.3365
     Both PROCESS arms sit above SFT-V1 by more than pooled noise (+0.0397, +0.0492); the
     OUTCOME arm does not. So the "did GRPO help at all" row currently reads: process-verified
     GRPO improved on its SFT initialization, outcome-only GRPO did not measurably. AWAIT SEED 2.]
  B3  (GRPO outcome)         0.281 / 0.371 / 0.381    0.344   0.045   0.258
  V2a (GRPO dense step)      0.381 / 0.357 / 0.390    0.376   0.014   0.306
  V2b (GRPO dense step+fin)  0.386 / 0.386 / 0.386    0.386   0.000   0.299

B1 IID reference (E2 test, n=30): 0.711.
Degradation IID -> composition-exclusion: 0.711 -> 0.614, i.e. -0.097 (-13.6%).

=================  PRE-REGISTERED DECISION RULE AND THE BRANCH TAKEN  =================
Rule committed in prereg.md BEFORE any number was looked at:
  (a) B1 holds near 0.71 (>= ~0.60)  -> accuracy story DEAD; paper reframes on
      verifiability / faithfulness / test-time scaling; E3 scale-up DEPRIORITIZED.
  (b) B1 collapses toward/below V2b (<= ~0.40) -> "direct mapping memorizes, verified
      chains generalize" becomes the headline; E3 scale-up JUSTIFIED.
  intermediate (0.40 < B1 < 0.60) -> report as partial; do not force a branch.

OBSERVED mean 0.614 >= 0.60  ==>  BRANCH (a) TAKEN.

ROBUSTNESS OF THE CALL (checked because 0.614 sits near the 0.60 boundary): the call does
NOT depend on the boundary. Even the WORST B1 seed (0.567) exceeds the BEST chain arm
(V2b, 0.386) by +0.181 — more than 3x the largest inter-arm gap the whole E3 matrix
produced. B1 beats B3 by +0.270, V2a by +0.238, V2b by +0.228.

=================  THE PRE-REGISTERED HYPOTHESIS WAS REFUTED  =================
We predicted, citing Chu et al. "SFT Memorizes, RL Generalizes" (arXiv 2501.17161, ICML'25;
verified from the primary source: "SFT ... tends to memorize the training data and struggles
to generalize out-of-distribution", and "RL also generalizes to visual OOD tasks, whereas
SFT continues to struggle"), that B1-direct would degrade SUBSTANTIALLY on unseen chemistry
while the GRPO chain arms retained more.

That did not happen. B1 lost only 13.6% relative and still leads every GRPO arm by a wide
margin. Stated plainly: in THIS setting, the SFT-memorizes/RL-generalizes pattern does not
reproduce. Candidate reasons (untested, listed as hypotheses not conclusions):
  - Our composition-exclusion split withholds ELEMENTS, not the visual/geometric regularity
    that determines crystal system. A held-out element still renders as the same lattice
    geometry, so the split may be OOD in chemistry while remaining IID in the feature the
    task actually depends on. This is the most likely explanation and it is a limitation of
    our split design, not evidence against 2501.17161.
  - Chu et al.'s RL arms were trained to convergence on the task reward; our GRPO arms ran
    300 steps from a weak SFT checkpoint and never exceeded it on accuracy at all (see process_reward).
    Our comparison is therefore not the comparison their claim is about.
  - B1's target is a 4-8 token label mapping — the easiest possible thing to fit and the
    least likely to be destabilized by distribution shift in a nuisance variable.

=================  CONSEQUENCES (what this decides)  =================
1. E3 SCALE-UP: DEPRIORITIZED. Branch (a) explicitly withdraws the accuracy justification
   for buying more compute. Per the item-4 gate, only branch (b) PLUS a growing eval gap
   justified the full rental; branch (a) removes half that condition before the probe runs.
2. THE PAPER'S CLAIM must be verifiability / faithfulness / test-time scaling, NOT
   accuracy. The defensible CoCr claims after exclusion_baselines + process_reward + calibration are:
     - process-verified rewards beat outcome-only on chain faithfulness (process_reward Gate 2, V2b)
     - dense verification prevents the DAPO zero-advantage pathology (~2% vs ~49% silent
       groups) — a training-dynamics result independent of final accuracy
     - dense verification partially mitigates RLVR calibration degeneration, by hedging
       (calibration: ECE 0.573 -> 0.493)
     - an answer-INDEPENDENT verifiable step predicts final correctness at AUC ~0.81, well
       above the model's own confidence (~0.62) — the E7 reranking premise
   NONE of these require the chain to be the most accurate predictor, and exclusion_baselines now says
   plainly that it is not.
3. AN HONEST HEADLINE THE DATA SUPPORTS: on this task a direct image->label mapping is the
   accuracy-optimal model, and the value of the verified chain is that it is CHECKABLE, not
   that it is more accurate. That is a narrower but genuinely defensible contribution.

=================  BUDGET ACCOUNTING (required by arXiv 2509.21882)  =================
2509.21882 ("The Hidden Costs and Measurement Gaps of RLVR") warns headline RLVR gains
often "conflate policy improvement with ... budget mismatch between RLVR and baseline
evaluations", and recommends budget-matched comparison. All counts below are MEASURED, read
off the live Qwen3-VL processor at the max_pixels=200704 used in every training and eval run
— NOT computed by formula (Qwen3-VL's 32x32-px/token arithmetic plus the max_pixels cap make
formula-derived counts wrong; the 768x768 renders yield 171 visual tokens/view, not the
naive value).

  MEASURED: 171 visual tokens per view x 5 views; 938 total prefill tokens per sample
            (constant across samples — all renders are 768x768); 75 question tokens.
  Generated: B1 ~6 tokens/sample (verified: stored answers are 13-20 chars);
             chain arms ~400 tokens/sample (measured mean 350-460).

  (1) GENERATED TOKENS       chain 1200 vs B1 18 per structure (x3 samples)  -> 66.7x
  (2) FLOPs-PROPORTIONAL     chain 4014 vs B1 2832 tokens processed          ->  1.42x  <== USED
      prefill is 70.1% of chain-arm compute and 99.4% of B1's, so the 5-view prefill
      dominates total FLOPs and the arms sit near parity despite the 66.7x decode gap.
  (3) WALL-CLOCK (measured)  B1 ~5 min/seed; SFT-V1 >171 min/seed             -> >34x
      Cause: SFT-V1 reaches [ANSWER] only 1.1% of the time, so every generation runs to the
      full 512-token cap. (The GRPO arms, which largely fixed termination, took ~2 h/seed.)

  THE BRANCH DECISION USES ACCOUNTING (2), FLOPs — the near-parity one, which is the
  conservative choice: it does NOT hand B1 a compute advantage to explain its win. (1) and
  (3) are disclosed above. Note the direction matters: under the generated-token accounting
  B1 uses 67x LESS compute and still wins, which only strengthens branch (a).

=================  SECONDARY (pre-registered)  =================
2501.17161 further finds — verified from the primary source — that "SFT stabilizes the
model's output format, enabling subsequent RL to achieve its performance gains". This is the
PUBLISHED rationale for the CoCr V1->GRPO lineage, and it matches our observation directly:
SFT-V1 reached [ANSWER] 1.1% of the time; after GRPO the arms reach it ~65-85% (B3 10/12,
V2a 8/12, V2b 10/12 in the full-length termination check). So the format-stabilisation half
of 2501.17161 REPRODUCES here even though the generalization half does not.

=================  CAVEATS  =================
- SFT-V1 rows are COMPLETE (all 3 seeds): 0.3524 / 0.3286 / 0.3286 -> mean 0.3365 +/- 0.0112,
  faithfulness 0.2523 +/- 0.0287. This supersedes an earlier caveat that quoted "~0.38 macro",
  which was the E2 IID test figure (n=30), NOT this exclusion-split number.
  The "did GRPO help at all" comparison, under the program pooling convention
  (ledger/CONVENTIONS.md):
      V2b - SFT-V1 = +0.0492  vs pooled 0.0079  -> EXCEEDS noise
      V2a - SFT-V1 = +0.0397  vs pooled 0.0127  -> EXCEEDS noise
      B3  - SFT-V1 = +0.0080  vs pooled 0.0328  -> WITHIN noise, not distinguishable
  i.e. process-verified GRPO improved on its supervised initialization; outcome-only GRPO did
  not measurably. NOTE (team directive item 3/4): this must be confirmed with PAIRED
  PER-STRUCTURE statistics before the sentence is frozen for the paper — the figures above are
  seed means. The freeze rule earned its keep here: the SFT-V1-vs-B3 DIRECTION FLIPPED between
  seed 1 and seed 2, and would have been reported backwards from a single seed.
  Branch (a) is unaffected either way (it is decided by B1 vs the GRPO arms).
- B1 seed spread is wide (0.567-0.686, SD 0.052) on n=210; the mean is what the rule uses.
- The composition-exclusion split withholds elements, not geometry — see the refutation
  discussion. A geometry-stratified or lattice-parameter-shifted split would test OOD
  generalization in the feature the task depends on, and is the natural follow-up.

REPRODUCE
  eval: python scripts/eval_e3.py --arm {B1,V1} --seed {0,1,2} --adapter adapters/{arm}_{seed} \
          --data-dir data/e3 --out evals_cp1b/eval_{arm}_s{seed}.json \
          --samples 3 --temperature 0.7 --max-new-tokens 512
  prereg: prereg.md (committed before any number was inspected)
  token counts: prefill_count.json (read from the live processor on the box)

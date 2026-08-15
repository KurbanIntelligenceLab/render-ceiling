CHECKPOINT: calibration (E9-lite)     GAP: calibration under verifiable-reward RL
STATUS: DONE (re-scoring only, no new GPU generation). RESULT: dense deterministic process
verification PARTIALLY mitigates outcome-RLVR calibration degeneration — but the gain is
MORE HEDGING, not better discrimination.

=================  WHAT WAS RUN  =================
Pure re-scoring of the EXISTING E3-matrix generations (9 adapters x 210 composition-exclusion
structures x 3 majority-vote samples = 5670 chains). No GPU training, no regeneration.

CONFIDENCE SOURCE — a limitation, logged as the critique required:
  The CoCr chain format never asks for a confidence statement, and a scan of 360 stored
  chains found ZERO verbalized-confidence expressions (0/360 matched
  confiden|certain|probab|N%|likel). So verbalized-confidence ECE is NOT computable from
  existing generations.
  We therefore use the MAJORITY-VOTE SHARE as the confidence signal (max votes / total
  votes over the 3 samples). This is a genuine, standard self-consistency confidence, but
  it is COARSE: only three levels are attainable (1/3, 2/3, 3/3), so the reliability
  diagram has 3 bins by construction, not by binning choice.
  ACTION FOR NEXT BIG RUN: add an explicit confidence slot to the eval protocol (and
  optionally to the chain target) so verbalized-confidence ECE becomes measurable.

=================  RESULT  =================
Confidence = 3-sample vote share. Bins are the 3 attainable levels. n=630 per arm.

  arm   ECE     mean_conf  accuracy  OVERCONF(conf-acc)  frac_unanimous(3/3)  AUC
  B3    0.5725  0.917      0.344     +0.572              0.775                0.620
  V2a   0.5271  0.903      0.376     +0.527              0.733                0.637
  V2b   0.4932  0.879      0.386     +0.493              0.659                0.619

Per-bin reliability (confidence -> empirical accuracy, n):
  B3    1/3: 0.000 (15)   2/3: 0.118 (127)   3/3: 0.414 (488)
  V2a   1/3: 0.067 (15)   2/3: 0.144 (153)   3/3: 0.463 (462)
  V2b   1/3: 0.071 (14)   2/3: 0.234 (201)   3/3: 0.470 (415)

ANSWER TO THE OPEN QUESTION (the framing this checkpoint was built to test):
  Q: does dense deterministic process verification mitigate outcome-RLVR's documented
     calibration degeneration?
  A: PARTIALLY, and by a specific mechanism. ECE falls monotonically with the density of
     process verification: B3 0.573 -> V2a 0.527 -> V2b 0.493 (a 14% relative reduction
     outcome->V2b). ALL arms remain severely overconfident (every bin sits below the
     diagonal; every gap is negative), so the degeneration is mitigated, NOT cured.

MECHANISM — and the honest deflation of the headline:
  The ECE gain is NOT purely an accuracy artifact (ECE is accuracy-coupled, and V2b is also
  the most accurate arm, so this had to be checked):
    - V2b goes UNANIMOUS LESS OFTEN (65.9% vs B3's 77.5%) and is MORE OFTEN RIGHT when it
      does (0.470 vs 0.414). Both move calibration the same way, and the confidence-profile
      shift (how often it hedges) is independent of the accuracy gain.
    - Accuracy-matched check (restricting to the 3/3 bin, where ECE reduces to |1-acc|):
      B3 0.586, V2a 0.537, V2b 0.530 — the ordering survives at matched confidence.
  BUT discrimination is FLAT: AUC (vote-share separating correct from incorrect) is
  0.620 / 0.637 / 0.619 for B3 / V2a / V2b — no better in the process arms.
  => The process arms are better calibrated because they HEDGE MORE, not because they can
     better TELL when they are wrong. That is a weaker claim than "process verification
     yields self-knowledge", and it is the claim the data supports.

=================  LITERATURE (primary sources verified this session)  =================
DCPO (arXiv 2603.09117, "Decoupling Reasoning and Confidence: Resurrecting Calibration in
  RLVR"): RLVR "significantly enhances large language models (LLMs) reasoning but severely
  suffers from calibration degeneration, where models become excessively over-confident in
  incorrect" answers. It further reports "a fundamental gradient conflict between the
  optimization for maximizing policy accuracy and minimizing calibration error" — relevant
  because our process reward improves BOTH here, without a calibration objective.
arXiv 2605.15588 ("Calibrating LLMs with Semantic-Level Reward"): "Standard reinforcement
  learning with verifiable rewards (RLVR) trains models with a binary correctness reward
  that is indifferent to confidence, providing no penalty for confident but wrong
  predictions and thereby degrading calibration"; "A model that guesses incorrectly with
  high confidence receives the same signal as one that abstains"; this "indifference
  structurally incentivizes overconfident guessing". Our B3 arm is exactly that binary
  regime, and it is the worst-calibrated arm — consistent.
arXiv 2509.21882 ("The Hidden Costs and Measurement Gaps of RLVR"): headline RLVR gains
  often "conflate policy improvement with three confounds: (i) budget mismatch ...
  (ii) attempt inflation and calibration drift that convert abstentions into confident
  answers, and (iii) benchmark data contamination", and recommends "budget-matched
  saturation curves with variance, calibration, and abstention tracking". This checkpoint
  IS the calibration-tracking component of that minimum standard for CoCr; the
  budget-matching component is handled in exclusion_baselines's FLOPs accounting.

=================  CAVEATS  =================
- Vote-share confidence is coarse (3 attainable levels) and is a self-consistency proxy,
  not a verbalized or logit-based confidence. Conclusions are about that signal.
- The 1/3 bin is tiny (14-15 per arm) — the reliability curve's left end is noisy; the
  ECE is dominated by the 3/3 bin, which is well populated (415-488).
- Per-arm n=630 pools 3 seeds x 210 structures; seeds are not independent replicates of the
  calibration statistic, so no seed-level SD is quoted.
- AUC is computed with ties at 0.5; with only 3 confidence levels ties are frequent, which
  compresses AUC toward 0.5 for ALL arms. The FLAT comparison across arms is the robust
  reading; the absolute AUC value is protocol-limited.

REPRODUCE
  re-score: handoff/e3m_votes.json (harvested vote distributions from evals_e3m/*.json)
  source generations: /root/work/e2/evals_e3m/eval_{B3,V2a,V2b}_s{0,1,2}.json
  figure: figures/calibration.png

=================  PER-STEP -> FINAL-ANSWER CORRELATION  =================
(the second component item-3 required; it doubles as the E7 selection-signal feasibility test)

CIRCULARITY CAUGHT AND EXCLUDED — recorded because the naive number was near-perfect and
would have been badly misleading:
  A first pass correlated FULL chain faithfulness with final-answer correctness and got
  AUC = 0.997-0.999, r = +0.88 for all arms. That is an ARTIFACT. score_chain's per_step
  vector CONTAINS step["system"], which scores whether the emitted crystal system equals the
  truth — the same quantity as final-answer correctness. bravais / point_group / space_group
  are likewise deterministic functions of (or tightly coupled to) the answer. So full
  faithfulness embeds the label, and correlating it with correctness is near-tautological.
  RETRACTED: "faithfulness predicts correctness with AUC 0.998". Do not cite that number.

VALID (answer-INDEPENDENT) TEST. The geometry step is scored purely against CIF-derived
lattice relations and does not reference the crystal-system answer, so it is a legitimate
predictor. Geometry survives in 90.7% of the stored 400-char snippets (it is the first
emitted step), so it is recoverable without regeneration:

  arm   n    r(geom, correct)   AUC    geom|correct   geom|incorrect
  B3    630  +0.523             0.811  0.885          0.511
  V2a   630  +0.539             0.812  0.893          0.526
  V2b   630  +0.553             0.818  0.874          0.496

READING: an answer-independent, deterministically verifiable step predicts final-answer
correctness at AUC ~0.81 — substantially better than the model's own self-consistency
confidence (vote-share AUC ~0.62 from the calibration section). This is direct evidence that
the CIF-grounded checker is a usable RERANKING signal for E7 test-time scaling, and that the
step scores carry information the model's own confidence does not. The near-identical AUC
across arms says this is a property of the CHECKER, not of any one training arm.

LIMITATION (logged): only geometry is recoverable this way. motif appears in 0% of stored
snippets (always past char 400) and system in only 36%, so re-scoring truncated text does
NOT reproduce eval-time faithfulness (re-scored mean 0.263 vs original 0.288). A full
answer-independent decomposition (geometry + motif, excluding system/bravais/point_group/
space_group) requires the FULL generations, which were not stored. ACTION: store full
generations (or at minimum a per-step score vector) in the next eval run — cheap, and it
unblocks the complete decomposition plus the E7 rerank study.

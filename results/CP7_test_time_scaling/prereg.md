# PRE-REGISTRATION — E7 / CP7 test-time scaling
# Written and committed BEFORE any E7 inference was run.

## WHY E7 IS THE RIGHT EXPERIMENT NOW
CP1b branch (a) killed the accuracy claim; CP8 showed a 19-feature structure model beats every
image arm and that both chain arms sit BELOW a 3-feature size-only floor (0.5286). CP0c item 2
showed the chain's geometry step is responsive to the image without being informed by it. What
survives is CHECKABILITY, and CP9 supplied the premise: an ANSWER-INDEPENDENT deterministic
checker (geometry step scored against CIF truth) predicts final correctness at AUC 0.811-0.818,
far above the model's own self-consistency confidence (0.62). E7 tests whether that checker
converts into deployable value.

## THE HARD PARTITION (non-negotiable; the directive's central requirement)
Every reported row is labelled DEPLOYABLE or ORACLE. They are never mixed in one number.

  DEPLOYABLE — uses ONLY information available at inference time, no ground-truth labels:
    D1  majority vote over K samples (the existing protocol, K=3 baseline; sweep K)
    D2  internal step-consistency: rerank samples by agreement of their OWN emitted steps
        (do the emitted lattice relations imply the emitted system? no CIF consulted)
    D3  tool-coupled: run spglib on the coordinates the model EMITS, and score consistency
        between that and the model's claimed system. Uses a tool, not the answer key.
  ORACLE — consults the sidecar/CIF truth; an upper bound, never a deployable claim:
    O1  rerank K samples by the CP0-truth geometry-step score (the AUC 0.81 signal)
    O2  best-of-K by final correctness (the absolute ceiling)

## PRIMARY METRICS
1. accuracy vs K (saturation curves), per row, per arm.
2. RISK-COVERAGE with checker-score abstention: AURC and E-AURC, plus explicit operating
   points at coverage 0.9 / 0.75 / 0.5. The CP8 regularity floor (0.5286) is drawn as a
   reference band on the risk-coverage figure (directive item 4).
3. PREDICT-AND-CERTIFY system row: B1 answers, chain+checker certifies, disagreement abstains.
   Reported as (coverage, accuracy-on-covered) pairs — the deployable system claim.

## ARMS AND CONFIG
Arms: B1_s0 (answerer), V2b_s0 (chain/certifier), V2a_s0 and B3_s0 if budget allows.
Eval: the 210-structure composition-exclusion set (data/e3), same as every other checkpoint.
EVAL AT 416-EFF (max_pixels=200704) — MATCHED TO TRAINING, per the demonstrated train/test
mismatch artifact in CP0c (B1 lost 0.133 at native). effective_resolution logged in results.json.
Sampling: temperature 0.7, max_new_tokens 512, K swept over {1,3,5,8}.
Self-revision: ONE bounded pass, reported as a SEPARATE row, never folded into the verifier
result — 2512.11109 (verified) reports iterative refinement often DEGRADES open VLMs.

## PRE-REGISTERED DECISION RULES
Threshold 0.05 absolute (program convention, ledger/CONVENTIONS.md).

  H7a (deployable value): some DEPLOYABLE row beats plain majority vote (D1 at matched K) by
      > 0.05 accuracy at equal compute, OR improves AURC by > 10% relative.
      => CONFIRMED: "the deterministic checker converts into deployable test-time gains."
      => NOT MET: report the null plainly; the checker's AUC 0.81 is then an oracle-only
         property and the paper must say so.
  H7b (certification value): the predict-and-certify row attains accuracy-on-covered
      >= 0.80 at coverage >= 0.5.
      => CONFIRMED: "the verified chain can certify a more accurate answerer's outputs."
      This is the claim most aligned with the legibility-tax frame: the chain need not be
      accurate to be USEFUL, if it can tell when the accurate arm is wrong.
  H7c (oracle gap): O1 minus the best deployable row quantifies the headroom lost to not
      knowing the truth. Reported descriptively, no pass/fail.

## WHAT WOULD MAKE E7 A NEGATIVE RESULT, STATED IN ADVANCE
If no deployable row beats majority vote AND the certify row cannot reach 0.80 at coverage 0.5,
then the checker is an oracle-only artifact and CoCr's verifiability claim rests on the CP3
faithfulness result alone. That is a publishable but much weaker paper, and it must be reported
as such rather than rescued with a post-hoc metric. (Two post-hoc rescues have already been
attempted and labelled this session — CP1c's stratified analysis and the CP8 mechanism
sentence. The pattern is logged; the standard is not negotiable.)

## COST
Inference only, no training. K=8 x 210 structures x ~4 arms is the dominant term; at the
measured ~5 min/seed for B1-style short outputs and ~3 hr for chain arms at K=3, the chain arms
dominate and the K sweep is run on V2b_s0 only, with B1 swept cheaply.

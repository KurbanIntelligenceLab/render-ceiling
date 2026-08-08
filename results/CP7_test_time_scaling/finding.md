CHECKPOINT: CP7_test_time_scaling     GAP: does the CIF-grounded checker convert into
                                            DEPLOYABLE test-time value?
STATUS: DONE (1 seed, K=8, 210-structure composition-exclusion eval, 416-eff matched to training)
RESULT: BOTH pre-registered hypotheses NOT MET. H7a fails outright — no deployable selection
rule beats plain majority vote, and every alternative is WORSE. H7b fails on coverage — the
certify row is highly accurate (0.912) but covers only 16% of structures.
This is the negative outcome the pre-registration described IN ADVANCE, and it is reported as
such rather than rescued with a post-hoc metric.

=================  ROWS (all scored from the SAME 1680 generations per arm)  =================
Generating once and scoring every rule offline means differences are the SELECTION RULE, never
sampling luck. 210 structures x 8 samples x 2 arms; claim parsed 100%; V2b emitted a lattice in
100% of samples (B1 emits none by design).

  V2b (chain / certifier)          kind         acc      AURC    E-AURC
    D1 majority vote               deployable  0.3810   0.6268   0.3740
    D2 internal step-consistency   deployable  0.3524   0.7970   0.5154
    D3 tool-coupled (spglib)       deployable  0.3524   0.7971   0.5155
    O1 truth-score rerank          ORACLE      0.4000   0.4659   0.2309
    O2 best-of-8                   ORACLE      0.4048   0.2306   0.0000

  B1 (direct / answerer)           kind         acc      AURC    E-AURC
    D1 majority vote               deployable  0.6190   0.2835   0.1985
    D2 internal step-consistency   deployable  0.6190   0.3803   0.2953
    D3 tool-coupled (spglib)       deployable  0.6190   0.3803   0.2953
    O1 truth-score rerank          ORACLE      0.5857   0.4465   0.3446
    O2 best-of-8                   ORACLE      0.8571   0.0111   0.0000
  (B1's D2/D3 correctly DEGENERATE to majority vote: a direct answer emits no lattice to check.
   They are listed for completeness, not as independent rules.)

=================  H7a — NOT MET, and the failure is informative  =================
Rule: some deployable row beats D1 by > 0.05 accuracy OR improves AURC by > 10% relative.
  V2b: D2/D3 accuracy -0.0286, AURC -27.2% RELATIVE WORSE
  B1:  D2/D3 accuracy +0.0000, AURC -34.1% RELATIVE WORSE
Not a near miss in either direction: filtering samples by self-consistency makes the ranking
WORSE than not filtering. The self-consistency signal is anti-correlated with correctness at
selection time, even though the CP9 checker score correlates with it at AUC 0.81.

WHY THOSE TWO FACTS COEXIST (the substantive finding): CP9's AUC 0.81 was measured with the
ANSWER-INDEPENDENT geometry step scored AGAINST CIF TRUTH. D2/D3 do not have truth; they can
only ask whether the model's emitted numbers are consistent with the model's own claim. A chain
that FABRICATES a clean lattice and then reasons correctly from it is maximally
self-consistent and wrong — exactly the failure CP2 diagnosed and CP0c confirmed is not a
resolution artifact. So self-consistency preferentially selects confident fabrications.
=> The checker's predictive power is REAL but ORACLE-ONLY: it requires the true structure, which
   at inference time is precisely what is unknown. This must be stated plainly in the paper.

=================  H7b — NOT MET on coverage, but the accuracy is striking  =================
Predict-and-certify (B1 answers, chain certifies, disagreement abstains):
    certify iff chain agrees with B1                     coverage 0.1619  acc 0.9118 (n=34)
    certify iff agrees AND chain majority self-consistent coverage 0.1524  acc 0.9062 (n=32)
    reference: B1 alone, no abstention                   coverage 1.0000  acc 0.6190
Rule required acc >= 0.80 AT coverage >= 0.5. Accuracy clears it comfortably (0.912 vs 0.80);
coverage misses badly (0.16 vs 0.50). VERDICT: NOT MET.

What is nonetheless true and worth reporting: when the verified chain AGREES with the direct
answer, that answer is right 91% of the time versus 62% unconditionally — a +29 pp lift. The
chain is a GOOD certifier on the slice it can certify; that slice is just small, because the
chain's own accuracy (0.38) bounds how often it can agree with a correct answer.

=================  H7c — oracle gap (descriptive, no pass/fail)  =================
    V2b: best deployable 0.3810 | O1 0.4000 | O2 0.4048   headroom to ceiling +0.0238
    B1:  best deployable 0.6190 | O1 0.5857 | O2 0.8571   headroom to ceiling +0.2381
Two readings:
 - V2b's ceiling is nearly saturated (+0.024): 8 samples of the chain almost never contain a
   correct answer that selection failed to find. The chain's problem is GENERATION, not selection.
 - B1 has large unrealised headroom (+0.238): a correct answer is present among its 8 samples
   far more often than any deployable rule can identify. Note O1 (truth-rerank) is WORSE than
   majority vote for B1 (0.5857 vs 0.6190) — the geometry-truth score cannot rank a direct
   answer that contains no geometry, so this is a null-by-construction row, not a finding.

=================  A BUG CAUGHT BEFORE IT BECAME A RESULT  =================
The first scoring pass reported D3 with a plausible-looking number. The enrichment metadata
showed spglib_resolved = 0 of 1680: spglib and pymatgen are NOT installed in the box's VLM
environment, and a bare `except` in enrich_e7.py silently converted every failure into "no
result", so D3 had degenerated into majority vote for EVERY sample. Had the metadata not been
logged, D3 would have been reported as a genuine tool-coupled row that was really D1 in
disguise. Fixed by computing D3 locally (spglib 2.7.0 + pymatgen), where it resolves 1680/1680.
LESSON RECORDED: a fallback path must be counted and surfaced, never silent.

=================  WHAT THIS MEANS FOR THE PAPER  =================
E7 was the experiment that could have supplied POSITIVE evidence for the verifiability claim.
It did not. The honest position after CP1b, CP8 and now CP7:
 - accuracy claim: dead (CP1b branch (a); CP8 floor and structure baseline)
 - deployable test-time gain from the checker: REFUTED HERE (H7a)
 - deployable certification at useful coverage: REFUTED HERE (H7b), though the certified slice
   is 91% accurate
 - what SURVIVES: CP3's Gate-2 faithfulness result, the ~49%-vs-~2% silent-group training
   mechanism, CP9's calibration improvement, and the CP0c/geometry-step evidence that the chain
   is responsive to the image without being informed by it.
The verifiability story is now narrower than "the checker is useful at inference": it is
"process verification measurably improves chain faithfulness and training dynamics, and the
resulting chain certifies a stronger answerer on a small high-precision slice."
Per the pre-registration: "That is a publishable but much weaker paper, and it must be reported
as such rather than rescued with a post-hoc metric."

CAVEATS: 1 seed, K=8, one eval set. The certify-coverage limit is bounded by the chain's own
0.38 accuracy, so a stronger chain would widen it — that is a hypothesis, not a result.

REPRODUCE
  generate: scripts/run_e7_tts.py --arm {V2b,B1} --seed 0 --k 8 --max-pixels 200704
  enrich:   scripts/enrich_e7.py  (D3 must run where spglib+pymatgen exist — NOT the box VLM env)
  score:    scripts/score_e7.py
  prereg:   prereg.md (committed before any E7 inference)

=================  FOLLOW-UP: IS THE CERTIFIED SLICE JUST THE EASY STRUCTURES?  =================
POST-HOC. Designed after seeing H7b fail, so it is exploratory and labelled as such — but unlike
the CP1c post-hoc attempt it SURVIVES its control, and the control is the one that matters.

THE WORRY: the certified slice is 91% accurate vs 62% unconditional, but chain agreement might
carry no information of its own — it could simply select structures B1 was already confident
about, in which case "the chain certifies" would be a restatement of "B1 knows when it is sure".

AGGREGATE CONTROL (and why it is MISLEADING):
    chain-certified            n=34  acc 0.9118   mean B1 vote-confidence 0.853
    top-34 by B1 confidence    n=34  acc 0.9118   <- IDENTICAL
Taken alone this looks like a clean refutation: the chain adds nothing. It is not, and reporting
only this number would have been wrong. The two selections OVERLAP ON ONLY 7 of 34 structures
(20.6%) — they achieve the same accuracy on largely DIFFERENT structures, and B1's confidence is
coarsely quantised at K=8 (only 6 possible values, 82 of 210 structures tied at 1.0), so a
"top-k by confidence" cut is mostly an arbitrary tie-break rather than a real ranking.

THE CORRECT TEST — stratify by B1 confidence and ask whether agreement adds accuracy WITHIN a
level (so difficulty and self-confidence are held fixed):
    B1 conf    n   agree n   acc|agree   acc|disagree     lift
      0.500   19        3       0.667        0.375      +0.292
      0.625   33        4       0.750        0.517      +0.233
      0.750   31        4       1.000        0.444      +0.556
      0.875   43        8       0.875        0.514      +0.361
      1.000   82       15       1.000        0.701      +0.299
    ALL 5/5 strata positive. Unweighted mean lift +0.348 (SD 0.125, SE 0.056, t=6.24, df=4);
    n-weighted mean lift +0.339.
    Cochran-Mantel-Haenszel stratified test:  z = 3.767  (p < 0.001)

RESULT: chain agreement carries information about correctness BEYOND the answerer's own
confidence. The most striking cell is the top one: among the 82 structures where B1 is
UNANIMOUS across all 8 samples, B1 is right 70.1% of the time on its own, but 100% (15/15) of
the time when the verified chain independently agrees. Self-consistency cannot distinguish those
cases; an independently-derived chain can.

WHAT THIS DOES *NOT* CHANGE: H7b still FAILS. The rule required accuracy >= 0.80 AT coverage
>= 0.5, and coverage is 0.16. This analysis explains WHY the certified slice is good rather than
rescuing the hypothesis, and the pre-registered verdict stands unchanged.

WHAT IT ADDS TO THE PAPER: the certification claim is stronger and more precisely stated than
CP7's headline suggested. Not merely "the chain agrees on easy cases" but "an independently
verified chain supplies correctness information that the answerer's own confidence does not
contain, including where the answerer is maximally confident." That is a genuine
process-verification result and it is consistent with CP3 (faithfulness) and CP9 (the process
arms hedge more appropriately) rather than in tension with them.

STATUS AND CAVEATS: EXPLORATORY, 1 seed, K=8, single eval set. Strata are thin (agree-n of 3-15
per level) and the CMH test treats strata as independent. Must be PRE-REGISTERED and re-run on
the 3-seed matrix before it is stated as a finding in the paper. Do not report it as confirmed.

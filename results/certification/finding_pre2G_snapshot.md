CHECKPOINT: certification    GAP: is a VERIFIED chain a better certifier than an unverified one?
STATUS: PRIMARY COMPARISON DONE (V2b vs B3). SFT-V1 arm and the K=16 equal-budget control are
still generating on box 1; this record will be completed when they land.
RESULT: PROCESS TRAINING IS WHAT MAKES THE CHAIN A CERTIFIER. The pre-registered contrast came
out positive and the outcome-trained control came out NULL-TO-NEGATIVE.

=================  THE COMPARISON  =================
Answerer: B1-direct, K=8 sampled, its own majority vote (base rate 0.6143 on the 210-structure
composition-exclusion split). A structure is CERTIFIED when an independently sampled chain's
majority answer AGREES with the answerer's.

  arm   coverage  acc|certified   CMH z   common OR   Breslow-Day p   systems emitted
  V2b     0.1635      0.9118      +3.767      8.989       0.570            4/7
  B3      0.1923      0.5250      -1.374      0.595       0.587            3/7

  V2b-certified lift over the answerer's base rate: +0.2975
  B3-certified  lift over the answerer's base rate: -0.0893

HOMOGENEITY GATE (the prereg amendment): Breslow-Day p = 0.570 (V2b) and 0.587 (B3), both well
above 0.05, so a common odds ratio is defensible and the CMH is reportable FOR BOTH ARMS. The
gate was added expecting it might block the CMH; it passes. Note this is stratification by
ANSWERER CONFIDENCE, the pre-registered endpoint. Stratified by CRYSTAL SYSTEM the odds ratios
are wildly heterogeneous (logOR -3.1 to +6.9) and must NOT be pooled — a separate finding about
WHERE certification fires, reported via the prediction-support table, never by pooling.

=================  WHAT IT MEANS  =================
The two chains are the SAME base model, SAME SFT checkpoint, SAME data, SAME K=8 protocol, and
differ ONLY in the reward that trained them: B3 got outcome-only, V2b got dense per-step
verifiable rewards. So the certifying ability is attributable to PROCESS TRAINING, not to
"having a chain", not to ensembling, and not to extra inference compute.

B3 does not merely certify worse — its agreement is if anything ANTI-correlated with correctness
(OR 0.595 < 1, z = -1.37, not significant but pointed the wrong way), and its certified slice
(0.525) sits BELOW the answerer's unconditional base rate (0.614). Agreeing with the
outcome-trained chain is not evidence the answer is right.

THIS IS THE POSITIVE RESULT THE PROGRAM HAS BEEN MISSING. process_reward showed process rewards win on
held-out accuracy and faithfulness by small margins; test_time_scaling showed the verifier is oracle-only and
NO deployable selection rule beat majority vote. certification finds the deployable use that does work:
not selecting among a chain's own samples, but CERTIFYING a separate, stronger, cheaper answerer.
The chain's value is not that it answers well — it answers at 0.386 — but that its agreement
carries information about someone else's answer, and ONLY when it was trained with verification.

=================  LIMITS, STATED  =================
- COVERAGE IS LOW. V2b certifies 16.4% of structures. This is a high-precision, low-recall
  instrument, not a general accuracy improvement.
- STRUCTURAL CEILING ON COVERAGE. V2b emits only 4 of 7 crystal systems, B3 only 3. A chain that
  never predicts hexagonal/monoclinic/triclinic cannot certify them, so coverage is bounded by
  prediction support and NOT by competence. Any coverage claim must carry this.
- ONE SEED, ONE ANSWERER. Both chains are seed 0 and the answerer is B1 seed 0.
- PENDING: SFT-V1 tests whether GRPO is needed at all or plain SFT suffices; the K=16 control
  tests whether the effect is just extra compute. Neither has landed. Until they do, the claim is
  "process-trained beats outcome-trained", NOT yet "verification specifically is required".

REPRODUCE
  python scripts/analyze_cp7b.py --answerer gen_B1_s0_k8_final.json \
    --chains V2b=gen_V2b_s0_k8_final.json B3=gen_B3_s0_k8_final.json --out cp7b_results.json
  NOTE: spglib_implies must be computed LOCALLY — spglib is absent from the GPU box and the
  enrichment's exception handler silently returns None there, which would degrade D3 to majority
  vote. Guard asserts >=95% resolution before scoring. (Same trap as test_time_scaling; caught both times.)

=================  MECHANISM: WHY PROCESS TRAINING MAKES A CERTIFIER  ========================
(exploratory, run on the SAME generations, no new compute; pre-registers nothing but answers the
first question a reviewer will ask — is V2b certifying merely because it is a better answerer?)

IT IS NOT. Both chains are weak answerers and neither is close to the answerer they certify:
    V2b own accuracy 80/210 = 0.381
    B3  own accuracy 59/210 = 0.281
    B1 answerer            = 0.614

THE DIFFERENCE IS IN THE ERRORS, NOT THE ANSWERS. Agreement is informative only when the
certifier's MISTAKES are not shared by the answerer. Conditioning on the chain being WRONG:
    V2b wrong on 130 structures; the answerer agreed with the wrong answer on   3  -> 2.31%
    B3  wrong on 151 structures; the answerer agreed with the wrong answer on  19  -> 12.58%
    difference +0.1028, z = 3.42
So V2b's false-certification rate is 5.4x lower than B3's. When V2b and B1 agree they agree on
the TRUTH 31/34 = 91.2% of the time; for B3 it is 21/40 = 52.5%.

Note also that in EVERY case where a chain and the answerer agreed on a wrong answer, the
answerer was also wrong (aw_ans_right = 0 for both arms) — agreement never certified a case where
the answerer alone would have been right. The failure mode of certification here is exclusively
"both wrong together", which is the benign direction for a precision instrument.

THE SHARPER CLAIM: process training did not make the chain a better answerer — it made the
chain's errors DECORRELATED from the answerer's. That is what agreement-based certification
actually requires, and it is why an outcome-trained chain of identical architecture, data and
inference budget fails at it. This also connects to external_baselines's error-overlap result, where the
structure-metric RF and the image model failed on different structures: error decorrelation, not
raw accuracy, is the recurring source of usable signal in this program.

CAVEAT: exploratory and post-hoc. It explains the pre-registered result rather than testing a new
hypothesis, and it uses the same seed and the same single answerer.

=================  COVERAGE CEILING: DECOMPOSED  =============================================
(exploratory, same generations, no new compute. Answers "is the 16.4% coverage fixable?", which
is the natural follow-up to the prediction-support limit stated above.)

V2b's emitted distribution over the 210 eval structures:
    tetragonal 79, cubic 68, trigonal 62, orthorhombic 1; NEVER hexagonal, monoclinic, triclinic.
So 4/7 systems have any support at all, and one of those (orthorhombic, n=1) is vestigial.

SPLITTING COVERAGE BY WHETHER THE TRUTH IS EXPRESSIBLE:
    truth IN  V2b's support: 120 structures, certified 32  -> 0.267
    truth OUT of support   :  90 structures, certified  2  -> 0.022
    overall                : 34/210 = 0.1619

MULTIPLICATIVE DECOMPOSITION:
    P(truth in support) = 120/210 = 0.571
    P(agree | in support)         = 0.267
    product                       = 0.153   vs observed 0.162  (close; the two factors are
                                             near-independent and both bind)

WHAT FIXING THE COLLAPSE WOULD BUY: if out-of-support structures behaved like in-support ones,
coverage would rise 0.162 -> 0.267, a +0.105 absolute / +65% relative gain. That roughly DOUBLES
the instrument's recall but does not approach full coverage.

WHY THE RESIDUAL IS NOT A DEFECT: even where the chain CAN express the truth it is right only
80/120 = 0.667 of the time, and certification additionally requires the ANSWERER to land on the
same label. The surviving disagreements are precisely the cases where the two models' errors do
NOT coincide — which is the property that makes the agreements informative in the first place.
Driving coverage toward 1.0 by making the chain agree more would destroy the signal.

CONSEQUENCE FOR THE PAPER: the honest framing is that coverage has TWO independent bottlenecks,
one of which (the collapsed output distribution) is an obvious engineering target worth roughly a
2x recall gain, and one of which (genuine disagreement) is load-bearing and should NOT be
optimised away. We do not know how to fix the collapse; it is stated as future work, not as a
result.
CAVEAT: exploratory, one seed, one answerer; the projection assumes out-of-support structures
would behave like in-support ones, which is an assumption and not a measurement.

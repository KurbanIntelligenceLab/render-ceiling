CHECKPOINT: CP7b_certification    GAP: is a VERIFIED chain a better certifier than an unverified one?
STATUS: PRIMARY COMPARISON DONE (V2b vs B3). SFT-V1 arm and the K=16 equal-budget control are
still generating on box 1; this record will be completed when they land.
RESULT: PROCESS TRAINING IS WHAT MAKES THE CHAIN A CERTIFIER. The pre-registered contrast came
out positive and the outcome-trained control came out NULL-TO-NEGATIVE.

=================  THE COMPARISON  =================
Answerer: B1-direct, K=8 sampled, its own majority vote (base rate 0.6143 on the 210-structure
composition-exclusion split). A structure is CERTIFIED when an independently sampled chain's
majority answer AGREES with the answerer's.

  arm   coverage  acc|certified   CMH z   common OR   Breslow-Day p   systems emitted
  V2b     0.1619      0.9118      +3.767      8.989       0.570            4/7
  B3      0.1905      0.5250      -1.374      0.595       0.587            3/7

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

B3 is NULL, not demonstrably harmful. Its certified slice (0.525) sits below the answerer's
unconditional base rate (0.6143), but the exact one-sided binomial test gives p = 0.159 — NOT
significant. The point estimate is below base rate and the odds ratio is below 1 (0.595, z=-1.37),
but the honest statement is that outcome-trained agreement carries NO usable information, not that
it is anti-correlated. Agreeing with the
outcome-trained chain is not evidence the answer is right.

THIS IS THE POSITIVE RESULT THE PROGRAM HAS BEEN MISSING. CP3 showed process rewards win on
held-out accuracy and faithfulness by small margins; CP7 showed the verifier is oracle-only and
NO deployable selection rule beat majority vote. CP7b finds the deployable use that does work:
not selecting among a chain's own samples, but CERTIFYING a separate, stronger, cheaper answerer.
The chain's value is not that it answers well — it answers at 0.386 — but that its agreement
carries information about someone else's answer, and ONLY when it was trained with verification.

=================  LIMITS, STATED  =================
- COVERAGE IS LOW. V2b certifies 34/210 = 16.19% of structures. This is a high-precision, low-recall
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
  vote. Guard asserts >=95% resolution before scoring. (Same trap as CP7; caught both times.)

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

FALSE-CERTIFICATION RATE (the non-tautological reliability quantity): of the structures where
the CHAIN is wrong, how often does the answerer nonetheless agree with it?
    process chain wrong on 130; answerer agreed on  3 -> 0.0231, Wilson 95% [0.008, 0.066]
    outcome chain wrong on 151; answerer agreed on 19 -> 0.1258, Wilson 95% [0.082, 0.188]
    difference +0.1028; z_unpooled = 3.421 (headline), z_pooled = 3.197; ratio 5.45x
[A previous version argued from 'in every agreed-wrong case the answerer was also wrong'.
 RETRACTED as TAUTOLOGICAL: agreement means the answerer's label EQUALS the chain's, so a
 wrong certified answer entails a wrong answerer BY CONSTRUCTION. It cannot be evidence of
 a benign failure mode. The false-certification rate above is the quantity that carries
 actual information.]

THE SHARPER CLAIM: process training did not make the chain a better answerer — it made the
chain's errors DECORRELATED from the answerer's. That is what agreement-based certification
actually requires, and it is why an outcome-trained chain of identical architecture, data and
inference budget fails at it. This also connects to CP8's error-overlap result, where the
structure-metric RF and the image model failed on different structures: error decorrelation, not
raw accuracy, is the recurring source of usable signal in this program.

CAVEAT: exploratory and post-hoc. It explains the pre-registered result rather than testing a new
hypothesis, and it uses the same seed and the same single answerer.

=================  COVERAGE CEILING: DECOMPOSED  =============================================
(exploratory, same generations, no new compute. Answers "is the 16.19% coverage fixable?", which
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
    product                       = 0.153   vs observed 0.1619 (close; the two factors are
                                             near-independent and both bind)

WHAT FIXING THE COLLAPSE WOULD BUY: if out-of-support structures behaved like in-support ones,
coverage would rise 0.1619 -> 0.267, a +0.105 absolute / +65% relative gain. That roughly DOUBLES
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

=================  2G COMPLIANCE — SIX REQUIRED FIXES APPLIED  ===============================
(i)   TAUTOLOGICAL CLAIM DELETED. The "aw_ans_right = 0" argument is retracted above and replaced
      with the false-certification rate (3/130 = 0.0231, Wilson [0.008, 0.066]).
(ii)  DENOMINATORS RECONCILED. The comparison table previously reported 0.1635 and 0.1923, which
      were 34/208 and 40/208; the decomposition used /210. CAUSE IDENTIFIED: exactly two
      structures (mp-1046323, mp-29816) have an answerer vote share of 0.375 (a 3/8 split), which
      is not one of the declared confidence strata {0.500, 0.625, 0.750, 0.875, 1.000}, so the
      stratified CMH necessarily excludes them. Coverage, however, is a POPULATION quantity:
      analyze_cp7b.py now divides by the full 210 and scores off-stratum structures as
      NOT-CERTIFIED per the standing convention. ALL COVERAGES ARE NOW /210:
          process 34/210 = 0.1619    outcome 40/210 = 0.1905
      The CMH denominator (208) is reported separately as cmh_denominator so the two quantities
      are never conflated again. One quantity, one value.
(iii) STATISTICS COMPLETED.
      Wilson 95% on the certified slice: process [0.770, 0.970]; outcome [0.375, 0.671].
      Exact one-sided binomial lift vs the 0.6143 base rate — THIS TEST WAS MISSING ENTIRELY:
          process 31/34 above base rate, p = 1.1e-4  -> SIGNIFICANT
          outcome 21/40 below base rate, p = 0.159   -> NULL, not harmful
      False-certification comparison: z_unpooled = 3.421 is the headline; z_pooled = 3.197 is
      reported alongside and the conclusion is unchanged.
      "Anti-correlated" softened to "null" throughout, per the p = 0.159 result.
(iv)  VERIFIABILITY. results.json now carries per_stratum 2x2 counts (agree_correct, agree_n,
      disagree_correct, disagree_n) for every answerer-confidence stratum, plus coverage_counts,
      cmh_denominator, lift_vs_base_rate, false_certification and
      false_certification_comparison. The CMH z, common OR and both Breslow-Day p-values are
      re-derivable from the file alone, same convention as McNemar discordant counts.
(v)   CLAIM BOUNDARY HELD. The SFT-only certifier and the K=16 equal-budget control are still
      generating. Until BOTH land, the claim is "PROCESS-TRAINED BEATS OUTCOME-TRAINED", NOT
      "verification specifically is required" — plain SFT might suffice (untested) and the effect
      might be inference compute (untested). The mechanism and coverage-ceiling sections remain
      labelled EXPLORATORY. ONE SEED AND ONE ANSWERER THROUGHOUT: every number here is
      certifier seed 0 against answerer B1 seed 0, and no result generalises past that until 4B's
      second answerer and second certifier seed are run.
(vi)  SPGLIB TRAP GUARDED. spglib_implies is computed LOCALLY; spglib is absent from the GPU box
      and the enrichment's exception handler silently returns None there, which would degrade the
      tool-coupled rule to majority vote. The assert requiring >=95% resolution before scoring is
      in place and passed at 1680/1680 = 100% for both arms. This trap has now bitten twice and
      been caught twice.

INTERNAL COUNT RECONCILIATION (all verified): 210-80=130 and 210-59=151 (chain-wrong counts);
31+3=34 and 21+19=40 (certified splits); 120+90=210 (support decomposition).

=================  REPLICATION ON A SECOND ANSWERER — MIXED, AND THE BAD HALF IS THE  ==========
=================  ONE I PRE-REGISTERED AS THE SHARPER TEST                          ==========
Second answerer: the CP12 adapter (native 768px, 3220 augmented examples), K=8, same 210
composition-exclusion structures, base rate 145/210 = 0.6905. The certifier chains (V2b, B3,
seed 0, K=8) are REUSED UNCHANGED, so the answerer is the only varied factor.

  certifier   coverage    acc | certified    headroom recovered   lift p      false-cert
  V2b process 57/210=0.2714  56/57 = 0.9825      94.3%            1.8e-08     0.0077
  B3  outcome 31/210=0.1476  28/31 = 0.9032      68.7%            0.0053      0.0199
  (answerer base 0.6905; R1 threshold 0.6905 + 0.50*0.3095 = 0.8453)

PRIMARY ENDPOINT: BRANCH R1 MET. V2b recovers 94.3% of available headroom (>= the 50% required)
at p = 1.8e-08. On answerer 1 it recovered 77.1%. So the process certifier REPLICATES, and does so
on an answerer that is better trained, higher resolution and higher base rate.

SECONDARY ENDPOINT: FAILED, AND IT MATTERS MORE. The pre-registration states verbatim: "The
OUTCOME chain (B3) must remain NULL on this answerer (p >= 0.05). If B3 suddenly certifies the A3
answerer, the process-vs-outcome contrast is answerer-specific and the whole CP7b claim weakens,
whatever V2b does. This is the sharper falsification test of the two."
B3 certifies this answerer at 0.9032, p = 0.0053, recovering 68.7% of headroom. It does NOT
remain null. By my own committed rule the process-vs-outcome contrast is ANSWERER-SPECIFIC.

THE MECHANISM STORY ALSO WEAKENS. On answerer 1 the false-certification rates were 0.0231 vs
0.1258, z_unpooled = 3.421 — a 5.45x gap that carried the error-decorrelation explanation. On
answerer 2 they are 0.0077 vs 0.0199, z_unpooled = 0.889 — same direction, NOT significant. The
decorrelation advantage of process training is not reproduced on a stronger answerer.

WHAT I THINK IS ACTUALLY GOING ON (labelled as interpretation, not result): a better answerer
makes agreement a stronger signal for ANY certifier. A3 is right 69.1% of the time unconditionally
versus B1's 61.4%, so when a chain agrees with A3 the joint event is more likely to be correct
regardless of how the chain was trained. That would predict exactly what we see — both arms rise,
and the gap between them shrinks. It also predicts the contrast was never about verification per
se but about how much headroom the answerer left for decorrelation to matter. THIS IS A
HYPOTHESIS AND IT IS NOT TESTED HERE.

WHAT THE PAPER MAY NOW CLAIM, AND MAY NOT:
  MAY: "An independently sampled chain's agreement certifies a stronger answerer at high
       precision, replicated across two answerers (0.9118 and 0.9825)." This is robust.
  MAY: "A process-trained certifier recovers more headroom than an outcome-trained one on both
       answerers (77.1% vs -- ; 94.3% vs 68.7%)." Directionally consistent.
  MAY NOT: "Only process training yields a usable certifier." REFUTED on answerer 2, where the
       outcome-trained chain certifies significantly.
  MAY NOT: "Process training decorrelates errors" as a general mechanism claim. The supporting
       statistic is significant on one answerer and not on the other.
  The headline must therefore shift from a process-vs-outcome claim to a CERTIFICATION claim:
  a below-floor chain certifies a stronger answerer, with process training helping but not being
  necessary. That is a weaker and more defensible paper than the one I was writing an hour ago.

LIMITS: two answerers, one certifier seed each, one dataset. The SFT-only arm (is any RL needed?)
and the K=16 equal-budget control (is it just compute?) are still generating on box 1 and both
bear directly on what remains of the process-vs-outcome contrast.

=================  IS A CHAIN NECESSARY? BRANCH C2 — CHAIN HELPS, IS NOT REQUIRED  ============
Pre-registered in prereg_chain_necessity.md before computing. Zero GPU: both generation sets
already existed. Same answerer (A3, base 0.6905), same exact-binomial test, same 50%-of-headroom
bar the chain certifiers were held to.

  certifier                    coverage        acc | certified   headroom recovered   lift p
  process CHAIN (V2b)          57/210 = 0.2714   56/57 = 0.9825      94.3%           1.8e-08
  DIRECT-answer model (B1)    120/210 = 0.5714  100/120 = 0.8333     46.1%           2.7e-04

BRANCH C2 FIRES: the direct certifier IS significant (p = 2.7e-04) but recovers 46.1% of headroom
against the chain's 94.3% — a gap of 48.2 percentage points, far past the pre-registered 15pp
threshold, and it falls BELOW the 0.8453 bar that C1 would have required.

WHAT THIS RESCUES, AND WHAT IT DOES NOT.
  RESCUES: the chain structure IS load-bearing. A second independently sampled model agreeing is
  NOT the whole mechanism — that variant certifies too, but roughly half as effectively. So CP7b
  is not merely SelfCheckGPT-style self-consistency relabelled, and the earlier collapse of the
  process-vs-outcome contrast does not collapse the chain claim with it.
  DOES NOT RESCUE: "verification is required". Both a chain trained on outcome-only reward
  (0.9032 on this answerer) and a chainless direct model (0.8333) certify significantly. The
  ordering is chain-with-process > chain-with-outcome > no-chain, which reads as a GRADIENT in
  how much the certifier's errors differ from the answerer's, not a binary requirement.

THE FALSE-CERTIFICATION STATISTIC NOW SEPARATES CLEANLY, AND IT IS THE MOST INFORMATIVE NUMBER
IN THIS WHOLE CHECKPOINT:
    process chain 3/390-equivalent -> 0.0077 | direct model -> 0.2500 | z_unpooled = 4.944
A direct certifier agrees with the answerer's WRONG answer 25% of the time it is itself wrong; the
process chain does so 0.77% of the time. That is a 32x difference and it is exactly the
error-decorrelation account — which had weakened on the process-vs-outcome comparison but is
strongly supported here. The reason is visible in the prediction support: the direct certifier
emits ALL 7 systems and the chain only 4, so the direct model is a near-copy of the answerer
(same architecture, same task framing, same failure modes) while the chain fails differently.
HIGH COVERAGE IS THEREFORE NOT A VIRTUE: the direct certifier covers 57.1% versus the chain's
27.1%, precisely BECAUSE it agrees with the answerer more often — including when both are wrong.

REVISED CLAIM AFTER THIS AND THE REPLICATION:
  DEFENSIBLE: a chain that scores far below the answerer, and below the regularity floor, certifies
  it at 0.98 precision; a chainless certifier of the same base model certifies at 0.83, and the
  gap tracks how decorrelated the certifier's errors are from the answerer's.
  NOT DEFENSIBLE: "only process training works" (refuted on answerer 2) or "verification is
  required" (refuted here).

=================  INFERENCE-PATH AUDIT (brief §9) AND A RESOLUTION ASYMMETRY  ================
Audited all three generating scripts for training/inference consistency, not just the trainer:
  train_e2_lora.py  apply_chat_template(..., add_generation_prompt=False)  [correct: target follows]
  eval_e3.py        apply_chat_template(..., add_generation_prompt=True)
  run_e7_tts.py     apply_chat_template(..., add_generation_prompt=True)
All three take max_pixels as an explicit argument and every generation file records
effective_resolution READ FROM THE LIVE PROCESSOR (grid_thw, patch/merge size, visual tokens per
view), per the brief's logging requirement.

EVERY RUN WAS MATCHED TO ITS OWN TRAINING RESOLUTION, which is the correct choice given CP0c
(a 416-trained adapter evaluated at 768 falls 0.5905 -> 0.4571 from train/test MISMATCH, not from
resolution):
    A3 answerer   576 visual tokens/view (768px)  — trained native.  MATCHED
    V2b certifier 169 visual tokens/view (416px)  — trained at 416.  MATCHED
    B3 certifier  169 visual tokens/view (416px)  — trained at 416.  MATCHED
    B1 answerer   169 visual tokens/view (416px)  — trained at 416.  MATCHED

CONSEQUENCE, STATED BECAUSE IT IS EASY TO MISS: in the SECOND-ANSWERER replication the answerer
and the certifiers see DIFFERENT IMAGES of the same structure (768px vs 416px). Assessed:
  - It cannot INFLATE agreement — different inputs make agreement harder, not easier, so the
    replication's positive result is if anything conservative.
  - It cannot MANUFACTURE the process-vs-outcome comparison — both certifiers ran at 416, so that
    contrast is internally resolution-matched.
  - It DOES falsify one framing: we may NOT write that certification works because the two models
    "see the same evidence and cross-check it". For the second answerer they demonstrably do not.
    The defensible framing is the one already adopted — agreement between models whose ERRORS are
    decorrelated, which does not require identical inputs and is arguably strengthened when the
    inputs differ.
No numbers change. This is a claim-boundary note, recorded so the framing is not written loosely
later.

=================  ALL THREE REMAINING ARMS LANDED — THE SEED REPLICATION FAILS  ==============
=================  THIS IS THE BINDING CONSTRAINT ON THE WHOLE CHECKPOINT       ==============
All on answerer B1 (base 0.6143), K=8 unless stated, same 210 composition-exclusion structures.
Bar is the same 50%-of-headroom rule used throughout: certified accuracy >= 0.8072 with p < 0.05.

  certifier                    coverage        acc | certified  headroom  lift p     verdict
  process, seed 0              34/210 = 0.1619  31/34 = 0.9118    77.1%   1.1e-04   MEETS
  SFT-only chain (no RL)       51/210 = 0.2429  39/51 = 0.7647    39.0%   0.0172    fails bar
  process, SEED 1              21/210 = 0.1000  15/21 = 0.7143    25.9%   0.24      NOT SIGNIFICANT
  K=16 equal-budget answerer   19/210 = 0.0905  18/19 = 0.9474    -       1.2e-03   (see below)

(1) SEED REPLICATION FAILS, AND IT IS THE MOST IMPORTANT OF THE THREE. A SECOND SEED of the SAME
    process-trained certifier, on the SAME answerer, with the SAME protocol, gives 0.7143 at
    p = 0.24 — not significant, and 51.2 percentage points of headroom below seed 0. Coverage also
    halves (34 -> 21). The pre-registration for the second-ANSWERER replication set the threshold
    and I apply the identical bar here: seed 1 does not clear it.
    CONSEQUENCE: the strong 0.9118 figure is SEED-SPECIFIC. Two seeds of the same recipe differ by
    0.198 in certified accuracy (0.9118 - 0.7143 = 0.1975), which is larger than every effect
    this checkpoint has reported.
    Any claim resting on a single certifier seed is unsupported, and that includes the headline.

(2) SFT-ONLY certifies significantly (p = 0.0172) but at 39.0% of headroom, below the bar. So RL
    is not REQUIRED for a chain to carry certification signal — plain supervised training is
    enough to beat the answerer's base rate — but it is materially weaker. This is consistent with
    the gradient already recorded (no-chain 46.1% < outcome 68.7% < process 94.3% on answerer 2),
    and it slots SFT-only into that gradient rather than overturning it.

(3) K=16 EQUAL-BUDGET CONTROL: doubling the ANSWERER's inference budget does NOT explain the
    effect — the process certifier still certifies at 0.9474, p = 1.2e-03. Coverage falls to
    19/210 because a K=16 vote is more decisive and agrees less often. Note the common odds ratio
    is nan (a stratum has a zero cell at this coverage), so only the exact binomial is quoted for
    this arm; the CMH is not reportable here and is not reported.

REVISED CLAIM AFTER ALL ARMS — this supersedes every earlier version in this file:
  SUPPORTED: agreement between an answerer and an independently sampled second model identifies a
  high-precision subset. Measured across 4 certifier configurations and 2 answerers, certified
  accuracy ranged 0.7143-0.9825 against base rates 0.6143-0.6905, and 5 of 6 configurations beat
  their base rate significantly.
  SUPPORTED: the certifier can be far weaker than the answerer — process chains score 0.381 and
  0.281, both below the 0.5286 regularity floor, while certifying at up to 0.98.
  NOT SUPPORTED: any specific effect SIZE. Certifier seed variance (0.9118 vs 0.7143 on identical
  configuration) exceeds every between-condition difference reported here.
  NOT SUPPORTED: "process training is necessary" (SFT-only works, p=0.0172), "verification is
  required" (chainless works, p=2.7e-04), or "only process training yields a usable certifier"
  (outcome chain works on answerer 2, p=0.0053).
  REQUIRED BEFORE PUBLICATION: >= 3 certifier seeds per condition, reported as mean +/- SD. With
  n=1 seed per cell the condition ordering is not established. This is the honest state and it is
  a materially weaker result than the one this checkpoint opened with.

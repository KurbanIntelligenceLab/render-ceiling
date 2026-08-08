# PRE-REGISTRATION — CP7b, CERTIFICATION RE-RUN (confirmatory)
# Written and committed BEFORE any number was regenerated. The CP7 exploratory run's strata are
# RE-DECLARED here rather than inherited; where they differ from the exploratory ones it is
# stated explicitly.

## WHY THIS RUN EXISTS
CP7's post-hoc follow-up found that chain agreement lifts B1's accuracy at every self-confidence
stratum (mean +0.348, CMH z=3.767). That analysis was EXPLORATORY — designed after H7b failed.
It is currently the strongest candidate for the paper's positive claim, so it must be
re-established under pre-registration with comparators and controls it lacked.

## LITERATURE POSITIONING (primary sources verified before writing this)
- arXiv 2606.13649 — VERIFIED, and the brief's description needs one correction. The paper is
  "Operadic consistency: a label-free signal for compositional reasoning failures in LLMs"
  (Bottman), not a direct-vs-decomposed agreement paper per se; its signal (OC) compares a
  model's answer to a composite question against sequentially answering its parts. It IS the
  closest prior art and it DOES use an equal-cost comparator: it reports "selective-prediction
  improvements (accuracy at fixed coverage) over a tuned CoT-SC baseline at the equal-cost K=3
  budget". Differentiate CoCr on: (i) visual scientific domain, (ii) the decomposition is
  DETERMINISTIC from a CIF rather than model-generated, (iii) the process-training comparator
  test below, which asks whether process training — not merely decomposition — is what makes
  the agreement signal work. That third point is ours and is not in the prior art.
- SelfCheckGPT (arXiv 2303.08896) — agreement-as-reliability lineage; cite for provenance.
- arXiv 2605.25133 (PVD) — procedural confidence; cite as adjacent.
- arXiv 2410.02173 — the brief cited this as "CoT-derived signals can cluster 0/1 and fail as
  abstention signals". CORRECTION AFTER READING: the paper is Zellinger & Thomson, "Efficiently
  Deploying LLMs with Controlled Risk". Its clustering statement is about PLATT SCALING —
  "standard Platt scaling does not work well for LLMs because its conditional probabilities tend
  to form a tight cluster near 1" — not about CoT-derived signals specifically. The caution is
  therefore adjacent rather than direct, and must be cited for what it says. The ACTIONABLE
  check it motivates is still valid and WAS RUN (below).

## THE CLUSTERING CHECK — RUN BEFORE DESIGNING THE STRATA (result already known, recorded here)
Continuous agreement score = fraction of the chain's K=8 samples matching B1's majority answer.
  distribution: 0.0 -> 172, 0.125 -> 3, 0.375 -> 1, 0.75 -> 1, 0.875 -> 14, 1.0 -> 19
  81.9% at exactly 0.0, 9.0% at exactly 1.0 => 91.0% AT THE EXTREMES, 9.0% interior
  AUC of the CONTINUOUS score vs B1 correctness = 0.602
CONSEQUENCE, DECLARED IN ADVANCE: the continuous agreement score IS severely clustered, exactly
the pathology the caution warns about, and it discriminates poorly (AUC 0.602). Therefore the
primary endpoint uses the BINARY agree/disagree indicator, NOT the continuous score. The binary
form is not merely a simplification: with 91% of mass at the extremes, the continuous score
carries almost no information the binary does not. The continuous score's AUC 0.602 will be
REPORTED as a negative sub-result so the choice is auditable rather than looking like a
favourable metric chosen after the fact.

## RUN
Same eval set (210-structure composition-exclusion), same K=8 protocol, same 416-eff resolution
matched to training, same saved generations where they exist. New generations required only for
the comparator chains (B3, SFT-V1).

## PRE-REGISTERED PRIMARY ENDPOINT — ONE, DECLARED NOW
  Cochran-Mantel-Haenszel COMMON ODDS RATIO for B1-correct, agree vs disagree, stratified by
  B1 self-confidence, computed separately for each certifying chain. The PRIMARY COMPARISON is
  V2b's common odds ratio against B3's. Everything else below is secondary.

## STRATA — RE-DECLARED (not inherited)
B1 self-confidence at K=8 takes 6 values. The exploratory run used 5 strata and dropped the
0.375 level (n=2). PRE-DECLARED HERE: strata are {0.500, 0.625, 0.750, 0.875, 1.000}; the 0.375
level (n=2) is EXCLUDED for insufficient cell count, a rule fixed now and applied identically to
every comparator arm. Any stratum with fewer than 3 observations in either cell is reported but
excluded from the CMH statistic, again applied uniformly.

## COMPARATOR ARMS (upgrade a — without this it is not a process-verification finding)
Same K=8, same eval set, agreement partner varies:
    B1 + V2b     (dense step-level process training)     <- primary
    B1 + B3      (outcome-only GRPO, NOT process-trained) <- primary comparator
    B1 + SFT-V1  (chain, no GRPO at all)
    B1 + V2a     (optional if budget allows)
H-CERT-1 (primary): V2b's CMH common odds ratio EXCEEDS B3's.
  Pre-registered outcomes:
    (i)  V2b > B3 with non-overlapping 95% CIs -> process training measurably improves the
         certification signal. This is the paper's positive claim.
    (ii) All chains certify comparably -> THE HONEST FINDING IS "chain agreement certifies
         (consistent with the agreement-signal literature), and process training adds nothing
         measurable to it." Report straight, do not bury. The certification result then belongs
         to the agreement-signal literature, not to process verification, and the paper must say so.
    (iii) V2b < B3 -> report as-is; would indicate process training HARMS certification.

## EQUAL-BUDGET CONTROL (upgrade b)
The chain costs extra model calls, so the comparison must be cost-matched, following
2606.13649's equal-cost design:
    arm A: B1 K=8 alone (self-consistency vote + its own vote-share confidence)
    arm B: B1 K=8 + chain K=8, certification by agreement
Arm B uses 2x the calls of arm A, so ALSO report:
    arm A': B1 K=16 self-consistency  (equal TOTAL sample budget to arm B)
H-CERT-2: certification with the chain beats B1 K=16 self-consistency at matched coverage.
If it does not, the honest statement is that the gain is a sampling-budget effect, not a
verification effect. NOTE the prefill accounting from CP1b applies: because prefill dominates,
2x the samples is NOT 2x the FLOPs; report the FLOPs ratio alongside the call ratio.

## REPORTING REQUIREMENTS (upgrade c) — NO CONDITIONAL ACCURACY WITHOUT ITS DENOMINATOR
Every cell reports: n, accuracy, Wilson 95% CI. The full 2x2 (agree/disagree x stratum) is
tabulated for every arm. A risk-coverage curve is reported per arm with the CP8 regularity floor
(0.5286) drawn as a band. The exploratory run's headline "0.70 -> 1.00 where B1 is unanimous"
must appear ONLY with n=82 total, n=15 agreeing, and the Wilson interval on 15/15 — which is
wide, and saying so is part of the result.

## UNIFORMITY
Both sides of every pre-registered comparison use the IDENTICAL K. No comparison mixes decode
budgets (the CP3 lesson where an inconsistent budget nearly manufactured a gate pass).

## WHAT WOULD MAKE THIS UNINFORMATIVE
If B1's accuracy on the certified slice does not exceed the CP8 regularity floor (0.5286) by
more than its Wilson interval, the certified slice has not demonstrated crystallographic
reasoning and the certification claim is not available regardless of the odds ratios.

=================  AMENDMENT — HOMOGENEITY GATE (added BEFORE comparator numbers landed)  ======
Found by a Lane-B exploratory analysis on the EXISTING generations while A1 was still generating.
It changes the primary endpoint's validity conditions, so it is amended in now rather than
discovered during analysis. prereg_v1_snapshot.md preserves the pre-amendment text.

PER-SYSTEM CERTIFICATION BREAKDOWN (exploratory, B1+V2b, existing K=8 generations):
  system         n   n_agree  acc|agree  acc|disagree    lift
  cubic         30       13     1.000       0.000      +1.000
  hexagonal     30        0       n/a       1.000         n/a   <- chain NEVER certifies
  monoclinic    30        0       n/a       0.767         n/a   <- chain NEVER certifies
  orthorhombic  30        1     0.000       0.897      -0.897
  tetragonal    30       16     1.000       0.286      +0.714
  triclinic     30        2     0.000       0.571      -0.571
  trigonal      30        2     1.000       0.000      +1.000
Certification is CONCENTRATED: 29 of 34 certified cases are cubic or tetragonal, and coverage is
exactly ZERO for hexagonal and monoclinic.

THE PROBLEM THIS CREATES FOR THE PRE-REGISTERED ENDPOINT:
  CMH stratified by crystal system gives z = 6.089 — MORE significant than the confidence-
  stratified z = 3.767. But CMH estimates a COMMON odds ratio, and the per-system odds ratios are:
    cubic 945.0 (logOR +6.85) | trigonal 285.0 (+5.65) | tetragonal 77.0 (+4.34)
    orthorhombic 0.044 (-3.12) | triclinic 0.152 (-1.89)
  logOR spread 9.97, SD 4.56, and the effect REVERSES SIGN across systems. A common odds ratio is
  not a defensible summary of that, so a bare CMH number — however significant — would be
  UNINTERPRETABLE. Reporting only the pooled z would have been a real error.

AMENDED ENDPOINT PROTOCOL (pre-declared, applied identically to every comparator arm):
  1. Run a BRESLOW-DAY homogeneity test on the stratified 2x2s FIRST. It GATES the CMH.
  2. If homogeneity is NOT rejected (p >= 0.05): report the CMH common odds ratio as the primary
     endpoint exactly as originally pre-registered.
  3. If homogeneity IS rejected (p < 0.05): the CMH common odds ratio is NOT reported as the
     primary endpoint. Instead report (a) per-stratum odds ratios with Wilson/exact CIs, (b) the
     count and direction of strata favouring each arm, and (c) the primary V2b-vs-B3 comparison
     as a per-stratum comparison rather than a single pooled number. State plainly that pooling
     was inadmissible and why.
  4. EITHER WAY, report the per-system coverage table above. A certification signal with zero
     coverage on 2 of 7 systems is a materially different claim from a uniform one, and the
     paper must say which it is.

WHY THIS STRENGTHENS RATHER THAN WEAKENS THE STUDY: the V2b-vs-B3 comparator test is unaffected
in DESIGN — it just has to be made per-stratum if homogeneity fails. And the concentration
finding is itself informative: it predicts that the chain certifies where lattice metric alone
is nearly decisive (cubic/tetragonal, high symmetry) and fails where it is not
(monoclinic/triclinic, low symmetry) — consistent with CP2's fabrication diagnosis and CP0c's
finding that the geometry step is responsive to the image without being informed by it.
That prediction is TESTABLE against the comparator arms and is pre-registered here as a
secondary hypothesis: H-CERT-3, the per-system coverage profile is similar across chains
(i.e. it is a property of the TASK's symmetry structure, not of process training).

=================  FURTHER PRE-COMPARATOR FINDING: THE CHAIN'S PREDICTIONS COLLAPSE  ==========
Found while B3's generations were still running. Recorded BEFORE the comparator numbers exist.

V2b's predicted-system distribution over the whole 210-structure eval:
    tetragonal 79 | cubic 68 | trigonal 62 | orthorhombic 1 | hexagonal 0 | monoclinic 0 | triclinic 0
The chain emits only FOUR of the seven systems, and effectively only three. Per true system:
    true cubic        -> cubic 30                        (perfect)
    true trigonal     -> trigonal 29, cubic 1            (near-perfect)
    true hexagonal    -> trigonal 29, cubic 1            (systematically confused with trigonal)
    true tetragonal   -> tetragonal 21, cubic 9
    true monoclinic   -> tetragonal 22, cubic 8
    true orthorhombic -> tetragonal 18, cubic 12
    true triclinic    -> tetragonal 18, cubic 7, trigonal 4

WHY THIS MATTERS FOR THE CERTIFICATION CLAIM: B1 can only be "certified" on a system the chain
actually EMITS. Certification coverage is therefore bounded by the chain's prediction support,
not by its competence. Zero coverage on hexagonal and monoclinic is now explained: the chain
NEVER PREDICTS those systems at all, so agreement is structurally impossible there.

SELF-CORRECTION: an intermediate note in this session said certification coverage "tracks the
chain's own per-system accuracy almost exactly". That overstates a Pearson r of +0.677 over 7
points, and trigonal contradicts it directly (accuracy 0.967 but coverage only 0.067). The
accurate statement is the one above — coverage is driven by the chain's PREDICTION SUPPORT, and
accuracy is correlated with that support only because both are high on cubic/tetragonal.

CONSEQUENCE FOR H-CERT-3, sharpened and pre-registered now:
  H-CERT-3 (revised): the comparator chains B3 and SFT-V1 show the SAME prediction collapse
  (support concentrated on a few high-symmetry systems). If they do, the collapse — and hence the
  certification coverage ceiling — is a property of the TASK and the chain FORMAT, not of process
  training, and the certification claim must be stated with that ceiling attached.
  If instead V2b's support is BROADER than B3's, that is a genuine process-training benefit and
  should be reported as one.
  This is now a primary reason the comparator arms matter, independent of the odds-ratio endpoint.

REPORTING REQUIREMENT ADDED: every arm's prediction-support table (which systems it ever emits,
and with what frequency) is reported alongside its certification numbers. A certifier that can
only certify 3 of 7 systems is a materially different instrument from one that covers all 7, and
the paper must say which it is.

=================  ANALYSIS SCRIPT BUILT AND VALIDATED (before comparator data arrives)  ======
scripts/analyze_cp7b.py implements the pre-registered endpoint end-to-end. VALIDATED against the
hand-computed exploratory result on the existing V2b data:
    script CMH z = 3.7666   vs hand-computed 3.767      (match)
    acc on covered 0.9118   vs hand-computed 0.9118     (match)
    coverage 0.1635 vs 0.1619 — the small difference is CORRECT and expected: the script drops
    items whose B1 confidence is not on a DECLARED stratum (the 0.375 level, n=2), exactly as the
    prereg specifies, whereas the exploratory pass included them.

AN IMPORTANT CLARIFICATION THE VALIDATION SURFACED — two different stratifications, two answers:
  stratified by B1 CONFIDENCE (the pre-registered endpoint):
      Breslow-Day stat 2.9455, df 4, p 0.570 -> homogeneity NOT rejected -> CMH IS reportable,
      common OR = 8.99.
  stratified by CRYSTAL SYSTEM (the exploratory pass recorded earlier in this file):
      odds ratios span logOR -3.1 to +6.9 and reverse sign -> homogeneity clearly violated ->
      a common OR there is NOT defensible.
BOTH are true and they are not in conflict: the pre-registered endpoint stratifies by
CONFIDENCE, where the effect is homogeneous, so the CMH is admissible for the primary
comparison. The system-level heterogeneity is a SEPARATE, real finding about WHERE
certification fires, and it is reported through the prediction-support table and the per-system
breakdown — NOT by pooling across systems. The amendment's gate stands as written; this note
records that the gate PASSES for the primary endpoint and fails for the secondary one, so
neither is applied to the wrong analysis.

PREDICTION SUPPORT confirmed by the script for V2b: emits 4 of 7 systems, never hexagonal,
monoclinic, or triclinic. H-CERT-3 now tests whether B3 and SFT-V1 show the same restriction.

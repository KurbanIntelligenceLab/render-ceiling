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

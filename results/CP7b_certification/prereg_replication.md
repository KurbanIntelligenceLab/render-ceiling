# CP7b REPLICATION — SECOND ANSWERER
# COMMITTED BEFORE THE SECOND ANSWERER'S GENERATIONS EXIST. Brief 4B requires a pre-registered
# replication threshold; brief 5 requires thresholds as a FRACTION OF HEADROOM, not absolute units.

## WHAT IS BEING RUN AND WHY THIS ANSWERER
The entire CP7b result rests on ONE answerer (B1 seed 0, 416px, 1610 examples, base rate 0.6143)
and ONE certifier seed. Brief 4B asks for a second answerer, "a different B1 seed at minimum,
ideally a different model".
We use the CP12 adapter B1_aug_s0 (native 768px, 3220 augmented examples, base rate 0.6619). This
is a STRONGER test than a second seed of the same recipe: it differs in resolution, training-set
size and view augmentation, so surviving it means the effect is a property of the CERTIFIER, not
a quirk of one answerer checkpoint. It is also already trained and sitting on an idle GPU.
The certifier chains are REUSED UNCHANGED (V2b and B3, seed 0, K=8) — only the answerer changes,
which is what isolates the answerer as the varied factor.

## THE HEADROOM PROBLEM, HANDLED EXPLICITLY
The two answerers have different base rates, so an absolute lift threshold is not comparable:
    B1 base 0.6143 -> headroom to 1.0 = 0.3857 ; observed lift +0.2975 = 77.1% of headroom
    A3 base 0.6619 -> headroom to 1.0 = 0.3381
An absolute +0.2975 on A3 would require 0.9594, which is a HARDER target purely because the
answerer is better. Thresholds below are therefore FRACTIONS OF HEADROOM.

## PRIMARY ENDPOINT
Certification precision of the PROCESS chain (V2b) on the A3 answerer, i.e. accuracy on the slice
where the independently sampled V2b majority agrees with the A3 majority.

## PRE-REGISTERED DECISION RULE
  R1 REPLICATES: V2b's lift recovers >= 50% of the headroom available above A3's own base rate,
     i.e. certified accuracy >= 0.6619 + 0.50*0.3381 = 0.8310, AND the exact one-sided binomial
     test of that slice against 0.6619 gives p < 0.05.
     -> The certification effect is answerer-independent. Report as replicated.
  R2 PARTIAL: lift is positive and significant (p < 0.05) but recovers < 50% of headroom.
     -> Report as replicated in DIRECTION but attenuated; state the fraction recovered and do not
        claim the B1-level effect size generalises.
  R3 FAILS: lift is not significant (p >= 0.05), or is negative.
     -> The B1 result does NOT generalise across answerers. Report that plainly; it would demote
        certification from a general capability claim to a single-checkpoint observation, and the
        CVPR framing must change accordingly.
  Threshold rationale: 50% of headroom is chosen because the B1 result recovered 77.1%; a rule at
  50% asks the effect to be more than half as strong on a different answerer, which is a genuine
  test rather than a formality, without demanding the exact original magnitude on a harder base.

## SECONDARY, ALSO COMMITTED NOW
  - The OUTCOME chain (B3) must remain NULL on this answerer (p >= 0.05). If B3 suddenly certifies
    the A3 answerer, the process-vs-outcome contrast is answerer-specific and the whole CP7b claim
    weakens, whatever V2b does. This is the sharper falsification test of the two.
  - FALSE-CERTIFICATION RATE: V2b's rate (B1: 3/130 = 0.0231) should stay below B3's. The
    error-decorrelation mechanism predicts this; a reversal falsifies the mechanism story.
  - COVERAGE will differ and that is EXPECTED, not a finding: coverage depends on how often the
    two models happen to agree, and A3 is a different model. Report it, do not interpret it as
    the instrument getting better or worse.

## WHAT I WILL NOT DO
  - Not swap the endpoint to whichever of V2b/B3 looks better after seeing the numbers.
  - Not re-choose the headroom fraction after the fact.
  - Not treat a coverage change as evidence either way.
  - Not claim "verification is required" — that still awaits the SFT-only arm now generating.

## THRESHOLD ARITHMETIC RECOMPUTED — RULE UNCHANGED, INPUT CORRECTED
# Written after generating but BEFORE computing any certification number.
The pre-registration above used base rate 0.6619, taken from CP12's K=3 evaluation. The
replication runs at K=8, and the A3 answerer's K=8 majority-vote base rate on the same 210
structures is 145/210 = 0.6905 (+0.0286 vs K=3 — more samples, better vote).
Certification is computed on THESE generations, so the lift must be measured against the base
rate of THESE generations. The RULE is untouched (50% of the headroom above the answerer's own
base rate, exactly as committed); only its arithmetic input changes:
    base 0.6905 | headroom 0.3095 | R1 requires certified accuracy >= 0.6905 + 0.50*0.3095 = 0.8452
This is a stricter bar than the 0.8310 implied by the stale input, so the correction cannot be
accused of loosening the test. R2 and R3 branches are unchanged and still keyed to significance
against 0.6905.
NOTE FOR FUTURE PRE-REGISTRATIONS: fix the base rate at the K the experiment will actually use.
Quoting a base rate from a different decoding budget is an easy way to write a threshold that
does not mean what it says.

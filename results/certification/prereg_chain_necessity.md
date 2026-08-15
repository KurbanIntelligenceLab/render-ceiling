# certification — IS A CHAIN NECESSARY AT ALL?
# COMMITTED BEFORE COMPUTING. Zero GPU: both generation sets already exist.

## WHY THIS TEST, AND WHY NOW
The second-answerer replication refuted "only process training yields a usable certifier": the
outcome-trained chain certified at p = 0.0053. That collapse of the process-vs-outcome contrast
raises the obvious next question, and it is the one a reviewer will ask first:

    Does the certifier need to be a CHAIN at all, or is "a second independently sampled model
    agrees" the entire mechanism?

Every certifier tested so far emits a reasoning chain. If a DIRECT-answer model — no chain, no
per-step verification, no reasoning trace — certifies just as well, then certification is not about chains,
not about verification, and not about process supervision. It is about model-pair agreement, which
is SelfCheckGPT-adjacent prior art and a far weaker contribution.

## SETUP
Answerer: A3 (native+augmented, K=8, base rate 145/210 = 0.6905) — the same answerer as the
replication, so results are directly comparable to the chain certifiers measured on it.
Certifier under test: B1-direct seed 0, K=8, ALREADY GENERATED. It emits a bare crystal-system
label with no chain whatsoever.
Comparators already measured on this answerer: process chain 0.9825 (94.3% of headroom),
outcome chain 0.9032 (68.7%).

## PRE-REGISTERED DECISION RULE
  C1 CHAIN IS NOT NECESSARY: the direct certifier recovers >= 50% of the headroom above A3's base
     rate (i.e. certified accuracy >= 0.8453) at p < 0.05 — the SAME bar the chain certifiers were
     held to.
     -> The mechanism is model-pair agreement. certification must be reframed: the contribution is the
        MEASUREMENT (a below-floor model certifies a stronger one, quantified against deterministic
        ground truth) and NOT any claim that verified reasoning is what does the work. The paper
        must cite SelfCheckGPT and arXiv 2606.13649 as the mechanism's prior art and differentiate
        only on the deterministic-ground-truth instrument.
  C2 CHAIN HELPS BUT IS NOT REQUIRED: direct certifier is significant (p < 0.05) but recovers
     materially less headroom than the process chain — operationalised as a gap of at least 15
     percentage points of headroom (i.e. direct <= 94.3% - 15 = 79.3%).
     -> Report chains as beneficial, not necessary. Keep the certification claim; drop any
        "verification is required" language permanently.
  C3 CHAIN IS NECESSARY: the direct certifier is not significant (p >= 0.05).
     -> The chain structure is load-bearing after all, and the process-vs-outcome collapse on
        answerer 2 is about the REWARD not mattering, while the CHAIN still does. This would
        partially rescue the original framing.

## COMMITMENTS
  - The endpoint is certification precision on the direct certifier's agreed slice, tested against
    A3's own base rate 0.6905 by exact one-sided binomial. Same test, same bar, same answerer as
    the chain arms.
  - I will report C1 even though it is the outcome that most weakens the paper. It is also the
    most likely outcome given that the process-vs-outcome contrast already collapsed.
  - Coverage will differ between certifiers and is NOT interpreted as quality, per the standing
    convention from the replication pre-registration.
  - If C1 fires, the false-certification statistic is also computed for the direct certifier, so
    the error-decorrelation framing is evaluated on it too rather than quietly dropped.

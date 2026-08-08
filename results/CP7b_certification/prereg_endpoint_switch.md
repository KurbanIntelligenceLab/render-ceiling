# CP7b — PRIMARY ENDPOINT SWITCH: certified accuracy -> FALSE-CERTIFICATION RATE
# COMMITTED BEFORE COMPUTING seed 1's false-certification rate. Zero GPU.

## WHY SWITCH (directive item 3, verified independently)
Certified accuracy is conditional on the agreed slice, which is n = 19-57 across configurations.
At p ~ 0.9 that gives SE ~ 0.051. The false-certification rate is conditioned on the
CERTIFIER-WRONG set, n = 130-151, giving SE ~ 0.012 — roughly 4x tighter. It is also the
instrument's actual reliability question ("if I trust an agreement, how often am I wrong?")
rather than an accuracy on a small conditional subset, and it produced the sharpest separation
anywhere in this checkpoint (0.0077 chain vs 0.2500 chainless, z = 4.944).

## THE ENDPOINT, DEFINED ONCE
false_certification_rate = P(answerer agrees with the certifier | certifier's majority is WRONG)
Denominator: structures where the certifier's K=8 majority != truth. Numerator: those where the
answerer's majority equals the certifier's. Lower is better. Wilson 95% intervals throughout.

## PRE-REGISTERED DECISION RULE
  E1 SEED-STABLE: seed 0 and seed 1 false-certification Wilson intervals OVERLAP, AND the
     two-proportion test between them is non-significant (p >= 0.05).
     -> The mechanism claim (error decorrelation) survives on an endpoint the noise does not
        swallow. The paper MAY then discuss the condition ordering ON THIS ENDPOINT ONLY
        (chain vs chainless vs SFT-only vs outcome), reporting each with its interval, and MUST
        still refrain from ordering claims on certified accuracy.
  E2 SEED-UNSTABLE: the two seeds differ significantly (p < 0.05) or their intervals are disjoint.
     -> Decisive and cheap. The paper reports certification as a CAPABILITY with no ordering on any
        endpoint, and the error-decorrelation mechanism is presented as an observation consistent
        with the data rather than an established mechanism.

## COMMITMENTS
  - I will not switch back to certified accuracy if the false-certification result is unfavourable.
  - The seed comparison is the gate. Cross-condition comparisons are computed either way but are
    only LICENSED for discussion under E1.
  - Both SD conventions are reported for any seed spread (project convention is population/ddof=0;
    power calculations use sample/ddof=1 as the unbiased estimator — stated because they differ).
  - Certified accuracy stays in the paper as a secondary, with the pooled figure and the honest
    note that the two seeds are NOT shown to differ from each other.

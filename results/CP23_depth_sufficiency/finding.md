CHECKPOINT: CP23_depth_sufficiency   GAP: does depth ordering carry the information a flat projection
                                     loses? The stated geometric precondition for the proposed
                                     depth-restoration ladder. (directive Stage 0b)
STATUS: DONE. THE QUANTIZATION-SATURATION CLAIM IS WITHDRAWN ENTIRELY — at full power neither four
        nor eight levels saturates (see POWERED COMPARISON). The depth-sufficiency answer is MIXED
        ACROSS THE TWO EVALUATION SETS — D3 on the original, D1 on the
        expansion. Depth restoration recovers only a small share of the gap it would need to close,
        and the FIRST operationalization I tried gave the wrong answer for an instructive reason.

=================  THE MEASUREMENT  ==========================================================
Lattice preserved in every variant (the cell edges are drawn, so the lattice is given); only atom
positions along the view axis are degraded. spglib crystal-system detection, symprec 1e-2, stratified
6 structures/system x 3 axis views = 126 measurements per evaluation set.
  P    = flat projection: view-axis coordinate replaced by a constant. What a flat render delivers.
  Qk   = depth quantized to k levels at true bin centres. What depth-graded COLOUR delivers.
  F    = unmodified. Upper bound.

  set         stratum            P        Q4       Q8       Q16      F
  original    box-sufficient   0.4286   0.5595   0.5595   0.5595   1.0000
  original    box-AMBIGUOUS    0.2381   0.2381   0.2381   0.2381   1.0000
  expansion   box-sufficient   0.4023   0.4713   0.4828   0.4828   1.0000
  expansion   box-AMBIGUOUS    0.1282   0.2564   0.2564   0.2564   1.0000

THE READING AGAINST THE PRE-REGISTERED BRANCHES. On the ORIGINAL set, quantized depth adds EXACTLY
NOTHING on the box-ambiguous stratum (0.2381 -> 0.2381) while helping box-sufficient (+0.1309): that
is branch D3, "helps where the answer was already available". On the EXPANSION set it doubles
box-ambiguous recovery (0.1282 -> 0.2564): that is branch D1. The precondition therefore holds on one
sample and fails on the other, and this is the third time a render-related result has split across
these two samples — the standing "measure on both sets" discipline is what caught it each time.

THE CEILING IS THE POINT, AND IT IS LOW. Even with 16 depth levels, box-ambiguous recovery reaches
0.2564 against 1.0000 with full depth. Depth quantization closes at most ~13 points of a ~75-point
gap on the stratum that needs it. Ordinal depth is NOT a substitute for metric depth, because
symmetry detection depends on exact metric relationships between atoms, not on their order.
QUANTIZATION SATURATES BY EIGHT LEVELS, NOT FOUR. Per stratum:
  set/stratum                  Q4       Q8       Q16    saturates at
  original/box-sufficient    0.5595   0.5595   0.5595        4
  original/box-ambiguous     0.2381   0.2381   0.2381        4
  expansion/box-sufficient   0.4713   0.4828   0.4828        8
  expansion/box-ambiguous    0.2564   0.2564   0.2564        4
Three of the four strata are flat from Q4 onward, but expansion/box-sufficient gains 0.0115 (one
measurement of 87) between Q4 and Q8 and only then flattens. So the saturation point ACROSS ALL
STRATA is EIGHT levels. If depth grading is ever implemented, eight distinguishable levels is the
safe figure and finer grading buys nothing; four suffices on three of four strata but is NOT
established as sufficient in general.
CORRECTION NOTE: an earlier version of this record and of REPORT.md declared "SATURATES AT FOUR
LEVELS" and licensed the recommendation "four levels is enough", while stating one line later that
the rows "differ by one measurement on the fourth". That was self-contradictory and the design
conclusion did not follow from the data. results.json's quantization_saturates_at was likewise
hard-coded to 4 and is now 8, with the per-stratum values recorded so the claim can be rechecked.

=================  THE FIRST OPERATIONALIZATION GAVE THE WRONG ANSWER  ========================
The pre-registration named "depth RANK" as the variant, and I implemented rank with UNIFORM spacing
(rank rescaled to the original extent). Run that way, depth ordering came out WORSE than a flat
projection: original box-sufficient 0.4286 -> 0.2619, expansion 0.4023 -> 0.2414.
That is a real effect and worth recording, but it is NOT the precondition test. Uniform rank spacing
is a NONLINEAR DISTORTION of the structure along the view axis: it moves atoms to positions they do
not occupy and destroys exact metric relationships that the flat projection at least leaves intact
(flattening preserves in-plane symmetry exactly). So the rank variant measured the harm of a
distortion, not the value of the added cue.
I caught it because R < P is not a coherent result for a variant that supposedly ADDS information, and
replaced it with quantization at TRUE bin centres, which is also the closer analogue of what
depth-graded colour actually delivers. Both variants are reported; the quantized one is the answer.
THE DESIGN WARNING THAT FALLS OUT OF IT: if a render supplies an ordinal depth cue and a reader
interprets the levels as evenly spaced, the result is WORSE than supplying no depth at all. Any depth
grading must be metric-faithful, not merely monotone.

=================  WHAT THIS MEANS FOR THE PROPOSED STAGE 1  ==================================
Taken with CP21, the case for the depth-restoration ladder is weak on three counts, none of which
required any API spend to establish:
  1. Two thirds of the occlusion is REDUNDANT (CP21), so the visible-information deficit is ~0.18-0.20,
     not ~0.55.
  2. Box-ambiguous structures are LESS informatively occluded than box-sufficient ones (CP21 item 0e),
     so restored visibility would land where it is least needed.
  3. Ordinal depth closes at most ~13 of the ~75 points available on the box-ambiguous stratum, and
     does so on only one of the two evaluation sets (this checkpoint).
The exact-height rung would do better, but the directive already flags that it LEAKS fractional
coordinates across five views, making it an oracle ceiling rather than a deployable protocol.
RECOMMENDATION: do not commission Stage 1 as an accuracy intervention. The Q4-saturation and
metric-faithfulness results are worth keeping as render-design observations, and they were free.

=================  LIMITS  ===================================================================
Perfect atom localisation is assumed throughout, exactly as in the oracle, so these are bounds on
what depth information COULD carry given extraction — not measurements of what any model reads. A
positive result here would have been necessary but not sufficient for Stage 1; a mixed one is
correspondingly weaker than it looks.

=================  POWERED COMPARISON: THE SATURATION CLAIM IS WITHDRAWN  ======================
The saturation claim rested on a 6-structure-per-system subsample (252 view-measurements). Rerun on
ALL structures and all 3 axis views — 1260 measurements, a 5x increase:
  set/stratum                 P        Q4       Q8       Q16
  original/box-sufficient   0.4444   0.5255   0.5301   0.5324
  original/box-ambiguous    0.1616   0.1566   0.1869   0.1970
  expansion/box-sufficient  0.4535   0.4558   0.4580   0.4603
  expansion/box-ambiguous   0.1005   0.2116   0.2169   0.2275
Q16 > Q8 > Q4 on ALL FOUR STRATA — the flatness that motivated "saturates at four levels" was a
low-power artifact of the subsample. Paired tests, pooled over all 1260 measurements:
  Q4 -> Q8 :  11 gained, 1 lost, exact p = 0.0063   REAL
  Q8 -> Q16:   6 gained, 0 lost, exact p = 0.0312   REAL
BOTH STEPS ARE SIGNIFICANT, so quantization does not saturate at four levels OR at eight within the
range tested. NO PROTOCOL RECOMMENDATION ON LEVEL COUNT IS SHIPPED. The honest statement is that finer
depth quantization keeps helping up to at least 16 levels, and where the gain stops is not established.
CORRECTION HISTORY, kept deliberately. This claim was stated three times and wrong each time: first
"saturates at four levels" (from the subsample, contradicted by its own per-stratum table), then
corrected to "saturates by eight" after a reviewer caught one stratum needing eight, and now withdrawn
outright once powered. The lesson is the one the directive states: do not ship a protocol
recommendation resting on a handful of discordant measurements. A per-stratum table with 1-2
discordant pairs cannot establish a saturation point in either direction.
NOTE ON THE ORIGINAL/BOX-AMBIGUOUS ROW: Q4 (0.1566) is slightly BELOW flat projection (0.1616) while
Q8 and Q16 are above it. Four levels is coarse enough to act partly as a distortion on that stratum,
which is the same failure mode as the rank variant, in milder form.

CHECKPOINT: CP28_classifier_refreeze   GAP: two cited classifiers cannot be reproduced from the record.
STATUS: DONE. THE PARTITION IS REFROZEN AND REPRODUCES. THE RANDOM FOREST IS A THIRD NON-RECOVERY:
        a refit under the recorded protocol gives 188/210, and NO reading of the recorded prose
        reproduces the published 186/210. Forward reproducibility is fixed; the historical value is not
        recovered. One published significance verdict CHANGES as a result.

=================  THE RANDOM FOREST  ==========================================================
The 19-feature specification WAS recorded (CP8 finding.md) and is quoted verbatim in
classifier_specifications.json. What was never recorded is the exact arithmetic form of three of the
features. Refitting on 1610 train / 210 eval, n_estimators=500, seed 23:
  CANONICAL REFROZEN VALUE           188/210 = 0.8952   macro-F1 0.8952   train acc 1.0000
The canonical form fixes "three scale-free EDGE RATIOS" as ratios of SORTED edge lengths, and the
angle/edge dispersion features as POPULATION standard deviations. The sorted form is justified by the
ARGUMENT that a scale-free descriptor must be invariant to axis LABELLING, which is a property of the
feature and not of its score.
CORRECTION TO AN EARLIER VERSION OF THIS PARAGRAPH, WHICH OVERCLAIMED MY OWN PROCESS. It previously said
the choice "was fixed before the variant grid was read." THAT IS FALSE and the transcript shows it: the
grid cell computed and PRINTED all twelve variants ranked by score, with both sorted variants tied at the
top (188/210), and only the next cell selected the canonical form. So the ranking was visible when the
selection was made. The invariance argument stands on its own merits and does not depend on the ordering,
but I cannot claim the selection was blinded, and describing it as blinded made a stronger reproducibility
claim than the record supports. What IS true: the canonical form is now specified exactly, so every future
recomputation is deterministic; and the sorted-vs-unsorted choice happens to be the top-scoring one, which
a reader should know rather than have hidden behind a blinding claim.
HOW TO DO THIS PROPERLY NEXT TIME: state the selection rule in the pre-registration, before the grid runs.
A rule stated after the scores are visible is a justification, not a pre-commitment, and the two must not
be described in the same language.
SENSITIVITY, AND WHY THIS IS A NON-RECOVERY. Twelve defensible readings of the recorded prose
(edge-ratio form x angle_std ddof x edge_cv ddof) span 183 to 188 of 210 — five structures. NONE
reproduces the published 186/210. 187 is reachable, but only under an angle-SD convention the record
does not state. So the refreeze makes every FUTURE recomputation exact and leaves the historical
0.8905 and 0.8857 both unrecovered.
A COLLISION WORTH NAMING. The plain-ratio variant gives 184/210 = 0.8762, numerically identical to the
recorded GRADIENT BOOSTING value. They are different models: GB under this protocol gives 183/210.
Anyone matching values across the ledger by number alone would conflate them.
DECISION RULE APPLIED. |0.8952 - 0.8857| = 0.0095, inside the pre-registered 0.02 band, so the
refrozen value is canonical and 0.8905 goes to a footnote as the unreproducible original.

=================  THE BOX-SUFFICIENCY PARTITION  ==============================================
CP25's predicate is adopted as canonical and its exact source is now in the ledger: 2% on lengths,
1 degree on angles, and a monoclinic branch that does NOT fire when beta is also ~90 (that is an
orthorhombic metric). It reproduces CP25's 140/70 on the original eval set EXACTLY, with ambiguous
composition {hexagonal_or_trigonal 60, tetragonal 4, cubic 3, orthorhombic 2, trigonal_rhombohedral 1}.
ONE-STRUCTURE DISAGREEMENT ON THE EXPANSION SET, STATED RATHER THAN TUNED AWAY. The canonical
predicate gives 141/69 where CP15's replication recorded 140/70. The recorded composition lists one
monoclinic ambiguous entry; under this predicate every monoclinic-metric structure in that set has
monoclinic truth, so no monoclinic entry can be ambiguous. I did not adjust tolerances to force
agreement — CP25 already established that CP15's exact rule is unrecoverable by a 50-combination grid.

=================  RECOMPUTED STRATIFIED ROWS, ORIGINAL EVAL, CANONICAL 140/70  ================
  arm                      sufficient   ambiguous     drop   Fisher p   counts
  A3 native-res K=8          0.7000      0.6714     +0.0286   0.7518    98/140, 47/70
  B1 direct K=8              0.6571      0.5429     +0.1143   0.1318    92/140, 38/70
  V2b chain K=8              0.3643      0.4143     -0.0500   0.5471    51/140, 29/70
  B3 chain K=8               0.1857      0.4714     -0.2857   0.0000    26/140, 33/70
  RF refrozen                0.9214      0.8429     +0.0786   0.0957   129/140, 59/70

A PUBLISHED SIGNIFICANCE VERDICT CHANGES, AND THE PRE-REGISTRATION REQUIRED PUBLISHING IT.
CP15 published B1's stratified drop as +0.1510 at p = 0.037 on the 137/73 split. On the canonical
predicate it is +0.1143 at p = 0.1318 — NO LONGER SIGNIFICANT. This is not a robustness check that
came out badly; it is the primary value under the canonical partition, and it makes the
ORIGINAL-sample leg of the stratified claim a FOURTH independent failure, alongside the expansion-set
sign reversal, the A3 null, and the RF control inversion.
THE B3 CHAIN ARM RUNS THE OTHER WAY, strongly: -0.2857 at p = 3e-05, better on AMBIGUOUS structures.
That is the opposite of the mechanism CP15 proposed and is not explained by it. Recorded as an open
observation, not folded into the claim.

=================  WHAT THIS DOES NOT ESTABLISH  ==============================================
Nothing in the paper becomes stronger because a classifier was refrozen. The purpose is that a
reviewer recomputing any stratified row now gets the published number. The RF remains a non-recovered
historical value with a reproducible replacement.

CHECKPOINT: oracle_stratified   GAP: is the information in box-ambiguous structures PRESENT and
                                     VISIBLE but UNUSED, or genuinely absent? (directive section D)
STATUS: DONE, AND NOW SUPERSEDED AS THE HEADLINE BY oracle_within_sample, which runs the same oracle ON the
        evaluation sets and makes the comparison within-sample and paired. Read oracle_within_sample first. The
        cross-sample result below stands as recorded, with two corrections added at the end.
STATUS (original): DONE. THE PRE-REGISTERED BRANCHES DO NOT FIRE CLEANLY and the honest answer is between them.
        The oracle recovers box-ambiguous structures at 0.8554 — high, but SIGNIFICANTLY below its
        0.9695 on box-sufficient (p = 0.0009). So the information is MOSTLY present, not fully.

=================  THE RESULT  ===============================================================
Oracle (ideal extraction, triangulated) on its own 280-structure sample, split by the SAME
conventional-cell metric rule box_sufficiency uses. Box-sufficient 197 (0.704), box-ambiguous 83.
  views   box-sufficient        box-ambiguous       difference   Fisher p
    2     0.9188 (181/197)      0.3253 ( 27/83)      -0.5935     <1e-4
    3     0.9645 (190/197)      0.7952 ( 66/83)      -0.1693     <1e-4
    4     0.9695 (191/197)      0.8554 ( 71/83)      -0.1141      0.0009
    5     0.9695 (191/197)      0.8675 ( 72/83)      -0.1021      0.0022
The stratum gap is present at every view count and is not a single-view-count artifact. It SHRINKS
monotonically with views (0.594 -> 0.169 -> 0.114 -> 0.102): most of the box-ambiguous deficit is
resolved by adding views, and what remains is small but real.

BRANCH READING, HONESTLY. V1 required the difference to be within ~0.10 AND non-significant. It is
0.1141 and p = 0.0009, so V1 DOES NOT FIRE. V2 ("the oracle also fails") is equally wrong: 0.8554 is
high in absolute terms and far above every pixel model. V3 (inversion) does not apply. The result sits
between the pre-registered branches, and I am reporting it that way rather than rounding it into V1.

=================  WHAT THIS DOES AND DOES NOT LICENSE  ======================================
LICENSED. On the box-ambiguous stratum: ideal extraction reaches 0.8554, the BEST pixel model reaches
0.6575 (A3_native_K8, the native-resolution retrained arm), the next best reaches 0.5205
(B1_direct_K8), and the shape-free floor is 0.4932. So 0.1979 of accuracy is available on that stratum
to a reader with the same views but perfect atom localisation, over and above the best pixel model —
0.3349 over the next best, and 0.3622 over the floor.
CORRECTION: an earlier version of this record named 0.5205 as "the best pixel model" while carrying the
delta 0.1979, which is arithmetically inconsistent (0.8554-0.5205=0.3349). The delta was computed
correctly from the true maximum; only the quoted value was wrong. It propagated into REPORT.md before
being caught, and it survived a verification pass that checked whether the figure APPEARED in the text
rather than re-deriving it from the source table — the same failure mode recorded in paired_resolution. Combined with occlusion_redundancy's finding that box-ambiguous structures are LESS
informatively occluded than average, the information there is mostly present and better-than-average
visible, and models are not using it. That is a localization statement.
NOT LICENSED — and these caveats are load-bearing, not decoration:
  (1) TWO DIFFERENT SAMPLES. The oracle's 280 structures have ZERO OVERLAP with the 210-structure
      evaluation set carrying the model numbers, and draw on a different source mix (140 MP + 140
      JARVIS vs MP-only). The bracket is assembled across samples and can never be stated as a
      per-structure claim.
  (2) THE MODEL LEG DID NOT REPLICATE. box_sufficiency item 3: on the expansion set the box-ambiguous drop
      REVERSED SIGN (+0.1510 -> -0.0500, p = 0.557) and the RF control became the only significant
      dropper. Any "models fail where the oracle succeeds" claim inherits that non-replication and
      must carry it in the same sentence.
  (3) A 0.1141 SIGNIFICANT DEFICIT means the render does lose something on this stratum even given
      perfect extraction. "Fully present" is false; "mostly present" is what the data support.
  (4) PERFECT ATOM LOCALISATION is assumed throughout. This bounds what is recoverable GIVEN
      extraction, never what is recoverable from pixels.
CONSEQUENCE FOR THE PROPOSED FOLLOW-ON PROBE. The directive gates a two-stage-prompt probe on D showing
"visible but unused". D shows "mostly present, better-than-average visible, and a ~0.20 gap to the best
pixel model" — a weaker premise than the gate assumed, on a stratum whose model result did not
replicate. The probe is defensible as an exploratory API-only experiment; it is NOT the confirmatory
test the directive's framing implies, and it must be pre-registered as exploratory if run.

=================  CORRECTION 1: THE PARTITION RATE WAS NEVER A DISCREPANCY  ==================
The oracle sample is 197/280 = 0.7036 box-sufficient against the evaluation set's 137/210 = 0.6524.
Fisher exact p = 0.2407 — within sampling noise. This needed no source-mix explanation and should not
have been framed as something requiring one. The sample-disjointness flag on the ACCURACY comparison
was a separate and legitimate concern, now resolved by oracle_within_sample.

=================  CORRECTION 2: THE STRATUM COMPOSITIONS DO DIFFER, AND IT MATTERED  =========
The evaluation set's ambiguous stratum is 61/73 = 83.6% trigonal/hexagonal metric. The ORACLE sample's
is 80/83 = 96.4% (80 hexagonal_or_trigonal + 3 tetragonal, no monoclinic, orthorhombic or cubic).
Fisher exact p = 0.0120 — the compositions DIFFER significantly.
CONSEQUENCE FOR THE CROSS-SAMPLE READING: part of the 0.1979 gap was composition rather than unread
information, exactly as a reviewer would have suspected. This is a real defect in the cross-sample
bracket, and it is why oracle_within_sample's within-sample computation was the right call rather than an optional
tidy-up. oracle_within_sample supersedes this reading; the numbers here remain as the record of what was computed.

=================  THE IMPLIED RESULT THIS CHECKPOINT DERIVES BUT DID NOT WRITE  ==============
The native-resolution arm (A3) shows NO stratum drop. On the original evaluation set: overall 0.6905,
box-sufficient 0.7000 (n=140), box-ambiguous 0.6714 (n=70), drop +0.0286, Fisher p = 0.7518 — not
significant. (Split from my reproduced classifier at 140/70; see oracle_within_sample for why box_sufficiency's exact 137/73 is
not recoverable. The conclusion does not turn on the 3-structure difference.)
THAT IS A THIRD INDEPENDENT INSTANCE of the stratified-accuracy claim failing, after the expansion-set
non-replication and the RF control becoming the only significant dropper there. Three instances is no
longer a replication failure to explain away; it is the result. A reviewer can derive this from numbers
already in the package, so omitting it would read badly.

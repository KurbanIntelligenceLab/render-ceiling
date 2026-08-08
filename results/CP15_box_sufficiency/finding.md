CHECKPOINT: CP15_box_sufficiency   GAP: do the models read the drawn CELL BOX rather than the
                                   atom MOTIF? (settles CP13's question without a human arm)
STATUS: DONE, THEN PARTLY OVERTURNED BY ITS OWN REPLICATION. Read the REPLICATION section
        at the end before citing anything above it. Zero compute — computed from per-structure predictions already on disk. This is the
        strongest mechanistic result in the package: every pixel-input model collapses to the
        regularity floor on structures whose cell box cannot disambiguate the crystal system, while
        no non-pixel baseline drops at all.

=================  THE STRATIFICATION  =================
A structure is BOX-SUFFICIENT if the metric of the CONVENTIONAL cell — the cell the renders
actually draw — uniquely implies its crystal system, and BOX-AMBIGUOUS otherwise. Computed on all
210 eval structures with tolerances 2% on lengths, 1 deg on angles.
    BOX-SUFFICIENT 137/210 = 0.6524      BOX-AMBIGUOUS 73/210 = 0.3476
This is the RIGHT quantity and neither previously recorded number was it: CP8's 113/210 = 0.538 was
computed on the STORED INPUT cells (often primitive, not what is drawn), and CP11's 41/50 = 0.820
was the 50-structure expert packet, not the eval set.
WHAT MAKES A STRUCTURE AMBIGUOUS — 60 of the 73 are the trigonal/hexagonal pair, which shares
a=b, gamma=120 deg in the conventional hexagonal setting, so the box cannot separate them at any
tolerance. The remainder are near-degenerate metrics (4 tetragonal, 3 monoclinic, 3 cubic,
2 orthorhombic, 1 rhombohedral-setting trigonal).

=================  RESULT: EVERY PIXEL MODEL COLLAPSES, NO NON-PIXEL BASELINE DOES  ===========
  arm                      box-sufficient  box-ambiguous     drop    Fisher p   vs floor-on-amb
  gemini-3.6-flash (K=3)       0.8540          0.5068       +0.3472   1.7e-07      +0.0137
  grok-4.5 (K=3)               0.6788          0.4932       +0.1857   0.0112      +0.0000
  B1-direct, ours (K=8)        0.6715          0.5205       +0.1510   0.0372      +0.0274
  claude-opus-4.8 (K=3)        0.6350          0.4795       +0.1556   0.0395      -0.0137
  ---
  RF, 19 lattice features      0.9124          0.8356       +0.0768   0.113 n.s.   +0.3425
  REGULARITY FLOOR, 3 feats    0.5474          0.4932       +0.0543   0.471 n.s.    0.0000
  A3 native+aug (K=8)          0.7080          0.6575       +0.0505   0.531 n.s.   +0.1644
  SFT-V1 chain (K=8)           0.3504          0.4658       -0.1154   0.137 n.s.
  V2b chain (K=8)              0.3723          0.3973       -0.0250   0.766 n.s.
  B3 outcome chain (K=8)       0.1898          0.4521       -0.2623   9.3e-05  (INVERTED)

ALL FOUR PIXEL-INPUT VLMs LAND WITHIN 0.028 OF THE FLOOR on the ambiguous stratum (floor there is
0.4932), and all four drops are significant. Gemini's entire advantage over our arm is on
box-SUFFICIENT structures: it is the best model on the stratum where the box suffices (0.8540) and
indistinguishable from a three-feature shape-free baseline where it does not (0.5068 vs 0.4932).

THE CONTROL THAT MAKES THIS A MECHANISM RATHER THAN A DIFFICULTY ARTIFACT. If box-ambiguous
structures were simply "harder", every model would drop. They do not:
  - The RF reads the same cell NUMERICALLY rather than as pixels and does NOT drop significantly
    (+0.0768, p = 0.113), staying 0.34 above the floor on the ambiguous stratum. The information
    needed to classify these structures IS present in the cell parameters; what fails is reading
    them off a drawing.
  - The floor itself does not drop (p = 0.471), so the strata are not separated by the size/density
    regularities the floor exploits.
  - The chain arms do not drop either, because they were never above the floor to fall from. B3
    INVERTS (-0.2623, p = 9.3e-05): it is worse on box-sufficient structures, which is what a model
    that is not reading the box at all looks like.

WHAT THIS ESTABLISHES, AND WHAT IT REPLACES. The claim "these models read the cell box and not the
atom motif" is now established on all 210 structures with a mechanism, rather than inferred from a
single confusion pair. It also explains CP13's mirrored failure: the trigonal/hexagonal pair is 82%
of the ambiguous stratum, so two arms collapsing it in OPPOSITE directions is the expected
signature of models that read the outline well and the motif poorly — which way they collapse is
then set by their prior, not by the image. CP13 and CP15 are one result and should be one section.
NO HUMAN ARM IS REQUIRED for this. The question CP11 was built to answer — is the failure the
models' or the renders' — is answered for the box-ambiguous stratum by the RF control: the
information is in the cell, and the pixel models do not extract it.

WHAT IT DOES NOT ESTABLISH. That the motif is unreadable in principle — the oracle (CP0b) recovers
93.6% of crystal systems from four views under ideal atom extraction, so the motif information is
present in the renders. The gap between 0.9357 (ideal extraction) and ~0.50 (pixel models on the
ambiguous stratum) is the extraction failure, and localising it is what the deterministic extractor
(item 4) is for.

REPRODUCE
  conventional_cell(structure) -> lattice metric class with tol 2% length / 1 deg angle;
  BOX-SUFFICIENT iff the class pins one system (hexagonal-vs-trigonal never does).
  Per-arm strata from the per-structure prediction files; between-strata test is Fisher exact
  (different structures, so unpaired); floor and RF regenerated with the recorded protocol
  (train on the 1610 train structures, test on the 210 eval; RF n_estimators=500, seed 23).

=================  TWO ARITHMETIC AUDITS, BOTH TRACED  ========================================
Raised because a reviewer recomputing the tables would hit them.

(a) THE GNN ROW 0.4889 DOES NOT SIT ON /210, AND CORRECTLY SO. 0.4889 x 210 = 102.669. It is a
    THREE-SEED MEAN of 0.4286 / 0.4952 / 0.5429, each of which IS an exact integer count on 210
    (90, 104, 114). A mean of three integer counts need not be an integer, so the row is right and
    the denominator note is what was missing. It must be labelled as a 3-seed mean, not presented
    alongside single-run counts as though it were one.
    A suspected carry-across was checked and EXCLUDED: 0.4889 also appears in CP3 as an outcome-arm
    silent-group rate, but the GNN value traces independently to its own three seeds in
    cgcnn_style_3seed.json, so the coincidence is just a coincidence.
    Note also the SD: the file records 0.0469, which is the POPULATION sd of those three seeds; the
    sample sd is 0.0574. Project convention is population sd, so 0.0469 is correct as recorded, but
    the two differ enough to matter and the convention should be stated where the value is quoted.

(b) THE RF STRATIFICATION SUMS TO 186, NOT THE HEADLINE 187 — AND THE CAUSE IS NOT A STRATUM BUG.
    0.9124 x 137 = 125 and 0.8356 x 73 = 61, summing to 186. Every OTHER arm reconciles exactly
    against its headline (Gemini 117+37=154, direct 92+38=130, Grok 93+36=129, Opus 87+35=122,
    floor 75+36=111, chain 51+29=80, A3 97+48=145). Recomputing the RF strata from the
    per-structure vectors gives exactly 125 + 61 = 186 = 0.8857.
    0.8857 IS THE REPRODUCED RF, not the recorded one. The recorded headline 0.8905 = 187/210 comes
    from the original CP8 run, whose exact 19-feature list was never written down (documented as a
    reproducibility gap in CP16). The stratification was computed on the REPRODUCED classifier, so
    it is internally consistent with 186/210 and differs from the headline by exactly the one
    structure that gap accounts for.
    FIX APPLIED: the stratified RF row is labelled as the REPRODUCED classifier (0.8857 = 186/210,
    125/137 sufficient and 61/73 ambiguous) and is NOT presented as a decomposition of the 0.8905
    headline. No conclusion changes — the RF's non-drop (+0.0768, p = 0.113) is unaffected by one
    structure, and it remains the modality-matched control that makes the stratification a mechanism.

=================  DE-CONCENTRATION TEST (directive item 2): THE MECHANISM SURVIVES  ==========
The concern is fair: 60 of 73 ambiguous structures (82.2%) are the trigonal/hexagonal metric class,
so as written the claim could rest on one confusion pair. Composition of the ambiguous stratum:
  hexagonal_or_trigonal 60 (82.2%) | tetragonal 4 | monoclinic 3 | cubic 3 | orthorhombic 2 |
  trigonal_rhombohedral 1
Excluding that class leaves n=13 (true systems: 5 triclinic, 3 orthorhombic, 3 tetragonal,
2 monoclinic). Floor on those 13 = 0.3077.
  arm                  sufficient(137)   residual-13   drop     Fisher p
  gemini-3.6-flash        0.8540           0.0000     +0.8540   3e-10
  grok-4.5                0.6788           0.3077     +0.3711   0.0127
  claude-opus-4.8         0.6350           0.3077     +0.3273   0.0344
  B1-direct (ours)        0.6715           0.4615     +0.2100   0.1396  n.s.
  RF (control)            0.9124           0.8462     +0.0663   0.3477  n.s.
THE PATTERN IS NOT PAIR-SPECIFIC: three of four pixel models drop significantly on the residual 13
and the RF control still does not. HONEST LIMITS AT n=13, where one structure is 7.7 points:
Gemini's 0.0000 is 0/13 and must not be read as "never"; B1's drop is NOT significant here
(p = 0.1396) though the point estimate is in the same direction; and the FLOOR also falls on these
13 (0.5474 -> 0.3077, p = 0.145), so they are harder for everything — which is exactly why the RF
control, not the raw drop, is the load-bearing comparison.

=================  REPLICATION ON THE EXPANSION SET (item 3): THE MECHANISM DOES NOT REPLICATE  ==
Box-sufficiency itself replicates almost exactly on the 210 NEW structures despite their very
different composition (median 22 vs 14 conventional atoms): 140/210 = 0.6667 sufficient against
137/210 = 0.6524, with the ambiguous stratum again 82.9% trigonal/hexagonal. So the CUE-SUFFICIENCY
PARTITION is a stable property of the render convention.
THE STRATIFIED ACCURACY PATTERN DOES NOT.
  arm            original drop    p        expansion drop    p
  B1-direct         +0.1510     0.037         -0.0500      0.557
  V2b chain         -0.0250     0.766         -0.0429      0.554
  RF (control)      +0.0768     0.113         +0.1643      0.002
  floor             +0.0543     0.471         +0.0286      0.736
Two things invert. B1's drop REVERSES SIGN and loses significance. And the RF — the
modality-matched control whose whole job is NOT to drop — becomes the ONLY arm that drops
significantly. The original reading ("pixel models collapse toward the floor where the box is
uninformative; a numeric reader of the same cell does not") is therefore NOT supported on the second
sample.
WHY, AND IT IS THE FLOOR AGAIN. The floor collapsed on this sample (0.5286 -> 0.2476 overall,
0.2286 on the ambiguous stratum), so "collapses to the floor" has no content here: the floor now
sits far BELOW every model and there is nothing to collapse to. B1 on the expansion ambiguous
stratum is +0.257 ABOVE the floor there, where in the original it sat within 0.027 of it. This is
the same floor sample-sensitivity documented in CP18, now shown to break a MECHANISM claim and not
only a threshold comparison.

WHAT MAY AND MAY NOT BE CLAIMED, REVISED.
  MAY: the cue-sufficiency partition is well defined, deterministic, and replicates across two
       independently drawn samples (0.6524, 0.6667), with the ambiguous stratum dominated by the
       trigonal/hexagonal pair in both (82.2%, 82.9%).
  MAY: on the ORIGINAL 210-structure sample, all four pixel models sit within 0.028 of the floor on
       the ambiguous stratum while the RF does not drop, and this survives excluding the dominant
       confusion pair.
  MAY NOT: that pixel models generally collapse toward the regularity floor on box-ambiguous
       structures. That is a claim about the original sample only; it fails on the expansion set,
       where B1's drop reverses and the control drops instead.
  The paper must present the stratification as a SAMPLE-SPECIFIC finding with an explicit failed
  replication, or reframe it around the partition itself (which does replicate) rather than around
  the accuracy pattern (which does not). It must not be presented as the paper's strongest result
  without that qualification.

RECONCILIATION [0.9321 -> 0.9357: the CP0b harness was rerun to record box-sufficiency per row; the rerun's 4-view value is 0.9357 (262/280) against the original 0.9321 (261/280). One structure of 280; the harness draws from a LIVE database so the seed fixes draw order, not the candidate pool. 0.9357 is the current value.]

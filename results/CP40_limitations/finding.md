CHECKPOINT: CP40_limitations   GAP: limitations are scattered across 36 checkpoint records with no single
                               list a reviewer can read. (ICLR plan, Phase F)
STATUS: DONE. TEN LIMITATIONS, each with its consequence for what may be claimed. Three are inherent or
        standing, four are disclosed-and-mitigated, two are named at every mention, and ONE IS OPEN.

L1  NO HUMAN EXPERT BASELINE. The 50-structure study was never fielded; the single returned sheet scored
    18% and was rejected because its answer pattern showed the respondent was not reading the images.
    CONSEQUENCE: "harder than humans find it" is claimed NOWHERE. Standing limitation, not chased.
L2  TWO CLASSIFIERS NOT REPRODUCIBLE FROM THE RECORD. The RF's published 186/210 is unreachable under
    twelve readings of its recorded prose; CP15's partition rule is unrecoverable by a 50-combination
    grid. MITIGATED FORWARD: RF republished at a refrozen 188/210, historical values footnoted, and the
    canonical predicate reproduces 140/70 exactly.
L3  THE ORACLE READS GROUND-TRUTH COORDINATES. A zero visibility correction makes the ceiling a tighter
    bound on structure-side identifiability and says nothing about pixel-side achievability. INHERENT.
L4  THE DETECTOR IS WEAK BY CONSTRUCTION — watershed, colour unmixing and learned detectors never
    attempted. The extraction failure is characterised (visibility and segmentation, not precision) but
    NOT bounded.
L5  THE SWEEP RAN TWICE through an aggregation defect. The second run is kept as an unplanned
    replication with its spread published. CONSEQUENCE: adjacent leaderboard rows are NOT separable.
L6  THE FLOOR IS SAMPLE-SPECIFIC, 0.5286 original against 0.2476 expansion, and the thirteen models ran
    on the original sample only. The below-floor result cannot be restated sample-free.
L7  K=3 FOR ZERO-SHOT ROWS, K=8 FOR THE FINE-TUNED REFERENCE. K is printed on every row; the same
    adapter at K=3 is 139/210.
L8  PARAMETER COUNTS ARE UNDISCLOSED for some evaluated models, and total vs active are separate axes
    with no cross-family ordering. Only the negative claim is supported.
L9  THE PRIOR-ART AUDIT IS INCOMPLETE — eight named rows done, three instruments unsearched. OPEN, and
    it gates any claim resting on them.
L10 V2B'S TRUE SEED SPREAD IS UNKNOWN. The recorded 0.000 SD is decode collapse, not stability, and the
    real spread was not estimated. No interval asserted.

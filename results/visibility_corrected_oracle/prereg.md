PRE-REGISTRATION — visibility_corrected_oracle visibility-corrected oracle   (ICLR plan, Phase B)
Committed BEFORE any condition is run. CPU only, deterministic, no API spend, no GPU.

GAP. atom_detection states it: the oracle assumes perfect centroid extraction of ALL atoms, so 0.9524 bounds
identifiability from the STRUCTURE, not from the IMAGES. No instrument in the package separates how much
of the perception deficit the rendering convention imposes from how much the model imposes.

PREREQUISITE, NOT FREE. atom_detection covers 28 structures and occlusion_redundancy covers 40 per set, both on the THREE AXIS
VIEWS only, while the oracle uses 4 or 5 cameras. The orbit-based occlusion classification must first be
extended to 210 structures per set across ALL FIVE views. Geometry only, no detector.

METHOD. Run the oracle_within_sample oracle UNCHANGED on per-view centroid sets with occluded detections removed.
Removal is PER VIEW, not global: an atom hidden down axis_c may be visible from body_diagonal, and
triangulation needs only two views. Redundancy is decided by space-group orbit (spglib equivalent_atoms,
symprec 1e-3) — the corrected rule occlusion_redundancy adopted after the integer-translate rule was found to undercount
centred lattices.

FOUR CONDITIONS, both eval sets, 4 and 5 views:
  O0  all detections present            reproduces oracle_within_sample — harness check
  O1  informative occlusion removed     the target condition
  O2  all occlusion removed             upper bound on visibility cost
  O3  redundant occlusion only removed  the control
Report crystal system primary, plus point group, space group and count_match, since the oracle fails
through OVER-TRIANGULATION on dense cells (identifiability, mp-1229124).

SECOND READOUT, free once the extension runs. Partition atoms into informatively occluded in NO view,
SOME views, ALL views. Only the last is unrecoverable from the frozen view set. Never computed, and it is
the quantity that actually bounds identifiability from the images.

DECISION RULE, fixed now.
  - Primary quantity is O0 minus O1 per eval set, paired per structure, McNemar exact.
  - O3 GOVERNS INTERPRETABILITY: if the O0-minus-O3 delta reaches HALF the O0-minus-O1 delta, the
    analysis is measuring DETECTION COUNT rather than information and O1 CANNOT be read. That is a
    stop, not a caveat.
  - If O0 does not reproduce oracle_within_sample to within ONE structure, nothing else is scored.

WHAT WOULD MAKE A CONDITION UNINFORMATIVE.
  - Any condition failing triangulation on >5% of structures is reported with its failure rate and NOT
    scored. oracle_within_sample recorded zero exceptions at O0.
  - Removing detections can produce SPURIOUS cross-view matches. Report the over-triangulation rate per
    condition alongside count_match; a condition whose over-triangulation rate exceeds O0's by more than
    5 points is measuring correspondence failure, not visibility.
  - The overlap covariate is ORDINAL ONLY. atom_detection's "1 - overlap" ceiling was withdrawn after 6 of 84
    measurements exceeded it. No ceiling arithmetic is performed on it here.

EXPECTED FINDING, WORTH STATING EITHER WAY. occlusion_manipulation attributes mean 0.2363 of total occlusion to exact
projective coincidence from supercell copies viewed down a lattice vector. The three axis views ARE that
worst case; body_diagonal and oblique2 are not. Every occlusion figure in the package to date is measured
on the three worst cameras, so the 0.18-0.20 informative estimate probably OVERSTATES what five views
withhold. If the five-view extension lowers it, that is a result about the render protocol, not a
weakening of the analysis.

SCOPE. This corrects for MEASURED visibility. It does NOT show that a model could perform the extraction,
and no such claim is licensed by any outcome here.

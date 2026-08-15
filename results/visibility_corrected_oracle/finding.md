CHECKPOINT: visibility_corrected_oracle   GAP: the oracle assumes perfect centroid extraction of
   ALL atoms, so 0.9524 bounds identifiability from the STRUCTURE, not the IMAGES. (ICLR plan, Phase B)
STATUS: DONE. THE PRIMARY QUANTITY IS EXACTLY ZERO ON BOTH EVAL SETS, AND THE O3 CONTROL BLOCKS THE
        TARGET CONDITION ANYWAY. Removing informative occlusion changes NOT ONE classification, while
        the redundant-only control removes 6 to 21. Both pre-registered stops fire. The visibility
        correction the plan was built around does not exist to be measured — and the reason is a
        result about the render protocol.

=================  THE PREREQUISITE, WHICH IS ITSELF THE HEADLINE  =============================
The orbit occlusion classification was extended from atom_detection's 28 and occlusion_redundancy's 40 structures on THREE AXIS
VIEWS to 210 structures per set across ALL FIVE views, 0 errors.
  view              occluded  redundant  informative      (original eval, means)
  axis_a             0.5548     0.4816      0.0732
  axis_b             0.5435     0.4486      0.0949
  axis_c             0.5967     0.4322      0.1646
  body_diagonal      0.2000     0.0200      0.1800
  oblique2           0.1386     0.0208      0.1178
THE PRE-REGISTERED PREDICTION IS CONFIRMED AND LARGER THAN STATED: the three axis views carry 3.34x
(original) and 2.25x (expansion) the occlusion of the two oblique views. EVERY occlusion figure
published in this package before this extension was measured on the three worst cameras in the protocol.

=================  THE SECOND READOUT OVERTURNS OUR OWN CEILING FRAMING  =======================
Triangulation needs TWO clear views, so the identifiability bound is not the per-view informative mean —
that counts an atom once per occluding view. Partitioning atoms by how many views informatively occlude
them, at 5 views:
  informatively occluded in NO view   0.5407 (original)   0.4474 (expansion)
  in SOME views                      0.4592              0.5520
  in ALL views                       0.0001              0.0007
  atoms with FEWER THAN 2 CLEAR VIEWS 0.0026              0.0087
UNDER ONE PERCENT of atoms are untriangulable from the frozen view set. The "~0.18-0.20 effective
visibility deficit" this project published two passes ago is a PER-VIEW quantity and MUST NOT be read as
a ceiling on what the images afford. That is a correction to our own framing, produced by the plan's own
free readout.

=================  THE FOUR CONDITIONS  ========================================================
Harness check first: with nothing removed the conditioned oracle reproduces oracle_within_sample EXACTLY — 200/210
original, 191/210 expansion, zero over-triangulation, zero errors. The pre-registered gate required
agreement within one structure. An earlier version of the harness scored 198 and 185 because it
generated candidates from every view pair rather than oracle_within_sample's anchor pair; that is a DIFFERENT acceptance
rule, the gate caught it, and the harness was corrected before any condition was read.
  condition                              original 5v      expansion 5v
  O0 all detections present              200/210 0.9524   191/210 0.9095
  O1 informative occlusion removed       200/210 0.9524   191/210 0.9095
  O2 all occlusion removed               122/210 0.5810   113/210 0.5381
  O3 redundant occlusion only removed    194/210 0.9238   170/210 0.8095
4-view values are identical to 5-view for O0/O1/O2 and within 2 for O3.

=================  BOTH PRE-REGISTERED STOPS FIRE  =============================================
PRIMARY QUANTITY O0 minus O1: ZERO structures on both sets. Paired McNemar: O0-only 0, O1-only 0,
p = 1.0000. There is no visibility correction to apply.
O3 CONTROL: |O0 - O3| is 6 (original) and 21 (expansion) against |O0 - O1| = 0. The pre-registered rule
was that if the O0-O3 delta reaches HALF the O0-O1 delta, the analysis is measuring DETECTION COUNT
rather than information and O1 cannot be read. With O1's delta at zero and O3's at 6-21, the control
dominates the target completely. O1 IS UNREADABLE BY THE RULE FIXED BEFORE THE RUN.

=================  WHY, AND THE FALSIFICATION I RAN AGAINST MYSELF  ============================
The natural objection is that the masks never reached the reconstructor. They did:
  O1 hides 548 of 16740 site-view slots (3.27%); O2 hides 3067 (18.32%); O3 hides 889 (5.31%).
  Of 40 structures, 38 have at least one site hidden under O1, and 7 of those changed n_recovered.
So the removals are real and do perturb reconstruction — they simply do not change SYMMETRY recovery.
THE MECHANISM IS SUPERCELL REDUNDANCY. A site is observable in a view when ANY of its 2x2x2 = 8 copies
is unoccluded there. Informative occlusion hits few copies of a given site, so a site almost never goes
dark; and with five cameras, losing one or two still leaves the two that triangulation needs. Redundant
occlusion is both more common and more correlated across copies, which is why O3 — the CONTROL — is the
condition that actually removes structures.
O2 IS THE INFORMATIVE NUMBER HERE: removing ALL occlusion costs 78 structures (0.9524 -> 0.5810). So
visibility does matter to this oracle in the aggregate; what does not matter is the INFORMATIVE
component specifically, which is the component the plan proposed to correct for.

=================  WHAT THIS MEANS FOR THE PAPER  =============================================
The plan's claim 2 and claim 3 CANNOT be built as written. There is no corrected ceiling distinct from
the ideal ceiling, so "corrected minus best-arm" and "ideal minus corrected" are the same number and
the promised separation of render-imposed from model-imposed deficit collapses.
WHAT SURVIVES, AND IT IS PUBLISHABLE AS MEASUREMENT: the frozen five-view protocol withholds almost
nothing (under 1% of atoms untriangulable); the axis views are 2-3x more occluded than the oblique ones,
so the protocol's own worst cameras drove every previous occlusion figure; and the full ideal-extraction
gap to the best model arm stands unreduced, because the visibility correction is zero.

=================  WHAT THIS DOES NOT ESTABLISH  ==============================================
Nothing here shows a MODEL could perform the extraction. The oracle reads ground-truth coordinates
throughout. A zero visibility correction makes the ideal ceiling a TIGHTER bound on structure-side
identifiability, not evidence about pixel-side readability.
The overlap covariate remains ORDINAL only; no ceiling arithmetic was performed on it.

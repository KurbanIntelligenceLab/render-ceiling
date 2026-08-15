CHECKPOINT: identifiability   GAP: premise for flagship label   STATUS: done (Gate 0 provisional pending human arm)

METHOD DONE: Tool-oracle identifiability study. For a stratified sample of 280
structures (140 Materials Project + 140 JARVIS-DFT, 20 per crystal system per
source, 2-40 sites), reconstructed 3D atom positions from the rendered multi-view
projections and ran spglib on the reconstruction, scoring recovery at three
hierarchy levels (crystal system, point group, space group) as a function of view
count {2,3,4,5}. The reconstructor inverts render.py's exact orthographic camera
matrices (screen = pos @ R, depth dropped) and re-solves cross-view atom
correspondence from element identity + ray geometry ALONE (correspondence is NOT
given — that is what projection overlap destroys, the screw-axis/glide blind spot the
plan warns of). Lattice taken as known (unit-cell edges are drawn). The oracle
therefore measures identifiability under PERFECT centroid extraction — an upper
bound on what any VLM could read from the view set. A separate small-noise arm
(0.03A, 4 views) is reported as a reconstruction-stability caveat only.

RESULT DONE: Oracle recovery (micro), ideal extraction, by view count:
             crystal_sys  point_grp  space_grp   count_match
   2 views      74.3%       64.6%      41.1%        26.1%
   3 views      91.4%       83.6%      74.3%        67.9%
   4 views      93.6%       91.4%      90.7%        98.9%
   5 views      93.9%       91.8%      91.1%        99.6%
TABLE REFRESHED FROM THE CURRENT results.json (2026-07-29). The harness was rerun to record the
box-sufficiency classification per row for oracle_stratified, which also added the 5-view column. The original
table read 73.9 / 90.7 / 93.2% at 2/3/4 views; the rerun reads 74.3 /
91.4 / 93.6%. The differences are 1-2 structures out of 280
and arise because the harness draws from a LIVE database, so the seed fixes draw order but not the
candidate pool — the non-reproducibility recorded in oracle_view_curve applies here too. These rates match oracle_view_curve's
independently computed curve to 4 decimal places at all four view counts.
Space-group macro-F1 at 4 views = 0.80 (crystal-system macro-F1 = 0.93). Recovery
rises steeply with view count (SG 40.7 -> 73.9 -> 91.1%), confirming the full 4-view
set carries most of the space-group information and fewer views do not.
Per-system SG recovery (4 views): cubic 100%, hexagonal 100%, tetragonal 97.5%,
triclinic 95%, monoclinic 90%, orthorhombic 80%, trigonal 75%. Two systems fall below
85% — trigonal (75%) and orthorhombic (80%); trigonal is the more systematic case: 9
of its 10 SG failures are rhombohedral-setting space groups
(R3/R-3/R32/R3m/R3c/R-3m/R-3c). Of those 9, 8 have exactly matching atom counts —
the atoms are recovered correctly but spglib assigns a lower setting to the
reconstruction (a genuine setting/labeling issue, not a reconstruction failure). The
9th (mp-1229124, R3c #161) is a true reconstruction failure: 60 atoms recovered vs 48
expected (spurious triangulations survived cross-view verification). So the trigonal
weakness is mostly a rhombohedral-setting sensitivity plus one dense-cell
over-triangulation. 4-view reconstruction is faithful (0 RMSD,
exact count, correct SG) on small/sparse cells but NOT universal: on dense
high-overlap cells a minority fail even at 4 views (this is the residual
identifiability limit, reflected in the 91.1% not being 100%). Stability caveat (4v,
0.03A noise, NOT Gate 0 evidence): SG 83.6% — the degradation reflects this
triangulator's noise-fragility (independent per-view jitter scrambles correspondence;
spglib then needs symprec ~6*sigma), not render identifiability; the flagship VLM
does not triangulate, so this does not bear on the label choice.

INTERPRETATION (GATE 0 — PROVISIONAL): The plan's retargeting trigger is "SG recovery
low even for the oracle/experts." The oracle ceiling is 91.1% overall at the full
4-view set, with every crystal system >= 75%. The trigger is therefore NOT met:
space group is view-identifiable in principle. DECISION: KEEP space group as the
flagship target, and FREEZE the full 4-view set (axis_a, axis_b, axis_c,
body_diagonal; 768px; conventional standard cell; 2x2x2 supercell; ball-and-stick,
dashed cell edges) as MANDATORY — recovery collapses below 4 views (SG 91->74->41%),
so the view set is not negotiable. Rhombohedral/trigonal is flagged as the weakest
class for targeted evaluation and possible coarse-credit scoring. This decision is
PROVISIONAL pending the human-expert arm: a 50-structure packet (renders + blind
answer sheet + hierarchical rubric) is assembled for crystallographers to confirm
human-solvability before the freeze is final. If the human arm shows SG is not
human-recoverable, the fallback is to demote SG to a top-k stretch metric and
retarget the flagship label to crystal system + Bravais + point group (all >= ~92%
oracle-recoverable).

SURPRISE: The rhombohedral setting is the single systematic failure mode — not
low-symmetry cells in general (triclinic recovers at 95%). Perfectly reconstructed
rhombohedral structures (counts exact) are assigned a lower monoclinic/triclinic
setting by spglib on the reconstruction, the same trigonal/hexagonal-family ambiguity
pipeline flagged, now localized specifically to R-centered groups (8 of 9 with exact atom
counts; 1, mp-1229124, is instead a genuine over-triangulation, 60 vs 48 atoms). Also: the naive
"noise arm = identifiability under imperfect vision" framing was wrong — it measured
the triangulator, not the renders; caught by diagnosing that atom counts matched
(88.9%) while symmetry collapsed, and moved out of the Gate 0 evidence.

=================  HOW THIS BOUND MAY AND MAY NOT BE CITED (2026-07-28)  =====================
The oracle bound was proposed as the paper's upper-bound row, substituting for the human study on
the "is 0.6143 bad, or is the task intrinsically hard?" question. Verified against results.json
before adopting, and THREE corrections are required.

1. THE 91% IS SPACE GROUP, NOT CRYSTAL SYSTEM. From summary.identifiability_ideal at 4 views:
       crystal_system 0.9357 | point_group 0.9143 | space_group 0.9071 | count_match 0.9893  (4 views, rerun)
   Our trained arms are evaluated on CRYSTAL SYSTEM. The comparable oracle number is therefore
   0.9357 at four views (0.9393 at five), not 0.91. Citing 91% against a crystal-system row would understate the oracle and
   compare across tasks.

2. IT IS NOT THE SAME STRUCTURES AS THE EVAL SET. The oracle used a 280-structure stratified
   sample (140 MP + 140 JARVIS, 20 per system, seed 0). Overlap with the 210-structure
   composition-exclusion eval set: ZERO. Overlap with the 1610 train structures: ZERO.
   So it is the same RENDER PIPELINE and the same VIEW GEOMETRY, but a DIFFERENT SAMPLE — and a
   different source mix (the E3 data is MP-only; the oracle is half JARVIS). The bound is an
   upper bound on what the render CONVENTION carries, NOT a row measured on the eval set, and it
   must be labelled that way. It cannot be placed in a single ranked table with the eval-set rows
   without that qualifier attached.

3. [SUPERSEDED BY THE RERUN] THE ORACLE TABLE ORIGINALLY TOPPED OUT AT FOUR VIEWS WHILE THE FROZEN
   RENDER SET IS FIVE. That was true of view_counts = [2,3,4]; the rerun adds the 5-view column
   (crystal system 0.9393), so the 5-view bound is now measured directly rather than floored.
   Since recovery rises monotonically with view count (crystal system 0.7429 -> 0.9143 -> 0.9357 -> 0.9393),
   0.9357 at 4 views is a CONSERVATIVE floor on the 5-view bound; the measured 5-view value is
   0.9393. Say "0.9357 at four views, 0.9393 at five" rather than implying it is the bound for the shipped renders.

WHAT THE BOUND LEGITIMATELY ESTABLISHES, stated precisely for the paper:
  With ideal extraction — atom positions read perfectly off the projections, lattice taken as
  known because the cell edges are drawn — spglib recovers the crystal system for 93.6% of a
  280-structure stratified sample from four of the frozen views (93.9% from all five), and the space
  group for 90.7% (91.1% from five).
  The renders therefore CARRY most of the symmetry information; the trained image arms' 0.6143 is
  not explained by the information being absent. That is exactly the question a human baseline
  would have addressed, and the oracle isolates information content from human skill.
WHAT IT DOES NOT ESTABLISH: that a human can perform the extraction, or that the renders are
"human-solvable". The oracle assumes perfect atom localisation, which is the hard part. The
checkability framing still requires the human study and must be dropped if that study does not run.

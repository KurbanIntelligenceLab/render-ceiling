CHECKPOINT: CP19_atom_detection   GAP: directive item 4's REQUIRED detection-quality gate, which
                                  CP17 skipped by building a wireframe reader instead
STATUS: PARTIAL — the ground-truth instrument is BUILT AND VERIFIED; the detector FAILS its gate
        (median precision 0.233, recall 0.400 over 84 stratified view-measurements). Reported as an implementation limit, and it surfaces a property of the
        render convention that matters more than the detector does.

=================  WHAT WAS BUILT  =================
Item 4 requires, before any extractor branch may be read: ground-truth projected atom positions from
the CIF and the frozen cameras, then detection PRECISION and RECALL against them per view, the
centroid error distribution, and per-structure projected-disc OVERLAP as a difficulty covariate.
The ground-truth half is now exact and free (no GPU, no network). Getting it right took FIVE wrong
transforms — see CP17_extractor/calibration.md, which records all five, because the fifth passed a
2-atom cubic control at 100% and a 25-structure median at 1.000 while being WRONG (it missed
equal-aspect letterboxing, and only a cell with a strongly non-square projected extent exposes it).
Verified form: 30 structures, centre-on-ink median 1.000, P25 1.000, min 0.672, with the dense
triclinic case going 55.8% -> 100.0% after the fix.

=================  THE GATE RESULT  =================
Pilot on three eval structures (view axis_c), which are all dense low-symmetry cells:
  structure        n_gt  n_det   precision  recall   centroid err   disc-overlap
  mp-1235466        120    127      0.24     0.25       0.87 px         0.32
  mp-2215870         88    123      0.23     0.32       0.81 px         0.14
  mp-1246840        144    142      0.13     0.13       0.72 px         0.32
MATCHED CENTROIDS ARE SUB-PIXEL ACCURATE (median 0.72-0.87 px). That is the decisive diagnostic: it
confirms the ground truth is correct, because a wrong transform cannot produce sub-pixel agreement
on the atoms it does match. The detector's problem is not localisation but SEGMENTATION — detected
blob COUNTS are close to the atom counts (127 vs 120, 142 vs 144) while precision and recall sit
near 0.2, meaning blobs are found in roughly the right number but merged and split across the wrong
atoms.
GATE VERDICT: FAILED at this effort level. Per the pre-registered logic of item 4, no statement
about the renders or the models may be derived from a downstream symmetry score computed on these
detections. The finding is "our detector is the bottleneck", exactly as the directive anticipated.

=================  THE PART THAT IS ABOUT THE RENDERS, NOT THE DETECTOR  ======================
The disc-overlap covariate is computed from geometry alone and is INDEPENDENT of detector quality:
14-32% of atoms in these cells have their centre covered by a NEARER atom's disc, so they are not
merely hard to detect, they are NOT VISIBLE. This is a property of the frozen render convention
(conventional cell, 2x2x2 supercell, radii 0.5 at 768px), not of any algorithm.
It bounds what ANY extractor could achieve on these structures, and it is a concrete, measured
statement of the kind item 4 was commissioned to produce — obtained even though the detector failed.
It also sharpens CP0b: the oracle's 0.9357 assumes PERFECT centroid extraction of ALL atoms, but on
dense cells a third of those atoms are occluded in the actual renders, so the oracle is an upper
bound on identifiability from the STRUCTURE, not from the IMAGES.

=================  STRATIFIED RUN (28 structures, 4 per system, 3 views = 84 measurements)  ====
The pilot's three structures were all dense and low-symmetry, so a stratified sample was run: 4 per
crystal system spanning each system's size range, on all three axis views.
  precision  median 0.233   mean 0.357
  recall     median 0.400   mean 0.390
  centroid error   median 0.717 px    (again sub-pixel -> ground truth confirmed)
  DISC-OVERLAP COVARIATE  median 0.553, range 0.208 - 0.929
THE OVERLAP RESULT IS THE FINDING, AND IT IS ABOUT THE RENDERS. Across a size- and system-stratified
sample, the MEDIAN structure has 55% of its atoms' centres covered by a nearer atom's disc. This is
computed from projected geometry alone and does not involve the detector at all.
DETECTION TRACKS OCCLUSION, NOT SIZE. recall vs overlap correlates -0.792; recall vs raw atom count
only -0.411. Splitting by occlusion tercile: low third (overlap < 0.50) recall 0.528, high third
(overlap > 0.61) recall 0.239 — recall HALVES while precision is flat (0.383 vs 0.360). A detector
that were simply weak would degrade with atom count; degrading with OCCLUSION specifically is what a
visibility limit looks like.

A CEILING ESTIMATE THAT DID NOT SURVIVE CHECKING. It is tempting to write max_recall = 1 - overlap
and report "we reach 89% of the achievable ceiling". THAT NUMBER IS WITHDRAWN: 6 of 84 measurements
EXCEED that ceiling, which is impossible for a true bound, so the overlap proxy (centre within half
a nearer disc's radius) OVERCOUNTS occlusion — a centre just outside that radius can still be
visible. The proxy is fine as an ordinal difficulty covariate, which is how it is used above, and
is NOT a quantitative visibility bound. Reported here rather than deleted because the failed check
is what establishes the covariate's correct scope.

=================  WHAT IS NOT CLAIMED  =================
Not claimed: that atom extraction from these renders is impossible; a stronger detector (watershed
on the distance transform, colour-aware unmixing, or a learned detector) is very likely to beat 0.2
precision, and none was attempted. Not claimed: any downstream symmetry-recovery number — none was
computed, precisely because the gate failed. Not claimed: any quantitative fraction of an
achievable ceiling (see the withdrawn estimate above). Not claimed: that these 28 structures
generalise to the full 210 — they are a stratified subsample, chosen to span systems and sizes, and
the full run is straightforward but was not needed to establish the occlusion result.

REPRODUCE
  scripts/detect_atoms.py --eval-jsonl data/e3/eval.jsonl --structures data/e3/structures.json
    --renders data/e3/renders/eval --views axis_a,axis_b,axis_c --out detection.json
  Ground truth: ASE PlottingVariables with equal-aspect letterboxing (see calibration.md).
  Matching: greedy nearest within max(3 px, half the projected disc diameter).

=================  AMENDMENT FROM CP20: WHAT THE 55.3% IS MADE OF  ============================
CP20 attempted to reduce occlusion by shrinking atom radii and found the covariate PINNED: a
fourfold radius reduction moved the median by under 2 points. The cause decomposes the figure.
Viewing down a lattice vector projects the 2x2x2 supercell copies onto IDENTICAL positions
(nearest-other-atom pixel distance exactly 0.000 on the affected structures), so a fixed fraction of
atoms are hidden back-copies that no disc size can separate.
  EXACT COINCIDENCE (tiling artifact)     mean 0.2363
  GENUINE DISC OVERLAP                    mean 0.2529
  total                                   mean 0.4891   (verified exhaustive to 1e-16)
About 48% of the occlusion is projective coincidence and 52% is disc crowding. Component MEDIANS are
not additive — only means are — so the split is reported in means.
WORDING CORRECTION. "55.3% of atom centres covered by a nearer atom's DISC" implies crowding. The
accurate statement is that over half the atom centres are NOT VISIBLE, roughly half of that because
supercell copies coincide when viewed down a lattice vector and roughly half because a nearer disc
covers them. This makes the limit harder to escape, not softer: the dominant component is intrinsic
to rendering a periodic structure along its own axes, and removing the supercell — the one
intervention that would eliminate it — was shown in CP1 to destroy genuine periodicity signal
(0.41 -> 0.21).
NO BEHAVIOURAL CONSEQUENCE IS ESTABLISHED. The pre-registered causal test could not be run because
the manipulation failed its own check, so this remains a geometric property of the renders.

RECONCILIATION [0.9321 -> 0.9357: the CP0b harness was rerun to record box-sufficiency per row; the rerun's 4-view value is 0.9357 (262/280) against the original 0.9321 (261/280). One structure of 280; the harness draws from a LIVE database so the seed fixes draw order, not the candidate pool. 0.9357 is the current value.]

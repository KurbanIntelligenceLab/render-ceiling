CHECKPOINT: detector_characterisation   GAP: G1, the audit's highest-value missing experiment.
     Proposition 2 says an extractor that is sound and complete at tau/2 reproduces R1. rung_R2_detector_oracle ran the
     oracle on detector output and it failed its pre-registered gate, but the paper could not say
     WHY in terms of its own theory, because the detector had never been characterised against
     Proposition 2's precondition.
STATUS: DONE. THE DETECTOR FAILS THE PRECONDITION ON ALL THREE AXES, BY MARGINS THAT EXPLAIN rung_R2_detector_oracle's
     COLLAPSE QUANTITATIVELY. Zero API calls; 210 structures x 5 views in 11m43s on 10 CPU processes.

=================  WHY THIS WAS PREVIOUSLY IMPOSSIBLE, AND WHAT CHANGED  =====================
atom_detection stored per-view AGGREGATES (tp, fp, fn, precision, recall, median centroid error in PIXELS) for
28 structures on 3 views. Proposition 2's band test needs per-atom errors in ANGSTROM, so it could
not be computed from the record, and the renders the detector reads were not on disk: eval.jsonl
points at data/e3/renders/eval/*.png and the repository contains zero PNG files.

The renders are regenerable from the local CIFs under the frozen protocol (conventional cell, 2x2x2
supercell, px=768, radii=0.5) with no API access. THE REGENERATION IS EXACT: re-running detection on
regenerated images reproduces all 84 of atom_detection's recorded view measurements identically — precision
0.2333, recall 0.4000, centroid error 0.7171 px — including n_det, which depends on the actual
pixels. The regenerated images are the frozen images.

The px-to-Angstrom scale is recovered from the same letterboxed transform the ground truth uses
(px / max(pv.w, pv.h)), which is what makes the band test computable at all.

=================  (a) CENTROID ERROR, 54,258 matched detections  ============================
  pixels:    median 0.7563   mean 3.3261   p95 15.879   max 72.81
  angstrom:  median 0.0329   mean 0.1112   p95 0.5239   max 1.0744

Full-sample precision and recall are HIGHER than atom_detection's 28-structure stratified subset (precision
median 0.4278 vs 0.2333; recall median 0.4227 vs 0.4000), because that subset was deliberately
stratified toward hard, high-overlap cases. The subset re-measures exactly, so this is a sampling
difference, not a disagreement.

=================  THE BINDING CONSTRAINT: PROPOSITION 2's LOCALISATION REQUIREMENT  =========
Proposition 2 requires soundness and completeness at tau/2 = 0.005 A. Measured:

  MATCHED CENTROIDS MEETING tau/2:  38 of 54,258  =  0.07%
  median error is 6.58x larger than the requirement

So even restricted to atoms the detector FINDS AND MATCHES CORRECTLY, its localisation misses the
precondition by more than half an order of magnitude on the median atom.

Soundness and completeness fail independently and by wider margins:
  precision median 0.4278  ->  most detections are spurious, so NOT SOUND
  recall    median 0.4227  ->  about 58% of atoms are missed outright, so NOT COMPLETE at ANY tolerance

=================  (c) THE BAND TEST PASSES 210/210, AND THAT IS VACUOUS  ====================
Per structure, taking eps as the median centroid error in Angstrom and kappa = 1.7689 from the theory
audit, the ambiguity band [tau - 2*kappa*eps, tau + 2*kappa*eps] has median half-width 0.0902 A
(max 0.7865). Every one of the 210 structures has ZERO compared distances inside the band, and the
band never reaches the closest pair in any structure (0 of 210).

THIS IS NOT EVIDENCE THE DETECTOR IS ADEQUATE. The band is centred on tau = 0.01 A, and the closest
interatomic distance anywhere in the evaluation set is 1.0951 A — about 11x the band's upper edge.
No physically realisable structure has interatomic distances near a 0.01 A tolerance, so the test
passes for a structural reason and cannot discriminate between a good detector and a bad one at this
tolerance. Reported here because the audit's protocol asks for it, with the caveat attached; it is
not the constraint that binds.

=================  WHAT THIS SETTLES FOR THE PAPER  ==========================================
rung_R2_detector_oracle reported R2 unscored under a pre-registered gate (zero-triangulation on 19.0% and 22.4% of
structures across two samples). That was an empirical stop with no explanation. detector_characterisation supplies the
explanation in the paper's own terms: the available detector violates Proposition 2's hypothesis on
soundness, on completeness, and on localisation simultaneously, so R2's collapse is what the theory
PREDICTS rather than an anomaly.

The consequence for the attribution claim is unchanged but now grounded: the extraction share stays
unbounded from both sides, because no available detector meets the precondition that would let the
oracle certify it — NOT because the experiment was skipped. Closing G1 properly needs a detector
roughly 7x better at localisation AND materially better at both soundness and completeness, which is
a new method, not a rerun.

Reproduce: python scripts/run_g1_detector.py   (rc-analysis env; CPU only; ~12 min on 10 processes)
Artifacts: detection_full.json (per-structure x per-view, with per-atom centroid errors and the
px-per-Angstrom scale), results.json (aggregates and the band test).

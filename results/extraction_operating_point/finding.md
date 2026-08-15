CHECKPOINT: extraction_operating_point   GAP: atom_detection's failed detector gate carries more than an
                                              implementation limit. (ICLR plan, Phase B)
STATUS: DONE, AND THE CONCLUSION IS NARROWER THAN THE PLAN ANTICIPATED. This is ARGUMENT from three
        already-measured quantities, not new measurement. All six values verified against atom_detection's stored
        summary. But the design it was written to license — visibility_corrected_oracle's visibility correction — returned a
        ZERO effect, so this section no longer licenses anything; it stands as a characterisation of
        where extraction fails.

=================  THE THREE MEASURED QUANTITIES, VERIFIED  ====================================
From atom_detection's stratified run, 28 structures x 3 views = 84 view-measurements:
  recall           median 0.400   mean 0.390
  precision        median 0.233   mean 0.357
  centroid error   median 0.717 px on MATCHED atoms — SUB-PIXEL
  recall vs occlusion covariate   r = -0.792
  recall vs atom count            r = -0.411
  across occlusion terciles: recall 0.528 -> 0.239 (HALVES) while precision 0.383 -> 0.360 (FLAT)

=================  WHAT THEY JOINTLY ESTABLISH  ================================================
EXTRACTION FAILS AT VISIBILITY AND SEGMENTATION, NOT AT PRECISION. Where the detector finds an atom it
localises it to better than one pixel, so a precision-requirement curve would answer a question already
answered. Recall tracks occlusion twice as strongly as it tracks atom count, and it halves across
occlusion terciles while precision does not move — the signature of atoms not being SEPARATED, rather
than being found and mislocated.
identifiability independently supports this from the other direction: its 0.03 A jitter arm was moved out of Gate 0
evidence precisely because independent per-view noise scrambles CROSS-VIEW CORRESPONDENCE, which the
reconstructor re-solves from element identity and ray geometry alone. Both instruments point at
correspondence and separation, not at localisation accuracy.

=================  THE LICENSING ARGUMENT DID NOT SURVIVE ITS OWN TARGET  ======================
The plan's purpose for this checkpoint was to license visibility_corrected_oracle's design: if extraction fails through
visibility, then correcting the oracle for measured visibility is the right instrument. visibility_corrected_oracle ran and the
correction is EXACTLY ZERO on both eval sets, with the O3 control dominating the target condition.
So the argument is sound about WHERE the detector fails and silent about what correcting for it buys —
because correcting for it buys nothing. Recorded that way rather than deleted, because the
visibility-and-segmentation diagnosis is still the correct reading of atom_detection and is cited by visibility_corrected_oracle's
mechanism section.

=================  WHAT THIS DOES NOT ESTABLISH  ==============================================
NO claim about what a stronger detector would achieve. atom_detection records that watershed segmentation, colour
unmixing and learned detectors were never attempted. The failure is characterised, not bounded.
The overlap covariate is ORDINAL. atom_detection's "1 - overlap" ceiling was WITHDRAWN after 6 of 84 measurements
exceeded it, and no arithmetic is performed on it here.

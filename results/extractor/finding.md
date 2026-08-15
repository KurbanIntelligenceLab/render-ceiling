CHECKPOINT: extractor    GAP: can a DETERMINISTIC reader recover cell geometry from the
                              renders well enough to classify? (review item 4)
STATUS: DONE — VALIDATION GATE FAILED. **SCOPE WARNING: this is NOT the probe directive item 4
        specified.** Item 4 asked for PNG -> ATOM CENTROIDS -> triangulation via identifiability's camera
        inversion -> spglib, gated on detection PRECISION/RECALL. extractor is a wireframe-only reader
        gated on edge-length ratios and never localises an atom. See scope_deviation.md. Item 4
        REMAINS OPEN and item 6 is BLOCKED on it. Per the pre-registration this is the checkpoint's RESULT,
        and NO conclusion about the renders or about the models may be drawn from the extractor's
        accuracy. Reported as an implementation-effort statement, not a finding about legibility.

=================  THE GATE, AND HOW IT FAILED  =================
Two gates were committed in prereg.md before any extraction ran.
  GATE 1  line detection on >= 80% of the 210 structures
          RESULT 203/210 = 0.9667  PASS
  GATE 2  median relative error on recovered edge-length RATIOS < 0.10
          RESULT 0.1021  FAIL (by 0.0021)

THE MARGIN IS SMALL AND THE FAILURE IS REAL. It would be easy to call 0.1021-vs-0.100 a rounding
artifact and proceed; the error DISTRIBUTION is what forbids that:
    p25 = 0.007      p50 = 0.102      p75 = 0.497
    ratios within 2% of truth : 33.5%
    ratios more than 25% off  : 39.6%
The distribution is BIMODAL — the extractor is either near-exact or catastrophically wrong, with
little in between. A median sitting exactly on the threshold while two-fifths of measurements are
off by more than a quarter is not a measuring instrument, whichever side of 0.10 the median lands.
Angles are the opposite story and worth recording: median absolute angle error 0.0 deg, p75 5.0 deg.
The Hough step recovers ORIENTATIONS well; what fails is LENGTH, because the projected extent of a
wireframe is contaminated by whichever atoms and cell corners happen to bound the view.

=================  WHAT IS THEREFORE NOT CLAIMED  =================
The extractor's 7-way-ish accuracy is 125/210 = 0.5952. THIS NUMBER IS RECORDED AND NOT
INTERPRETED, for two independent reasons:
  1. The gate failed, so per the pre-registration no branch (E1-E4) may be read.
  2. The number is not commensurable with any model accuracy even if the gate had passed. The
     extractor emits a metric CLASS, and the class "hexagonal_or_trigonal" is scored correct
     against EITHER true label, because a cell metric cannot separate that pair at any precision.
     The models are scored on a strict 7-way label. Comparing 0.5952 with B1's 0.6143 would be
     comparing a 6-way-with-a-free-pass task against a 7-way one.
No claim is made that the render convention is illegible. The correct statement is narrow: A
DETERMINISTIC READER OF THIS CONVENTION COULD NOT BE BUILT TO INSTRUMENT QUALITY AT THIS EFFORT
LEVEL, using darkness-threshold wireframe isolation plus a Hough transform on the three
orthographic axis views. That is a fact about our implementation.

=================  WHAT THE ATTEMPT NEVERTHELESS ESTABLISHES  =================
Two things survive the gate failure, because they do not depend on the extractor being accurate.
  (a) THE WIREFRAME IS FINDABLE. Line detection succeeded on 96.7% of structures and angle recovery
      is essentially exact at the median. So the cell OUTLINE is unambiguously present in the pixels
      at 768px; the renders are not visually degenerate.
  (b) THE HARD PART IS METRIC LENGTH, NOT ORIENTATION. This is a specific, testable localisation of
      the difficulty and it is consistent with box_sufficiency: what separates crystal systems is largely
      length EQUALITY (a=b, a=b=c), and length is exactly what this reader recovers worst.
      box_sufficiency showed pixel models collapse to the floor when the box cannot disambiguate the system;
      extractor adds that even reading the box's lengths off the drawing is itself unreliable.
  These two are reported as observations about the render convention, NOT as the licensed E1-E4
  claims, which remain unavailable.

=================  IMPLICATION FOR THE PAPER  =================
box_sufficiency's wording must stay as it is and must NOT be strengthened. box_sufficiency says pixel models fail to
extract information that IS present in the cell parameters — that claim rests on the RF control
(which reads the cell numerically and does not collapse), not on this extractor. extractor does not
support the stronger reading "an easy deterministic reader beats the VLMs", and the paper must not
imply it. Nor does extractor license the opposite softening: a failed instrument is evidence about the
instrument.
The honest one-line summary for the discussion: we attempted a non-learned reader of the render
convention as a way to localise the extraction gap, it failed its own pre-registered validation
gate, and we report that rather than a number.

REPRODUCE
  scripts/extract_cell.py --eval-jsonl data/e3/eval.jsonl --renders data/e3/renders/eval
    --structures data/e3/structures.json --out extraction.json
  Gate computed against conventional_cell() lattices; RATIOS only, since an orthographic projection
  has unknown global scale. Tolerances for the class rule are box_sufficiency's (2% length, 1 deg angle) so the
  two checkpoints would have been commensurable had the gate passed.

RECONCILIATION [0.9321 -> 0.9357: the identifiability harness was rerun to record box-sufficiency per row; the rerun's 4-view value is 0.9357 (262/280) against the original 0.9321 (261/280). One structure of 280; the harness draws from a LIVE database so the seed fixes draw order, not the candidate pool. 0.9357 is the current value.]

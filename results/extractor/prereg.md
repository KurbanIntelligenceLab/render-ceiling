[SUPERSEDED VALUE NOTE — appended after the fact, the text below is UNCHANGED because a
 pre-registration records what was believed BEFORE computing and must not be rewritten.
 The oracle values quoted below (0.9321 / 93.2% at four views) are from the ORIGINAL identifiability
 run. The harness was later rerun to record box-sufficiency per row; the current values are
 0.9357 (262/280) at four views and 0.9393 at five. The difference is one structure of 280
 and arises from a live-database draw, not a computation change. No pre-registered reading
 is affected.]

PRE-REGISTRATION — extractor (review item 4)
COMMITTED BEFORE ANY EXTRACTION IS RUN. Nothing below is filled in after seeing a result.

QUESTION. box_sufficiency established that pixel-input models collapse to the regularity floor on
box-ambiguous structures, while an RF reading the same cell NUMERICALLY does not. identifiability established
that under IDEAL atom extraction plus spglib, four views recover 93.2% of crystal systems. The gap
between 0.9321 and the ~0.50 the pixel models reach on the ambiguous stratum is therefore an
EXTRACTION gap, and this checkpoint asks where in the pipeline it sits: can a DETERMINISTIC,
non-learned reader recover the cell geometry from the rendered pixels well enough to classify?

WHY THIS IS THE RIGHT PROBE. The renders' three axis views are ORTHOGRAPHIC projections down a, b
and c (VIEWS in src/cocr/render.py: "0x,-90y,0z", "-90x,0y,0z", "0x,0y,0z"), drawn with
show_unit_cell=2, so the cell edges appear as straight line segments whose 2D lengths and mutual
angles are affine images of the true cell metric. If a classical CV reader can recover the metric
class from those lines, the information is legible in the pixels and the VLMs' failure is a
perception failure. If it cannot, the render CONVENTION is the bottleneck and the paper's framing
must change accordingly.

METHOD, FIXED NOW.
  Input: the SAME frozen renders every arm was evaluated on (data/e3/renders/eval, 768px, 5 views).
  No re-rendering, no new structures, no learned components anywhere in the extractor.
  1. Detect the cell wireframe by colour/darkness thresholding (ASE draws the cell as dark lines
     distinct from the atom spheres), then Hough-transform line detection.
  2. From the three axis views recover the projected edge lengths and the in-plane angles.
  3. Assemble a metric estimate (a, b, c, alpha, beta, gamma) and classify with the SAME tolerance
     rule box_sufficiency used (2% on lengths, 1 deg on angles), so the two checkpoints are commensurable.
  Denominator FIXED at 210. A structure on which line detection fails is scored as WRONG, not
  dropped — dropping failures would silently convert a coverage problem into an accuracy claim.

VALIDATION GATE, AND IT RUNS FIRST. Before any accuracy number is interpreted, the extractor is
validated against the KNOWN cell parameters of the same structures (available in
data/e3/structures.json). Required: median relative error on recovered edge-length RATIOS below
10%, and successful line detection on at least 80% of the 210 structures.
  IF THE GATE FAILS, the extractor is not a measuring instrument and NO conclusion about the
  renders or the models may be drawn from its accuracy. The checkpoint then reports the gate
  failure as its result: "a deterministic reader of this render convention could not be built at
  this effort level", which is a statement about our implementation and NOT evidence that the
  information is absent. This is the branch I expect to be at real risk.

BRANCHES, ON THE BOX-SUFFICIENT STRATUM (n=137), COMMITTED NOW.
  E1  extractor >= 0.80: the geometry IS legible deterministically. The VLMs' collapse is a
      perception failure, not a render-convention limit. This is the strongest version of the
      paper's mechanism claim and licenses "the renders carry the information; the models do not
      extract it" ON THIS STRATUM.
  E2  extractor in [0.6715, 0.80): the extractor beats our best pixel VLM (B1 at 0.6715 on this
      stratum) but is not near-perfect. Licenses the same direction more weakly: a non-learned
      reader outperforms a fine-tuned 8B VLM at reading a cell off a drawing.
  E3  extractor in [0.5474, 0.6715): between the floor-on-this-stratum (0.5474) and B1. NO claim
      that the models underperform an easy reader; report as "the deterministic reader is
      comparable to the VLMs", which is evidence the convention is genuinely hard to read.
  E4  extractor < 0.5474: the deterministic reader is at or below the shape-free floor. The render
      convention, not the models, is then the binding constraint, and the paper must say so
      explicitly and soften box_sufficiency's "models do not extract it" to "no reader we built extracts it".

WHAT NO OUTCOME LICENSES. None of E1-E4 says anything about the box-AMBIGUOUS stratum, where the
cell metric cannot disambiguate the system at any precision — that is a convention limit already
established, and an extractor cannot beat it. Accuracy on the ambiguous stratum is reported for
completeness and is expected at or near the floor for every method including this one.
ALSO NOT LICENSED: any claim that this extractor is a competitive method. It is an instrument for
localising the gap, not a baseline to be beaten, and must never be presented as a proposed system.

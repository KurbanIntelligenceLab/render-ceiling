CHECKPOINT: perception_transplant   GAP: rung_R3_coords_as_text showed 12 of 14 models are REASONING-limited given
     perfect geometry. Is the strong models' advantage PERCEPTION, and does it TRANSPLANT? A descriptive
     ladder cannot answer that; a substitution can. (ICLR directive)
STATUS: DONE. NO PRE-REGISTERED BRANCH FIRES, AND THE ACCURACY IS NOT THE RESULT. The informative number is
     the direct measurement of the strong model's emitted positions, which is the quantity the
     pre-registration called out as unavailable to prior work — and it comes back at MEDIAN RECALL 0.0000.

=====  THE ACCURACY IS UNSCORABLE, AND THE REASON IS VISIBLE IN ONE LINE  =====

A3 (strong extracts -> weak reasons) = 30/210 = 0.1429. The pre-registered branches: T1 (near A2 = 0.7333)
no; T2 (near A1 = 0.2048) no; T3 (between A1 and A4 = 0.5048) no; T4 (above A4) no. NOTHING FIRES, and A3
sits BELOW the weak model's own pixel accuracy.
But the arm predicted only 2 OF 7 CLASSES: 205 of 210 answers were "cubic". And 0.1429 is EXACTLY the cubic
stratum's base rate (30 of 210 structures are cubic, 1/7 = 0.1429). So the arm scored precisely what a
constant "cubic" responder scores. THIS IS PREDICTION COLLAPSE, not symmetry reasoning, and an accuracy
produced by a collapsed predictor cannot be read as a reasoning measurement at all.

=====  THE REAL RESULT: THE STRONG MODEL'S POSITIONS DO NOT CORRESPOND TO ATOMS  =====

The pre-registration required scoring the emitted positions DIRECTLY against ground truth by the same
matching criteria used for the atom_detection detector, on the grounds that prior two-stage work can only compare
stages through downstream accuracy because it has no exact positions to compare against. That measurement:

  median recall                      0.0000
  median precision                   0.0000
  structures with ZERO matched atoms   105 of 206
  median error on the atoms that DID match   0.0817 fractional units
  (atom_detection's connected-component detector, for contrast: median recall 0.400, precision 0.233)

The strong model emits well-formed, plausible-looking coordinate lists — median 48 atoms, correct element
symbols, five-decimal precision — and on half the structures NOT ONE of them lands within tolerance of a
real atom. It is generating the FORM of an extraction without the content. A learned model that
hallucinates numeric coordinates is a worse extractor than a colour-threshold blob detector, which is a
sharper statement than any accuracy comparison in this package.

=====  WHY THIS IS NOT A NULL, AND WHAT IT LICENSES  =====

The design premise fails rather than the hypothesis: A3 was meant to test whether perception TRANSPLANTS,
and it can only test that if the transplanted content is perception. It is not. So:
  NOT SUPPORTED: any claim about whether the strong/weak difference is perception.
  SUPPORTED, and it is new: model-emitted structured extractions can be entirely fabricated while remaining
  syntactically perfect, and downstream accuracy alone would NOT have revealed it — a 0.1429 could have been
  read as "the weak model reasons badly". Only scoring the intermediate against exact ground truth exposes it.
This is a direct argument for the paper's instrument: a two-stage pipeline whose intermediate cannot be
checked will attribute fabrication to reasoning.

=====  GATES, ALL PASSED, SO THE FAILURE IS NOT A HARNESS ARTEFACT  =====

  unparseable extractions   4/210 = 1.9%   (gate 5%)
  extraction API errors     0/210          (gate 5%)
  fewer than 3 atoms emitted 4/210 = 1.9%  (gate 20%, which would have bounded FORMAT rather than extraction)
The handoff carried a median of 48 atoms. The strong model complied with the format and withheld the
symmetry answer as instructed. What it did not do is look at the images.

=====  A DEFECT IN MY OWN READING, RECORDED BECAUSE THE PATTERN RECURS  =====

THE PREFIX DEFECT LEAKED TWICE, NOT ONCE. I flagged the biased prefix and discarded it for the ACCURACY
number, then let its atoms-emitted figure of 45 stand in the prose of this file and of results.json while
the numeric field correctly held 48. Recomputed over all 206 structures with an emitted list:
median 48, mean 53.3, range 5 to 288. Discarding a biased sample for one quantity is not
discarding it: every figure derived from it has to be recomputed, and the check is that each prose number
equals the field beside it.

At 43 of 210 completed I observed 0 correct and nearly reported it as a catastrophic result. The executor
submits in file order and eval.jsonl is ORDERED BY CRYSTAL SYSTEM, so the first 43 results were all
triclinic and monoclinic — a biased prefix, exactly the defect already recorded in CONVENTIONS.md. The
partial number was meaningless; the full-sample number is what stands. Never read a partial result off a
class-ordered file.

=====  SCOPE  =====

One strong model (gemini-3.6-flash), one weak model (llama-4-scout), one sample, one handoff format. A
different prompt might elicit real coordinates; this shows that the obvious prompt does not. A2 (0.7333) is
NOT the reference for A3 — A4 (0.5048) is, since the weak model's ceiling with PERFECT geometry is 0.5048.
The pre-registration named that asymmetry before the run.

PRE-REGISTRATION — CP20 occlusion manipulation (directive item 4)
WRITTEN AND SAVED BEFORE ANY RE-RENDERING OR ANY MODEL CALL. Nothing here is filled in after seeing
a number.

QUESTION. CP19 measured that the median rendered structure has 55.3% of its atom centres covered by
a nearer atom's disc. That is a geometric fact about the render convention. It is NOT yet evidence
that occlusion CAUSES any part of the models' failure. This checkpoint tests the causal claim.

THE PREDICTION, AND IT IS AN INTERACTION, NOT A MAIN EFFECT.
If occlusion is a real second failure mode (the first being an uninformative cell box), then
reducing occlusion should help SPECIFICALLY where the motif has to be read:
  * BOX-AMBIGUOUS stratum — the cell metric does not determine the crystal system, so the answer can
    only come from the atom arrangement. Reducing occlusion should IMPROVE accuracy here.
  * BOX-SUFFICIENT stratum — the answer is already available from the drawn cell. Reducing occlusion
    should leave accuracy ROUGHLY UNCHANGED here.
THAT DIFFERENTIAL IS THE TEST. Two outcomes FALSIFY the occlusion account:
  * a UNIFORM improvement across both strata (then the manipulation improved something else —
    legibility in general, or it made the task easier for an unrelated reason);
  * a UNIFORM null (then occlusion at this level does not bind on model behaviour at all).

BRANCHES, COMMITTED NOW. Let d_amb and d_suff be the paired accuracy changes (reduced-occlusion
minus canonical) on each stratum, per model, tested with paired McNemar on the same structures.
  O1  d_amb > 0 significantly AND d_suff not significant  -> OCCLUSION ACCOUNT SUPPORTED. Licenses:
      "reducing projected-disc occlusion improves crystal-system accuracy specifically where the
      cell box is uninformative", plus the render-design recommendation.
  O2  both d_amb and d_suff significantly > 0             -> FALSIFIED AS STATED. Report as a
      general legibility effect, NOT as evidence about occlusion and the motif. The render-design
      recommendation may still be made but must be framed as "clearer renders help generally".
  O3  neither significant                                 -> FALSIFIED. Occlusion at this level does
      not bind. Report the null; CP19's 55.3% stays a geometric measurement with no demonstrated
      behavioural consequence, and the report must say so.
  O4  d_amb significant and NEGATIVE (reduced occlusion HURTS) -> report as a CP1-type finding: the
      manipulation removed real signal. See the carried warning below.

METHOD, FIXED NOW.
  Structures: the SAME 210 composition-exclusion evaluation structures. No new structures.
  Manipulation: re-render with REDUCED projected-disc overlap by shrinking the atom radii scale.
  HELD FIXED, and this is what makes it a clean manipulation: camera set (the same 5 frozen views),
  supercell extent (2x2x2 — NOT reduced), cell-edge style, image size (768px), background, and the
  element colour map. ONLY the radii change.
  MANIPULATION CHECK, REQUIRED BEFORE ANY MODEL CALL: recompute the median centre-occlusion with the
  existing geometric routine on the new renders. If it does not fall materially below 55.3%, the
  manipulation failed and NO model evaluation is run — that would be spending API budget on a
  condition that does not differ from the control.
  Models: the three frontier models zero-shot (Gemini 3.6-flash, Grok 4.5, Opus 4.8), K=3 majority
  vote, identical prompt, denominators FIXED at 210 with parse failures scored as errors. Zero-shot
  deliberately: our own adapters are coupled to the training resolution and style, so a retrained
  arm would confound the manipulation with adaptation.
  Analysis: stratum x convention, paired McNemar within stratum, per model.

CARRIED WARNING FROM CP1, AND IT IS THE REASON FOR O4. CP1's "more legible" single-cell redesign
LOWERED canonical accuracy 0.41 -> 0.21, because removing the supercell removed genuine
translational-periodicity signal. Smaller radii could plausibly do something similar by making
atoms harder to see at all. The supercell is NOT touched here, and O4 exists so that a negative
result is reported as a finding rather than as a failed experiment.

WHAT NO OUTCOME LICENSES. No outcome here says anything about whether an EXTRACTOR could recover
atom positions — that is CP19's failed gate and remains open. No outcome licenses a claim about
our own trained arms, which are not evaluated in this checkpoint.

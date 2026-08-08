PRE-REGISTRATION — CP41 no-image control   (ICLR plan, Phase D)
Committed BEFORE any call is made. API spend only, no GPU.

GAP. Every zero-shot row in CP26 is prompted with renders AND a text preamble carrying the chemical
formula. Nothing establishes how much of the measured accuracy needs the IMAGE at all. A model that
scores from formula alone is not doing crystallography from pixels, and the whole benchmark premise
rests on the image mattering.

METHOD. Re-run a SUBSET of the CP26 roster on the identical original eval set (n=210) under two arms
that differ ONLY in whether the renders are attached:
  IMAGE   the frozen CP26 prompt, renders + formula preamble   (already measured — reuse, do not re-run)
  TEXT    byte-identical prompt with the image blocks REMOVED, formula preamble retained
K=3, temperature 0.7, majority vote — identical to CP26 so IMAGE rows are reusable verbatim.
ROSTER, fixed now: the CP26 top-3 by micro (llama-4-maverick, qwen3-vl-8b, gpt-4.1-mini) plus the
bottom-1 (seed-1.6) as a floor check. Four models x 210 x K=3 = 2520 calls.

DECISION RULE, fixed now.
  - Primary quantity is IMAGE minus TEXT per model, PAIRED per structure, McNemar exact.
  - N1  TEXT >= IMAGE on any model that clears the shape-free floor -> that model's benchmark row does
        NOT measure vision and MUST be reported as formula-driven. This would be a severe finding about
        the benchmark and will be published as such, not buried.
  - N2  TEXT significantly below IMAGE on every model -> the images carry the signal; the benchmark
        premise holds.
  - N3  TEXT below IMAGE but NOT significant on some models -> report per model with its p-value; make
        NO pooled claim, because pooling across models with different priors is not meaningful.
  - Compare TEXT against the SHAPE-FREE FLOOR (111/210 on this sample), not against chance. A text-only
    model with the formula can infer composition-correlated structure, which is exactly what the floor
    already measures.

WHAT WOULD MAKE THIS UNINFORMATIVE.
  - Any arm with >5% API errors or unparseable outputs is reported with its rate and NOT scored.
  - If a model refuses without an image at a high rate, that is a REFUSAL result, not an accuracy
    result, and is reported separately from the accuracy row.

EXPECTED, STATED SO IT CANNOT BE RENEGOTIATED. I expect TEXT to land near the shape-free floor, since
the floor is itself a composition-only model. If TEXT lands ABOVE the floor, the formula preamble is
doing more work than the floor captures and the floor is the wrong reference for the whole leaderboard —
a finding that would require revising CP26's framing, and I will report it.

SCOPE. This bounds how much the IMAGE contributes for these four models on this sample. It says nothing
about the fine-tuned arms, which were trained on renders and are not part of this comparison.

PRE-REGISTRATION — CP26 model sweep (directive item 3)
WRITTEN BEFORE ANY MODEL IS CALLED.

PURPOSE. A four-row leaderboard is not a benchmark. This adds open-family rows at multiple scales so
the benchmark reports a landscape rather than three frontier models plus our fine-tune.

PROTOCOL, IDENTICAL TO CP1/CP14 — NOTHING IS TUNED PER MODEL.
  Renders: the frozen protocol, 5 views, conventional cell, 2x2x2 supercell, 768 px, canonical style.
  Prompt: the CP14 prompt verbatim. Same for every model. No per-model prompt engineering.
  Decoding: K=3 samples, temperature 0.7, majority vote. Same parser as CP14.
  Denominators: FIXED at 210 per evaluation set. Parse failures and API errors are scored as ERRORS,
    never dropped. api_errors and unparseable are reported per model.
  Sets: BOTH evaluation sets in this first presentation, per standing discipline.
  Anonymized condition: NOT run for the sweep (it is a contamination control for the frontier ceiling,
    already reported in CP14 for the three models where it matters).

ROSTER, fixed now — 14 models spanning 6 open families and a scale ladder inside two of them:
  qwen/qwen3-vl-8b-instruct, qwen/qwen3-vl-32b-instruct, qwen/qwen3-vl-235b-a22b-instruct
    (a 3-point scale ladder within one family, which is the row that makes a scaling statement possible)
  qwen/qwen2.5-vl-72b-instruct                     (previous generation, same family)
  meta-llama/llama-4-scout, meta-llama/llama-4-maverick   (2-point ladder)
  mistralai/mistral-small-2603, mistralai/mistral-medium-3.1
  z-ai/glm-4.6v
  moonshotai/kimi-k2.6
  bytedance-seed/seed-1.6
  amazon/nova-pro-v1
  google/gemini-2.5-flash                          (bridges to the CP14 frontier rows)
  openai/gpt-4.1-mini
Total: 14 models x 210 structures x K=3 x 2 sets = 17,640 calls.

THE READING, COMMITTED BEFORE THE NUMBERS EXIST.
  S1  NO OPEN MODEL BEATS THE REGULARITY FLOOR (0.5286 original / 0.2476 expansion). Then the floor is
      not an artifact of our own arms being weak, and the benchmark's central difficulty claim is
      established across the field rather than on four rows.
  S2  SOME OPEN MODELS CLEAR THE FLOOR. Then the floor is passable and the benchmark must report WHICH
      models pass and what they share. This weakens no claim in the package; it strengthens the
      leaderboard.
  S3  SOME OPEN MODEL BEATS OUR BEST FINE-TUNE (0.6905 A3 / 0.4524 B1 expansion) ZERO-SHOT. Then the
      fine-tuning contribution is bounded by that row and must be reported as such, in the abstract.
      I commit to reporting this if it fires.
  SCALING: report accuracy against parameter count within the two families that have ladders. A flat or
      non-monotone ladder is itself a finding (scale does not buy this task); a monotone one bounds how
      much of the deficit is capacity.

WHAT NO OUTCOME LICENSES. Zero-shot rows are not comparable to our fine-tuned arms as a method
comparison — different training exposure. They bound TASK DIFFICULTY, not method quality.

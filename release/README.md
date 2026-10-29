# Diagnostic benchmark records

| Record | Contents |
|---|---|
| [frozen_prompts.json](frozen_prompts.json) | Archived diagnostic prompts |
| [classifier_specifications.json](classifier_specifications.json) | Numeric classifier specification |
| [Raster-control manifest](../results/supervised_pixel_baseline/manifest.json) | Raster training and validation records |
| [eval_coords_as_text.jsonl](eval_coords_as_text.jsonl) | Exact-text lattice and site inputs |
| [predictions/](predictions/) | Per-structure pixel, exact-text and geometry-handoff predictions |

The `coords_as_text__`, `zeroshot__` and `frontier__` filenames identify input conditions and API model identifiers. Each paired comparison uses its matching recorded pixel and exact-text runs. [paired_geometry_outcomes.json](../results/geometry_substitution/paired_geometry_outcomes.json) identifies all 17 models and their paired counts. The original 14 models use archived predictions; the three additional frontier models use [native API records](../results/geometry_substitution/).

The [reconstructed-coordinate handoff](../results/coordinate_handoff/report.md) links exact prompts, input mappings, local model revisions, sampled runs, invalid responses, and downstream comparisons for Sonnet, Gemma, and Qwen.

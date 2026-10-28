# Diagnostic benchmark records

| Record | Contents |
|---|---|
| [frozen_prompts.json](frozen_prompts.json) | Archived diagnostic prompts |
| [classifier_specifications.json](classifier_specifications.json) | Numeric classifier specification |
| [Raster-control manifest](../results/supervised_pixel_baseline/manifest.json) | Raster training and validation records |
| [eval_coords_as_text.jsonl](eval_coords_as_text.jsonl) | Exact-text lattice and site inputs |
| [predictions/](predictions/) | Per-structure pixel, exact-text and geometry-handoff predictions |

The `coords_as_text__`, `zeroshot__` and `frontier__` filenames identify input conditions and API model identifiers. Each paired comparison uses the matching recorded pixel run and exact-text run. [Figure 3 data](../results/paper_figures/figure_3/paired_outcomes.json) identifies the 14 included models and their paired counts.

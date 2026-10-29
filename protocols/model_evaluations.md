# Model evaluation experiments

Run from the repository root with the pinned base environment:

```sh
uv sync --group dev
uv run python -m render_ceiling.verify_model_results
uv run render-ceiling verify
```

The offline audit recomputes the frontier paired outcomes and the coordinate-handoff three-run means and sample standard deviations from saved raw responses. It performs no API requests, downloads, or model inference.

## Paired image and exact-geometry evaluation

`src/render_ceiling/frontier_<model>_pilot.py` contains each seven-case runner; `frontier_<model>_run.py` and `frontier_<model>_score.py` contain its 210-case runner and scorer. `src/render_ceiling/prompt_cache.py` preserves shared cache eligibility and token accounting. The original last-label parser is in `src/render_ceiling/frontier_parser.py`. Finished responses are in `results/geometry_substitution/<model>/{pilot,full}/`. `results/geometry_substitution/paired_geometry_outcomes.json` identifies all 17 models, including the original 14-model roster.

Generation uses `CLAUDE_API_KEY` from the environment. The recorded protocol preserves native defaults, sequential repeats within an input for prompt reuse, concurrent independent inputs, fixed cohorts, output allowances, truncation-only replacements, and uncertain-charge reservations. Starting a runner can incur API charges; completed records are retained and must not be overwritten. The default offline audit needs no credential.

Images follow the paths in `data/primary/eval.jsonl`. Read each CIF from `data/primary/structures.json`, convert it with `render_ceiling.render.conventional_cell`, and render with `render_ceiling.render.render_views` using `px=768`, `supercell=(2, 2, 2)`, `radii=0.5`, and the default fixed view order. Use stem `MP_<material_id>` under the manifest's render directory. Recorded input checksums identify the images used for the reported run; PNG encoding can depend on the rendering-library versions. `render_ceiling.reconstruct.projection_matrices` supplies the cameras. The exact-text inputs are in `release/eval_coords_as_text.jsonl`.

## Reconstructed-coordinate handoff

`src/render_ceiling/coordinate_handoff_inputs.py` prepares the 28-case pilot using the saved atomic inputs and Huber coordinates; `src/render_ceiling/coordinate_handoff_sonnet.py` and `src/render_ceiling/coordinate_handoff_parallel.py` implement its API evaluation. `src/render_ceiling/coordinate_handoff_extension.py` adds the remaining 21 parents, and `src/render_ceiling/coordinate_handoff_lattice.py` adds the lattice-only control. `src/render_ceiling/coordinate_handoff_gemma.py` and `src/render_ceiling/coordinate_handoff_qwen.py` implement the complete 112-case local comparisons. Their `--help` describes preparation, inference, and scoring actions.

Sonnet uses the native API and recorded output-limit amendments. Local inference uses Apple Silicon MLX, with model revisions, installed runtime versions, and file checksums retained in each study record. Model files are supplied locally and are not part of this repository. Set `GEMMA_MODEL_PATH` or pass `--model` for Gemma; pass `--model` for Qwen. Prepare in a separate checkout or output directory when recreating a study: preparation refuses to overwrite completed records.

The local-generation runners require network isolation and verify it at startup. On the supported macOS MLX setup, launch inference with `sandbox-exec -p '(version 1)(allow default)(deny network*)' uv run --offline python -m render_ceiling.coordinate_handoff_gemma run --name gemma` (use the Qwen module for Qwen). Scoring and the offline audit do not require this sandbox.

For existing local results, the scorer reads the included records without model loading:

```sh
uv run python -m render_ceiling.coordinate_handoff_gemma score --name gemma
uv run python -m render_ceiling.coordinate_handoff_qwen score --name qwen
```

Scoring validates saved prompts, case mappings, protocol hashes, and source records without requiring model files. Inference additionally validates all local model-file hashes. Use the offline audit for a read-only check. The [handoff report](../results/coordinate_handoff/report.md) explains the matched inputs, pilot and extension roles, means versus majority voting, and descriptive uncertainty. The model-loading imports are optional and invoked only for local generation; the pinned numerical package dependencies are unchanged.

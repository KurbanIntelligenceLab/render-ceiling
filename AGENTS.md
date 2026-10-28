# Repository instructions

This is a research repository supporting the v3 manuscript and supplementary evaluations. Keep the public repository focused on their methods, inputs and reported results.

## Scope and layout

- The current manuscript is `development/cvpr-template-v3/`. Read its main sections and SI when deciding whether material belongs in the public repository. Keep manuscripts and historical versions in ignored `development/`.
- Put reusable numerical implementations in `src/render_ceiling/` with descriptive filenames. The public CLI provides `render-ceiling reconstruct` and `render-ceiling verify`. Keep CLI and Python behavior aligned through the validated `ReconstructionInput`, `Reconstructor` and `ReconstructionResult` interface in `workflow.py`, documented in `REPRODUCIBILITY.md`.
- Keep only completed figure/table outputs and supporting records in `results/`. Figure/table generation scripts belong in `development/`.
- Move experiments and results outside the paper/SI scope into `development/`, preserving the originals. For mixed records, keep only relevant fields and retain their provenance and original checksum.
- Every retained result file has a purpose and checksum in `results/INDEX.json`. Update these only for intentional, verified changes. Do not rewrite numerical evidence merely to make a check pass.
- The README describes what the repository contains. Do not list omitted or retired work. Public documentation and runnable code must not depend on files in `development/`.

## Working practices

- Preserve the scientific method, frozen parameter choices, cohort roles and numerical results unless explicitly asked to change them. Distinguish code refactoring from new experiments.
- Verify reported claims against the manuscript and recorded outputs, then cross-check before reporting completion. Use focused functional tests when changing behavior.
- Keep the workflow lightweight: no CI pipelines, mandatory gates, Ruff, automatic formatting, type-checking setup or pre-commit hooks unless the user requests them.
- Run relevant commands manually: `uv sync --group dev`, `uv run pytest`, `uv run render-ceiling --help`, and `uv run render-ceiling verify`. `--root PATH` lets the verifier target a checkout from another directory. These are local checks, not commit or publishing requirements.
- When checking end-to-end behavior, exercise the public Python API with observations, cameras and lattice; test all three reconstruction methods through the CLI, JSON output, help, successful verification and invalid-input behavior. Keep the small `examples/silicon_projections.json` demonstration runnable. Keep temporary outputs in `development/` or a temporary directory.
- Do not run paid APIs, download new research data, start full evaluation campaigns, stage, commit or publish unless requested. Preserve existing user changes.
- Keep each local checkpoint and its verification results in one file rather than creating branching checkpoint files.
- Use Markdown for documents. Keep each LaTeX paragraph on one source line. Do not add timelines unless requested.
- `LICENSE` contains MIT code terms and CC BY 4.0 data terms; preserve upstream attribution.

`~/SCALAR` means `/Users/jp/SCALAR`.

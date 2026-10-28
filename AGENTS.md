# Repository instructions

This research repository contains reconstruction methods, benchmark inputs and results for the paper and supplementary evaluations.

## Layout

- Keep reusable numerical implementations in `src/render_ceiling/` with descriptive filenames.
- Keep `render-ceiling reconstruct` and the Python API aligned through `ReconstructionInput`, `Reconstructor` and `ReconstructionResult` in `workflow.py`.
- Store completed figure/table outputs and supporting records in `results/`. Publish figure artwork as PDFs alongside its supporting data. Each result file has a purpose and checksum in `results/INDEX.json`.
- Identify figures and tables by their published numbers. Link to figure PDFs and numerical results using those numbers.
- Keep README instructions concise, runnable and consistent with the included files. Document the Python API in `REPRODUCIBILITY.md`.

## Changes and verification

- Preserve scientific methods, parameter choices, cohort roles, numerical results and source attribution when refactoring.
- Update result checksums only for intentional, verified changes.
- Run relevant checks manually: `uv run pytest`, `uv run render-ceiling --help` and `uv run render-ceiling verify`. Use `verify --root PATH` to check a checkout from another directory.
- Exercise all three reconstruction methods, JSON output and invalid-input handling when changing the public interfaces. Keep `examples/silicon_projections.json` runnable.
- Keep the research workflow lightweight. Do not add CI, linting, formatting or pre-commit tooling unless requested.
- Preserve existing changes. Do not stage, commit, publish, run paid APIs, download data or start full evaluation campaigns unless requested.

## Style

- Add comments only when useful. Inline comments must contain 3–5 words.
- Docstrings are allowed only directly under function definitions, on a single physical line using triple double quotes. Do not add module/class docstrings or standalone comments.
- Use Markdown for documentation. Keep descriptions independent of manuscript revisions.
- Preserve dependency versions and original dataset provenance identifiers.
- Follow the code and data terms in `LICENSE`.

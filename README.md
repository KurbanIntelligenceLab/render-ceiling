# Render ceiling and symmetry-aware reconstruction

Code and results for **Separating perception from reasoning in vision-language models: a model-free render ceiling for crystal structures**, including the supplementary evaluations. Reconstruct crystal coordinates from species-labelled orthographic projections and a known lattice using atomic decomposition, localized-or-collective reconstruction, or robust triangulation.

## Run

From the repository root, install with [uv](https://docs.astral.sh/uv/) (Python 3.13):

```sh
uv sync --group dev
uv run render-ceiling reconstruct examples/silicon_projections.json --output outputs/prediction.json
uv run render-ceiling reconstruct examples/silicon_projections.json --method collective --output outputs/collective.json
uv run render-ceiling verify
uv run pytest
```

The included example contains five ideal projections of a four-atom silicon cell. Replace it with your JSON containing `observations` (`xy` centroids and atomic-number `species` per view), `cameras` (5 × 3 × 3), and `lattice` (3 × 3). Coordinates are in angstroms; projection is `cart @ camera[:, :2]`. Each view contains the same atoms, in any order.

`--method` accepts `atomic` (default, paired one-SE selection), `collective` (localized-or-collective split), and `huber` (adaptive comparator). Output JSON contains selected coordinates, species, crystal-system label and full fit diagnostics. Omit `--output` to print JSON. Use `render-ceiling reconstruct --help` for options; the [reproducibility guide](REPRODUCIBILITY.md) documents the Python API and numerical modules.

## Results and reproducibility

Saved inputs, raw responses, protocol settings, and numerical results are in [results/](results/README.md). Descriptive records include:

- [Paired image/exact-geometry outcomes](results/geometry_substitution/paired_geometry_outcomes.json) for 17 VLMs, with [complete frontier-model responses](results/geometry_substitution/).
- [Reconstructed-coordinate accuracy](results/coordinate_handoff/coordinate_handoff_accuracy.json) for the 112-case Sonnet, Gemma, and Qwen comparisons.
- [Atomic reconstruction metrics](results/symmetry_selector_refinement/metrics.json), [per-case outputs](results/symmetry_selector_refinement/heldout.jsonl), and [external collective evaluations](results/collective_validation/study.json).

The [reproducibility guide](REPRODUCIBILITY.md) documents the Python API and numerical implementations. The [model-evaluation protocol](protocols/model_evaluations.md) documents the saved model runs and offline scoring.

[Data](data/) contains benchmark structures and split manifests. [Diagnostic records](release/README.md) contain prompts, classifier settings, and saved predictions. [LICENSE](LICENSE) contains MIT code terms and CC BY 4.0 data terms.

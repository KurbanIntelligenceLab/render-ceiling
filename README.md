# Separating perception from reasoning in vision-language models: a model-free render ceiling for crystal structures

Code and results for the paper and supplementary evaluations. Reconstruct crystal coordinates from species-labelled orthographic projections and a known lattice using atomic decomposition, localized-or-collective reconstruction, or robust triangulation.

## Abstract

Vision-language models (VLMs) often predict plausible structural labels from images without recovering the three-dimensional geometry behind them. End-to-end scores cannot tell whether an error comes from ambiguous views, lost visual information, or flawed reasoning. Multi-view 3D reconstruction faces its own trade-off: rigid symmetry priors erase genuine distortions, while unconstrained triangulation absorbs measurement outliers. We separate visual perception from structural reasoning through an inspectable 3D geometric intermediate. Its foundation is a model-free render ceiling: an exact reference for what calibrated, species-labeled projections determine, obtained by ruling out projective phantoms. Across a 1,950-structure census, every tested combination of four or five calibrated views uniquely determined the 3D sites from complete, species-labeled centroids. Against this reference, replacing images with exact text coordinates lowers the error rate of all 17 evaluated VLMs on crystals. The three frontier models gain 10.0–19.5 percentage points yet still miss 8.1–21.0% of cases. To recover geometry from imperfect observations, our symmetry-aware split reconstruction jointly estimates a symmetric base, coherent 3D physical displacements, and view-specific 2D corruption, adaptively selecting between atomic and collective distortion modes. Relative to Huber triangulation, it reduces coordinate error by 36.7% under Gaussian noise and 41.2% under corruption. Adaptive mode selection further cuts collective error up to 30.4% relative to atomic split across two external cohorts without sacrificing localized fidelity. Given reconstructed rather than Huber coordinates, downstream models improve. Geometric recovery thus becomes an explicit, testable foundation for structural understanding.

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

Saved inputs, raw responses, protocol settings, and numerical results are in [results/](results/README.md). [Figures 1–2 and Tables 1–3, S1–S7](results/README.md#paper-figures-and-tables) link the paper to supporting numerical records. Descriptive records include:

- [Paired image/exact-geometry outcomes](results/geometry_substitution/paired_geometry_outcomes.json) for 17 VLMs, with [complete frontier-model responses](results/geometry_substitution/).
- [Reconstructed-coordinate accuracy](results/coordinate_handoff/coordinate_handoff_accuracy.json) for the 112-case Sonnet, Gemma, and Qwen comparisons.
- [Atomic reconstruction metrics](results/symmetry_selector_refinement/metrics.json), [per-case outputs](results/symmetry_selector_refinement/heldout.jsonl), and [external collective evaluations](results/collective_validation/study.json).

The [reproducibility guide](REPRODUCIBILITY.md) documents the Python API and numerical implementations. The [model-evaluation protocol](protocols/model_evaluations.md) documents the saved model runs and offline scoring.

[Data](data/) contains benchmark structures and split manifests. [Diagnostic records](release/README.md) contain prompts, classifier settings, and saved predictions. [LICENSE](LICENSE) contains MIT code terms and CC BY 4.0 data terms.

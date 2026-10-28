# Render ceiling and symmetry-aware reconstruction

Code and results for **Separating perception from reasoning in vision-language models: a model-free render ceiling for crystal structures**, including the supplementary evaluations. Reconstruct crystal coordinates from species-labelled orthographic projections and a known lattice using atomic decomposition, localized-or-collective reconstruction, or robust triangulation.

## Run

From the repository root, install with [uv](https://docs.astral.sh/uv/) (Python 3.11–3.13):

```sh
uv sync --group dev
uv run render-ceiling reconstruct examples/silicon_projections.json --output development/prediction.json
uv run render-ceiling reconstruct examples/silicon_projections.json --method collective --output development/collective.json
uv run render-ceiling verify
uv run pytest
```

The included example contains five ideal projections of a four-atom silicon cell. Replace it with your JSON containing `observations` (`xy` centroids and atomic-number `species` per view), `cameras` (5 × 3 × 3), and `lattice` (3 × 3). Coordinates are in angstroms; projection is `cart @ camera[:, :2]`. Each view contains the same atoms, in any order.

`--method` accepts `atomic` (default, paired one-SE selection), `collective` (localized-or-collective split), and `huber` (adaptive comparator). Output JSON contains selected coordinates, species, crystal-system label and full fit diagnostics. Omit `--output` to print JSON. Use `render-ceiling reconstruct --help` for options; the [reproducibility guide](REPRODUCIBILITY.md) documents the Python API and numerical modules.

## Paper figures and tables

All finished outputs and supporting records are under [results/](results/). The [detailed results map](results/README.md) describes their contents and raw evaluations.

| Item | Finished output | Supporting data |
|---|---|---|
| Figure 1 | [reconstruction_v2.pdf](results/paper_figures/figure_1/reconstruction_v2.pdf) | [paper_figures/figure_1/crystal.json](results/paper_figures/figure_1/crystal.json) |
| Figure 2 | [collective_v3.pdf](results/paper_figures/figure_2/collective_v3.pdf) | [paper_figures/figure_2/example.json](results/paper_figures/figure_2/example.json) |
| Figure 3 | [paired_outcomes.pdf](results/paper_figures/figure_3/paired_outcomes.pdf) | [paper_figures/figure_3/paired_outcomes.json](results/paper_figures/figure_3/paired_outcomes.json) |
| Table 1 | [table_1.tex](results/paper_tables/table_1.tex) | [symmetry_selector_refinement/metrics.json](results/symmetry_selector_refinement/metrics.json) |
| Table 2 | [table_2.tex](results/paper_tables/table_2.tex) | [cohort 1](results/collective_validation/study.json), [cohort 2](results/mode_replication/study.json) |
| Table S1 | [table_S1.tex](results/paper_tables/table_S1.tex) | [symmetry_selector_refinement/comparisons.json](results/symmetry_selector_refinement/comparisons.json) |
| Table S2 | [table_S2.tex](results/paper_tables/table_S2.tex) | [symmetry_selector_refinement/metrics.json](results/symmetry_selector_refinement/metrics.json) |
| Table S3 | [table_S3.tex](results/paper_tables/table_S3.tex) | [symmetry_selector_refinement/metrics.json](results/symmetry_selector_refinement/metrics.json) |
| Table S4 | [table_S4.tex](results/paper_tables/table_S4.tex) | [paper_audits/external_verified.json](results/paper_audits/external_verified.json) |
| Table S5 | [table_S5.tex](results/paper_tables/table_S5.tex) | [cohort 1](results/collective_validation/study.json), [cohort 2](results/mode_replication/study.json) |
| Table S6 | [table_S6.tex](results/paper_tables/table_S6.tex) | [physical_readout/study.json](results/physical_readout/study.json) |

[Data](data/) contains benchmark structures and split manifests. [Release records](release/README.md) contain prompts, classifier settings and saved model predictions; [protocols](protocols/) describe the evaluations. [LICENSE](LICENSE) contains MIT code terms and CC BY 4.0 data terms.

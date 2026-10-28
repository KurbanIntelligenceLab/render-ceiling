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

## Paper figures and tables

Find each item by its number in the paper PDF; S1–S6 refer to the supplementary tables. Links open figure PDFs or the saved numerical results and supporting data. The [detailed results map](results/README.md) also links the evaluation records.

| Number in the paper PDF | Contents | Results and data |
|---|---|---|
| Figure 1 | Mechanism illustration | [Figure 1 (PDF)](results/paper_figures/figure_1/figure_1.pdf), [Figure 1 data](results/paper_figures/figure_1/crystal.json), [Display geometry](results/paper_figures/figure_1/display_cell.json) |
| Figure 2 | Localized and collective departures | [Figure 2 (PDF)](results/paper_figures/figure_2/figure_2.pdf), [Figure 2 data](results/paper_figures/figure_2/example.json) |
| Figure 3 | Paired pixel and exact-text outcomes | [Figure 3 (PDF)](results/paper_figures/figure_3/paired_outcomes.pdf), [Figure 3 data](results/paper_figures/figure_3/paired_outcomes.json) |
| Table 1 | Atomic reconstruction | [Table 1 results](results/symmetry_selector_refinement/metrics.json), [Per-case data](results/symmetry_selector_refinement/heldout.jsonl) |
| Table 2 | External collective evaluations | [Table 2: cohort 1](results/collective_validation/study.json), [Table 2: cohort 2](results/mode_replication/study.json) |
| Table S1 | Parent-bootstrap coordinate comparisons | [Table S1 results](results/symmetry_selector_refinement/comparisons.json) |
| Table S2 | Gaussian atomic outcomes | [Table S2 results](results/symmetry_selector_refinement/metrics.json), [Per-case data](results/symmetry_selector_refinement/heldout.jsonl) |
| Table S3 | Corrupted-view atomic outcomes | [Table S3 results](results/symmetry_selector_refinement/metrics.json), [Per-case data](results/symmetry_selector_refinement/heldout.jsonl) |
| Table S4 | External coordinate intervals | [Table S4 results](results/paper_audits/external_verified.json) |
| Table S5 | Complete external controls | [Table S5: cohort 1](results/collective_validation/study.json), [Table S5: cohort 2](results/mode_replication/study.json) |
| Table S6 | Support-refit ablation | [Table S6 results](results/physical_readout/study.json), [Verification](results/paper_audits/refit_verification.json) |

[Data](data/) contains benchmark structures and split manifests. [Release records](release/README.md) contain prompts, classifier settings and saved model predictions; [protocols](protocols/) describe the evaluations. [LICENSE](LICENSE) contains MIT code terms and CC BY 4.0 data terms.

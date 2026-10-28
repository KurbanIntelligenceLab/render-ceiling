# Paper and supplementary results

Find each item by its number in the paper PDF; S1–S6 refer to the supplementary tables. Figure links open PDFs. Table links open the saved numerical results and supporting data for that numbered table. Shared records contain results for more than one table.

| Number in the paper PDF | Contents | Results and data |
|---|---|---|
| Figure 1 | Mechanism illustration | [Figure 1 (PDF)](paper_figures/figure_1/figure_1.pdf), [Figure 1 data](paper_figures/figure_1/crystal.json), [Display geometry](paper_figures/figure_1/display_cell.json) |
| Figure 2 | Localized and collective departures | [Figure 2 (PDF)](paper_figures/figure_2/figure_2.pdf), [Figure 2 data](paper_figures/figure_2/example.json) |
| Figure 3 | Paired pixel and exact-text outcomes | [Figure 3 (PDF)](paper_figures/figure_3/paired_outcomes.pdf), [Figure 3 data](paper_figures/figure_3/paired_outcomes.json) |
| Table 1 | Atomic reconstruction | [Table 1 results](symmetry_selector_refinement/metrics.json), [Per-case data](symmetry_selector_refinement/heldout.jsonl) |
| Table 2 | External collective evaluations | [Table 2: cohort 1](collective_validation/study.json), [Table 2: cohort 2](mode_replication/study.json) |
| Table S1 | Parent-bootstrap coordinate comparisons | [Table S1 results](symmetry_selector_refinement/comparisons.json) |
| Table S2 | Gaussian atomic outcomes | [Table S2 results](symmetry_selector_refinement/metrics.json), [Per-case data](symmetry_selector_refinement/heldout.jsonl) |
| Table S3 | Corrupted-view atomic outcomes | [Table S3 results](symmetry_selector_refinement/metrics.json), [Per-case data](symmetry_selector_refinement/heldout.jsonl) |
| Table S4 | External coordinate intervals | [Table S4 results](paper_audits/external_verified.json) |
| Table S5 | Complete external controls | [Table S5: cohort 1](collective_validation/study.json), [Table S5: cohort 2](mode_replication/study.json) |
| Table S6 | Support-refit ablation | [Table S6 results](physical_readout/study.json), [Verification](paper_audits/refit_verification.json) |

Figure 2 uses the [first external cohort](collective_validation/study.json). Figure 3 uses the [individual model predictions](../release/predictions/). Table S4 uses raw records from [cohort 1](collective_validation/study.json) and [cohort 2](mode_replication/study.json).

Additional records support the text and reproducibility details:

| Evaluation | Records |
|---|---|
| Atomic cohort, selection and provenance | [symmetry_selector_refinement/](symmetry_selector_refinement/) |
| Earlier reserved atomic cohort described in SI | [symmetry_defect_validation/](symmetry_defect_validation/) |
| Primary and replication geometric reference | [replication_expansion/](replication_expansion/) |
| Projective-phantom census | [phantom_census_four_view/](phantom_census_four_view/) |
| Paired exact-text diagnostic | [coords_as_text/results.json](coords_as_text/results.json) |
| Raster controls | [supervised_pixel_baseline/](supervised_pixel_baseline/) |
| Numeric classifier and canonical cell-metric partition | [classifier_refreeze/](classifier_refreeze/), [label_granularity_sweep/](label_granularity_sweep/) |
| Pixel-to-coordinate handoff | [perception_transplant/](perception_transplant/) |
| Arithmetic verification of reported results | [paper_audits/](paper_audits/) |

Saved study files contain the paper-specific fields, source-record checksums and cohort analysis roles. In the second external cohort, the paper reports the unchanged-method comparator outputs. Paths and source hashes inside historical manifests describe the original runs.

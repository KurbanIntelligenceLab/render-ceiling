# Paper and supplementary results

Figure and table numbers follow the v3 paper and SI. Table `.tex` files contain the finished table content matching the manuscript. RMSD units and denominators appear in each table caption.

| Paper item | Finished output | Supporting data | Contents |
|---|---|---|---|
| Figure 1 | [reconstruction_v2.pdf](paper_figures/figure_1/reconstruction_v2.pdf) | [paper_figures/figure_1/crystal.json](paper_figures/figure_1/crystal.json) | Mechanism illustration; display geometry in `paper_figures/figure_1/display_cell.json`. |
| Figure 2 | [collective_v3.pdf](paper_figures/figure_2/collective_v3.pdf) | [paper_figures/figure_2/example.json](paper_figures/figure_2/example.json) | Selected ZrZn2 example; cohort record in `collective_validation/study.json`. |
| Figure 3 | [paired_outcomes.pdf](paper_figures/figure_3/paired_outcomes.pdf) | [paper_figures/figure_3/paired_outcomes.json](paper_figures/figure_3/paired_outcomes.json) | Paired counts and deficit shares; individual predictions in `../release/predictions/`. |
| Table 1 | [table_1.tex](paper_tables/table_1.tex) | [symmetry_selector_refinement/metrics.json](symmetry_selector_refinement/metrics.json) | Atomic reconstruction; per-case outputs in `symmetry_selector_refinement/heldout.jsonl`. |
| Table 2 | [table_2.tex](paper_tables/table_2.tex) | [collective_validation/study.json](collective_validation/study.json) | Cohort 1; cohort 2 in `mode_replication/study.json`. |
| Table S1 | [table_S1.tex](paper_tables/table_S1.tex) | [symmetry_selector_refinement/comparisons.json](symmetry_selector_refinement/comparisons.json) | Parent-bootstrap coordinate comparisons. |
| Table S2 | [table_S2.tex](paper_tables/table_S2.tex) | [symmetry_selector_refinement/metrics.json](symmetry_selector_refinement/metrics.json) | Gaussian atomic outcomes; raw outputs in `symmetry_selector_refinement/heldout.jsonl`. |
| Table S3 | [table_S3.tex](paper_tables/table_S3.tex) | [symmetry_selector_refinement/metrics.json](symmetry_selector_refinement/metrics.json) | Corrupted-view atomic outcomes; same raw outputs. |
| Table S4 | [table_S4.tex](paper_tables/table_S4.tex) | [paper_audits/external_verified.json](paper_audits/external_verified.json) | External coordinate intervals; raw cohorts in `collective_validation/study.json` and `mode_replication/study.json`. |
| Table S5 | [table_S5.tex](paper_tables/table_S5.tex) | [collective_validation/study.json](collective_validation/study.json) | Complete cohort 1 controls; cohort 2 in `mode_replication/study.json`. |
| Table S6 | [table_S6.tex](paper_tables/table_S6.tex) | [physical_readout/study.json](physical_readout/study.json) | Support-refit ablation; verification in `paper_audits/refit_verification.json`. |

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

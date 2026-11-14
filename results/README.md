# Research results

Each record has a purpose and SHA256 checksum in [INDEX.json](INDEX.json). Numerical study records are organized by experiment. The links below identify figures and tables by their paper numbers.

| Experiment | Main records |
| --- | --- |
| Image versus exact geometry | [paired_geometry_outcomes.json](geometry_substitution/paired_geometry_outcomes.json), [frontier raw responses](geometry_substitution/), [original model predictions](../release/predictions/) |
| Reconstructed-coordinate handoff | [coordinate_handoff_accuracy.json](coordinate_handoff/coordinate_handoff_accuracy.json) |
| Atomic reconstruction and penalty selection | [metrics.json](symmetry_selector_refinement/metrics.json), [heldout.jsonl](symmetry_selector_refinement/heldout.jsonl), [comparisons.json](symmetry_selector_refinement/comparisons.json) |
| Joint support refitting | [study.json](physical_readout/study.json) |
| Collective reconstruction | [first cohort](collective_validation/study.json), [secondary cohort](mode_replication/study.json) |
| Geometric recovery and replication | [Census tolerance sweep](replication_expansion/census_tolerance_results.json), [primary and replication records](replication_expansion/) |
| Projective phantoms | [records](phantom_census_four_view/) |
| Raster controls | [records](supervised_pixel_baseline/) |
| Numeric classifier | [records](classifier_refreeze/), [cell-metric partition](label_granularity_sweep/) |

The handoff uses the same 112 cases for three runs per model and retains its initial 28-case controls separately. Each study includes frozen prompts, case mappings, generation settings, outputs, and scoring. The second external cohort is a secondary analysis of the unchanged-method comparator.

## Paper figures and tables

Tables link directly to the existing numerical records. Tables S1–S7 are numbered in their order of appearance in the supplement. Figure entries link to supporting data; artwork and manuscript sources are kept outside the released repository.

| Paper item | Records |
| --- | --- |
| Figure 1: reconstruction overview | [Crystal](paper_figures/figure_1/crystal.json), [display cell](paper_figures/figure_1/display_cell.json) |
| Figure 2: reconstruction comparisons | [Comparisons](paper_figures/figure_2/coordinate_comparisons.json), [example](paper_figures/figure_2/example.json) |
| Table 1: Paired geometry substitution | [Paired outcomes](geometry_substitution/paired_geometry_outcomes.json) |
| Table 2: Atomic reconstruction | [Atomic metrics](symmetry_selector_refinement/metrics.json), [Refit study](physical_readout/study.json) |
| Table 3: Coordinate handoff | [Handoff accuracy](coordinate_handoff/coordinate_handoff_accuracy.json) |
| Table S1: Complete paired counts | [Paired outcomes](geometry_substitution/paired_geometry_outcomes.json) |
| Table S2: Atomic coordinate intervals | [Atomic metrics](symmetry_selector_refinement/metrics.json), [Per-case outputs](symmetry_selector_refinement/heldout.jsonl) |
| Table S3: Gaussian reconstruction | [Atomic metrics](symmetry_selector_refinement/metrics.json) |
| Table S4: Corrupted-view reconstruction | [Atomic metrics](symmetry_selector_refinement/metrics.json) |
| Table S5: Support-refit ablation | [Refit study](physical_readout/study.json) |
| Table S6: External coordinate intervals | [Cohort 1](collective_validation/study.json), [Cohort 2](mode_replication/study.json) |
| Table S7: Complete external controls | [Cohort 1](collective_validation/study.json), [Cohort 2](mode_replication/study.json) |

# Research results

Each record has a purpose and SHA256 checksum in [INDEX.json](INDEX.json). Records are organized by experiment rather than manuscript numbering.

| Experiment | Main records |
| --- | --- |
| Image versus exact geometry | [paired_geometry_outcomes.json](geometry_substitution/paired_geometry_outcomes.json), [frontier raw responses](geometry_substitution/), [original model predictions](../release/predictions/) |
| Reconstructed-coordinate handoff | [coordinate_handoff_accuracy.json](coordinate_handoff/coordinate_handoff_accuracy.json) |
| Atomic reconstruction and penalty selection | [metrics.json](symmetry_selector_refinement/metrics.json), [heldout.jsonl](symmetry_selector_refinement/heldout.jsonl), [comparisons.json](symmetry_selector_refinement/comparisons.json) |
| Joint support refitting | [study.json](physical_readout/study.json) |
| Collective reconstruction | [first cohort](collective_validation/study.json), [secondary cohort](mode_replication/study.json) |
| Geometric recovery and replication | [records](replication_expansion/) |
| Projective phantoms | [records](phantom_census_four_view/) |
| Raster controls | [records](supervised_pixel_baseline/) |
| Numeric classifier | [records](classifier_refreeze/), [cell-metric partition](label_granularity_sweep/) |

The handoff uses the same 112 cases for three runs per model and retains its initial 28-case controls separately. Each study includes frozen prompts, case mappings, generation settings, outputs, and scoring. The second external cohort is a secondary analysis of the unchanged-method comparator.

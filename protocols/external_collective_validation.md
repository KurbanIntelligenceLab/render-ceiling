# External collective reconstruction evaluation

Two disjoint cohorts contain 80 distinct reduced compositions each from a saved 2,000-entry MC3D PBE-v1 frame. Each parent supplies original, localized and collective variants, two camera sets, and Gaussian noise with or without one corrupted centroid: 960 cases per cohort.

Cohort 1 prospectively evaluates the frozen combined method. Cohort 2 reports a secondary analysis of unchanged-method comparator outputs. Material-bootstrap resampling keeps related variants and cameras together. The three primary coordinate comparisons use 98.333% intervals from 20,000 draws.

The complete source frame, eligibility decisions, structures, schedules, outputs and analysis are retained in the [first cohort](../results/collective_validation/study.json) and [second cohort](../results/mode_replication/study.json) records.

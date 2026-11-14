# Joint support-refit ablation

The ablation reuses all 1,568 cases of the second reserved atomic cohort. The no-refit pipeline retains penalized physical and observation-error coefficients in each fold and final fit, refitting only affine coefficients. All other rules remain unchanged; altered fold losses may change candidate selection.

The ablation compares paired one-SE and fixed-four with and without joint refitting. Descriptive 95% intervals use 5,000 paired parent-bootstrap draws. Raw outcomes and scores are in [the support-refit record](../results/physical_readout/study.json).

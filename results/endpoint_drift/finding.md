CHECKPOINT: endpoint_drift   GAP: G3/G5/G6 all assume a new model arm run today is comparable
     to the released K=3 ladder. That assumption was never tested. It is false.
STATUS: DONE, AND IT BLOCKS G3/G5/G6 AS SCOPED. A validation slice against a released arm does not
     reproduce it. Total cost of establishing this: $6.82 over 184 calls, against the ~$404 the
     full programme would have cost on a premise that does not hold.

WHAT WAS RUN. x-ai/grok-4.5 re-queried through the same harness path, same frozen prompt text, same
K=3 majority vote, same frozen render protocol (conventional cell, 2x2x2 supercell, px=768,
radii=0.5), on the first 20 structures of data/e3/eval.jsonl. Same sample, same structures, same
truth labels as release/predictions/frontier__x-ai__grok-4_5__K3.json (verified: 20/20 id overlap,
0/20 truth mismatches).

=================  THE RESULT  ===============================================================
  released (frontier arm, same 20 structures)        7/20
  re-run today, provider default reasoning           1/20
  re-run today, effort: minimal                      0/20

=================  IT IS NOT SAMPLING NOISE, AND NOT A DECODE SETTING  =======================
Pairwise agreement on the 20 predictions:

  new-default  vs  new-minimal      17/20
  new-default  vs  released         13/20
  new-minimal  vs  released         13/20

The two new runs used very different reasoning budgets (9,099 vs 1,266 output tokens per call, a
7.2x difference) and still agree with each other far more than either agrees with the release. If
the discrepancy were temperature-0.7 sampling variance, the new runs would disagree with each other
about as much as they disagree with the release. They do not. The endpoint behind the identifier
`x-ai/grok-4.5` is serving a different system than the one the paper's arms were measured on.

The failure has a consistent shape: the current endpoint collapses triclinic onto monoclinic.
Predicted-class distribution on 20 triclinic-truth structures:

  released  monoclinic 11, triclinic 7, orthorhombic 2
  new def   monoclinic 15, orthorhombic 3, triclinic 1, hexagonal 1
  new min   monoclinic 18, orthorhombic 2

SAMPLING CAVEAT ON THIS SLICE. The first 20 rows of eval.jsonl are all triclinic, the hardest
stratum, where the released arm itself scores only 10/30 = 0.333. That amplifies the visible gap.
It does not cause it: the agreement structure above is stratum-independent evidence. A stratified
20-structure slice would give a tighter estimate of the drift magnitude and has not been run.

A SECOND, SEPARATE FINDING. At provider default the model emitted 9,099 output tokens per call
against a max_tokens of 900, one probe reaching 16,524 tokens at $0.10 and 384 s for a SINGLE call.
The released arms show no such behaviour. This is a property of THIS endpoint, not of vision models
generally: a claude-opus-5 probe on the same task returned 731 output tokens at its own default.
Notably, on a single paired probe of one structure, 16,524 reasoning tokens and 894 tokens
(default and effort:minimal respectively) produced the SAME wrong answer on the probe
structure, and minimal reasoning scored no better than default across the slice (0/20 vs 1/20).

=================  WHY THIS BLOCKS THE REMAINING GAPS  =======================================
G3 (current-frontier arm), G5 (model arms at scale) and G6 (prompt sensitivity) are all comparisons
of a NEW measurement against the EXISTING K=3 ladder. If the existing rows cannot be reproduced on
their own endpoints, any such comparison confounds the effect under study with uncontrolled model
drift. A frontier arm run today could not distinguish "a current model closes the gap" from "the
endpoints moved". The gaps stay open, and the honest reason is now recorded rather than assumed.

G4 (reasoning budget) is the one that survives, because it is an internal contrast between two
settings of the SAME model at the SAME time and needs no comparison to the released ladder. The
slice above is already weak evidence that the budget does not help on this task.

=================  WHAT THIS IS WORTH TO THE PAPER  ==========================================
This is direct evidence for the paper's own thesis. A leaderboard is a claim about models at a
moment; re-running it later does not recover the same numbers, because the model identifiers are
not stable referents. R1, the render ceiling, is model-free: the view sweep in view_subset_sweep reproduced it
exactly at 200/210 = 0.9524 through an independent code path. The contrast between a ceiling that
reproduces and a leaderboard that does not is the argument for reporting model-free bounds, and it
was obtained here as a measurement rather than an assertion.

SCOPE. One model, one 20-structure single-stratum slice, one point in time. It is enough to
invalidate the comparability premise behind G3/G5/G6, which is what it was run to test. It is not
enough to quantify drift across the roster, and no such claim is made.

Reproduce: python scripts/run_model_arm.py --model x-ai/grok-4.5 --arm r4 --K 3 \
  --ids <20 eval ids> --structures data/e3/structures.json --labels data/e3/eval.jsonl --out <path>
Artifacts: rerun_default_reasoning.json, rerun_minimal_reasoning.json, released_same_20.json,
and the runner scripts/run_model_arm.py.

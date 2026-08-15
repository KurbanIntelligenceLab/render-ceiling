CHECKPOINT: reasoning_budget   GAP: G4 / red flag R11a. Frontier models ship extended thinking
     by default, and the paper cites work showing chain-of-thought can DEGRADE visual spatial
     reasoning. No released arm set a reasoning parameter, so every scored model ran at its
     provider's default and the paper could not say whether the budget mattered.
STATUS: DONE. A CLEAN PAIRED NULL. 5.4x the reasoning tokens buys ZERO accuracy on this task.
     This is the one API gap that endpoint drift (endpoint_drift) does not block, because it is an internal
     contrast between two settings of the SAME model at the SAME time and needs no comparison to
     the released ladder. Cost $34.00 over 1,260 calls.

WHAT WAS RUN. claude-opus-5, the frozen main_zeroshot prompt verbatim, frozen five-view renders
(conventional cell, 2x2x2 supercell, px=768, radii=0.5), K=3 majority vote, temperature 0.7, on the
full 210-structure evaluation sample. Two legs, paired per structure:

  leg A  reasoning = {"effort": "minimal"}   -- reproduces the released token profile
  leg B  no reasoning field sent             -- exactly what every released arm did (the control)

=================  THE RESULT  ===============================================================
                    accuracy        out-tok/call    cost      wall
  minimal           130/210 = 0.6190      89       $14.45     608 s
  default           130/210 = 0.6190     482       $19.55   2,073 s

  default emits 5.4x the output tokens, costs 1.35x more, and takes 3.4x longer
  for IDENTICAL accuracy.

The identical totals are not the same predictions. Agreement is 169/210 = 0.8048, so the two
settings disagree on 41 structures and happen to break even:

  McNEMAR, exact binomial on discordant pairs
    minimal right / default wrong   13
    default right / minimal wrong   13
    discordant 26,  two-sided p = 1.0000

That is as clean a null as this design can produce: the budget reshuffles which structures are
answered correctly without moving the total in either direction.

A COST THE DEFAULT PAYS THAT ACCURACY HIDES. The default leg returned empty content on 11 of 210
structures (22 individual calls across K=3), which score as unanswered; the minimal leg returned
zero. Extended thinking therefore consumed the token budget without emitting an answer often enough
to matter, and those 11 count against it in the totals above. Restricting to the 199 structures BOTH
legs answered, minimal is 126/199 = 0.6332 and default 130/199 = 0.6533, with McNemar 9 versus 13
discordant and p = 0.5235 — still no detectable difference. So the null is not an artifact of the
unanswered structures: the two settings tie on the full sample and remain statistically
indistinguishable on the subset where both produced an answer.

=================  PER-STRATUM (minimal / default)  ==========================================
  triclinic      0.067  /  0.000
  monoclinic     0.767  /  0.767
  orthorhombic   0.367  /  0.400
  tetragonal     0.767  /  0.900
  trigonal       0.867  /  0.900
  hexagonal      0.500  /  0.367
  cubic          1.000  /  1.000

The reshuffling is structured, not random. Extended thinking helps on tetragonal (+0.133) and
trigonal (+0.033) and hurts on hexagonal (-0.133) and triclinic (-0.067) — the two strata where the
cell metric is closest to degenerate. Cubic is saturated at 1.000 under both, and monoclinic is
unchanged to three decimals. So the null total conceals a real trade: more deliberation moves
accuracy toward the strata with distinctive metrics and away from the ambiguous ones. With n = 30
per stratum these per-stratum differences are individually underpowered and are reported as
description, not as claims.

=================  WHAT THIS SETTLES  ========================================================
R11a asked the paper to state per model whether extended thinking was enabled. The honest answer was
that no arm ever set the parameter, so all ran at provider defaults that were never logged. This
checkpoint upgrades that from a disclosure to a measurement: on this task, at this sample size, and for THIS ONE MODEL, the
reasoning budget does not change what it gets right, and the paper can say so with a
paired test rather than an apology.

It also matters for the ceiling argument. The gap between the model (0.6190) and the render ceiling
(0.9524) is not a deliberation deficit. Giving the model 5.4x more reasoning tokens closes none of
it, which is consistent with the paper's claim that the binding constraint is perception rather than
downstream inference.

SCOPE. One model, one prompt, one sample, one pair of settings. It does not establish that reasoning
budgets are irrelevant to spatial tasks generally, and no such claim is made. `effort: minimal` is
also not identical to the released arms' configuration — it is the closest reproducible stand-in for
a token profile the released arms achieved by running before extended thinking became a default.

Reproduce:
  python scripts/run_model_arm.py --model anthropic/claude-opus-5 --arm r4 --K 3 \
    --reasoning '{"effort":"minimal"}' --ids <210 eval ids> \
    --structures data/e3/structures.json --labels data/e3/eval.jsonl --out opus5_minimal.json
  (omit --reasoning for the default leg)
Artifacts: opus5_minimal.json, opus5_default.json (per-structure predictions and votes),
results.json (the paired contrast and McNemar test).

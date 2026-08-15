# Checkpoint 1.2 — the delta/tau relationship in the main text

## What was required

State delta = 0.15 A explicitly in the method (it appeared only inside the algorithm block), state
tau = 0.01 A next to it, and add the condition that delta must be <= tau to avoid over-merging.

## What was written

A new paragraph in Section 3.1 (`sections/03_method.tex`), headed "Two tolerances, and why they must be
tied", placed immediately after the oracle description and before Definition 1. It states:

- the oracle carries a tolerance delta at which it accepts a ray intersection and merges candidates;
- the label map carries the symmetry tolerance tau at which spglib decides;
- these are independent knobs and they interact: if delta > tau the merge can combine two genuinely
  distinct atoms, displacing the survivor by an amount spglib can see, so the reconstruction is faithful
  in atom count yet wrong in symmetry;
- tau = 0.01 A throughout; the released pipeline shipped delta = 0.15 A, fifteen times tau;
- the identifiability results use delta <= tau, and Section 4.2 traces the whole frontier;
- the operating rule is delta <= tau, which is what makes the merge in Theorem 1(c) the one the theorem
  assumes.

Every oracle number in the revised manuscript is now reported with both tolerances stated, either in the
sentence or in the table caption.

## Why the condition is delta <= tau and not something looser

Verified against the joint grid in `results/option_a_frontier/results.json` (`delta_symprec_grid`),
correct of 210 over delta in {0.001, 0.01, 0.05, 0.15} against symprec in {0.001, 0.01, 0.05, 0.1}:

| delta \ tau | 0.001 | 0.01 | 0.05 | 0.1 |
|---|---|---|---|---|
| 0.001 | 210 | 210 | 210 | 209 |
| 0.01  | 208 | 210 | 210 | 209 |
| 0.05  | 204 | 206 | 210 | 208 |
| 0.15  | 198 | 200 | 203 | 206 |

No cell with delta > tau reaches 210, and the cells that do reach it all satisfy delta <= tau. The
manuscript's claim is exactly this and no more: reaching the full sample requires delta <= tau. The
residual loss at (delta = 0.01, tau = 0.001) is the same over-merging effect one decade down, which is why
the condition is relative rather than an absolute threshold on delta.

## Where it appears

- `sections/03_method.tex`: the new paragraph, plus the delta value in Table 1's note b.
- `sections/04_results.tex`: Section 4.2 and Table 3, both captioned with tau and delta.
- `main.tex`: the abstract names the condition ("at an extraction tolerance matched to the symmetry
  tolerance") rather than deferring it.

PRE-REGISTRATION — CP23 depth-ordering sufficiency (directive Stage 0b)
WRITTEN BEFORE COMPUTING. This is the stated geometric precondition for the proposed
depth-restoration ladder (Stage 1): "if depth ordering adds nothing on box-ambiguous structures, do
not run Stage 1."

THE QUESTION. Depth-graded colour — the directive's main experimental rung — supplies ORDINAL depth,
not exact coordinates. So the precondition is: does (projected position, depth RANK) determine the
crystal system where projected position ALONE does not?

OPERATIONALIZATION, fixed now. For each structure and each of the 3 axis views, build three variants
of the atom coordinate set and run spglib crystal-system detection on each:
  P  PROJECTION ONLY   — the view-axis coordinate replaced by a CONSTANT (all atoms coplanar).
                         This is what a flat render delivers geometrically.
  R  DEPTH RANK        — the view-axis coordinate replaced by its RANK among all atoms, rescaled to
                         the original extent. This is what ordinal depth-grading delivers.
  F  FULL              — unmodified. The upper bound.
Recovered crystal system is compared to the true label. Lattice is preserved in all three variants
(the cell edges are drawn, so the lattice is given); only atom positions are degraded.
Report on stratified samples from BOTH evaluation sets, split by box-sufficiency.

THE READING, COMMITTED BEFORE THE NUMBERS EXIST.
  D1  R substantially above P ON THE BOX-AMBIGUOUS STRATUM -> depth ordering carries the missing
      information there. This is the precondition Stage 1 needs, and Stage 1 is licensed.
  D2  R indistinguishable from P on box-ambiguous -> ordinal depth adds nothing where it is needed.
      DO NOT RUN STAGE 1 as an ordinal-depth intervention; only the exact-height rung (which leaks)
      could work, and that is an oracle ceiling rather than a deployable protocol.
  D3  R substantially above P but ONLY on the box-SUFFICIENT stratum -> depth ordering helps where the
      answer was already available. Stage 1 would measure a redundant gain; report as such.
  D4  P already recovers the crystal system at a high rate -> the projection itself is nearly
      sufficient and the whole occlusion line of argument is weaker than assumed.

WHAT NO OUTCOME LICENSES. This is geometry with PERFECT atom localisation assumed, exactly like the
oracle. It bounds what depth information could carry GIVEN extraction; it says nothing about whether a
model reads it. A positive result here is necessary but not sufficient for Stage 1 to be worth running.

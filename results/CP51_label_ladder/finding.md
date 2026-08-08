CHECKPOINT: CP51_label_ladder   GAP: the benchmark scored ONE 7-way label. A single label with a floor at
     0.5286 is a probe, not a benchmark, and gives no difficulty axis. (ICLR directive)
STATUS: DONE. FOUR LABELS SCORED FOR THREE MODEL-FREE ARMS. The headline is that the ORACLE IS FLAT ACROSS
     GRANULARITY while the tabular baseline COLLAPSES — which strengthens the ceiling argument and
     simultaneously explains what the cell metric does and does not encode.

  label            classes    chance    chance    floor3    RF19    ORACLE (R1)
                   present   majority  1/n_cls
  crystal system    7/7       0.1429    0.1429    0.5286   0.8952     0.9524
  bravais lattice  13/14      0.2286    0.0714    0.4762   0.9095     0.9429
  point group      21/32      0.1381    0.0312    0.4476   0.7143     0.9524
  space group      44/230     0.1095    0.0043    0.4048   0.6810     0.9429

WHAT THE ORACLE ROW MEANS, AND IT IS THE RESULT THAT MATTERS.
The oracle does not degrade with label granularity: 0.9524 / 0.9429 / 0.9524 / 0.9429. It is FLAT because
spglib reads the reconstruction exactly — a structure is either reconstructed correctly, in which case all
four labels follow, or it is not. So the identifiability ceiling is NOT specific to crystal system: the
renders determine SPACE GROUP to 0.9429 given ideal extraction. The paper's central claim generalises from
a 7-way label to a 230-way one, which is the single most useful thing this checkpoint returns.

WHAT THE RF ROW MEANS, AND IT SHARPENS THE FLOOR ARGUMENT.
The 19-feature cell-metric random forest goes 0.8952 -> 0.9095 -> 0.7143 -> 0.6810. Crystal system and
Bravais lattice are nearly metric-determined, which is expected: the metric constraints ARE the crystal
system's defining conditions, and centering is partly visible in the conventional cell. Point group and
space group are NOT, and the reason is substantive rather than statistical: they depend on the ATOM
POSITIONS AND SITE SYMMETRIES, which 19 lattice numbers do not encode. So the finer labels are a genuinely
harder task for a metric-only model, and the gap between the RF and the oracle WIDENS from 0.0572 at
crystal system to 0.2619 at space group.
This is the cleanest available answer to "your task is trivial for a tabular baseline": it is, at crystal
system, and it stops being so two rungs up the ladder.

BRAVAIS EXCEEDS CRYSTAL SYSTEM FOR THE RF (0.9095 vs 0.8952) AND THAT IS NOT AN ERROR. 13 of 14 Bravais
classes are present and the centering letter is partly determined by the conventional cell the features are
computed on, so the extra classes come with extra metric signal. Reported as observed, not smoothed.

MACRO-F1 IS WITHHELD ON THE FINER LABELS, AS PRE-REGISTERED. Space group has 18 SINGLETON classes among the
44 present (of 230 possible) and point group has 3 among 21. Macro-F1 over mostly-singleton support is
arithmetic, not information. Micro accuracy plus classes-present is reported instead, and the absence is
stated rather than left as a gap.

BOTH CHANCE DEFINITIONS ARE REPORTED BECAUSE THEY DIVERGE SIXFOLD. For space group, majority-class is
0.1095 and 1/n_classes is 0.0043. Quoting only 1/230 would make every arm look far better than it is.

A DEFECT I FOUND BY AN IMPOSSIBLE ORDERING, RECORDED BECAUSE THE DETECTION METHOD IS REUSABLE.
My first oracle pass derived the Bravais label as get_lattice_type()[0] + symbol[0] and returned 0.7571 —
BELOW the space-group score of 0.9429. That is impossible: Bravais is strictly coarser than space group, so
a correct Bravais derivation cannot score lower. The cause was my derivation, not the oracle. labels.py maps
the CRYSTAL SYSTEM to a lattice-family letter with trigonal DELIBERATELY grouped as 'h', then appends the
centering from the space-group symbol; get_lattice_type() does not reproduce that grouping. Rerunning with
the pipeline's own bravais_lattice() gives 0.9429 and restores the ordering.
THE LESSON: when a coarser label scores worse than a finer one derived from the same object, the derivation
is wrong. That ordering constraint is now a cheap correctness check on any future label added to the ladder.

WHAT THIS DOES NOT SHOW. Model arms are NOT re-prompted here, so the ladder currently has no learned-VLM
row: the models were only ever asked the 7-way question, and scoring them on space group would require a
new prompt and a new run. The ladder as it stands is a MODEL-FREE difficulty axis (chance, floor, tabular,
oracle). Wyckoff occupation is absent from the sidecar and out of scope.

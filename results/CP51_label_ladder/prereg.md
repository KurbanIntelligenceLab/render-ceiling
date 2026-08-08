PRE-REGISTRATION — CP51 label ladder
Committed BEFORE the run. CPU only for the oracle and classical arms; model arms reuse stored per-structure
predictions where the label is derivable, and are NOT re-prompted in this checkpoint.

GAP. The benchmark scores ONE 7-way label. A single label with a floor at 0.5286 is a probe, not a
benchmark, and it gives no difficulty axis.

WHAT IS ALREADY AVAILABLE, VERIFIED BEFORE PLANNING. All 1820 structures in labels_sidecar.json already
carry crystal_system, bravais_lattice, point_group and space_group. So the ground truth costs nothing;
this checkpoint is a scoring exercise, not a labelling one. WYCKOFF OCCUPATION IS NOT in the sidecar and
is therefore OUT OF SCOPE here rather than silently skipped.

METHOD. For each of four labels — crystal system (7 classes), Bravais lattice (14), point group (32),
space group (230) — report on the original eval set (n=210):
  - CHANCE, computed as the majority-class rate AND as 1/n_classes, since for 230 space groups those
    differ enormously and quoting 1/230 alone would understate the trivial baseline;
  - the SHAPE-FREE FLOOR (3 features: n_sites, density, volume) refit per label, same protocol as CP28;
  - the RANDOM FOREST on the 19 lattice-metric features, refit per label from the frozen specification;
  - the GEOMETRIC ORACLE (R1), which returns a reconstruction whose symmetry is computed by spglib, so all
    four labels come from the same reconstruction at no extra cost.

DECISION RULE, fixed now. This checkpoint is DESCRIPTIVE: it establishes a difficulty axis, so there is no
pass/fail branch. What IS pre-registered:
  D1  If the oracle stays high on all four labels, the identifiability result generalises beyond crystal
      system and the ladder is a genuine difficulty axis.
  D2  If the oracle DEGRADES sharply with label granularity, then the renders support coarse symmetry but
      not fine, which BOUNDS the paper's central claim to crystal system and must be said plainly.
  D3  If the shape-free floor stays close to the RF on the finer labels, the finer labels are ALSO
      predictable from size-and-density regularities, and their apparent difficulty is not about shape.

WHAT WOULD MAKE A ROW UNINFORMATIVE. Any label whose eval set contains classes with a single member
cannot support a meaningful macro-F1; report micro accuracy plus the class count actually present, and do
NOT report macro-F1 where the support is degenerate. For 230 space groups on 210 structures most classes
are absent by construction, and that must be stated rather than hidden behind a low number.

EXPECTED, STATED FIRST. I expect monotone degradation with granularity for every arm, and I expect the
oracle to degrade LESS than the learned arms because spglib reads the reconstruction exactly. If the
oracle degrades as fast as the models, the reconstruction is losing fine detail and the ceiling argument
weakens for the finer labels.

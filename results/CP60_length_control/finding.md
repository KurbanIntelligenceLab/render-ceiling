CHECKPOINT: CP60_length_control   GAP: the symbolic bucket is a residual R1-R3 against a solver. If R3
              accuracy falls as the coordinate list lengthens, part of that residual is long-list
              handling rather than symmetry reasoning. (directive P4 / A1b)
STATUS: DONE. BRANCH L2 FIRES, THE CONFOUND CONTROL DOES NOT RESCUE IT, AND A HEADLINE NUMBER IS
        DOWNGRADED FROM A MEASUREMENT TO AN UPPER BOUND.
        Zero new API calls: CP53's 14 per-structure prediction vectors already existed and all 14
        reproduce their recorded R3 accuracies exactly.

THE ASSOCIATION IS NEGATIVE AND POOLED-SIGNIFICANT. Spearman rho between per-structure R3 correctness
and conventional-cell atom count, original eval, n=210, K=3:
  pooled over 14 models, 2940 model-structure pairs   rho = -0.0908   p = 8.13e-07
  individually significant at 0.05                    2 of 14, both negative
  13 of 14 models have rho < 0; only claude-opus-4.8 is positive (+0.0484, p = 0.485)
Effect size at the atom-count median (14 atoms): pooled R3 accuracy 0.5551 on small cells against
0.5129 on large, a drop of 0.0422, 816/1470 against 754/1470, Fisher p = 0.0241.

THE PRE-REGISTERED CONFOUND CONTROL FAILS TO EXPLAIN IT, WHICH IS THE INFORMATIVE PART. The prereg
named the obvious alternative in advance: atom count correlates with crystal system (rho = -0.1866
against symmetry rank, p = 0.0067), so the association could be symmetry difficulty rather than list
length. Computing rho WITHIN each system and combining:
  cubic -0.4438   monoclinic -0.3150   tetragonal -0.3369   hexagonal -0.0541   triclinic -0.0542
  orthorhombic +0.1422   trigonal +0.3246
  5 of 7 systems negative; mean within-system rho = -0.1053 against the pooled -0.0908
THE WITHIN-SYSTEM ASSOCIATION IS STRONGER THAN THE POOLED ONE, NOT WEAKER. Controlling for the
confound does not attenuate the effect by 16%; it AMPLIFIES it by 16%. So the effect is not symmetry
difficulty masquerading as length — the length association exists inside symmetry classes, most
sharply in cubic and tetragonal, which are the classes where a long coordinate list is least
informative per row.

WHAT THIS DOWNGRADES. CP53's median perception share is 0.3092, so the symbolic share is 0.6908. Part
of that residual is demonstrably list handling. THE SYMBOLIC SHARE IS THEREFORE AN UPPER BOUND ON A
SYMMETRY-REASONING DEFICIT, NOT A MEASUREMENT OF ONE, and it must be reported that way in the same
paragraph as the median. Per directive A1a the component is also renamed from "reasoning share" to
"symbolic share", defined at first use as the residual between a deterministic solver and a model given
the same exact geometry.

WHAT IT DOES NOT TOUCH. The oracle-to-model gap is measured against PIXELS, not text, so no outcome
here moves it. The direction of CP53's headline finding is also unaffected: models given exact geometry
still fall short of the solver, and the shortfall is still larger than the perception component for
most models. What changes is the interpretation of the residual's composition.

TWO HONEST LIMITS. The effect is small (0.042 accuracy across the median split) and it is measured on
the original sample only, where atom counts run 2 to 57 with median 14; the expansion sample's larger
cells would give more spread and are not used here. And two systems run positive, which the report
states rather than pooling away — in trigonal (+0.3246) more atoms go with HIGHER R3 accuracy, which
is consistent with atom count proxying symmetry richness in that class, exactly the confound the
prereg named. The pooled claim survives because 5 of 7 are negative and the two largest-magnitude
negatives are twice the largest positive, not because every class agrees.

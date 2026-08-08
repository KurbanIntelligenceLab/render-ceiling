CHECKPOINT: CP13_trigonal_hexagonal    GAP: Q4 — is the trigonal/hexagonal confusion intrinsic to
                                        the render, or a model failure?
STATUS: DONE for the model half (the human half is CP11, still awaiting raters). RESULT: the two
        arms confuse the SAME pair in OPPOSITE DIRECTIONS, which is much stronger evidence for an
        intrinsic render ambiguity than either arm alone.
        Found while closing the brief's §6 requirement to report macro-F1 and per-system
        breakdowns everywhere; it was not the object of the audit.

=================  THE MIRROR  =================
DIRECT arm (B1, K=8 majority vote, 210 composition-exclusion structures):
    trigonal   2/30 correct   -> 28 of 30 called HEXAGONAL
    hexagonal 30/30 correct   -> never called anything else
CHAIN arm (recorded earlier, CP7b prediction support):
    all 30 true hexagonals called TRIGONAL; the chain never emits "hexagonal" at all.
Same pair. Opposite direction. One arm collapses trigonal into hexagonal, the other collapses
hexagonal into trigonal. Neither direction is shared, so neither is a learned bias inherited from
a common source — what is shared is that THE PAIR IS NOT SEPARATED.

WHY THIS IS THE EXPECTED FAILURE IF THE AMBIGUITY IS INTRINSIC. In the conventional hexagonal
setting a trigonal cell and a hexagonal cell have the SAME metric (a=b, gamma=120 deg), so the
dashed cell outline — the primary cue, sufficient for 41/50 of the CP11 sample — cannot separate
them. Separation requires reading the ATOM MOTIF inside the cell. A model that reads the outline
well and the motif poorly must collapse the pair, and WHICH way it collapses is then determined by
its prior, not by the image. Two arms with different training collapsing it in different
directions is exactly that signature.

CONSEQUENCE FOR MACRO-F1, AND WHY THE BRIEF IS RIGHT TO REQUIRE IT. B1 micro 0.6190 vs macro-F1
0.5793 — a 4-point gap driven almost entirely by trigonal (per-system F1 0.125, next worst
tetragonal 0.5714). Micro alone hides a class the model essentially cannot do. Full per-system F1:
    cubic 0.5909 | hexagonal 0.6818 | monoclinic 0.6970 | orthorhombic 0.7222
    tetragonal 0.5714 | triclinic 0.6667 | trigonal 0.1250
Note hexagonal's F1 (0.6818) is depressed BELOW its perfect recall precisely because it absorbs
28 false positives from trigonal — the pair damages both classes, which a recall-only view misses.

OTHER CONFUSIONS, for completeness: cubic->tetragonal 15, triclinic->monoclinic 10,
tetragonal->orthorhombic 8. Every one is a symmetry-descent pair (a higher-symmetry system read as
its lower-symmetry subgroup, or vice versa), which is the physically sensible error mode and
further evidence the model reads cell geometry rather than guessing.

WHAT THIS DOES NOT SETTLE. It shows the pair is hard for BOTH model arms and explains why
geometrically. It does NOT establish that the pair is unresolvable from the renders — only a human
who separates it cleanly would show the information IS present and the failure is the models'.
That is exactly CP11's pre-registered P3' prediction (trigonal is the single predicted human
failure mode, 0/7 separable by cell outline alone), and it remains the open half of Q4.

REPRODUCE
  from e7/gen_B1_s0_k8.json: majority-vote each record, tabulate (truth, pred) pairs,
  macro-F1 = unweighted mean of per-class F1 over the 7 systems.

CHECKPOINT: claim_ledger   GAP: no single document states what this paper claims, what each claim
                                rests on, and which prior work occupies it. (ICLR plan, Phase F)
STATUS: DONE. TEN CLAIMS ENUMERATED. Four are contributions, two are supporting replications, TWO ARE
        WITHDRAWN, and two are explicitly NOT CLAIMED because prior work occupies them. Every value in
        the ledger is read from a results.json, not retyped — one entry (C5) was caught coming from a
        hardcoded fallback rather than its source file and was corrected.

=================  CONTRIBUTIONS  ==============================================================
C1  The geometric oracle. Inverting the frozen orthographic cameras, re-solving cross-view
    correspondence from element identity and ray geometry alone, and running spglib on the
    reconstruction: 0.9524 (original) and 0.9095 (expansion), paired against every trained arm at
    p < 1e-11. No cited work computes an identifiability ceiling this way (related_work_audit).
C2  The frozen five-view protocol withholds under 1% of atoms — 0.26% original, 0.87% expansion, have
    fewer than two clear views. This is what makes C1 a TIGHT bound rather than a loose one.
C3  Orbit decomposition of occlusion at full coverage (210 structures x 5 views per set), and the
    finding that the protocol's three axis views carry 2.25-3.34x the occlusion of its two oblique views.
C5  A coordinate-input GNN (0.6492 +/- 0.0287) and an 8B pixel model (0.6190) are statistically
    indistinguishable, paired McNemar p = 0.256.

=================  SUPPORTING, NOT CONTRIBUTIONS  ==============================================
C4  Thirteen zero-shot VLMs from eight vendors all below the shape-free floor on the original sample,
    best at 93/210 against the floor's 111/210, one-sided binomial p = 0.0078. DEMOTED because
    2605.29446 already reports VLMs failing on rendered crystallographic images. Ours adds vendor
    breadth and a deterministic-label target.
C6  Chain-of-thought underperforms direct answering (n=420, p=4.8e-04). DEMOTED to a cited replication
    of 2604.16060.

=================  WITHDRAWN  ==================================================================
C7  The cue-sufficiency stratified accuracy drop. FOUR independent failures: the expansion-set sign
    reversal, the A3 null (+0.0286, p=0.752), the RF control inversion, and now the original-sample leg
    losing significance under the canonical partition (+0.1143, p=0.1318 against a published +0.1510,
    p=0.037). Four failures is the result, not a run of bad luck to explain away.
C8  The visibility-corrected ceiling and the render-imposed vs model-imposed separation. visibility_corrected_oracle's primary
    quantity is EXACTLY ZERO on both eval sets and its pre-registered control dominates the target
    condition, so there is no corrected ceiling distinct from the ideal one.

=================  NOT CLAIMED, BECAUSE PRIOR WORK OCCUPIES IT  ================================
C9   Perception-not-reasoning. 2605.20177 states it almost verbatim. Cited as established; what is ours
     is the geometric instrument, not the conclusion.
C10  Composition-exclusion benchmark design for VLMs on crystal images. 2506.13051 already runs a
     Compositional-Exclusion benchmark over nine VLMs with space-group validity scoring.

=================  THE GATE THAT IS STILL CLOSED  ==============================================
related_work_audit's audit covers eight named works. Three instruments have NOT been searched against the
materials-informatics literature: the resolution-versus-reseed comparison, the cue-sufficiency partition,
and the oracle-only checker. By the plan's own rule no claim resting on those enters as a contribution
until those rows are filled. C1, C2, C3 and C5 do not rest on them.

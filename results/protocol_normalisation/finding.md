CHECKPOINT: protocol_normalisation   GAP: three inconsistencies a reviewer recomputing tables
                                          will hit. (ICLR plan, Phase A)
STATUS: DONE. Items (a) and (b) applied. Item (c) was ALREADY FIXED and is recorded as verified rather
        than re-applied. Item (d) is SCOPED DOWN with a reason, not blanket-applied — applying it as
        written would have required asserting resolutions I never read.

=================  (a) K IS NOW PRINTED ON EVERY ROW  ==========================================
model_sweep's leaderboard compares 13 zero-shot rows at K=3 against an A3 reference at K=8. That is not a
like-for-like decode budget. The same A3 adapter at K=3 is 139/210 = 0.6619 against 145/210 = 0.6905 at
K=8, so the reference row was 6 structures more generous than the rows it anchored.
Both the report and the paper's results section now print K on the reference row and state the K=3
value beside it. The zero-shot ordering is unaffected — no zero-shot model comes within 46 structures
of either A3 value — but the comparison is now readable without inferring the budget.

=================  (b) THE FLOOR IS NAMED WHEREVER IT APPEARS  =================================
The regularity floor is SAMPLE-SPECIFIC and moves by more than a factor of two:
  original eval sample    111/210 = 0.5286
  expansion eval sample    52/210 = 0.2476
Floor-relative phrasing is retired. Every mention now names its sample, and a standing note records
that the "thirteen models below the floor" result is an ORIGINAL-SAMPLE claim: those thirteen models
were never run on the expansion set, so the claim cannot be restated sample-free.

=================  (c) ORACLE VALUES IN EVAL-SET FIGURES — ALREADY CORRECT  ====================
The plan flags frontier_ceiling's bracket citing 0.9357, which is identifiability's DISJOINT 280-structure sample. Checked:
frontier_ceiling's results.json no longer contains 0.9357; that was corrected in an earlier pass. No change made.
Recorded because "verified and already correct" is a different statement from "fixed", and a reviewer
comparing the plan against the ledger will otherwise look for a change that does not exist.
CANONICAL for any figure containing eval-set rows: oracle_within_sample's 0.9524 (original) and 0.9095 (expansion).

=================  (d) EFFECTIVE RESOLUTION — SCOPED, WITH THE REASON STATED  ==================
The plan asks that the effective_resolution block, read from the live processor, be present in every
cited results file. Audited: 24 of 30 checkpoint results.json files do not carry it.
I DID NOT RETROFIT IT, and the reason is the point. That block records what a LIVE processor reported
at generation time. Writing it into a closed checkpoint now would mean asserting a resolution I did not
read from that checkpoint's run — the same class of defect as the fabricated parameter counts already
recorded in model_sweep. Most of the 24 never ran a processor at all (geometry, occlusion, venue, external
structure baselines), so a blanket requirement is also the wrong test.
WHAT IS TRUE AND SUFFICIENT: the audited configuration is recorded ONCE, in resolution_audit, read from the live
processor — max_pixels 200704, grid 1x26x26, patch 16, merge 2, effective 416x416, 169 visual tokens
per view, 5 views, 938 prefill tokens per sample. Every arm in this package was generated under that
configuration, and resolution_audit is the audit of record that establishes it. Checkpoints cite resolution_audit rather than
each re-asserting it.

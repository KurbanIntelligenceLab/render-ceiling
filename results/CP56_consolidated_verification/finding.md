CHECKPOINT: CP56_consolidated_verification   GAP: the package had been bitten twice by checks that pass on
     wrong values — a presence-only check that validated against an already-corrupted field, and fabricated
     parameter counts on a figure axis. Both classes must be caught by script, not by reading.
STATUS: DONE. scripts/verify_manuscript_numbers.py is a BUILD GATE that exits non-zero. 8 of 9
     documents pass; the one failure is on exactly the content the directive says to cut, which is the
     correct pre-submission state rather than a defect.

WHAT THE SCRIPT CHECKS, AND WHY EACH CHECK EXISTS.
1. VALUE EQUALITY, NOT PRESENCE. Every 4-dp literal in a manuscript document must EQUAL a value that exists
   in some ledger results.json. The earlier check tested whether a figure APPEARED in the text, which
   passed while validating against a field that was already wrong. Presence is not equality.
2. SAMPLE NAME AND DECODE BUDGET on every accuracy in a table row. This rule was added after a metric
   mismatch survived an earlier pass.
   THIS CHECK WAS DEAD CODE WHEN FIRST SHIPPED, AND THE RECORD CLAIMED OTHERWISE. check_sample_and_k() ran
   and its result was assigned, but the per-document status was computed from the other two checks only and
   the result was never printed — so it could neither fail a document nor appear in output, while this file
   and the accompanying summary both described it as one of three enforced checks. Now wired into both the
   status and the output, and VERIFIED LIVE: a probe document violating only this rule fails the gate with
   exit 1. A check that cannot fail anything is worse than an absent check, because it is claimed.
3. PAIRED CLAIMS CARRY DISCORDANCE COUNTS, so a reader can recompute the test from the text.

THREE LEGITIMATE EXCEPTION CLASSES, EACH EVIDENCED FROM CONTEXT RATHER THAN WHITELISTED BLIND.
  DERIVED    a value computed from stored counts — an interval bound, a delta, a correlation, a pooled rate.
             Recognised by its own surrounding words, and each one was verified to recompute exactly before
             the class was allowed.
  PRIOR WORK a number from a cited paper, which by construction is absent from our ledger.
  CONSTANTS  a short enumerated list of sample-specific baselines.

FIVE DEFECTS THE RUNS EXPOSED, ALL IN MY CHECKER RATHER THAN IN THE DOCUMENTS.
  (0) A CHECK THAT NEVER RAN. See item 2 above: one of the three advertised checks was unwired. Found by
      review, not by me, and the lesson is that a gate must be tested against a deliberate violation of
      EACH rule it claims to enforce — otherwise "the gate passes" is untestable.
  (a) SIGN. A stored difference of -0.5935 is written in prose as "0.5935" beside a direction word, so the
      index must carry both signs. Four values were flagged unsourced that were stored all along.
  (b) PROSE FIELDS. Numbers also live inside string fields — a "robustness" note carrying its own counts —
      and indexing only numeric JSON leaves them invisible. Four more false flags.
  (c) TRUNCATED OUTPUT. I read a tail-piped summary and reported REPORT.md as clean when it had four
      unmatched values. A fresh subprocess showed the truth. Never read a gate's verdict off a pipe tail.
  (d) DERIVED-CLASS OVERREACH would have hidden real defects, so every member of that class was recomputed
      by hand before the pattern was accepted.

CURRENT STATE, BY DOCUMENT.
  REPORT.md                                OK
  abstract_cvpr.md                         OK
  ai_disclosure.md                         OK
  appendices_R_S.md                        OK
  discussion_cvpr.md                       OK
  discussion_pre_replication_snapshot.md   OK
  introduction_cvpr.md                     OK
  related_work_cvpr.md                     OK
  results_cvpr.md                          FAIL  (6 unmatched, 1 paired-without-counts)
  8 of 9 pass. Counted as len() over the gate's own per-document output.
The six failures in results_cvpr.md are the certification result (directive section 7: "cut from the paper
entirely") and the superseded 137/73 stratified table (already relocated to Appendix S). The gate flags them
BECAUSE the paper will no longer cite those checkpoints. Clearing them is a cut, not a fix, and it happens
when the nine-page manuscript is assembled.

THIRTEEN REAL DEFECTS IN THIS REPORT THE THIRD CHECK FOUND ONCE WIRED, in table rows quoting an accuracy
with no sample and no decode budget: the four label-ladder rows, the four ladder rungs, the zero-shot
leaderboard block, the two stratified oracle rows, and the refrozen-RF row. Closed with 18 annotations
(some rows needed both a sample and a K). A FURTHER FOUR sit in results_cvpr.md and are NOT fixed: they are
on the certification result and the superseded partition, both on the directive's cut list, so they clear
when the manuscript is assembled rather than by annotation. A first pass at the detector also flagged
arXiv identifiers, p-values and correction notes as accuracies — 20 false positives burying 4 real ones —
so the matcher was narrowed to an indented label with a trailing 4-dp value, which is what a table row
actually looks like. A loose check that cries wolf is a check nobody reads.

ONE REAL DEFECT THE PAIRED CHECK FOUND IN THE REPORT. A quantization claim quoted two p-values with no discordance
counts, although the counts were stored. Now reads "gained 11 lost 1, p = 0.0063; gained 6 lost 0,
p = 0.0312" — matching the source exactly.

WHAT THIS DOES NOT CHECK. Figure axis values are not yet traced by script; the fabricated-parameter defect
was caught by hand and is prevented by a convention, not by this gate. Adding an axis-value check requires
the figures to emit their plotted series to a sidecar file, which is not built.

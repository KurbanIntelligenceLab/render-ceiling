# CoCr ledger — statistical conventions (program-wide, adopted 2026-07-27)

Unified after an inconsistency was found between process_reward and the exclusion_baselines SFT comparison.

## 1. POOLED SEED SD
    pooled = sqrt( (s1^2 + s2^2) / 2 )        <- RMS of the two arms' seed SDs
This is process_reward's definition and it is now the program-wide convention, chosen because Gate 2 was
PRE-REGISTERED with it (changing it retroactively would alter a pre-registered threshold).

The exclusion_baselines SFT-V1 comparison originally used quadrature-sum pooling, sqrt(s1^2 + s2^2), which
gives LARGER (more conservative) thresholds. Recomputed under the adopted convention:

    comparison        delta     pooled(adopted)   verdict     pooled(old)   verdict(old)
    B3   - SFT-V1    +0.0080        0.0328        within        0.0464        within
    V2a  - SFT-V1    +0.0397        0.0127       EXCEEDS        0.0180       EXCEEDS
    V2b  - SFT-V1    +0.0492        0.0079       EXCEEDS        0.0112       EXCEEDS

NO VERDICT CHANGES. Verification that process_reward really used this definition: V2b-B3 macro delta 0.041
vs pooled(0.000, 0.045) = 0.0318, matching the 0.032 recorded in process_reward's gate2 block.

## 2. DDOF
POPULATION standard deviation (ddof = 0) throughout, as previously disclosed. With n = 3 seeds
the sample SD (ddof = 1) is ~22% larger; every threshold in the ledger is the population form.
Rationale: the 3 seeds are the complete set of runs performed, not a sample from a larger pool,
and the population form was used consistently from sft_chain onward.

## 3. MOVEMENT THRESHOLD
0.05 absolute is the standing movement threshold for pre-registered branch rules (resolution_audit, prototype_exclusion),
chosen as the largest single-arm seed SD observed at the time it was set (B1, 0.0515).

## 4. EFFECTIVE RESOLUTION (standing field, adopted after resolution_audit)
Every results.json carries, read from the LIVE processor and never derived by formula:
    {max_pixels, grid_thw, patch_size, merge_size, effective_px, visual_tokens_per_view,
     n_views, non_visual_prompt_tokens, prefill_tokens_per_sample}
All results through calibration were measured at max_pixels=200704 => 416x416 effective, 169 visual
tokens/view. See resolution_audit/.

## 5. DIRECTION CLAIMS
Every ordering, above/below, and delta-vs-threshold statement is COMPUTED and printed before it
enters prose or a record. Adopted after three direction errors were caught in one session
(SFT-V1 vs B3; the prototype_exclusion branch classification; the prototype_exclusion arm ordering) — in each case the
computed values were correct and the narration was not.

## Job-monitoring conventions learned the hard way (2026-07-27)

DETACHED STDOUT IS NORMAL, NOT A HANG. A long training run launched via submit_job keeps running
after the job's shell exits, but its stdout is no longer captured — the log file stops growing
while the process is perfectly healthy. Do NOT infer failure from a stale log. The A3 run showed
zero step lines for 3h14m and was training normally throughout.
  DIAGNOSE INSTEAD BY: (1) sampling `ps -o times=` twice ~40s apart — a live trainer accumulates
  CPU time at roughly wall-clock rate; (2) nvidia-smi utilization; (3) comparing elapsed time
  against a COST MODEL derived from a completed cell, not against a guess.
  COST MODEL IN USE: SFT at native resolution ran 241 min for 1610 examples (the S1 cell). Scale
  linearly by example count: the 3220-example augmented run should take ~480 min (~8h).

A MOMENTARY 0% GPU READING IS NOT A STALL. Between optimizer steps utilization dips; a single
sample caught A3 at 0% and looked like a stall. Always take a second reading before acting.

TRANSFER THRESHOLD. submit_job auto-harvest silently leaves large outputs on the remote
(reason "threshold"); a 154MB adapter tarball did not come down. For cross-box moves the options
are (a) retrain on the target box, (b) explicit two-hop through the sandbox, (c) inter-box SSH.
(c) requires placing a private key on a rented box and MUST be asked about first, not assumed.
Prefer (b); prefer neither if the target box is already saturated — parallelising onto a busy
card contends rather than helps, which is why the certification queue was left serial.

## exit 124: the wrapper timed out — RE-CHECK before concluding the work survived (2026-07-28)
## (heading corrected: it previously read "...not that the work died", which asserted the very
##  claim the body retracts. In this instance the work DID die.)
CORRECTED ENTRY. The certification comparator job returned exit_code 124 (SIGTERM from timeout) after its
21600s limit. At first inspection the generation process was still alive, and I recorded that the
child survives the wrapper. THAT WAS WRONG: the SIGTERM propagated moments later and the SFT-V1
arm died after ~3h with NO output written. ~3h of GPU time was lost. The accurate rule is that a
child may briefly outlive the wrapper, so the FIRST check can mislead — re-check before concluding
the work survived, and never rely on it surviving. Do not treat exit 124 as automatically fatal
either; check, then decide:
  1. `pgrep -f <script>` on the box before assuming anything died;
  2. check the output directory for partial products;
  3. only relaunch what is genuinely missing, and use the resumable skip-if-exists pattern so a
     relaunch cannot clobber a completed arm.
Related and already recorded above: a detached process stops writing to its log while healthy.
Both failure-shaped signals — a stale log and exit 124 — have now been mistaken for real failures
once each. The reliable liveness test in both cases is CPU-time advancing under `ps -o times=`.
SET LONGER TIMEOUTS for multi-arm generation loops: three K=8 arms at ~5h each needs >54000s, not
21600s. The relaunch uses 72000s AND a resumable skip-if-output-exists guard, so a future timeout
costs at most the in-flight arm rather than the whole loop. WRITE OUTPUT INCREMENTALLY where
possible: run_e7_tts.py writes only at completion, which is why a timeout loses the entire arm.

## THREAT CLOSED: tolerance-flip policy (brief §6) — decided, frozen, and VERIFIED IMPLEMENTED
THE POLICY (frozen in pipeline/finding.md, not re-litigated here):
    keep_for_training = (neighborhood_stable AND source_agrees)
    i.e. CARRY the production-tolerance (canonical, symprec 0.01 / angle 5.0) label, and quarantine
    ONLY structures that are unstable in a NEIGHBOURHOOD of the production tolerance AND disagree
    with the source database.
ONE-SENTENCE JUSTIFICATION, as the brief requires: the blunt "flips anywhere in the sweep ->
exclude" rule drops 7.1% concentrated in exactly the low-symmetry strata models are weakest on
(triclinic 15.6%, trigonal 12.5%), which would bias the evaluation toward the easy classes; the
frozen rule instead removes only structures whose label is genuinely unstable where we actually
read it, which is the defensible criterion.

VERIFIED ON THE PRODUCTION DATASET (this session, not assumed):
    quarantined under the frozen policy: 0/1820 = 0.0000
    per system: 0/260 for ALL SEVEN systems; neighborhood-unstable 0/260 for all seven
    range across systems: 0.0000 to 0.0000
So the stratified-balance concern DOES NOT BIND on the E3 data: every one of the 1820 structures
is neighbourhood-stable AND source-agreeing, the splits are exactly 260/system by construction,
and no class is thinned at all. The 7.1% figure belongs to the pipeline label-correctness AUDIT
(n=224, a separate certification exercise) and must NOT be quoted as an exclusion rate on the
1820-structure production set. These two numbers have distinct provenance and are easy to conflate.

GOTCHA FOR WHOEVER CHECKS THIS NEXT: keep_for_training is NESTED inside the sidecar's
label_policy dict, not a top-level field. A top-level lookup returns nothing and silently reports
0 structures carrying the flag, which looks identical to "the policy was never applied". Read
side[mid]["label_policy"]["keep_for_training"].

## Standing rule: NEVER VALIDATE ON A PREFIX SLICE (added after the second occurrence)
Two wrong numbers in this package came from assuming file or array order was arbitrary when it was not:
  1. THE LETTERBOXING CONTROL. A 2-atom cubic structure passed a projection calibration at 100% while
     the transform was wrong, because that structure's projected extents are equal and cannot expose an
     aspect-ratio bug. A control too easy certifies a wrong implementation.
  2. THE FIRST-30-ROWS SLICE. Total mean occlusion was reported as 0.4891 from `rows[:30]` of
     eval.jsonl. That file is written CRYSTAL-SYSTEM BY CRYSTAL-SYSTEM, so the slice is
     triclinic/monoclinic only — a subset presented as a whole-sample number. Recomputation on exactly
     those 30 rows reproduces 0.4891, which confirms the cause rather than assuming it. The correct
     stratified figures are 0.5699 (original) and 0.5900 (expansion).
THE RULE: any subsample used for a reported number must be STRATIFIED or SHUFFLED, never a prefix. The
cheapest check is whether a known aggregate reproduces on the subsample — box-sufficiency at 0.975
against a recorded 0.652 is what exposed the second case. And validate geometric transforms on the
ASYMMETRIC case, never the high-symmetry one.

## Standing rule: DO NOT SHIP A RECOMMENDATION ON A HANDFUL OF DISCORDANT MEASUREMENTS
Depth quantization was reported as saturating at four levels, then corrected to eight after review
caught one stratum needing eight, then WITHDRAWN entirely once powered:
  252 view-measurements (6 structures/system):  Q4 = Q8 = Q16 on 3 of 4 strata -> "saturates at 4"
  1260 view-measurements (all structures):      Q16 > Q8 > Q4 on ALL 4 strata; paired pooled tests
                                                Q4->Q8 p = 0.0063, Q8->Q16 p = 0.0312, BOTH REAL
The claim appeared three times before withdrawal. A per-stratum table with 1-2 discordant pairs cannot
establish a saturation point in either direction. THE RULE: before any protocol recommendation, compute
the discordant counts and run the paired test at full available power; if the deciding difference is a
handful of measurements, report the uncertainty instead of the recommendation.

## Standing rule: A CITED CLASSIFIER MUST HAVE ITS EXACT PARAMETERS IN THE LEDGER
Two classifiers in this package cannot be reproduced from the record: the random-forest 19-feature list
(0.8905 vs a reproducible 0.8857) and box_sufficiency's box-sufficiency rule (137/73 recorded; 140/70 at the
documented 2%/1deg tolerances, 144/66 at 1%/0.5deg, with the ambiguous stratum matching on 5 of 6
metric classes). Both were caught only when a downstream analysis failed to reconcile. THE RULE: when a
classifier's output is cited anywhere, its exact parameters — feature list, tolerances, branch order,
symprec — go into the ledger at first use, not into a comment.

RULE: ANY NUMBER PLACED ON A PLOT AXIS NEEDS A PRIMARY SOURCE IN THE LEDGER.
  Violated once, badly: a scaling figure plotted parameter counts for two Mistral models whose sizes
  are NOT publicly disclosed. Those figures were invented from an impression of model tiering and would
  have shipped as data. The same figure also treated a 235B model as the largest tested when a 400B
  model was in the roster, which inverted the conclusion — the largest model tested is TIED FOR BEST,
  not the worst offender.
  Consequences, now standing:
    a) A model with an undisclosed parameter count may appear on an accuracy leaderboard but NEVER on a
       size axis. List the excluded models explicitly in results.json.
    b) Record TOTAL and ACTIVE parameters separately. Conflating them makes an expert-count effect look
       like a compute-scale effect: two models sharing 17B active parameters differed by 50 structures.
    c) Before writing "largest", "smallest", or an "Nx range", compute the max and min from the recorded
       figures. Do not infer them from the plot's rightmost point or from family naming.

RULE (2026-08-06, from a real defect): VERIFY THE FILE YOU SAVE, NOT A DIFFERENT COPY OF IT.
Edits in this project are applied to the repo path (the repo path), but save_artifacts reads from
the workspace, so a copy staged BEFORE an edit will be saved while the verification passes against the
edited repo file. That happened to REPORT.md: sections 4c-4f were added and every value checked against
the live file, but v17 was a pre-edit staged copy and contained none of it.
THE TELL IS FREE AND MUST BE CHECKED: if save_artifacts returns a checksum IDENTICAL to the previous
version of that filename, nothing was saved. After every save, re-read host.artifact_path(<returned
version_id>) and assert it byte-matches the file the checks ran against. Restage and re-save if not.
Note that a byte-identical file can still show a smaller character count than its on-disk byte size —
that is UTF-8 multibyte, not missing content; compare CONTENT, not sizes.

RULE (2026-08-06, from a silent whole-arm loss): A SHELL LOOP'S "DONE" IS NOT EVIDENCE THE ARM RAN.
Two no_image_control roster arms printed DONE and wrote NO output file. Cause: probe_frontier.py's ask() returns None
when every retry is exhausted, and the aggregation called txt.startswith(...) on it, raising
AttributeError AFTER all 630 calls had been paid for. The `echo DONE` in the driving loop fires on the
next iteration regardless of the python exit status, so the loss was invisible in the log.
FIXED IN THE HARNESS: a None return is now counted as an api_error instead of crashing the run.
THE STANDING CHECK: after any per-model fan-out, diff the set of models with an output FILE against the
requested roster before scoring anything. Never infer completion from loop output. In this case the audit
caught 14 of 16 present, which is how the two losses were found at all.

RULE (2026-08-06, from a scope count that contradicted its own data): NEVER STATE A COUNT YOU HAVE NOT
LENGTHED, AND NEVER ADD TWO DIFFERENT UNITS.
The related_work_audit scope note said "eleven rows" — arrived at by adding 8 PAPERS to 3 INSTRUMENT ROWS, two different
units — while the results.json it sat in held 13 paper-keyed entries. The cell that wrote the note printed
"rows total: 13" three lines earlier, so the contradiction was visible in my own output and I did not check.
THE CHECK: any count appearing in prose must be computed as len(...) of the structure it describes, in the
same cell that writes the prose, and the structure must carry an explicit accounting field naming the unit
(here: row_accounting with pass_1 + pass_2 = total_cited_works, and the distinct instrument-row count kept
separate). If two counts differ because they measure different things, say what each measures rather than
summing them.

RULE (2026-08-06, from a README that silently lost 96 lines): WHEN APPENDING TO A DOCUMENT THAT ALSO EXISTS
AS AN ARTIFACT, READ THE LATEST ARTIFACT VERSION FIRST — NOT THE IN-REPO COPY.
I appended the attribution-ladder section to cvpr_template/README.md, but that in-package copy was a stale
rebuild; the current content lived in artifact version v5, written after my base. The append succeeded, the
save succeeded, and 96 lines of aim/structure/claims text vanished with no error. Only the save tool's
stale-base warning caught it.
THE CHECK: before appending to any file that has an artifact history, diff the in-repo copy against the
latest artifact version (host.artifact_path on the newest version_id) and merge if they differ. After
saving, assert the returned version is byte-identical to the file the append was applied to AND that no
line present in the prior version is absent from the new one — a line-set difference, not just a checksum.

RULE (2026-08-06, from a verification gate whose third check was dead code): A GATE MUST BE TESTED AGAINST A
DELIBERATE VIOLATION OF EACH RULE IT CLAIMS TO ENFORCE.
verify_manuscript_numbers.py advertised three checks. The third ran and its result was assigned to a
variable, but the per-document status was computed from the other two and the variable was never printed —
so it could neither fail a document nor surface in output, while the checkpoint record and the summary both
described it as enforced. Every document "passed" a check that did not exist. Once wired it immediately
found 13 real defects in the report.
THE CHECK: for each rule a gate claims, write a probe input that violates ONLY that rule and confirm the
gate fails with a non-zero exit. A gate that has never failed is not evidence of correctness — it is
untested. Delete the probe after; keep the fact that it passed in the record.
COROLLARY on detector precision: the same check, first written loosely, flagged arXiv identifiers, p-values
and correction notes as accuracies — 20 false positives around 4 real ones. Narrow the matcher until the
false-positive rate is near zero, because a gate that cries wolf is a gate nobody reads.

RULE (2026-08-06, from a discarded biased sample whose figures survived in prose): DISCARDING A BIASED
SAMPLE FOR ONE QUANTITY IS NOT DISCARDING IT. RECOMPUTE EVERY FIGURE DERIVED FROM IT.
In perception_transplant I read a 43-record partial result off a CLASS-ORDERED file, correctly identified it as a biased
prefix, and discarded it for the accuracy number — then let its atoms-emitted median of 45 stand in the prose
of finding.md and results.json, while the numeric field in the same JSON object correctly held 48. The two
were written from one dict literal in a single cell, so the contradiction was introduced at write time and a
reader comparing the prose to the field two keys above it would have caught it immediately.
THE CHECK: when a sample is disqualified, enumerate EVERY number computed from it and recompute each on the
full sample before any of them reaches prose. And assert that each prose figure equals the field it sits
beside — a JSON object whose narrative contradicts its own data is worse than one with no narrative.

RULE (2026-08-06, from claiming full coverage of a finding list while my own cell printed one as unmarked):
NEVER CLAIM COMPLETE COVERAGE OF A LIST WITHOUT DIFFING WHAT I HANDLED AGAINST THE LIST ITSELF.
I said "worked through all of them" about ten review findings. My own audit cell had PRINTED
`left unmarked: [...]` naming three, and one of those — a claim that a specific marketplace offer was "the
pick" — never appeared in the summary at all. The evidence contradicting my claim was in my own output,
one screen up.
THE CHECK: when closing a list of N items, compute the set difference between the item ids and the ids I
acted on, print it, and either handle the remainder or name it as outstanding in the summary. "All of them"
is a claim about a set, so it needs a set operation, not a recollection. A skipped-marker return
(`review_exhausted`, etc.) means the marking failed, NOT that the item was addressed.

RULE (same date, from the same finding): AN UNFALSIFIABLE SUPERLATIVE ABOUT AN EPHEMERAL LISTING IS NOT A
FINDING, IT IS A HABIT TO DROP. Calling a rented GPU offer "the pick — highest reliability at a reasonable
price" cannot be checked later because marketplace listings vanish. Record the FILTER and the SORT KEY, which
are reproducible, plus the full candidate list if the choice matters. "Reasonable price" with no threshold is
not a measurement.

RULE (external rules and policies). NEVER STATE A VENUE RULE, POLICY, OR DEADLINE FROM MEMORY, AND NEVER
ATTRIBUTE ONE TO A SOURCE NOT RE-READ IN THE SAME TURN AS THE WRITING. If the source document is in the
session, quote it verbatim in a blockquote and say it is quoted. If it is not reachable, say so and tell
the reader to confirm at the primary source before acting. An attribution ("verified against X") transfers
the writer's confidence to the reader and is worse than no attribution when the check did not happen.
COROLLARY, AND THIS IS WHAT MADE THE CoCr C8 ERROR HARD TO SPOT: echoing one genuine phrase from a real
document around otherwise invented content makes the whole passage read as sourced. If any phrase in a
claim came from the real text, either the whole claim is quoted or none of it is.

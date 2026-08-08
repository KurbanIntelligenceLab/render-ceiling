# PRE-REGISTRATION — CP10, the MERGED retrain (closes CP1c and CP0c in one run)
# Written and committed BEFORE the retrain was launched and before any retrain number existed.

## WHY ONE RUN CLOSES TWO QUESTIONS (team directive item 3)
Two questions are currently open, and both need the SAME run:

  Q1 (from CP1c, branch (iii)): is B1-direct's OOD robustness chemistry-specific, or does it
     extend to unseen structural arrangements? CP1c could not answer this: the built
     prototype-exclusion eval was 90.0% contaminated for existing checkpoints, and the valid
     no-retrain probe returned a DIFFICULTY SHIFT (all five arms past threshold), which the
     pre-registration explicitly forbids reading as a memorization result. A post-hoc
     difficulty-controlled analysis was underpowered (best |t| = 1.63).
  Q2 (from CP0c, branch (ii)): was B1's 0.133 accuracy drop at native resolution a genuine
     resolution effect or a train/test mismatch? Unresolvable without training at native
     resolution.

A single run trained at NATIVE resolution on the BALANCED geometric-OOD split answers both.

## THE RUN
  data:       data/e3geo  (built + audited in CP1c: 1610 train / 210 eval, 230 and 30 per system
              across all 7 systems, 0 prototype overlap, 0 eval-only elements, seed 23)
  resolution: max_pixels = 589824  -> 48x48 grid -> 768x768 effective, 576 visual tokens/view
              (verified from the live processor; prefill 2973 tokens/sample)
  arms:       B1 (direct) and V2b (dense step-level, the Gate-2 winner)
  seeds:      0, 1, 2
  eval:       data/e3geo/eval at the SAME native resolution used for training (so this run has
              NO train/test resolution mismatch — that is the entire point of Q2)
  protocol:   3-sample majority vote, temp 0.7, 512 max new tokens; effective_resolution logged

REFERENCE VALUES this run is compared against (all at 416-eff, composition-exclusion eval):
    B1  0.6143 +/- 0.0515      V2b 0.3857 +/- 0.0000      regularity floor 0.5286

## DECISION RULES — Q1 (memorization / geometric OOD)
Threshold 0.05 absolute; pooled SD per ledger/CONVENTIONS.md, i.e. sqrt((s1^2+s2^2)/2).
Compare B1 retrained-on-e3geo, evaluated on e3geo-eval (geometry-OOD) against B1's
composition-exclusion value 0.6143.

  Q1-(i)  B1 DROPS by > 0.05 while V2b holds within 0.05
          => B1's robustness IS chemistry-specific; the memorization story PARTIALLY REVIVES for
             geometric OOD. Report both splits side by side; state that the direct arm's
             advantage does not extend to unseen arrangements.
  Q1-(ii) B1 HOLDS within 0.05
          => B1's robustness is GENERAL across both OOD axes. The memorization story is closed
             as refuted, and CP1b branch (a) is strengthened on a properly powered test.
  Q1-(iii) BOTH arms drop > 0.05
          => difficulty shift again; compare ORDERING only, and state that a balanced
             geometric-OOD split is simply harder. (Unlike CP1c this is now a TRAINED
             comparison, so a joint drop is informative about task difficulty, not about
             contamination.)
  In ALL cases: report each arm against the CP8 regularity floor (0.5286), not only against
  chance, because an arm below the floor has not demonstrated crystallographic reasoning.

## DECISION RULES — Q2 (resolution)
Compare each arm's native-trained/native-eval accuracy against its 416-trained/416-eval value.

  Q2-(i)  an arm IMPROVES by > 0.05 at native
          => resolution WAS a real constraint; CP0c's B1 drop was train/test mismatch, now
             confirmed. All prior perception results must be annotated as resolution-limited,
             and future runs use native resolution.
  Q2-(ii) accuracies are FLAT within 0.05 for both arms
          => resolution was NOT a constraint at this render size; CP0c's "resolution excluded"
             becomes defensible (it is currently NOT, per CP0c branch (ii)), and the 416-eff
             results stand as-is.
  Q2-(iii) an arm DEGRADES by > 0.05 at native even when trained natively
          => a genuine and surprising result (more pixels hurting a natively-trained model);
             investigate before reporting, do not assert a mechanism.
  SECONDARY, pre-registered: geometry-STEP accuracy for V2b native-trained vs the 0.6349 /
  0.6476 pair from CP0c item 2. If the natively-TRAINED geometry step still fails to beat the
  416 value by > 0.05, the fabrication diagnosis is confirmed under the strongest available
  test, and the "responsive to the image without being informed by it" sentence stands. If it
  DOES improve, that sentence must be weakened to apply only to 416-trained models.

## CONFOUNDS FIXED IN ADVANCE
- Q1 and Q2 are entangled BY DESIGN in this run (new split AND new resolution). This is
  acceptable only because the 416-eff/composition-exclusion references already exist for both
  arms; each comparison changes one axis relative to a known reference. It is NOT a clean
  2x2 and must not be described as one. A full factorial (2 splits x 2 resolutions x 3 seeds)
  is 4x the cost and is explicitly NOT being run.
- data/e3geo eval is 93.8% contained in data/e3's TRAIN set. That is irrelevant HERE because
  this run trains on data/e3geo/train, which is disjoint from data/e3geo/eval by construction
  (0 prototype overlap, verified). But it means these checkpoints must NEVER be evaluated on
  data/e3's eval set, and the 416-eff references must never be recomputed from them.
- Budget: at native resolution prefill is 3.17x larger, so expect ~3x the wall-clock of the
  416-eff runs. This is a cost note, not a confound.

## WHAT WOULD MAKE THIS RUN UNINFORMATIVE
If both arms land below the CP8 regularity floor (0.5286) on the balanced geometric-OOD eval,
then neither arm demonstrated crystallographic reasoning on this split and both Q1 and Q2 become
unanswerable from it — report that plainly rather than interpreting sub-floor differences.

=================  LAUNCH READINESS (verified ON THE BOX before launch)  =================
  renders available (768x768 on disk, reused per material_id):  9100, 0 missing for any row
  data/e3geo_sft/train.jsonl   3220 rows (1610 structures x arms B1, V1)
  data/e3geo_sft/eval.jsonl     420 rows (210 structures x arms B1, V1)
  data/e3geo/train.jsonl       1610 rows   data/e3geo/eval.jsonl  210 rows
  train n eval material_id INTERSECTION = 0                       VERIFIED on the box
  labels_sidecar.json present in both dirs                        VERIFIED

TWO GAPS FOUND AND CLOSED DURING PREP (recorded because they would have silently broken the run):
1. data/e3geo was built in CP1c as an EVAL split, from the GRPO prompt format, and therefore
   LACKED the `target` and `arm` fields the SFT harness requires. Fixed by generating targets
   deterministically from labels_sidecar.json via cocr.traces.make_target for arms B1 and V1 ->
   data/e3geo_sft/. No new labels were invented; the targets come from the same sidecar that
   produced every other arm's training data.
2. No re-rendering is needed. The renders on disk are genuinely 768x768, so native resolution is
   reached purely by raising --max-pixels to 589824; the 416x416 of all prior runs was a
   PROCESSOR cap, never a render limitation.

HARNESS SUPPORT CONFIRMED (no code changes needed):
  scripts/train_e2_lora.py  accepts --data-dir, --max-pixels (default 200704), --arm {B1,V1}
  scripts/train_e3_grpo.py  accepts --data-dir, --max-pixels, --train-file, --sft-adapter
  scripts/eval_e3.py        accepts --data-dir, --max-pixels

RUN ORDER (V2b requires an SFT initialization at the SAME resolution, so the chain is):
  1. SFT B1 on data/e3geo_sft, 3 seeds, --max-pixels 589824
  2. SFT V1 on data/e3geo_sft, 3 seeds, --max-pixels 589824      (V2b's initialization)
  3. GRPO V2b from each V1 seed, --data-dir data/e3geo, --max-pixels 589824
  4. eval B1 and V2b on data/e3geo/eval at --max-pixels 589824, 3-sample majority vote
NOTE this makes CP10 larger than the "~1 day" estimate quoted earlier: native resolution is
~3x the prefill, and V2b needs its own SFT stage first. Expect ~2-3 days for the full 3-seed
chain. A 1-seed pilot of steps 1-4 is the cheaper de-risking option and is the recommended
first move, exactly as E3 was piloted before its matrix.

=================  PILOT SCOPE (1 seed) — launched, queued behind E7 generation  =================
User decision: pilot first, then the full matrix if the path works. Same de-risking sequence as
E3 (whose 1-seed pilot caught a trainer wiring bug that would have wasted the whole matrix).

PILOT = seed 0 only, full four-stage chain at native resolution:
  1. SFT B1  on data/e3geo_sft, --max-pixels 589824, 3 epochs, lr 1e-4, grad-accum 8
  2. SFT V1  on data/e3geo_sft, same config                       (V2b's initialization)
  3. GRPO V2b from adapters_geo/V1_geo_s0, --data-dir data/e3geo, 300 steps,
     group 8, lr 1e-5, beta 0.02, --max-pixels 589824             (the E3 frozen config)
  4. eval B1 and V2b on data/e3geo/eval at --max-pixels 589824, 3-sample majority vote

WHAT THE PILOT CAN AND CANNOT DECIDE — stated in advance so a 1-seed number is not overread:
  CAN: prove the native-resolution training path runs end to end (no OOM at 3.17x prefill, the
       GRPO reward wiring still fires on the new data dir, eval completes); give a first
       point estimate for both Q1 and Q2; expose any cost surprise before 3 seeds are committed.
  CANNOT: satisfy EITHER pre-registered decision rule. Both Q1 and Q2 compare against pooled
       seed SDs, which do not exist at n=1. NO branch may be declared from the pilot. Any pilot
       number is explicitly a DE-RISKING observation, exactly as CP3's pilot was, and must be
       labelled as such if reported.

SCHEDULING NOTE: the pilot waits on E7 GENERATION only (SFT is compute-bound and would contend
for the card), and deliberately does NOT wait on the leftover native-resolution audit arm, which
is decode-bound and overlaps harmlessly. Verified before launch: 16 GB of 32 GB free at 85%
utilization with E7 running.

===================================================================================
=========  PILOT DESIGN REVISED BEFORE LAUNCH — 3-AXIS CONFOUND CAUGHT  ===========
===================================================================================
The v1 pilot above was QUEUED AND THEN STOPPED before it wrote a single adapter. Reason: a
comparison against the B1 0.6143 reference would have confounded THREE axes, not the two the
prereg accounted for.

  axis 1  split        composition-exclusion  ->  balanced geometric-OOD
  axis 2  resolution   416x416 (max_pixels 200704)  ->  768x768 (589824)
  axis 3  SFT DATA SIZE  115 examples/arm  ->  1610 examples/arm   (14x)   <-- MISSED IN v1

Axis 3 was invisible in v1 because data/e3geo_sft was built at the full split size (1610), while
every existing SFT reference (B1 0.6143, V1 0.3365) came from data/e2, whose SFT stage used only
115 examples per arm. Verified by counting records: data/e2/train.jsonl = 460 rows = 115 x 4
arms; data/e3geo_sft/train.jsonl = 3220 rows = 1610 x 2 arms.
v1 prereg text above is superseded for the PILOT; prereg_v1_snapshot.md preserves it.

## REVISED PILOT — FIVE CELLS, 1 SEED EACH, FROZEN CONFIG
Native = max_pixels >= 589824, verified from the LIVE processor (48x48 grid, 576 tok/view).

  SFT cells
    S1  B1  @ native  x  comp-1610      (data/e3 composition-exclusion, 1610 structures)
    S2  V1  @ native  x  comp-1610      -> initialization for G1
    S3  B1  @ native  x  geo-1610       (data/e3geo balanced geometric-OOD)
    S4  V1  @ native  x  geo-1610       -> initialization for G2
    S5  B1  @ 416     x  comp-1610      (ADDED CELL — minutes-scale; makes axis 3 MEASURABLE)
  GRPO cells
    G1  V2b from S2, native x comp      G2  V2b from S4, native x geo
  EVAL
    every model at ITS OWN training resolution (CP0c mismatch rule, non-negotiable);
    comp-trained models on the 210 composition eval, geo-trained on the 210 geometric eval;
    effective_resolution logged per run, read from the live processor.

## THE THREE PRE-REGISTERED COMPARISONS (branch rules written BEFORE any number exists)
Threshold 0.05 absolute; pooled SD per ledger/CONVENTIONS.md.

  Q1  RESOLUTION:  B1 (S1, native-comp-1610)  vs  B1 (S5, 416-comp-1610)
      Size and split are FIXED; only resolution varies. This is the clean version of the test
      CP0c could not run.
        Q1-(i)   native HIGHER by > 0.05  -> resolution WAS a real constraint; CP0c's B1 drop
                 was train/test mismatch, now confirmed; annotate all 416-era perception results
                 as resolution-limited.
        Q1-(ii)  |delta| <= 0.05          -> resolution is NOT a constraint at this render size;
                 CP0c's "resolution excluded" becomes defensible and the 416-era results stand.
        Q1-(iii) native LOWER by > 0.05   -> surprising; investigate before asserting a mechanism.

  Q2  SPLIT:  per arm, native-comp-1610  vs  native-geo-1610
      Size and resolution are FIXED; only the split varies. CP1c's branch rules apply verbatim
      (Q1-(i)/(ii)/(iii) of the CP1c prereg: B1 collapses while chains hold / B1 holds / all drop).
      Every arm is ALSO reported against the CP8 regularity floor 0.5286, not only chance.

  Q3  SCALE:  B1 (S5, 416-comp-1610)  vs  B1 (416-comp-115, the existing 0.6143)
      Resolution and split are FIXED; only SFT data size varies (14x). This is what the added
      cell buys.
      CONDITIONALITY, STATED IN ADVANCE SO IT CANNOT BE APPLIED SELECTIVELY: the analogous V1
      comparison (V1 native-comp-1610 vs V1 416-comp-115 = 0.3365) is RESOLUTION-CONFOUNDED and
      may be made ONLY IF Q1 returns branch (ii) (resolution null for SFT arms). If Q1 returns
      (i) or (iii), the V1 scale comparison is NOT made and is reported as unavailable.

## CHAIN-ARM 416 COMPARATOR
The existing CP3 V2b (0.3857) was GRPO-trained on 1610 prompts but from an SFT stage of only 115
examples. It may be cited for effect DIRECTION only, and the SFT-lineage caveat must appear
wherever it is cited.

## PILOT INTERPRETATION RULES (1 seed)
Pipeline validation + effect DIRECTION only. NO gate verdicts. The words "confirmed" and
"refuted" are not to be used of any pilot result; the 3-seed matrix decides. Pooled-SD rules
cannot be evaluated at n=1 and no branch may be declared from this run.
Standing requirements carried over: snapshot the record before any correction; log the
zero-variance-group panel for GRPO cells; run the adapter-diff audit across seeds when the
matrix runs (bit-identical adapters would indicate a save-twice bug, as checked in CP3).
IF ANY Q SHOWS A DIRECTION THAT WOULD CHANGE THE E7 WRITE-UP, FLAG IT BEFORE THE MATRIX RUNS,
not after.

=================  IN-FLIGHT: COST MODEL CORRECTED, S5 COMPLETE  =================
COST CORRECTION (made before the run was far along, not discovered at the end). I described the
added S5 cell as "minutes-scale". That was WRONG: it applied the E2 reference timing (4.5 min)
without accounting for E2's SFT stage having only 115 examples per arm, while S5 trains on 1610.
  measured E2 rate: 4.5 min / 115 ex = 2.35 s/example at 416-eff
  predicted S5:     2.35 s x 1610 = 63 min
  ACTUAL S5:        3608 s = 60 min                       <- prediction confirmed
Revised whole-pilot estimate from measured rates (native = 3.17x prefill):
    5 SFT cells (1x416 + 4xnative)   14.4 h
    2 GRPO runs at native            12.7 h
    5 evals                          19.6 h
    TOTAL                           ~47 h (~2 days); the 3-seed matrix would be ~3x that.
The eval stage is the largest and most compressible block; a pilot-only reduction to K=1 greedy
would cut ~13 h without affecting what a 1-seed pilot can legitimately conclude (direction only).
Flagged to the user for a decision rather than changed unilaterally.

S5 RESULT (cell complete, checkpoint verified):
  B1 @ 416 x comp-1610: 603 steps, loss 4.4815 -> 0.0064 (mean first10 1.1326 -> last10 0.0224),
  60 min, adapter 174.7 MB written.
  OBSERVATION RELEVANT TO Q3, recorded now so it is not read into the result later: a final
  training loss of 0.0064 on 1610 examples indicates the model has essentially MEMORISED the
  training targets. For the B1 arm the target is a single crystal-system word, so near-zero
  training loss is expected and is NOT by itself evidence of overfitting to the eval. But it does
  mean Q3 (scale: 115 -> 1610 examples) is comparing two REGIMES that have both saturated their
  training objective, and any Q3 difference must therefore be attributed to what the larger
  sample TAUGHT rather than to longer optimisation. State this when Q3 is reported.

=================  PILOT PAUSED AND RESCOPED (team direction, 2026-07-27)  =================
SEQUENCE DIRECTED: finish current cell -> CP7b certification re-run -> remaining Q1/Q3 cells ->
Q2 cells CUT.

STATE AT PAUSE (stopped at a clean cell boundary; nothing lost):
  adapters_geo/B1_comp416_s0   COMPLETE  (S5: 416 x comp-1610; 603 steps, loss ->0.0064, 60 min)
  adapters_geo/B1_compnat_s0   COMPLETE  (S1: native x comp-1610; 603 steps, loss ->0.0146, 241 min)
  adapters_geo/V1_compnat_s0   PARTIAL   (S2 had just started; directory only, no weights —
                                          the resumable loop will re-run it from scratch)
S1's 241 min against the 200 min estimate confirms the corrected cost model to within ~20%.

Q2 CELLS CUT FROM THE PILOT. Rationale (recorded so the cut is auditable): Q2 is the split axis,
which serves the memorization question that CP1b branch (a) already made non-load-bearing and
that CP1c returned an uninterpretable branch (iii) on. Deferred to the matrix stage, revived only
if the certification story needs a robustness row. The data/e3geo and data/e3geo_sft artifacts are
BUILT, AUDITED and RETAINED (0 leakage, 0 missing renders, 3220 SFT rows) — holding them costs
nothing and they are ready if Q2 is revived.

REMAINING PILOT CELLS (Q1 + Q3 only, ~15 h):
  S2  V1 @ native x comp-1610          (needed as G1's initialization)
  G1  V2b GRPO from S2, native x comp
  evals: B1_comp416 (K=1), B1_compnat (K=1), V2b_compnat (K=3)
  Q1 = B1_compnat vs B1_comp416     Q3 = B1_comp416 vs B1 416-comp-115 (existing 0.6143)

EVAL TRIM ADOPTED (split rule, not blanket):
  B1 evals   -> K=1     (4-8 token outputs; negligible sampling variance)
  chain evals -> K=3 majority RETAINED (greedy has a documented MOTIF-trap history; if any chain
                 cell must run greedy, log the termination rate and revert to K=3 if <50%)
  UNIFORMITY: both sides of every pre-registered comparison use the IDENTICAL K. Q1 and Q3 are
  B1-vs-B1 comparisons, so both sides are K=1 — the trim does not break either comparison.
  Note this changes the Q3 comparison's protocol relative to the existing 0.6143 reference, which
  was measured at K=3. Q3 must therefore EITHER re-measure the 115-example reference at K=1, OR
  run B1_comp416 at K=3. DECIDED: run B1_comp416 at K=3 to match the existing reference, and
  B1_compnat at K=3 as well so Q1 stays internally uniform. The K=1 trim is applied only where
  BOTH sides of a comparison are new. Saving is smaller than 10h but the comparisons stay valid.

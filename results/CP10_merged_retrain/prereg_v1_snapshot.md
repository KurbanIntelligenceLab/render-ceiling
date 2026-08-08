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

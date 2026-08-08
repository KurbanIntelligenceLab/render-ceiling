# PRE-REGISTRATION — CP12, THE SOTA PUSH (thread A3)
# Written before any A3 training run. Lane A, box 2 (gpu-5090-vlm-project-2).

## THE TARGET AND WHY IT IS WORTH CHASING
CP8 established the uncomfortable comparison: from ATOMIC STRUCTURE, published GNNs reach
ALIGNN 75.6% / CGCNN 63.4% on 7-way crystal-system classification (verified from the
DeepCrysTet paper table; note the brief that first quoted these had the task rows transposed),
and our own 19-feature random forest on lattice metrics reaches 0.8905 on OUR eval
(structure_baseline.json random_forest; the 0.8762 in that file is GRADIENT BOOSTING).
From PIXELS our best arm is B1-direct at 0.6143.

Nobody holds an image-input SOTA on this task. That is the opening: a model that identifies
crystal system from RENDERS at ALIGNN-from-coordinates level would be a genuine result even
though the structure-input number is higher, because the input is strictly weaker.

## WHAT CHANGES vs THE 0.6143 BASELINE (each is a separately ablatable axis)
  A. NATIVE RESOLUTION. Every prior run saw 416x416 (max_pixels 200704) — a 3.408x AREA
     decimation of the 768x768 renders (CP0c). A3 trains at max_pixels >= 589824.
  B. FULL TRAINING SET. The 0.6143 reference was SFT-trained on 115 examples/arm; A3 uses the
     full 1610 (CP10's Q3 axis, 14x).
  C. VIEW AUGMENTATION. New: additional camera angles beyond the frozen 5-view set, as
     augmentation at train time only. The frozen set stays the EVAL protocol so every number
     remains comparable to CP1b/CP3/CP7.
  D. TOOL COUPLING (second stage, only if A-C land): emit coordinates, run spglib on them,
     feed the result back. Note CP7 showed a tool-coupled SELECTION rule fails; this is
     different — tooling inside the forward path, not as a post-hoc selector.

## PRE-REGISTERED TARGETS AND STOPPING RULE
Eval: the SAME 210-structure composition-exclusion set, the SAME frozen 5-view protocol, the
SAME K=3 majority vote. Any change to the eval protocol invalidates the comparison.
  T1 (minimum publishable): > 0.6143 + 0.0515 = 0.666, i.e. beat the existing B1 mean by more
     than its own seed SD. Below this, A3 has not moved the needle and is reported as a null.
  T2 (the headline): >= 0.756, matching ALIGNN's structure-input number FROM PIXELS.
  T3 (stretch): >= 0.8905, matching our own structure-metric RF. [CORRECTED: written as 0.876,
      which is the GRADIENT-BOOSTING value, not the RF's 0.8905. T1/T2 unaffected.]
STOPPING RULE, fixed now to prevent an open-ended spend: A3 gets at most FOUR training runs on
box 2. If none clears T1, the honest finding is "image-input accuracy does not close on
structure-input methods under resolution + data + view augmentation", which is itself a
CVPR-relevant negative and pairs with the CP11 human row. No fifth run without a new hypothesis.

## ABLATION REQUIREMENT (so a win is attributable)
If T1 is cleared, the axes must be separated before the number enters a paper:
    run 1  native res + full data                 (isolates A+B; this is CP10's S1 cell, done)
    run 2  native res + full data + view aug      (isolates C)
Any claim of the form "view augmentation gave us X" requires run 1 and run 2 to differ by more
than seed noise, which at 1 seed cannot be established — so a single-seed A3 win is DIRECTIONAL
and must be re-run at 3 seeds before it is stated as SOTA.

## WHAT WOULD MAKE A WIN UNINTERPRETABLE
 - Any eval-protocol change (resolution, view set, K, or eval split) relative to the references.
 - Training on any structure that appears in the 210-structure eval set. The composition-
   exclusion split guarantees this at the material_id level; verify leakage = 0 before each run.
 - Reporting against the RF's 0.8905 without noting it takes ATOMIC COORDINATES as input while
   A3 takes only pixels. The comparison is informative precisely because the inputs differ, and
   the paper must say so in the same sentence.
 - Beating T1 while falling below the CP8 regularity floor (0.5286) on any per-system cell
   would indicate the gain is dataset regularity, not crystallography. Report per-system.

## RELATIONSHIP TO THE OTHER THREADS
 - CP10's S1 adapter (B1 @ native x comp-1610, already trained on box 1, loss ->0.0146) IS
   A3's run 1. Do not retrain it; evaluate it and use it as the A3 baseline. This also gives
   CP10's Q1/Q3 their number, so the two threads share the cell rather than duplicating it.
 - CP11's human row calibrates what T2/T3 mean. If experts score below T2 from the same
   renders, then matching ALIGNN from pixels would exceed human performance on this task, and
   that framing needs the human number first.

=================  BOX 2 SETUP AND AUGMENTATION BUILD (before any A3 training number)  ========
BOX: gpu-5090-vlm-project-2, vast contract 46011021, ssh6.vast.ai:11020, RTX 5090, $0.433/hr.
Verified before committing training time: torch 2.8.0+cu128, CUDA available, Qwen3-VL-8B loads
in 4-bit at 6.4 GB VRAM. NOTE this box runs transformers 5.14.1 while box 1 runs an older
version — the load path was smoke-tested here specifically because a silent API difference
would otherwise have surfaced hours into a run.

AUGMENTATION VIEWS (axis C of the prereg), defined and verified:
    aug_j1 -15x,-75y,-10z   aug_j2 -75x,-15y,-20z   aug_j3 -45x,-45y,-30z
    aug_j4 -20x,-40y,-60z   aug_j5 -70x,-50y,-05z   aug_j6 -35x,-20y,-75z
  Deliberately off-axis and deliberately NOT the frozen eval cameras
  ('0x,-90y,0z', '-90x,0y,0z', '0x,0y,0z', '-60x,-30y,-15z', '-30x,-60y,-45z').
  ZERO-OVERLAP with the eval set is ASSERTED in code, not assumed.
  The renderer already supported custom cameras via view_names/view_map — no code change.
  Rendered 9660 PNGs for 1610/1610 train structures, 0 failures, 681 s.
  LEAKAGE ASSERTED: no eval structure is augmented (train n eval overlap = 0, checked on box).

AUGMENTED TRAINING SET: each structure appears twice — once with the frozen 5 eval views, once
with 5 of its 6 augmentation views (input shape held at 5 images/example). B1 training examples
go 1610 -> 3220. THE EVAL FILE IS UNTOUCHED: eval remains the frozen 5-view protocol at K=3, so
every A3 number stays comparable to CP1b/CP3/CP7.

TWO HARNESS MISMATCHES CAUGHT BY INLINE ASSERTIONS BEFORE ANY GPU TIME WAS SPENT (recorded
because the second would have produced a meaningless number against T1):
 1. scripts/train_e2_lora.py has NO --train-file flag (that is the GRPO harness). Failed at
    argument parsing in seconds. Fixed by giving the augmented set its own data dir
    (data/e3_aug/) since the SFT harness reads <data-dir>/train.jsonl.
 2. The augmented rows referenced 8050 MISSING images: box 2 had only the augmentation renders,
    while the base 5-view renders lived on box 1. An `assert missing==0` stopped it. Without
    that line, training would have run for hours with half the examples failing to load and the
    resulting accuracy would have been reported against T1 as if it were real. Same class of
    bug as CP7's silent spglib fallback. FIX: box 2 renders the frozen base set itself
    (~15 min at the measured rate) rather than transferring 308 MB — this also keeps the two
    boxes independent, with no inter-box SSH keys.

DELIBERATE ALLOCATION (no 308 MB adapter transfer): each box works on what it already holds.
  box 1 has the trained B1_compnat_s0 adapter -> it runs A3 RUN 1's evaluation locally, which
        simultaneously produces CP10's Q1/Q3 number. One cell serves both threads.
  box 2 has the data + renderer -> it builds augmentation and runs A3 RUN 2 (new work).

=================  ANALYSIS PRE-REGISTRATION, WRITTEN BEFORE THE A3 NUMBER EXISTS  ===========
Run 2 (native 768px + 6-view augmentation, 3220 training examples) is still training. Committing
the interpretation now so the reading is not chosen after seeing the value.

THE THREE-WAY CONFOUND THAT MUST BE STATED WHATEVER THE RESULT. Run 2 changes THREE things at
once relative to the B1 reference (0.6143 +/- 0.0515 at 416px, 1610 examples):
    (i)   resolution 416 -> 768 (3.41x visual tokens)
    (ii)  view augmentation (6 extra cameras per structure, disjoint from the frozen eval views)
    (iii) training-set size 1610 -> 3220 examples
A gain CANNOT be attributed to any one of these. The pre-registered ablation requirement stands:
the CP10 pilot's S1 cell (native res, 1610 examples, NO augmentation) isolates (i)+(iii) from
(ii), and is the ONLY comparison that licenses an augmentation claim.

DECISION RULE, RESTATED FROM THE TOP OF THIS FILE:
  T1 = 0.666  movement threshold. Below this, run 2 has not moved the number and the SOTA push
              is reported as attempted-and-flat. No further runs.
  T2 = 0.756  the published ALIGNN crystal-system figure. Reaching it from PIXELS would be the
              paper's strongest single claim, and it is the only value that justifies further
              GPU spend under the stopping rule (at most 4 runs total).
  Between T1 and T2: report the gain, run the S1 ablation comparison, and STOP. A partial gain
              does not license a third and fourth run.

WHAT WOULD MAKE A WIN UNINTERPRETABLE, CHECKED BEFORE ANY CELEBRATION:
  a. LEAKAGE. The augmentation cameras must be disjoint from the 5 frozen eval views. Verified at
     render time (assert in a3_render_all.log, 0 overlap) but MUST be re-verified against the
     final eval manifest before the number is quoted.
  b. EVAL DRIFT. Run 2 must be evaluated on the SAME 210-structure composition-exclusion set, at
     the SAME K and temperature, as every row it is compared against. Any change makes the
     comparison invalid rather than favourable.
  c. THE 416-TRAINED REFERENCE IS NOT A FAIR CEILING. CP0c showed B1 drops 0.5905 -> 0.4571 when
     a 416-TRAINED adapter is evaluated at 768 — a train/test mismatch, not a resolution effect.
     Run 2 is TRAINED at native, so it must be compared against B1's 416-trained-416-evaluated
     0.6143, and the mismatch row must not be quoted as the baseline.
  d. REGULARITY FLOOR. Any new number is reported with its distance from the 0.5286 floor, and
     if it lands below the floor it is reported as below the floor regardless of how it compares
     to other arms.

IF RUN 2 LANDS BELOW T1: that is a reportable negative and it strengthens, not weakens, the
paper's framing — it would say the image-input ceiling is not a resolution or view-coverage
artifact, which is exactly what the CP0c insensitivity result already suggests. Report it plainly.

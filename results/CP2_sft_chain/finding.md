CHECKPOINT: CP2_sft_chain          GAP: does a hierarchical reasoning chain help?          STATUS: done (pilot scale, n_train=115; full-scale SFT arm pending). E2 has NO pre-registered gate in the plan; it reports whether the chain schema helps and, per plan, an indistinguishable/negative result shifts the program's weight to E3.

[This is a CORRECTED record (two follow-up rounds). The original is preserved verbatim
in finding_precorrection_snapshot.md. Round 1: (1) truncation audit — EXCLUDED, V1 row
stands; (2) mechanism example corrected (recurring string is a=b!=c -> tetragonal, not
"a=b=c -> cubic"); (4) renamed misappropriated "H1"/"Gate 2" labels; (5) McNemar tests,
V1-vs-B2 indistinguishability, pilot-scale qualifiers, structural-tilt note; (3) added
the V1b arm. Round 2 (this version): (1) RETRACTED the invalid distinct-string collapse
metric for V1b (low-cardinality vocab by design) and replaced with per-structure
geometry-step ACCURACY (V1/V1b ~32-36% full-triple); (4) transition analysis +
gold-prefix probe RE-DIAGNOSED the failure — it is a MOTIF repetition trap, not section
looping, and the answer mapping IS learned (gold-prefix 20/20); (2) bridged the
V1-recitation tension; (3) reworded E3's effect as hypothesis not fact; EOS-in-labels
confirmed. Audit outputs: samples/.]

METHOD DONE: Fine-tuned Qwen3-VL-8B-Instruct with QLoRA (4-bit nf4, LoRA r=16 on
attention+MLP proj, 3 epochs, lr 1e-4) on a held-out E2 dataset of 167 structures
(train 115 / val 22 / test 30), stratified across the 7 crystal systems and drawn
from BOTH sources (MP + JARVIS), DISJOINT from the CP0b/CP1 samples (0 leakage,
verified). Three training arms share the identical (5 images, question) input and
differ ONLY in the supervision target:
  B1  direct     -> "ANSWER: <crystal system>"
  B2  free CoT   -> free-form reasoning, then the answer
  V1  CoCr chain -> [GEOMETRY][SYSTEM/BRAVAIS][SYMMETRY][MOTIF][ANSWER], every step
                    generated deterministically from the CP0 label (symmetry step
                    justified by parsing the Hermann-Mauguin glyphs).
Arms B1/B2/V1 trained at 3 seeds (9 LoRA runs); a fourth arm V1b (3 seeds) was added
in the CP2 follow-up (see V1b section) for 12 runs total, all on an RTX 5090. Evaluated on the
held-out test split with deterministic decoding; primary metric = crystal-system
accuracy (micro over 30 structures, macro over 7 systems).

HYPOTHESIS (H-E2, this experiment's own hypothesis — NOT the plan's H1, which is
E3's process-vs-outcome comparison): V1 > B2 > B1 (the hierarchical chain, by
decomposing the task into checkable sub-steps, should beat free CoT, which beats
direct answer). The plan anticipated only two outcome branches for E2: V1 > B2 > B1
(schema helps) or V1 ~= B2 (shifts weight to E3).

RESULT: H-E2 is refuted at pilot scale (n_train=115). Direct supervision wins.

  arm                     micro acc (test, n=30)      macro
  B1  direct              0.711 +/- 0.069  <- best    0.672
  V1  hierarchical chain  0.378 +/- 0.069             0.411
  B2  free CoT            0.344 +/- 0.016             0.435
  (chance = 1/7 = 0.143)                              (figures/arm_comparison.png)

The observed outcome — B1 > BOTH reasoning arms — fell OUTSIDE both branches the plan
anticipated (it considered only V1 > B2 > B1 or V1 ~= B2). Recorded honestly as a gap
in the plan's E2 decision rule: pure-SFT direct supervision beating structured
reasoning at pilot scale was not among the pre-registered possibilities.

STATISTICS (paired, on the shared 30 test structures; per-structure majority vote
across the 3 seeds; exact McNemar on discordant pairs):
  B1 vs V1:  discordant b=15 / c=2,  McNemar p=0.0023  -> B1 significantly better
  B1 vs B2:  discordant b=15 / c=3,  McNemar p=0.0075  -> B1 significantly better
  V1 vs B2:  discordant b=4  / c=5,  McNemar p=1.00     -> INDISTINGUISHABLE
So the two reasoning arms (V1 0.378 vs B2 0.344) are NOT statistically separable; the
0.034 micro gap is well inside the n=30 binomial noise (SE ~= 0.091, ~+/-0.18 at 95%).
Only the 33 pp B1 advantage survives that noise. All 9 runs converged cleanly (B1
train loss -> ~0.05, reasoning arms -> ~0.2).

MECHANISM (why the chains lose — verified, not inferred): the reasoning arms
substitute MEMORIZED template geometry for actually reading the image, and reason
with CORRECT logic on those fabricated inputs (case (a): fabricated inputs, sound
downstream logic — see samples/mechanism_examples.json for 3 verbatim generations).
  - The V1 [GEOMETRY] step emits only 30 DISTINCT cell-parameter strings across 90
    test generations; one fabricated string "a=4.002, b=4.002, c=10.005" recurs 22
    times. That string is a=b!=c (a tetragonal-like metric), and in ALL 22 cases the
    model's [SYSTEM/BRAVAIS] step concludes "tetragonal, Bravais tP" — logically
    CONSISTENT with the fabricated a=b!=c. (My pre-correction text mis-stated this as
    "a=b=c -> cubic"; that conflated it with a different memorized string,
    "a=4.000,b=4.000,c=4.000". Corrected: the recurring 22x case is tetragonal, and
    the model's logic on its own fabricated numbers is sound — the failure is the
    fabrication, not the reasoning.) The fabricated a=b!=c is simply WRONG for the
    orthorhombic structures it is emitted on, so the tetragonal conclusion is wrong
    there. B2 is less collapsed (59/90 distinct) but still rounds to memorized values.
    (figures/mechanism.png panel a)
  - Termination: V1 reaches the [ANSWER] line in only 1.1% of generations, V1b in
    0/90 (B1 and B2: 100%). DIAGNOSED (CP2 follow-up item 4, correcting my earlier
    "loops through chain steps" claim): a transition analysis shows the chain emits
    each section tag exactly ONCE (4-5 tags/gen) — it does NOT cycle the sections.
    The generation instead gets stuck in a REPETITION LOOP INSIDE the [MOTIF] Wyckoff
    enumeration ("Ag on 4d, Ag on 4d, Ag on 4d, ...") and hits the token cap before
    reaching [ANSWER]. A gold-prefix probe confirms the answer mapping itself was
    learned: feed the gold chain through [MOTIF] and V1b emits [ANSWER] 20/20, CORRECT
    20/20. So the dominant failure is a DECODING-REPETITION pathology in the
    variable-length MOTIF step, not a failure to learn the system->answer mapping and
    not (primarily) a geometry-grounding failure. Scored fairly via a
    last-crystal-system fallback, both chain arms still lose. (samples/, and truncation
    audit below rules out target clipping.)
  - B1 has no intermediate text to fabricate: LoRA maps the visual features straight
    to the label, so there is no hallucinated geometry to poison the answer.

TRUNCATION AUDIT (blocking item 1 — EXCLUDED): tokenized all 115 V1 and 115 B2
training targets with the exact training tokenizer (Qwen3-VL processor). V1 target
lengths min/median/max = 205/231/294 tokens; B2 = 103/111/116; B1 = 4/6/8. Training
used NO truncation (processor called with padding=True only, no max_length) and the
model context is 262,144 tokens, so 115/115 V1 targets retained their [ANSWER] line +
EOS intact. V1's non-termination is therefore a GENUINE learned behavior, not a
clipped-target pipeline artifact — the V1 row stands as measured, no rerun required.

This is consistent with E0.5 + E1: the renders make crystal system recoverable in
principle (oracle 91%), but the finite static views do NOT let the model MEASURE
cell parameters to the precision the V1 chain's geometry step demands. Forced to
verbalize a measurement it cannot make, the model recites a plausible constant. But
V1b (below) shows this recitation is NOT specific to unmeasurable targets — it also
collapses when the geometry step asks only for view-makeable qualitative relations;
the collapse at pilot scale is driven by the data-hunger of generative-trace SFT, and
the ungroundable exact-value target made it worse, not possible. And the re-scored
geometry-step accuracy (item 1, below) shows the geometry step is weak but not
trivially wrong (~32-36% full-triple correct), so it is not the sole cause of the low
answer accuracy — the MOTIF repetition trap is the larger driver.

E2 OUTCOME -> E3 (no gate here; per plan, an indistinguishable/negative E2 shifts
weight to E3): the schema hypothesis is not supported by PURE SFT at pilot scale —
but the failure is diagnostic, not fatal, and it names E3's job precisely. The
hierarchical chain's advantage is contingent on its steps being GROUNDED in the
pixels. SFT teaches the chain's surface FORM (the model fluently produces the
five-part structure) but not its grounding (it fills the geometry slot with memorized
text and stalls in the MOTIF enumeration). Whether E3's PROCESS REWARD — scoring each
step against the source CIF — corrects this is precisely the HYPOTHESIS E3 tests (the
plan's H1): the intended mechanism is that a step whose content is contradicted by the
structure gets penalized, which should push the model toward reading rather than
reciting. That is a prediction, not an established result here. E2's role is to
MOTIVATE E3 and to specify its reward schema (see below), not to demonstrate E3's
effect; the program's weight shifts to the RL stage.

V1b ARM (fair-schema retest — CP2 follow-up item 3): V1's geometry step demanded exact
cell parameters the renders cannot supply, so its collapse could be blamed on an
ungroundable step rather than on the chain schema itself. V1b keeps the identical 5-part
schema and identical steps 2-5, but replaces the [GEOMETRY] step with ONLY
view-measurable qualitative relations (a~=b vs a!=b; angles ~90/~120/oblique; a coarse
axial-ratio bin) — no exact cell parameters anywhere. Same 115 structures, same images,
same config, 3 seeds. (traces.py:_qualitative_geometry; targets verified faithful across
all 7 systems.)

  arm                     micro acc (test, n=30, 3 seeds)
  B1  direct              0.711 +/- 0.068  <- best
  V1  chain (exact geom)  0.378 +/- 0.068
  B2  free CoT            0.344 +/- 0.016
  V1b chain (qual geom)   0.300 +/- 0.098

RESULT: V1b does NOT rescue the chain. It is statistically indistinguishable from V1
(McNemar p=1.0) and B2 (p=0.77), and B1 still beats it (p=0.0013). Sharper findings:
  - GEOMETRY-STEP ACCURACY (item 1 — the VALID metric; the distinct-string count is
    RETRACTED here because V1b's qualitative vocabulary is low-cardinality BY DESIGN
    (~7 canonical patterns for 7 systems), so "4 distinct in 90 gens" is also what a
    perfectly grounded model would emit — the count only diagnosed collapse for V1's
    continuous numeric strings). Scored per-structure against the CP0-label relations:
      component      V1 (exact geom)   V1b (qual geom)
      edge relation      0.500             0.678
      angle family       0.811             0.456
      ratio bin          0.489             0.700
      FULL triple        0.322             0.356
    Both arms get the full geometry triple right only ~32-36% of the time — the step
    is WEAK but not trivially collapsed (V1b better on edge/ratio, V1 better on angle).
    The over-emission is still real (one V1b pattern emitted 50x where at most ~13
    structures could genuinely carry it), but per-structure accuracy is the honest
    measure and it says the step is unreliable, not uniformly template-locked.
  - FAILURE LOCUS is NOT primarily the geometry step. The gold-prefix probe (item 4)
    shows V1b emits a CORRECT [ANSWER] 20/20 when handed a gold chain through [MOTIF] —
    the system->answer mapping is learned. The dominant failure is a decoding
    REPETITION TRAP in the variable-length [MOTIF] Wyckoff enumeration that prevents
    termination (both V1 and V1b). So the low answer accuracy is driven more by
    non-termination than by geometry grounding.
CONSEQUENCE FOR E3 (revised after the item-1/item-4 diagnostics): two concrete design
implications, stated as design choices, not as claims about E3's outcome.
  (a) Reward QUALITATIVE geometry, not exact values. V1b confirms qualitative relations
      (edge/angle/ratio) are what the views support; exact-value matching would reward
      an unmeasurable target. E3's process-reward geometry check should score the
      relations, at the ~edge/angle/ratio granularity V1b uses.
  (b) Do NOT inherit the free-form MOTIF enumeration as-is. The repetition trap that
      sinks both chain arms lives in the open-ended Wyckoff list; E3 should either
      constrain that step (fixed slots / dedup / length cap) or make termination
      explicitly rewarded, else GRPO will optimize a policy that also never reaches the
      answer. Whether the process reward then lifts grounding is E3's hypothesis to
      test, not a foregone conclusion.

CAVEATS (honest):
  - PILOT SCALE. Train n=115 structures is small in absolute terms; every "refuted"
    here means "refuted at pilot scale (n_train=115)". E2 is deliberately a WITHIN-ARM
    comparison on identical data; the 3 seeds bound the noise, and the B1-vs-reasoning
    gap (33 pp) dwarfs the seed spread (<7 pp) and survives paired McNemar (p<0.01).
  - STRUCTURAL TILT toward B1 at pilot scale. At 115 examples B1 fits a 7-way
    classification mapping (target 4-8 tokens), whereas the chain arms must fit long
    generative targets (V1 ~231 tokens). Reasoning-trace SFT is the most data-hungry
    regime, so a pilot systematically FAVORS the direct arm; the comparison is not
    neutral on sample size. The plan's full-scale SFT (50k-150k traces) is the
    definitive arm comparison — the pilot answers "does the chain help for free at
    small scale" (no), not "is the chain schema wrong" (untested at scale).
  - V1 tested "chains with an UNMEASURABLE step", not "chains" in general: its
    geometry step demands exact cell parameters the renders cannot supply, so template
    collapse is the optimal solution to that objective. The V1b arm (below) retests
    the schema with a view-measurable qualitative geometry step to separate "the
    schema fails" from "that particular step was ungroundable".
  - Test n=30, with thin per-system cells (monoclinic n=2, tetragonal/trigonal n=3),
    so per-system accuracies are indicative, not precise. The micro/macro headline
    is robust; the per-system table is directional.
  - V1 was re-evaluated at 900 max_new_tokens (vs 400) specifically to rule out
    answer-line truncation as the cause of its low score. The template collapse and
    non-termination persist -> the result is a real property of the SFT'd chain, not
    a measurement artifact.

LABEL/EOS NOTE (item 4): training supervises the assistant target incl. EOS —
labels = input_ids.clone() with the prompt span masked to -100 (train_e2_lora.py
L93-101); the target's terminal EOS is NOT masked, so termination WAS in the labels.
The model still fails to terminate under free decoding because generation derails into
the MOTIF repetition loop before the EOS position is reached.

REPRODUCE:
  build:  PYTHONPATH=src python scripts/build_e2_dataset.py --per-system 12
  train:  python scripts/train_e2_lora.py --arm {B1,B2,V1,V1b} --seed {0,1,2} ...  (on GPU box)
  eval:   python scripts/eval_e2.py --arm ... --adapter ... --out ... [--max-new-tokens 900]
  data:   data/e2/{train,val,test}.jsonl + manifest.json ; results.json (this dir)
  audits: samples/{mechanism_examples,truncation_audit,geometry_step_accuracy}.json

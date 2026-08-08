CHECKPOINT: CP2_sft_chain          GAP: does a hierarchical reasoning chain help?          STATUS: done (Gate 2: schema not supported by pure SFT; motivates E3)

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
Each arm trained at 3 seeds (9 LoRA runs total) on an RTX 5090. Evaluated on the
held-out test split with deterministic decoding; primary metric = crystal-system
accuracy (micro over 30 structures, macro over 7 systems).

HYPOTHESIS (from plan): H1 = V1 > B2 > B1 (the hierarchical chain, by decomposing
the task into checkable sub-steps, should beat free CoT, which beats direct answer).

RESULT: H1 is REFUTED at this training scale. Direct supervision wins decisively.

  arm                     micro acc (test, n=30)      macro
  B1  direct              0.711 +/- 0.069  <- best    0.672
  V1  hierarchical chain  0.378 +/- 0.069             0.411
  B2  free CoT            0.344 +/- 0.016             0.435
  (chance = 1/7 = 0.143)                              (figures/arm_comparison.png)

All 9 runs converged cleanly (B1 train loss -> ~0.05, reasoning arms -> ~0.2). The
gap is stable across seeds and far larger than the seed spread, so it is a real
ranking, not noise.

MECHANISM (why the chains lose — verified, not inferred): the reasoning arms
substitute MEMORIZED template geometry for actually reading the image.
  - The V1 [GEOMETRY] step emits only 30 DISTINCT cell-parameter strings across 90
    test generations; one fabricated string "a=4.002, b=4.002, c=10.005" recurs 22
    times on structures that are triclinic, orthorhombic AND tetragonal. The model
    then reasons CORRECTLY from the fabricated numbers (a=b=c -> cubic) — good logic
    on hallucinated inputs. B2 is less collapsed (59/90 distinct) but still rounds to
    memorized values. (figures/mechanism.png panel a)
  - V1 also never learned to TERMINATE: only 1.1% of generations reach the [ANSWER]
    line; the rest loop through chain steps until the token cap (persists at 900
    tokens, so this is not eval truncation). Scored fairly via a last-crystal-system
    fallback, V1 still loses. (figures/mechanism.png panel b)
  - B1 has no intermediate text to fabricate: LoRA maps the visual features straight
    to the label, so there is no hallucinated geometry to poison the answer.

This is consistent with E0.5 + E1: the renders make crystal system recoverable in
principle (oracle 91%), but the finite static views do NOT let the model MEASURE
cell parameters to the precision the chain's geometry step demands. Forced to
verbalize a measurement it cannot make, the model recites a plausible constant.

GATE 2 DECISION: the schema hypothesis is not supported by PURE SFT at this scale —
but the failure is diagnostic, not fatal, and it names E3's job precisely. The
hierarchical chain's advantage is contingent on its geometry step being GROUNDED in
the pixels. SFT teaches the chain's surface FORM (the model fluently produces the
five-part structure) but not its grounding (it fills the geometry slot with memorized
text). This is exactly the failure that E3's PROCESS REWARD — scoring each step
against the source CIF — is designed to correct: a step that fabricates cell
parameters contradicted by the structure gets penalized, forcing the model to read
rather than recite. E2 therefore MOTIVATES E3 rather than substituting for it, and
shifts the program's weight toward the RL stage.

CAVEATS (honest):
  - Train n=115 structures is small in absolute terms. E2 is deliberately a
    WITHIN-ARM comparison on identical data; the 3 seeds bound the noise, and the
    B1-vs-reasoning gap (33 pp) dwarfs the seed spread (<7 pp). A larger trace set
    would sharpen the numbers but is unlikely to flip a gap this size.
  - Test n=30, with thin per-system cells (monoclinic n=2, tetragonal/trigonal n=3),
    so per-system accuracies are indicative, not precise. The micro/macro headline
    is robust; the per-system table is directional.
  - V1 was re-evaluated at 900 max_new_tokens (vs 400) specifically to rule out
    answer-line truncation as the cause of its low score. The template collapse and
    non-termination persist -> the result is a real property of the SFT'd chain, not
    a measurement artifact.

REPRODUCE:
  build:  PYTHONPATH=src python scripts/build_e2_dataset.py --per-system 12
  train:  python scripts/train_e2_lora.py --arm {B1,B2,V1} --seed {0,1,2} ...  (on GPU box)
  eval:   python scripts/eval_e2.py --arm ... --adapter ... --out ...
  data:   data/e2/{train,val,test}.jsonl + manifest.json ; results.json (this dir)

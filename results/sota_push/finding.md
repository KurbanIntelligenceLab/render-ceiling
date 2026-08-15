CHECKPOINT: sota_push    GAP: Q3 — can pixel-input performance be pushed materially higher?
STATUS: RUN 2 DONE (native resolution + view augmentation, 1 seed). PRE-REGISTERED RULE FIRES
        AGAINST THE DIRECTION I WAS LEANING: T1 NOT CLEARED. No further runs under the stopping
        rule. Reported as attempted-and-flat.

=================  RESULT  =================
Direct arm, trained at NATIVE 768px (max_pixels 589824, 576 visual tokens/view read from the live
processor) on 3220 examples (1610 structures x2: base 5-view + 6-camera augmentation), 3 epochs,
1206 steps, final loss 0.1419, 8h12m on an RTX 5090. Evaluated on the SAME frozen 210-structure
composition-exclusion split, SAME K=3 / temperature 0.7 / 512 tokens, at native resolution
(matched to training, NOT the train/test mismatch of resolution_audit).

    A3 native + augmented   139/210 = 0.6619   Wilson 95% [0.5955, 0.7225]
    B1 reference (416px, 1610 examples, no augmentation)  0.6143 +/- 0.0515
    delta +0.0476

DECISION AGAINST THE PRE-REGISTERED THRESHOLDS (committed before this number existed):
    T1 movement 0.666  -> observed 0.6619, delta -0.0041  -> NOT CLEARED
      [PRECISION: the shortfall is -0.0039 against the UNROUNDED T1 of 0.6658; -0.0041 is
       against the rounded 0.666 as written in the prereg. Verdict identical either way.]
    T2 ALIGNN   0.756  -> delta -0.0941                   -> NOT REACHED
THE RULE SAYS STOP. Observed falls short of T1 by 0.0041 (0.0039 against the unrounded 0.6658),
which is 0.62% of the threshold. It
would be easy to call 0.6619 "essentially 0.666" and claim movement; the pre-registration exists
precisely to forbid that, and it is obeyed here. This is the fifth worked example in this program
of a pre-registered rule firing against the direction the agent was leaning.

WHY THE RULE IS RIGHT ON THE MERITS, NOT JUST PROCEDURALLY: the +0.0476 gain is WITHIN one
reference-seed SD (0.0515). The B1 reference's own three seeds span 0.567-0.686 — and 0.6619 sits
INSIDE that range, below its best seed. A single-seed result inside the reference's seed spread
is not evidence of movement. Promoting this to 3 seeds is what the pre-registration requires
before any comparison the paper cites, and the stopping rule forbids spending that here.

THE THREE-WAY CONFOUND, STATED AS REQUIRED: run 2 changes resolution (416 -> 768), view
augmentation (+6 cameras), AND training-set size (1610 -> 3220 examples) simultaneously. Even had
T1 cleared, no single factor could be credited. The merged_retrain pilot's S1 cell (native, 1610, NO
augmentation) is the only comparison that would isolate augmentation, and it is not yet run.

WHAT THIS DOES SUPPORT: the arm remains well ABOVE the regularity floor (+0.1333 over 0.5286), so
it is reading shape, not size. And it is consistent with resolution_audit's finding that this task's image
arms are insensitive to large increases in visual information — 3.41x more pixels plus doubled
data plus six extra viewpoints moved the number by less than the seed noise. That is the honest
reading and it corroborates, rather than contradicts, the rest of the paper.

CONSEQUENCE FOR Q3: pixel-input performance was NOT pushed materially higher by resolution, data
scale, or view augmentation. The remaining untested lever in 4E is TOOL COUPLING (model predicts
coordinates, spglib determines symmetry), which is a hybrid and must be reported as such, never as
pure pixel input. The gap to published ALIGNN (0.756 on THEIR data and split) is unclosed from
pixels, and after this run the honest position is that it is unlikely to close by scaling the
current recipe.

LIMITS: one seed. Single base model and LoRA configuration. The augmentation cameras were verified
disjoint from the 5 frozen eval views at render time (0 overlap, 9660 renders); the eval set,
protocol, K and temperature are identical to every row this is compared against.

REPRODUCE
  train: python scripts/train_e2_lora.py --arm B1 --seed 0 --data-dir data/e3 \
           --out adapters_a3/B1_aug_s0 --max-pixels 589824 --epochs 3 --lr 1e-4 --grad-accum 8
         (data/e3/train.jsonl swapped to the augmented 3220-row file; renders merged 8050+9660)
  eval:  python scripts/eval_e3.py --arm B1 --seed 0 --adapter adapters_a3/B1_aug_s0 \
           --data-dir data/e3 --samples 3 --temperature 0.7 --max-new-tokens 512 \
           --max-pixels 589824
  effective_resolution: 576 visual tokens/view (LIVE processor read, not a formula)

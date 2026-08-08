CHECKPOINT: CP29_v2b_seed_hygiene   GAP: V2b's three seeds give byte-identical macro-F1 (0.3857,
                                    81/210 each), recorded as macro_sd = 0.0.
STATUS: DONE, AND THE CAUSE IS SETTLED. The three adapters are NOT identical, so this is not a seeding
        defect. It is DECODE COLLAPSE: three genuinely different models emit the same restricted label
        set. The 0.000 SD is removed from every table and pooled-SD computation.

=================  THE DISCRIMINATING TEST  ====================================================
The plan offered this as optional. It was cheap because the adapters survive in the
all_adapters_weights.tar.gz artifact, so no retraining and no GPU were needed.
Pairwise LoRA parameter differences over 504 tensors / 43,646,976 parameters:
  pair      L2 diff    max|diff|   relative L2
  s0-s1      0.5538     0.000687      0.0147
  s0-s2      0.5507     0.000717      0.0146
  s1-s2      0.5609     0.000710      0.0149
IDENTICAL ADAPTERS WOULD GIVE EXACTLY ZERO. They give ~1.5% relative L2, mutually consistent across
all three pairs. So the seeds DID diverge in training; the seeding is not broken.
THEREFORE THE IDENTICAL MACRO-F1 IS A DECODE PROPERTY, not a training one: three different models
produce the same per-class score because they emit the same restricted set of labels, and macro-F1 over
a collapsed label set is insensitive to the weight differences that do exist. This is consistent with
the prediction collapse already recorded for the chain arms.

=================  WHAT IS DONE ABOUT IT  ======================================================
The 0.000 SD is REMOVED, not explained. It is not a measurement of seed variability and must not enter
a pooled SD, an error bar, or a power calculation.
NO CLAIM IN THIS PAPER USES V2B'S ACROSS-SEED SPREAD, which is why this is bookkeeping rather than a
retraction:
  - direct-versus-chain is paired McNemar on per-structure vectors, which needs no spread;
  - the CP14 and CP12 comparison bands use B1's seed SD (0.0515), not V2b's.
Recorded so that a future reader does not resurrect 0.000 as evidence of seed stability. It is the
opposite: it is evidence that macro-F1 cannot see this arm's seed variation at all.

=================  WHAT THIS DOES NOT ESTABLISH  ==============================================
The magnitude of V2b's true seed spread is UNKNOWN and is not estimated here. Establishing it needs
per-structure dumps from all three seeds under the same decode settings, which would be a new
measurement. No interval is asserted.

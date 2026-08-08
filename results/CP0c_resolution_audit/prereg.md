# PRE-REGISTRATION — effective-resolution audit (BLOCKING for the scope reframe)
# Written and committed BEFORE any re-eval number was produced.

## THE CONFOUND (verified from the live processor, not from formula)
Every CoCr run to date (E1, E2, E3, CP1b, CP9) used max_pixels=200704. Measured on the box
with the actual Qwen3-VL processor on a real 768x768 render:

  image_grid_thw          = [1, 26, 26] patches
  patch_size / merge_size = 16 / 2   (=> 32 px per emitted visual token)
  EFFECTIVE PIXELS        = 416 x 416
  visual tokens per view  = 169   (the 171 quoted in CP1b included 2 delimiter tokens)
  downsample vs 768px     = 1.846x linear, 3.408x in AREA

So the models never saw the 768x768 renders we designed and validated; they saw 416x416.
Raising the cap: max_pixels >= 589824 yields grid 48x48 = 768x768 px = 576 tokens/view
(2880 visual tokens for 5 views, vs 845 today). Values above 589824 give no further gain
(the render is the ceiling).

## WHAT IS BEING RUN
Re-evaluate EXISTING checkpoints on the SAME 210-structure composition-exclusion eval set,
SAME majority-vote protocol (3 samples, temp 0.7, 512 max new tokens), changing ONLY
max_pixels 200704 -> 589824. NO retraining.
Arms: B1 (direct), SFT-V1 (chain, pre-GRPO), V2b (Gate-2 winner). Seed 0 first for all three;
extend to all seeds only if seed 0 shows movement (to bound cost).
Metrics: micro/macro accuracy AND geometry-step correctness (the perception-specific metric).

## A CONFOUND INSIDE THE AUDIT — pre-registered so it cannot be read selectively
The LoRA adapters were TRAINED at 416x416. Evaluating at 768x768 is therefore a train/test
resolution mismatch, and Qwen3-VL's native-dynamic-resolution handling is not a guarantee of
transfer. Consequences for interpretation, fixed in advance:
  - An INCREASE at higher resolution is a CLEAN POSITIVE: the information was there and was
    being destroyed by downsampling, and the model can use it despite the mismatch.
  - A DECREASE is AMBIGUOUS: it may be train/test mismatch rather than evidence that
    resolution is irrelevant. A decrease therefore does NOT license "resolution excluded";
    it licenses only "not testable without retraining at native resolution".
  - NO MOVEMENT (< seed SD) is the only outcome that supports "resolution excluded", and even
    then only for these checkpoints at this eval.

## DECISION RULE (pre-registered)
Reference seed-SDs from the existing matrix: B1 SD 0.0515, V2b macro SD 0.000 (3 seeds
identical), B3 SD 0.045. Use 0.05 as the movement threshold for accuracy (the largest
observed arm SD), and report geometry-step movement against its own spread.

  (i)  ANY arm's accuracy OR geometry-step correctness moves UP by > 0.05
       => RESOLUTION IS A CONFOUND in every perception claim. Actions: rerun the affected
          evals at native resolution; annotate ALL prior findings (CP1, CP2, CP3, CP1b, CP9)
          with the effective resolution they were measured at; and explicitly reconsider
          whether CP2's geometry FABRICATION finding partially reflects cell edges that were
          unreadable at 416px rather than a pure grounding failure.
  (ii) Movement DOWN by > 0.05 => record as "confounded by train/test mismatch; not
          resolvable without retraining"; do NOT claim resolution is excluded.
  (iii) |movement| <= 0.05 on both metrics for all three arms => record "RESOLUTION EXCLUDED"
          and freeze renders/max_pixels as-is.

## STANDING FIELD (adopted regardless of outcome)
Every future results.json carries an `effective_resolution` block:
  {max_pixels, grid_thw, patch_size, merge_size, effective_px, visual_tokens_per_view,
   n_views, prefill_tokens_per_sample}
read from the live processor, never computed by formula.

## KNOWN DOWNSTREAM CORRECTION (independent of the outcome)
CP1b's budget accounting used 171 visual tokens/view and 938 prefill tokens/sample. The
correct current-config numbers are 169 tokens/view and the same 938 measured prefill (the
delimiters are real prompt tokens, so the prefill total stands; only the attribution changes).
At native resolution prefill becomes ~2973 tokens/sample, which CHANGES the FLOPs ratio
between B1 and the chain arms and must be recomputed if native resolution is adopted.

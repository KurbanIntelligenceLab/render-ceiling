CHECKPOINT: resolution_audit     GAP: were all perception claims measured at a resolution
                                            that could support them?
STATUS: DONE for all three arms (B1, V2b, V1 — seed 0 each; V1 and V1_s0 rows are in
        results.json under results_like_for_like_per_seed). The earlier header said the V1
        arm was 'still generating'; it landed and this record is complete.
RESULT: pre-registered BRANCH (ii) — AMBIGUOUS. Resolution is NOT shown to be a confound, but
it is also NOT excludable, because the only arm that moved moved DOWNWARD and the adapters were
trained at the low resolution. Per the pre-registration a decrease licenses ONLY "not testable
without retraining at native resolution".

=================  THE CONFOUND (confirmed, and worse than the estimate)  =================
Measured from the live processor on a real 768x768 render, and independently confirmed in the
harness code (scripts/eval_e3.py:46, --max-pixels default 200704):

  max_pixels used in EVERY run to date (E1, E2, E3, exclusion_baselines, calibration): 200704
  image_grid_thw = [1, 26, 26] patches; patch_size 16, merge_size 2 (=> 32 px per visual token)
  EFFECTIVE PIXELS SEEN BY THE MODEL:  416 x 416      (not 768 x 768)
  visual tokens per view: 169     (exclusion_baselines quoted 171; the extra 2 were image delimiters)
  downsample vs the designed renders: 1.846x linear, 3.408x IN AREA
  native 768x768 requires max_pixels >= 589824 -> grid 48x48 -> 576 tokens/view
    (values above 589824 buy nothing; the render is the ceiling)

So the models never saw the renders we designed and validated in E0. They saw a 3.4x-decimated
version. That is a real pipeline finding independent of whether it changed any number.

=================  RESULT (like-for-like, PER SEED, not arm means)  =================
Same 210-structure composition-exclusion eval, same protocol (3-sample vote, temp 0.7, 512 max
new tokens), ONLY max_pixels changed. No retraining.

  arm      metric   416x416   768x768    delta    vs 0.05 threshold
  B1_s0    micro     0.5905    0.4571   -0.1334   EXCEEDS
  V1_s0    micro     0.3524    0.3619   +0.0095   within
  V1_s0    faith     0.2489    0.2278   -0.0211   within
  V2b_s0   micro     0.3857    0.3714   -0.0143   within
  V2b_s0   faith     0.2744    0.2694   -0.0050   within
  ALL THREE ARMS NOW COMPLETE.

  The V1 arm STRENGTHENS the reading rather than merely adding a row: BOTH chain checkpoints
  (V1 pre-GRPO and V2b post-GRPO) are insensitive to a 3.408x AREA change, and V1's accuracy
  even moves slightly UP (+0.0095). The insensitivity is therefore a property of the CHAIN
  FORMAT, reproduced across two independently trained checkpoints, not an idiosyncrasy of one
  adapter. Only the DIRECT arm is resolution-sensitive, and it moves DOWN — the signature of
  train/test mismatch, since it alone has no chain text to fall back on when the visual
  statistics shift.

=================  BRANCH (ii), AND WHY IT IS NOT "RESOLUTION EXCLUDED"  =================
The pre-registration fixed the interpretation in advance precisely so this could not be read
selectively:
  - an INCREASE would have been a clean positive (information was being destroyed);
  - NO MOVEMENT on all arms would have supported "resolution excluded";
  - a DECREASE is AMBIGUOUS, because the adapters were TRAINED at 416x416, so evaluating at
    768x768 is a train/test resolution mismatch. Qwen3-VL's native-dynamic-resolution handling
    is not a guarantee of transfer.
B1 fell 0.133 — far outside threshold and outside its own seed SD (0.0515). That is most
plausibly the mismatch, not evidence that higher resolution HURTS perception. It cannot be
distinguished from a genuine resolution effect without retraining at native resolution.

WHAT CAN BE SAID:
  - The CHAIN arm (V2b) is essentially INSENSITIVE to the 3.4x resolution change on both
    accuracy (-0.014) and faithfulness (-0.005). This is meaningful evidence that the chain
    arms' weak geometry was NOT primarily caused by unreadable cell edges at 416px — the
    information they were failing to use was already present at the lower resolution.
  - Therefore the sft_chain geometry-FABRICATION diagnosis is NOT overturned by this audit. It is not
    fully vindicated either (V1 pending, single seed), but the resolution explanation for it is
    now the LESS likely one.
  - No prior conclusion is retracted on the basis of this audit.

WHAT CANNOT BE SAID:
  - "Resolution excluded." B1's drop forbids it.
  - That native resolution would not help a model TRAINED at native resolution. Untested.

=================  ACTIONS TAKEN  =================
1. ANNOTATION: all prior perception findings must record the effective resolution they were
   measured at (416x416, 169 visual tokens/view). Adopted as a standing field.
2. STANDING FIELD in every future results.json, read from the live processor, never by formula:
     {max_pixels, grid_thw, patch_size, merge_size, effective_px, visual_tokens_per_view,
      n_views, non_visual_prompt_tokens, prefill_tokens_per_sample}
3. BUDGET CORRECTION: see budget_correction.md. Native prefill is 2973 vs 938 tokens/sample
   (3.17x). TWO RATIOS MUST BE KEPT SEPARATE (team item 2 fix — do NOT pair a native FLOPs
   ratio with 416-trained accuracy in one claim):
     DEPLOYED-CONFIG ratio (what every reported accuracy was measured at): 1.417x
     NATIVE-REGIME ratio (hypothetical):                                   1.132x
   The native-regime ratio is PENDING native-TRAINED accuracies. B1's measured native accuracy
   (0.4571) is train/test-mismatched and cannot be combined with the 1.132x figure. So the
   correct statement is: at the deployed config B1 wins at a 1.417x compute disadvantage-adjusted
   comparison; IF a native-trained comparison is run, the ratio would be 1.132x, and only then
   may the two be paired.
4. OPEN ITEM: any future training run should use max_pixels >= 589824 so the models actually see
   the renders E0 validated. Cost: prefill 938 -> 2973 tokens/sample, and measured wall-clock at
   native resolution was ~3x slower per eval arm.

REPRODUCE
  audit:  python scripts/eval_e3.py --arm {B1,V2b,V1} --seed 0 --adapter <ckpt> \
            --data-dir data/e3 --out evals_res768/eval_<arm>_s0_mp589824.json \
            --samples 3 --temperature 0.7 --max-new-tokens 512 --max-pixels 589824
  prereg: prereg.md (committed before any re-eval number existed)
  counts: res_audit_current.json (read from the live processor on the box)

=================  GEOMETRY-STEP PROBE (item 2): READING (b) CONFIRMED  =================
Both candidate sentences were written BEFORE the numbers existed (geometry_step_prereg.md).
The data picked reading (b), and a follow-up test made it sharper than the pre-registered form.

V2b seed 0, same 210 structures, geometry-STEP accuracy scored against pipeline truth:
    @ max_pixels 200704 (416x416):  0.6349
    @ max_pixels 589824 (768x768):  0.6476
    DELTA = +0.0127          -> FLAT (|delta| <= 0.05) -> pre-registered branch (ii)

## THE PRE-REGISTERED SENTENCE NEEDED SHARPENING, NOT REPLACING
The pre-registered wording for (ii) argued the step is "invariant to the pixels it purports to
measure ... an output that never depended on the image cannot respond to improving it." The
aggregate supports that, but a per-structure check does NOT support the strong "never depended
on the image" clause, and it must not be written that way:

    structures whose geometry score CHANGED at all:  111/210 (52.9%)
    mean |change| per structure:                     0.2190
    improved 58 / worsened 53 / unchanged 99
    mean change +0.0127, sd 0.3201, se 0.0221, t = +0.57
    sign test on the 111 changed: z = +0.47  -> INDISTINGUISHABLE FROM RANDOM CHURN

So the outputs DO move when the pixels change — they are not literally independent of the image.
What they do not do is move in the RIGHT DIRECTION. The change is symmetric noise.

## THE NOISE-FLOOR COMPARISON THAT SETTLES IT
Same resolution, V2b seeds 1 vs 2 (a pure reseed, no input change at all):
    changed 79/210 (37.6%), mean |change| 0.1413, mean delta +0.0206
Versus the 3.4x resolution change: changed 52.9%, mean |change| 0.2190, mean delta +0.0127.
A 3.408x increase in visual information moves the geometry step by about as much as, and in no
better a direction than, changing the random seed. The mean improvement from more pixels
(+0.0127) is SMALLER than the mean drift from reseeding (+0.0206).

## SENTENCE TO WRITE (replaces the pre-registered (ii) wording)
"Giving the chain 3.4x more visual information changes its geometry step no more meaningfully
 than changing the random seed does: 53% of per-structure scores move, but symmetrically
 (58 up, 53 down, sign-test z = 0.47) and with a net effect (+0.013) smaller than seed-to-seed
 drift (+0.021). The step is responsive to the image without being informed by it — which is
 the fabrication signature, and is why the sft_chain diagnosis survives the resolution audit."

## WHY THIS IS THE STRONGER RESULT
It converts a null (nothing improved) into positive mechanistic evidence: genuine measurement
must improve when resolution improves; recitation-with-noise must not. The chain sits in the
second regime. Reading (a) — "the information was already present" — is NOT what the data shows,
because if the chain were reading available information, more of it should have helped at least
directionally. It did not.

CAVEATS: single seed at native resolution (V2b_s0), single arm; the native run is also
train/test resolution-mismatched (resolution_audit branch (ii)), which could suppress a real gain. The
noise-floor comparison partly controls for that by using a same-resolution reseed as the
yardstick, but a native-TRAINED model is still the clean test (queued in the merged retrain).

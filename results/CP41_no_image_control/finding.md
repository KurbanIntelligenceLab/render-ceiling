CHECKPOINT: CP41_no_image_control   GAP: every zero-shot row is prompted with renders AND a formula
   preamble. Nothing established that the IMAGE was doing the work. (ICLR plan, Phase D)
STATUS: DONE. BRANCH N2 FIRES DECISIVELY — the images carry the signal. And the expectation I
        pre-registered was WRONG in a direction that STRENGTHENS the benchmark: text-only lands near
        CHANCE, not near the composition-only floor.

=================  THE CONTROL  ================================================================
Byte-identical prompt text with the image blocks removed, same 210 structures, K=3, temperature 0.7 —
so the IMAGE rows are CP26's verbatim and nothing was re-run on that side.
  model                        IMAGE     TEXT    delta   img-only  txt-only     exact p
  llama-4-maverick            0.4429   0.1381   +0.3048       73         9     1.4e-13
  qwen3-vl-8b-instruct        0.3762   0.1667   +0.2095       60        16     3.9e-07
  bytedance-seed-1.6          0.2571   0.1524   +0.1048       37        15     3.2e-03
  gpt-4.1-mini                    --  REFUSAL   210/210 unparseable -> NOT SCORED
Paired McNemar per structure. Discordance is heavily one-sided in both cases (73:9 and 60:16).

=================  THE REFUSAL IS A RESULT, REPORTED SEPARATELY  ===============================
gpt-4.1-mini returned NOTHING parseable on all 210. That is not accuracy 0.0 and is not scored as such.
The pre-registration required reporting a high refusal rate separately from an accuracy row, and I
checked the mechanism rather than inferring it: the raw response is an explicit request for the missing
images ("Please upload or share the images of the crystal structure you want me to analyze..."). So the
model declined the task without visual input. Recorded as REFUSAL, 210/210, excluded from the paired
comparison by the >5% unparseable gate fixed before the run.

=================  MY REGISTERED EXPECTATION WAS WRONG, AND THAT MATTERS  ======================
I wrote down that TEXT would land NEAR the shape-free floor, on the reasoning that the floor is itself a
composition-only model and the preamble supplies the formula. It does not:
  llama-4-maverick TEXT  29/210 = 0.1381   vs floor 111/210   one-sided p = 2.7e-32
  seed-1.6         TEXT  32/210 = 0.1524   vs floor 111/210   one-sided p = 7.7e-30
  qwen3-vl-8b      TEXT  35/210 = 0.1667   vs floor 111/210   one-sided p = 1.6e-27
  7-way chance                   0.1429
Both TEXT arms sit at CHANCE, far BELOW the floor. So the formula preamble does far less work than the
composition-only floor captures — a learned model reading composition does something these VLMs do not do
from the formula string alone.
CONSEQUENCE, AND IT RUNS THE OTHER WAY FROM WHAT I EXPECTED: the shape-free floor is a HARDER reference
than a text-only VLM, not an easier one. The "thirteen models below the floor" result is therefore
stronger than if TEXT had matched the floor, because the floor is not merely reproducing what the prompt
already gives away.

=================  WHAT THIS ESTABLISHES  ======================================================
For the THREE scored models on this sample, the IMAGE contributes 0.105 to 0.305 accuracy, paired and
significant on every one (p = 3.2e-03, 3.9e-07, 1.4e-13). The benchmark measures vision, not formula
lookup. Note the spread: the image is worth three times as much to the strongest model as to the weakest,
so "the images matter" is not a uniform statement across the roster.
ALL THREE TEXT ARMS SIT BELOW THE FLOOR AND NEAR CHANCE: 0.1381, 0.1524, 0.1667 against 7-way chance
0.1429, with floor p-values of 2.7e-32, 7.7e-30 and 1.6e-27.

=================  WHAT THIS DOES NOT ESTABLISH  ==============================================
Three scored models of four attempted, on the ORIGINAL sample only. Nothing about the fine-tuned arms,
which were trained on renders and are not part of this comparison. And nothing about WHICH visual cue
carries the 0.21-0.30 — that is the cue-sufficiency question, whose stratified claim is withdrawn.

=================  ROSTER EXTENSION (directive P2-1) — R2 FIRES, NOT R1  =======================
Extended from 4 attempted models to the FULL 16-model roster (13 CP26 + 3 CP14 frontier). 13 SCORED,
3 unscored under the pre-registered gates. K=3 on every row; IMAGE rows are CP26/CP14 verbatim, not re-run.
  model                            IMAGE     TEXT     delta   i-only  t-only    exact p
  gemini-3.6-flash (K=3)          0.7333   0.1619   +0.5714     139      19    1.0e-23
  claude-opus-4.8 (K=3)           0.5810   0.1667   +0.4143      98      11    1.3e-18
  glm-4.6v (K=3)                  0.4429   0.1286   +0.3143      93      12    2.4e-13
  llama-4-maverick (K=3)          0.4429   0.1381   +0.3048      73       9    1.4e-13
  qwen3-vl-8b (K=3)               0.3762   0.1667   +0.2095      60      16    3.9e-07
  qwen3-vl-235b-a22b (K=3)        0.3333   0.1429   +0.1905      58      18    4.7e-06
  qwen2.5-vl-72b (K=3)            0.2524   0.1286   +0.1238      43      17    1.1e-03
  qwen3-vl-32b (K=3)              0.2286   0.1190   +0.1095      41      18    3.8e-03
  seed-1.6 (K=3)                  0.2571   0.1524   +0.1048      37      15    3.2e-03
  mistral-medium-3.1 (K=3)        0.2286   0.1476   +0.0810      40      23    4.3e-02
  --- NOT SIGNIFICANT, NAMED INDIVIDUALLY AS THE PRE-REGISTRATION REQUIRED ---
  llama-4-scout (K=3)             0.2048   0.1762   +0.0286      30      24    4.97e-01
  nova-pro-v1 (K=3)               0.1810   0.1429   +0.0381      16       8    1.52e-01
  mistral-small-2603 (K=3)        0.1476   0.1619   -0.0143      22      25    7.71e-01
  --- UNSCORED, WITH THE GATE THAT EXCLUDED EACH ---
  gpt-4.1-mini (K=3)              210/210 unparseable: the raw response is an explicit request for the
                                  missing images, so it DECLINED rather than answered wrongly
  grok-4.5 (K=3)                   27/210 unparseable = 0.129, over the 5% gate
  gemini-2.5-flash (K=3)          302/630 API errors = 0.479, over the 5% gate

R1 DOES NOT FIRE. Ten of thirteen scored models show a significant positive image contribution (+0.0810 to
+0.5714, max p = 0.043). Three do not, so the roster-level claim is SCOPED, not universal: THE BENCHMARK
MEASURES VISION FOR EVERY MODEL THAT CAN DO THE TASK AT ALL.

THE THREE NULLS ARE MOSTLY NOT FORMULA-LOOKUP, AND THE DISCRIMINATING TEST IS FREE. A formula-lookup row
must score ABOVE CHANCE WITH IMAGES — it is scoring from the text. A floor-effect row is already at chance
with images, so removal has nothing to cost. Against 7-way chance:
  nova-pro-v1          38/210, p = 0.073 -> NOT above chance: FLOOR EFFECT
  mistral-small-2603   31/210, p = 0.452 -> NOT above chance: FLOOR EFFECT
  llama-4-scout        43/210, p = 0.009 -> ABOVE chance yet no image contribution:
                       GENUINELY AMBIGUOUS, named rather than absorbed into either reading.

THE PRE-REGISTERED ARITHMETIC CAVEAT IS EXACTLY WHAT HAPPENED, which is why it was written down before the
run. Spearman(IMAGE accuracy, delta) = 0.9725, p < 1e-4: image contribution is almost perfectly
rank-correlated with how well the model does WITH images. The three nulls are the three weakest models.

R3 DOES NOT FIRE. Every scored TEXT arm sits at chance (0.1190-0.1762 against 7-way chance 0.1429) and
significantly below the sample's floor, so the floor remains a HARDER reference than a text-only VLM.

A HARNESS DEFECT WAS FOUND AND FIXED HERE, AND IT COST TWO WHOLE ARMS SILENTLY. Two models printed DONE
and wrote NO output file: ask() returns None when retries are exhausted, and the aggregation called
.startswith() on it, raising AttributeError AFTER all 630 calls had been paid for, while the driving shell
loop's echo fired regardless of exit status. None is now counted as an api_error. CP26 was audited and is
unaffected: all 13 rows have output files. The standing check is now to diff models-with-a-file against the
requested roster before scoring anything.

CHECKPOINT: CP53_rung_R3_coords_as_text   GAP: R1's oracle uses a PERFECT reasoner (spglib) while the model
     arms use their own, so perception and symbolic reasoning are confounded. R3 removes extraction by
     supplying ground-truth geometry as text. (ICLR directive, rung R3)
STATUS: DONE, 14 OF 15 ARMS SCORED. BRANCH C3 FIRES ON ALL 14 — AND THE DECOMPOSITION CONTRADICTS THE
     DIRECTIVE'S THESIS. Perception is the MINORITY share of the gap for 12 of 14 models.

THE HEADLINE, AND IT IS NOT WHAT THE DIRECTIVE PREDICTED.
Given PERFECT geometry as text, no model reaches the oracle. Best R3 is 0.8524 (gemini-3.6-flash and
grok-4.5, tied) against the oracle's 0.9524. C1 ("the entire deficit is perception") DOES NOT FIRE.
C2 ("models cannot reason at all from geometry") also does not fire — every arm is far above the
formula-only text control. What fires is C3, on all 14 scored arms, and the pre-registered decomposition
then says something the directive assumed away:
    perception share = R3 - R4    (what supplying geometry buys)
    reasoning share  = R1 - R3    (what remains missing WITH perfect geometry)
  median perception fraction 30.9%, range 0.9% to 70.4%.
  Only 2 of 14 models have perception as the majority share; 12 of 14 have REASONING as the larger share (gemini-3.6-flash, grok-4.5 are the exceptions).
SO "PERCEPTION IS THE BOTTLENECK" IS FALSE AS A GENERAL STATEMENT ON THIS TASK. It is true for the two
strongest models and false for the rest, and the direction is systematic.

THE CONTROL PAIR THAT MAKES THIS READABLE, and it is the reason the number is trustworthy.
CP41 removed the images and left the FORMULA: every scored arm collapsed to 7-way chance (mean 0.1357).
CP53 removes the images and supplies the FULL GEOMETRY: every arm jumps to 0.41-0.85. The two controls
differ in exactly one thing, so the jump is attributable to the geometry rather than to text-mode prompting.
That rules out the obvious objection that models simply do better without images.

  model                              PIXELS    formula-only   GEOMETRY    delta   paired p
  google/gemini-3.6-flash            0.7333       0.1619       0.8524    +0.1191   2.6e-03
  x-ai/grok-4.5                      0.6143       0.1238       0.8524    +0.2381   7.8e-08
  anthropic/claude-opus-4.8          0.5810       0.1667       0.6667    +0.0857   9.8e-02
  qwen/qwen3-vl-235b-a22b            0.3333       0.1429       0.5429    +0.2096   1.6e-05
  meta-llama/llama-4-scout           0.2048       0.1762       0.5048    +0.3000   3.0e-09
  meta-llama/llama-4-maverick        0.4429       0.1381       0.4952    +0.0523   3.5e-01
  amazon/nova-pro-v1                 0.1810       0.1429       0.4667    +0.2857   2.7e-11
  mistralai/mistral-medium-3.1       0.2286       0.1476       0.4524    +0.2238   1.9e-06
  mistralai/mistral-small-2603       0.1476       0.1619       0.4524    +0.3048   1.6e-10
  qwen/qwen3-vl-32b-instruct         0.2286       0.1190       0.4524    +0.2238   3.0e-07
  qwen/qwen3-vl-8b-instruct          0.3762       0.1667       0.4524    +0.0762   1.8e-01
  z-ai/glm-4.6v                      0.4429       0.1286       0.4476    +0.0047   1.0e+00
  bytedance-seed/seed-1.6            0.2571       0.1524       0.4238    +0.1667   1.6e-03
  openai/gpt-4.1-mini                0.3667         --         0.4143    +0.0476   3.9e-01
  9 of 14 gains are significant at 0.05. Five are not, and they are not pooled away.

THE INVERSE CORRELATION IS THE MOST INTERESTING NUMBER HERE.
Spearman(pixel accuracy, perception share) = -0.6439, p = 0.0130. The models that read pixels WORST gain
LEAST in absolute share terms relative to their total gap — because their reasoning ceiling binds first.
Supplying perfect geometry to a weak model does not make it competent: mistral-small goes 0.1476 -> 0.4524
and still leaves 0.5000 on the table. The bottleneck MOVES with model strength, which is a more precise
statement than either "perception" or "reasoning" alone and is only visible because the oracle fixes the
top of the ladder.

WHAT WAS NOT SCORED, AND WHY.
qwen/qwen2.5-vl-72b-instruct: 217 of 630 calls returned API errors (34.4%), over the pre-registered 5%
gate, with 5.7% unparseable also over gate. Reported UNSCORED rather than dropped silently. Roster is
14 of 15.

PROMPT-LENGTH CONFOUND, MEASURED RATHER THAN ASSUMED. The pre-registration required reporting prompt length
so a length effect would be visible. Mean approx 177 tokens, median 170, max 250, and NO structure exceeded
the 60-atom truncation threshold, so no geometry was withheld from any model. The R3 prompts are SHORTER
than the five-image pixel prompts they are compared against, so a length advantage cannot explain the gain.

SCOPE. Original eval sample only, ground-truth geometry. This bounds symbolic reasoning GIVEN perfect
perception; it says nothing about what any real pipeline achieves. Not novel as a design: this is the
CIF-supplied condition of 2605.29446 and the no-image family of 2604.16060, cited as prior use.

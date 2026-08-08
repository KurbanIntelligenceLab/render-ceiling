CHECKPOINT: CP26_model_sweep   GAP: a four-row leaderboard is not a benchmark. Does the difficulty
                               claim hold across the field, or only on our own arms? (directive item 3)
STATUS: DONE. BRANCH S1 FIRES, AND IT FIRES ON TWO INDEPENDENT RUNS. All 13 models fall below the
        shape-free regularity floor and the best falls significantly below it. The difficulty claim is
        established across EIGHT vendors and a 50x range in total parameters (8B to 400B), with the
        LARGEST model tested tied for best and still 18 structures short of the floor.
        READ THE MEASUREMENT-PROVENANCE SECTION BEFORE QUOTING ANY NUMBER: this sweep was accidentally
        run twice, and an earlier version of this record mixed the two runs into one table.

=================  THE CANONICAL LEADERBOARD — ORIGINAL EVAL SET, n=210, K=3 MAJORITY VOTE  ====
Frozen protocol, CP14 prompt verbatim, no per-model tuning, denominators fixed at 210, parse failures
and API errors scored as errors rather than dropped. All counts recomputed from the per-structure
prediction vectors, not read from a stored summary field.
  model                                 k/210   micro    macro-F1   api err
  meta-llama/llama-4-maverick           93      0.4429   0.3620     0
  z-ai/glm-4.6v                         93      0.4429   0.4204     0
  google/gemini-2.5-flash               90      0.4286   0.3802     0
  qwen/qwen3-vl-8b-instruct             79      0.3762   0.3079     0
  openai/gpt-4.1-mini                   77      0.3667   0.3127     0
  qwen/qwen3-vl-235b-a22b-instruct      70      0.3333   0.2420     3
  bytedance-seed/seed-1.6               54      0.2571   0.2092     0
  qwen/qwen2.5-vl-72b-instruct          53      0.2524   0.2191     2
  qwen/qwen3-vl-32b-instruct            48      0.2286   0.2231     0
  mistralai/mistral-medium-3.1          48      0.2286   0.1845     0
  meta-llama/llama-4-scout              43      0.2048   0.1806     0
  amazon/nova-pro-v1                    38      0.1810   0.0966     0
  mistralai/mistral-small-2603          31      0.1476   0.0827     0
  ---------------------------------------------------------------------------
  SHAPE-FREE REGULARITY FLOOR          111      0.5286      —        —
  our best fine-tuned arm (A3)         145      0.6905      —        —

=================  BRANCH S1: NO OPEN MODEL CLEARS THE FLOOR  =================================
Best open models are llama-4-maverick and glm-4.6v, tied at 93/210 = 0.4429, which is 18 structures
BELOW the floor's 111/210. One-sided binomial against the floor rate: p = 0.0078 — significantly below,
not merely short of it.
S3 DOES NOT FIRE: no model approaches our best fine-tune (145/210); the nearest is 52 structures behind.
The fine-tuning contribution is not bounded by any zero-shot row here.
WHAT THIS ESTABLISHES. The floor result was previously open to the objection that our own arms were
simply weak. Thirteen models from EIGHT vendors — Meta, Google, Z-AI, OpenAI, Qwen, Mistral, Amazon,
ByteDance — all land below a baseline that uses no shape information at all. That is a property of the
task under this render protocol, not of our training.

=================  MEASUREMENT PROVENANCE — THE SWEEP RAN TWICE, AND I MIXED THE RUNS  =========
This must be stated plainly because an earlier version of this record was wrong.
I launched the sweep with nohup, concluded from a process check that it had died, and relaunched it
model-by-model. THE FIRST SWEEP HAD NOT DIED. It completed and wrote results_original.json at 13:33,
covering 9 of the 14 rostered models, while the relaunch wrote one m_*.json per model. My aggregation
globbed BOTH sources, so 9 models were present twice and the table silently took whichever file the
glob ordered last — mixing two independent runs in one leaderboard.
  RUN A (canonical): the per-model relaunch, 13 models, one measurement each, published above.
  RUN B (replication): the original sweep, 9 models, results_original.json.
WHAT THE DUPLICATION BOUGHT — AN UNPLANNED REPLICATION AT TEMPERATURE 0.7:
  model                              run A    run B    diff
  meta-llama/llama-4-maverick        93       97        +4
  meta-llama/llama-4-scout           43       48        +5
  mistralai/mistral-medium-3.1       48       59       +11
  mistralai/mistral-small-2603       31       33        +2
  qwen/qwen2.5-vl-72b-instruct       53       54        +1
  qwen/qwen3-vl-235b-a22b-instruct   70       75        +5
  qwen/qwen3-vl-32b-instruct         48       49        +1
  qwen/qwen3-vl-8b-instruct          79       72        -7
  z-ai/glm-4.6v                      93       84        -9
Mean absolute difference 5.0 structures, maximum 11 (0.052 accuracy). That is the run-to-run spread of
K=3 majority voting at temperature 0.7 on this benchmark, and it is a USEFUL NUMBER: any single-run
leaderboard position here carries roughly +/- 0.05, so adjacent rows are not separable. Report it
alongside the leaderboard rather than presenting the ordering as exact.
EVERY HEADLINE CLAIM SURVIVES BOTH RUNS INDEPENDENTLY:
  all models below floor            run A yes        run B yes
  best significantly below floor    run A p=0.0078   run B p=0.0310
  no model reaches the fine-tune    run A yes        run B yes
  Qwen ladder non-monotone          run A 79>48      run B 72>49
So the mixing changed individual cell values but not one conclusion. That is luck, not diligence, and
the defect is recorded rather than quietly corrected.

=================  SCALE DOES NOT CLOSE THE GAP TO THE FLOOR  =================================
PARAMETER FIGURES, VERIFIED AGAINST PRIMARY SOURCES, TOTAL AND ACTIVE. Only models whose sizes are
publicly disclosed appear on a parameter axis:
  model                             total    active   experts   k/210   below floor
  meta-llama/llama-4-maverick        400B      17B      128       93        18
  qwen/qwen3-vl-235b-a22b-instruct   235B      22B      MoE       70        41
  meta-llama/llama-4-scout           109B      17B       16       43        68
  qwen/qwen3-vl-32b-instruct          32B      32B     dense      48        63
  qwen/qwen3-vl-8b-instruct            8B       8B     dense      79        32
THE LARGEST MODEL TESTED IS TIED FOR BEST AND STILL FAILS. llama-4-maverick at 400B total parameters
scores 93/210, tied with glm-4.6v for the top of the leaderboard, and is STILL 18 structures below the
111/210 floor. That is the correct and stronger form of the difficulty claim: it is not that large
models do poorly, it is that the largest model available to us is the best of the thirteen AND does not
clear a baseline computed from three lattice numbers.
CORRECTION, RECORDED RATHER THAN QUIETLY FIXED. An earlier version of this record said "a 30x parameter
range" and "the largest model tested stays 41 structures below the floor". Both were wrong: they treated
the 235B-A22B model as the largest, when maverick at 400B is larger, and attached the 235B model's
41-structure deficit to it. The range is 50x (400/8), and the largest model's deficit is 18.
A SECOND, WORSE DEFECT IN THE SAME PLACE. The earlier scaling figure plotted a Mistral ladder at 24B and
41B. MISTRAL HAS NOT DISCLOSED THE PARAMETER COUNT OF EITHER MODEL — Mistral Medium 3.1 is proprietary
and its size is explicitly undisclosed. Those two figures were invented. The Mistral ladder is REMOVED
from any parameter axis, and the eight models with undisclosed sizes (both Mistral, glm-4.6v, kimi-k2.6,
seed-1.6, nova-pro, gemini-2.5-flash, gpt-4.1-mini) appear only on the accuracy leaderboard, never on a
size plot. Standing rule extended: a number on an axis needs a primary source in the ledger, exactly as
a cited classifier needs its parameters.
WHAT THE VERIFIED FIGURES ACTUALLY SHOW, WITH THE TWO AXES KEPT SEPARATE:
  DENSE PAIR, same family and generation: 8B scores 79, 32B scores 48. The SMALLER model wins by 31
    structures — six times the 5-structure run-to-run spread, so this is not sampling noise. Scale
    inverts here.
  FIXED ACTIVE COMPUTE, varying total capacity: llama-4 scout and maverick have IDENTICAL 17B active
    parameters and differ only in expert count (16 vs 128) and total size (109B vs 400B). Accuracy goes
    43 -> 93. So total capacity at fixed active compute helps substantially — this is an expert-count
    effect, NOT a compute-scale effect, and the earlier text conflated the two axes by plotting total
    parameters as though it were one ladder.
  ACROSS THE MoE MODELS on active parameters: 17B (maverick, 93), 22B (qwen-235B, 70), 17B (scout, 43).
    Active parameters do not order accuracy at all.
NO SINGLE SCALING STATEMENT IS SUPPORTED. Within a dense family the smaller model wins; at fixed active
compute more total capacity helps; across families active parameters carry no signal. What IS supported
is the negative claim, and it is the one that matters for the benchmark: across a 50x total-parameter
range and every architecture tested, NOTHING clears the floor.

=================  WHAT THIS DOES NOT LICENSE  ===============================================
Zero-shot rows are NOT a method comparison against our fine-tuned arms — different training exposure.
They bound TASK DIFFICULTY, not method quality. The anonymized contamination control was not run for
the sweep; it is reported in CP14 for the three frontier models where memorisation was the live concern.
ONE MODEL COULD NOT BE SCORED. moonshotai/kimi-k2.6 was in the pre-registered roster and hangs
indefinitely on this workload — no response on a 2-structure K=1 probe after 10 minutes, so the failure
is the model endpoint rather than the harness. Reported as UNSCORED rather than dropped silently; the
roster is 13 of a pre-registered 14.

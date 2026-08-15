PRE-REGISTRATION — no_image_control roster extension (directive P2-1)
Committed BEFORE any additional call. API spend only, inference only, frozen protocol.

GAP. Three scored models establish that the image matters; they do not support a ROSTER-LEVEL claim. The
image contribution spans 0.105-0.305 across those three — a threefold range — so no statement about the
benchmark as a whole is available from three points.

METHOD, identical to the three already run so the existing arms are reusable verbatim. Byte-identical
prompt text with the image blocks removed, same 210 original-eval structures, K=3, temperature 0.7,
majority vote, paired per structure. IMAGE rows come from model_sweep (13 models) and frontier_ceiling (frontier models) and
are NOT re-run.

ROSTER: all 13 model_sweep models. The 3 frontier_ceiling frontier models are attempted only if their IMAGE per-structure
vectors exist in the ledger; a frontier row without a stored vector CANNOT be paired and will be reported
as unavailable rather than approximated.

REPORT PER MODEL: IMAGE accuracy, TEXT accuracy, delta, discordance both directions, exact McNemar p, and
parse rate. Refusals are scored as refusals under the pre-registered >5% unparseable gate, NOT as 0.0.

PRE-REGISTERED READINGS, fixed now.
  R1  Every scored model shows a significant POSITIVE image contribution -> the benchmark measures vision
      at roster level, and the thirteen-below-floor result is strengthened.
  R2  Some models show NO significant contribution -> those rows are formula-lookup and MUST be named;
      the roster-level claim narrows explicitly to the models that clear it.
  R3  Text-only CLEARS THE FLOOR on any model -> the floor is not the harder reference it appeared to be
      on three models, and the section-4f framing changes. This would be a finding against our own
      current claim and will be reported as such.

WHAT WOULD MAKE A ROW UNINFORMATIVE
  - >5% unparseable or >5% API errors: reported with its rate, NOT scored.
  - A model that hangs rather than answering is an ENDPOINT failure, reported unscored with the evidence
    (a single-call isolation test), not silently dropped. One model in the earlier sweep behaved this way.

EXPECTED, STATED SO IT CANNOT BE RENEGOTIATED. I expect R1 with a wide spread, because all three scored
models so far show a significant positive contribution and text-only sat at chance in every case. If a
weak model shows NO significant contribution, R2 fires and the roster claim narrows — I will not pool it
away. Note the arithmetic risk: a model whose IMAGE accuracy is already near chance has little room to
drop, so a null on such a row is weak evidence of formula-lookup and will be reported with that caveat
rather than as a positive finding.

SCOPE. Original eval sample only. Nothing about the fine-tuned arms, which trained on renders. Nothing
about WHICH visual cue carries the contribution.

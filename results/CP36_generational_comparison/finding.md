CHECKPOINT: CP36_generational_comparison   GAP: does the benchmark survive the next model release?
              (directive Phase D, Option A)
STATUS: DONE, ZERO NEW COMPUTE. Both arms already existed; this is analysis of stored per-structure vectors.
     THE HEADLINE READING REVERSES UNDER THE MANDATORY CONTROL, which is the whole content of the finding.

OPTION A, chosen as the directive requires before generating: the single clean generational pair on the
frozen protocol. Option B (adding each frontier model's predecessor) not run.

THE PAIR. gemini-2.5-flash to gemini-3.6-flash, original eval n=210, K=3, paired per structure:
  0.4286 -> 0.7333, discordance 72:8, exact p = 5.4e-14.

BY STRATUM, RAW:
  box-sufficient (n=140)   0.6286 -> 0.8357   +0.2071
  box-ambiguous  (n=70)    0.0286 -> 0.5286   +0.5000
Read alone this says the newer generation is closing the render-imposed gap FASTEST — the ambiguous gain is
more than double the sufficient one.

NORMALISED BY HEADROOM TO THE ORACLE (0.9524, not 1.0), THE READING REVERSES:
  box-sufficient   closes 64.0% of its headroom
  box-ambiguous    closes 54.1% of its headroom
The larger raw gain is substantially a LOW-BASELINE EFFECT: the ambiguous stratum started at 0.0286, near
the floor of what is measurable, so it had far more room by construction. Against the ceiling that actually
bounds the task, the generation closes LESS of the ambiguous gap.

THE DIFFICULTY AXIS SURVIVES A GENERATION. gemini-3.6-flash still scores 0.5286 ambiguous against 0.8357
sufficient, Fisher p = 4.95e-06. Progress narrowed the absolute gap without erasing the partition.

=====  A PROCESS DEFECT IN THIS CHECKPOINT, RECORDED BECAUSE IT AFFECTS HOW THE RESULT SHOULD BE READ  =====
I RAN THE ANALYSIS BEFORE WRITING ITS RECORD. The accompanying document is a POST-HOC ANALYSIS RECORD, not
a pre-registration, and it is labelled as such in its own first line. The headroom control was added AFTER
the raw deltas suggested a conclusion I distrusted. It then reversed the reading — the right outcome by the
wrong process.
WHY THE REVERSAL IS STILL CREDIBLE: every quantity is arithmetic on stored per-structure vectors that
anyone can recheck, so it is verifiable rather than trusted. But it is not evidence that the outcome was
constrained in advance, and it should not be read as such.

WHAT IS NOT CLAIMED. No trend, no rate of progress, no extrapolation to the next release. Two models one
generation apart on one sample is a comparison. CP26 separately established that parameter count does not
order accuracy on this task at all, so no scaling statement is available either.

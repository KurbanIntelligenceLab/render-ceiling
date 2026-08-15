POST-HOC ANALYSIS RECORD — generational_comparison generational comparison (Option A)
NOT A PRE-REGISTRATION, AND THE FILENAME IS KEPT ONLY FOR DIRECTORY CONSISTENCY. I ran the analysis first
and wrote this after, which inverts this project's standing rule. Stating it here because a document that
reads like a pre-registration but was written afterwards is worse than no document: the G1/G2/G3 readings
and the headroom control below were formulated DURING the analysis, not before it, and the headroom control
in particular was added only after the raw deltas suggested a conclusion I did not believe. That control
then reversed the reading, which is the right outcome by the wrong process.
WHAT THIS COSTS: the reversal is credible because it is arithmetic on stored values that anyone can
recheck, not because it was pre-committed. Treat the G-branch framing as a description of what I did, not
as evidence that the outcome was constrained in advance. Directive Phase D. ZERO new compute: both arms already exist.

OPTION CHOSEN BEFORE GENERATING, as the directive requires: A. Report the single clean generational pair
(gemini-2.5-flash vs gemini-3.6-flash, frozen protocol, same sample, same K) with its stratified
decomposition. Option B (adding each frontier model's predecessor to a 16-model roster) is not run.

HARD CONSTRAINT THE DIRECTIVE IMPOSES ON OPTION A: NO TREND LANGUAGE ANYWHERE. One pair is a comparison,
not a trajectory. model_sweep further established that active parameters do not order accuracy at all, so no
scaling statement is available either.

WHAT IS MEASURED. Paired per structure on the original 210, K=3, exact binomial on discordant pairs.
Stratified by the classifier_refreeze canonical 140/70 partition.

READINGS FIXED NOW.
  G1 the newer model gains MORE on box-ambiguous than box-sufficient -> a generation is closing the gap the
     render convention imposes
  G2 gains are comparable across strata -> generational progress is not stratum-specific
  G3 the newer model gains LESS on ambiguous -> the difficulty axis is hardening
MANDATORY CONTROL, because a raw stratum delta is confounded by baseline: normalise each stratum's gain by
its HEADROOM TO THE ORACLE (0.9524), not to 1.0. A stratum starting near zero has more room by construction,
and the raw delta will overstate its progress. Whichever of G1/G2/G3 the RAW deltas suggest, the
headroom-normalised comparison is the one reported as primary.
ALSO REPORTED regardless of outcome: whether the newer model still separates the strata at all (Fisher
exact). If it does, the partition survives as a difficulty axis even under generational progress.

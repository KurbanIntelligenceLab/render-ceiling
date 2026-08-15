PRE-REGISTRATION — oracle_within_sample oracle on the EVALUATION sets (directive item 1)
WRITTEN BEFORE COMPUTING. This converts oracle_stratified's cross-sample subtraction into a within-sample paired
quantity, so the reading must be fixed first.

THE PROBLEM IT SOLVES. oracle_stratified's localization bracket is assembled across two disjoint samples: oracle
0.8554 = 71/83 on its own 280-structure sample, best pixel model 0.6575 = 48/73 on the evaluation set.
Every use of that result currently carries a sample-disjointness caveat. The oracle is a deterministic
geometric computation over ground-truth positions and the frozen cameras, and the evaluation sets have
both, so it can be run on the SAME structures the models were scored on.

COMPUTE. Run the ideal-extraction oracle (triangulate atom positions from the frozen cameras at
perfect localisation, then spglib) on all 210 structures of BOTH evaluation sets, at the shipped 5
views and at 4 for comparability with oracle_stratified. Then, on the SAME NAMED STRUCTURES:
  - oracle vs each model arm, McNemar exact with discordant counts, overall and by box-sufficiency;
  - the oracle's own box-sufficient / box-ambiguous split.
Report both evaluation sets in this first presentation, per standing discipline.

THE READING, COMMITTED BEFORE THE NUMBERS EXIST.
  W1  ORACLE >> MODELS, PAIRED AND SIGNIFICANT, on both sets. The localization becomes within-sample
      and per-structure: the information is recoverable from these exact renders given extraction, and
      these exact models do not recover it. The sample-disjointness caveat is REMOVED and this becomes
      the paper's strongest single claim.
  W2  NO SIGNIFICANT GAP on the evaluation sets (oracle within noise of the best model). Then oracle_stratified's
      0.1979 was substantially a SAMPLE-COMPOSITION artifact, the localization claim collapses, and
      the honest conclusion is that these renders are near the extraction-limited ceiling already.
      This would RETIRE the localization headline. I commit to reporting it if it fires.
  W3  ORACLE BELOW SOME MODEL on some stratum. That would indicate the oracle is not an upper bound
      under this render convention — a defect in the instrument rather than a result — and I would
      audit the oracle before reporting anything.

WHAT NO OUTCOME LICENSES. Perfect atom localisation is assumed. The gap measures what is unrecovered
GIVEN extraction; it never shows a model COULD have extracted it from pixels. And the oracle reads the
same 5 views, so it is a fair-information comparison only in the sense of view count, not of
perceptual difficulty.

RISK I ACCEPT IN ADVANCE. If the oracle scores very high on the evaluation set, the gap will be large
and the result flattering. That is the direction I expect, which is exactly why W2 is written down: a
null must be reportable without renegotiation.

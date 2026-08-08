PRE-REGISTRATION — CP60 length control on the symbolic share   (directive P4 / A1b)
WRITTEN BEFORE ANY REGRESSION WAS RUN. Zero new API calls: CP53 already holds per-structure R3
verdicts and the conventional-cell atom counts are in the label pipeline.

THE OBJECTION THIS TESTS, stated as a reviewer would state it. The decomposition assigns R1-R3 to a
"reasoning" bucket. R1 is spglib on exact coordinates; R3 is a model reading a coordinate list. If R3
accuracy FALLS as the coordinate list gets longer, then part of that bucket is long-list handling —
numeric tokenisation, context length, arithmetic over many rows — and not symmetry reasoning. The
30.9% median share would then be an upper bound contaminated by list length.
WHY THE EXISTING prompt_length KEY DOES NOT ANSWER IT. CP53's prompt_length shows geometry prompts are
SHORTER than the five-image prompts they beat. That rules out "the lift is a length artefact". It says
nothing about whether the symbolic residual INFLATES with atom count WITHIN the geometry condition.
Different question, and the directive is right that C3 conflated them.

TEST. Per model, Spearman rho between per-structure R3 correctness (0/1) and conventional-cell atom
count, over the structures CP53 scored. Plus a pooled test across models. Two-sided alpha = 0.05.
Report rho and p for every model whether or not significant.

BRANCHES, committed now.
 L1  NO ASSOCIATION (pooled p >= 0.05 and no more than 1 model individually significant at 0.05):
     the objection is CLOSED in one sentence in the same paragraph as the median share. The symbolic
     residual is not explained by list length.
 L2  NEGATIVE ASSOCIATION (pooled rho < 0 at p < 0.05): the symbolic share is PARTLY a long-list
     effect. The paper says so beside the 30.9% figure, in the same paragraph, and the share is
     reported as an UPPER BOUND on symmetry-reasoning deficit rather than a measurement of it. This
     WEAKENS a headline number and is reported regardless.
 L3  POSITIVE ASSOCIATION (pooled rho > 0 at p < 0.05): unexpected — more atoms would mean MORE
     recoverable structure. Report as-is and do not narrate it as support for anything; a positive
     result here means atom count proxies something else (symmetry richness), which is a confound in
     its own right and must be named.
 L4  MIXED (some models negative-significant, others not): report per model, no pooled claim, and
     state the share as model-dependent.

CONFOUND NAMED IN ADVANCE. Atom count CORRELATES WITH CRYSTAL SYSTEM: low-symmetry cells hold more
atoms. So any association could be symmetry difficulty rather than list length. Therefore a second,
pre-registered analysis: partial association controlling for crystal system, computed as the pooled
within-system Spearman (rho computed inside each system, then combined). If the association survives
within system, list length is implicated; if it vanishes, the effect is symmetry difficulty and the
objection is closed by the confound rather than by the null.
NO OUTCOME HERE CHANGES THE ORACLE-TO-MODEL GAP, which is measured against pixels, not text.

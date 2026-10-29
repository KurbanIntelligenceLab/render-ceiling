# claude-opus-5-5: paired image and exact-geometry evaluation

The same structures and questions are evaluated with five rendered views or complete reference lattice/site geometry as text. Three answers per input are combined using the archived last-label parser and majority voting over valid answers; ties follow repeat order. All-invalid votes count as incorrect.

Cases: 210. This record is the full evaluation.

| Input | Correct | Accuracy |
| --- | ---: | ---: |
| Images | 145/210 | 69.05% |
| Exact geometry | 166/210 | 79.05% |

Paired corrections: 45; regressions: 24. Closed deficit: 32.31%. Refusals: 0; unresolved API failures: 0; final truncations: 0.

Recorded token cost including pilot: $30.4288. Possible unreported charges are retained separately in the run record. These are estimates, not an invoice.

Native API defaults are preserved, with no temperature or reasoning override. Output limits, prompt caching, failed transports, and truncation-only replacements are recorded with all earlier attempts. The original 14-model roster used a different API route and temperature 0.7; cross-roster rankings are descriptive.

[Raw responses and protocol](run.json) · [Scoring summary](summary.json) · [Verification](verification.json)

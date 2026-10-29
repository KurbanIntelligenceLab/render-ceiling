# claude-sonnet-5-5: paired image and exact-geometry evaluation

The same structures and questions are evaluated with five rendered views or complete reference lattice/site geometry as text. Three answers per input are combined using the archived last-label parser and majority voting over valid answers; ties follow repeat order. All-invalid votes count as incorrect.

Cases: 210. This record is the full evaluation.

| Input | Correct | Accuracy |
| --- | ---: | ---: |
| Images | 152/210 | 72.38% |
| Exact geometry | 193/210 | 91.90% |

Paired corrections: 54; regressions: 13. Closed deficit: 70.69%. Refusals: 0; unresolved API failures: 0; final truncations: 0.

Recorded token cost including pilot: $15.2113. Possible unreported charges are retained separately in the run record. These are estimates, not an invoice.

Native API defaults are preserved, with no temperature or reasoning override. Output limits, prompt caching, failed transports, and truncation-only replacements are recorded with all earlier attempts. The original 14-model roster used a different API route and temperature 0.7; cross-roster rankings are descriptive.

[Raw responses and protocol](run.json) · [Scoring summary](summary.json)

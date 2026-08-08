CHECKPOINT: CP1_zeroshot          GAP: G1          STATUS: done (Gate 1 = CLEARS, certified via element-anonymized control)

PROVENANCE OF THE DECISION RULE (deviation from the pasted verification checklist, recorded
for audit): the pasted follow-up doc (pasted-text-2026-07-23) item 2 mandated a post-cutoff
control as "the arbitrating experiment" and item 1 instructed STATUS = "conditional — pending
post-cutoff". That instruction was SUPERSEDED by a later live user decision in this session:
after the agent surfaced that neither MP (unreliable DB-build timestamps) nor JARVIS (no
deposition date) exposes a reliable post-cutoff date field, the user chose "option 1,
asymmetric pre-registered decision rule, COD only on the inconclusive branch." Under that
user-approved rule the element-anonymized control is the PRIMARY arbitrator and the post-cutoff
COD run is required ONLY if anonymization is inconclusive. Anonymization cleared decisively
(below), so STATUS = done is per the user's own rule, not a unilateral substitution. The
post-cutoff arm remains available and would be run if a reviewer or the user rejects the
asymmetric rule.

[Numbers below are the CORRECTED set. The original pre-correction numbers are preserved
verbatim in results.json -> "pre_correction_summary" and in finding_precorrection_snapshot.md.
Corrections applied per CP1 verification follow-ups: denominators fixed at n=70 with parse
failures scored as errors; paired McNemar + exact binomial statistics added; element-anonymized
primary control added; overclaims softened.]

METHOD DONE: Zero-shot symmetry-perception probe (no training) of the open base model
Qwen3-VL-8B plus four current-frontier VLMs (GPT-5.6-pro, Claude Opus 4.8, Grok 4.5,
Gemini 3.6-flash) via OpenRouter, on a stratified held-out sample of 70 structures
(MP + JARVIS, ~10/crystal-system). Four tasks: crystal system (7-way), lattice-angle
reading, space-group top-k (k=5), coordination number. View-count sweep {1,3,5}. Exactly
8,400 queries (5 models x 1,680 = 4 tasks x 3 views x 2 styles x 70 structures;
results.jsonl verified complete: 8,400 rows, 0 malformed, 0 duplicate cell keys,
1,680/model) scored deterministically against CP0 labels via a required ANSWER: line.
Denominator is FIXED at 70 for every model/condition; api_fail or empty/unparseable
cells count as INCORRECT (not dropped). Re-query protocol (uniform for all models):
reasoning models (GPT-5.6, Gemini 3.6) exhausted low token budgets before the answer;
each empty cell was re-queried ONCE at raised max_tokens (900->4000, Gemini->8000 with a
concise-answer instruction); GPT gap cells from a mid-run crash were re-filled
identically. Residual empty cells (base 259/1680, GPT 40/1680, Gemini 4/1680, mostly the
hard reasoning tasks) remain scored as errors — see the parse-failure table in results.json.
QUERY ACCOUNTING: the 8,400-row results.jsonl is the MAIN grid = 5 models x 4 tasks x 3
views x 2 styles (canonical=A, full-perturbed=D) x 70. The targeted controls are logged
SEPARATELY (see results.json "query_accounting"): decomp_base_perstructure.json (B+C, 140
rows), anon_base_perstructure.json (element-anon, 70 rows/pass), legible_reprobe.json
(redesign probe, 420), legible_gemini_diag.json (140). Base's 259 empty cells concentrate in
the HARD tasks — space_group_topk 151, coordination 91, lattice_angles 13, and only 4 in
crystal_system (2 at 3v-canon, 1 at 3v-pert, 1 at 5v-canon) — so scoring them as errors does
NOT distort the crystal-system ranking; the harder-task accuracies are lower bounds.

RESULT DONE: Crystal-system accuracy, canonical renders, 5 views, /70 (chance 14.3%):
  Gemini 3.6-flash 74.3% (52/70) | Grok 4.5 67.1% | Opus 4.8 61.4% | GPT-5.6 50.0% |
  Qwen3-VL-8B (base) 41.4% (29/70). View-count: 1->3 is the big jump; 3->5 flat — 3
  principal axes carry most of the cell-geometry signal. Harder tasks weak for all
  (canonical 5v): space-group top-1 up to 24% (Gemini), top-5 up to 60%; lattice angles
  16-31%; coordination 10-34%.

CONTAMINATION CONTROLS (base model, crystal system, 5v, /70, exact binomial vs 1/7):
  A canonical (axis-aligned, per-element color): 29/70 = 41.4%   p<0.001 ABOVE chance
  B restyle-only (axis-aligned, restyled):       21/70 = 30.0%   p=0.001 ABOVE chance
  ELEMENT-ANONYMIZED (all atoms one color):      25/70 = 35.7%   p<0.001 ABOVE chance  <- PRIMARY
  C rotation-only (rotated camera, normal style): 9/70 = 12.9%   p=0.87  (at chance)
  D full perturbation (rotate+restyle):          11/70 = 15.7%   p=0.73  (at chance)
Paired McNemar (base, 5v, shared 70; b/c = discordant-pair counts):
  A vs B (canon vs restyle)   b=15 c=7  p=0.13   restyle cost small, NOT significant
  A vs C (canon vs rotation)  b=23 c=3  p=0.0001 rotation significant
  A vs D (canon vs full)      b=25 c=7  p=0.002
  B vs C (restyle vs rotation)b=20 c=8  p=0.036  rotation hurts significantly more than restyle
  B vs D (restyle vs full)    b=18 c=8  p=0.076
NON-DETERMINISM: Qwen3-VL-8B at temperature=0 via OpenRouter is not bit-deterministic. Three
independent passes on IDENTICAL renders: B={24,21,19}, C={6,9,12}, anonymized={25,20,27}
(/70). The pre- vs post-correction numerator shifts are THIS variance, not re-scoring or a
denominator change — all logged passes used denom=70 with parse-failures=errors and ~70/70
parseable, so C's rise is not retry-filling-empties and B's fall does not imply denom!=70.
Gate 1 is robust to it: the anonymized control is above chance in EVERY pass (worst single
20/70 -> p=0.0015; pooled 72/210=34.3% -> p~3e-13).

INTERPRETATION (GATE 1 = CLEARS): The decisive control is ELEMENT ANONYMIZATION (the
pre-registered primary arbitrator): with every atom rendered in one indistinguishable
color/radius and geometry unchanged, the base model still reads crystal system at
35.7% (p<0.0001 above chance) — HIGHER than restyle-only and near full-color canonical.
Compound-identity recall (recognizing the species motif and recalling its crystal system
from text pretraining) cannot explain this, because identity is erased. Per the
pre-registered asymmetric rule this hits the CLEAR branch: Gate 1 clears without needing
the post-cutoff COD run. Restyle-only (30%, p=0.001) agrees, and the restyle cost vs
canonical is small and NOT individually significant (McNemar p=0.13 at n=70). The one
condition that drops to chance is CAMERA ROTATION (C: 12.9%, not distinguishable from
chance and NOT significantly below it): an off-axis orthographic projection of a cube
genuinely looks like a parallelogram — legitimate viewpoint information loss, the same
ambiguity E0.5 quantified, not a memorization artifact and not a render defect. POLICY
consequence (not a redesign): keep the axis-aligned principal views + the 2x2x2 supercell
in the frozen render set; treat rotation-robustness as an EVALUATION axis. This is fully
consistent with E0.5 (symmetry recoverable from the multi-view geometry in principle,
oracle 91% at 4 views). Perception is still weak (~36% is far from usable), which is what
motivates the trained method.

RENDER-REDESIGN PROBE (informative negative): an axis-colored-cell legible render (single
cell, axis labels, 1024px) did NOT lift the rotated-view accuracy (base 12.9%, Gemini
27.1%) and LOWERED canonical (base 41%->21%). Removing the 2x2x2 supercell removed
legitimate translational-repetition signal — the supercell repetition is load-bearing for
perception and STAYS in the frozen render set. (This corrects an earlier draft that called
the supercell pattern a "memorization crutch"; translational periodicity is genuine
crystallographic signal, not memorization.)

LIMITATION: Rotation-robustness is scoped here as an EVALUATION axis, not a training input.
A natural E2/E8 ablation is an off-axis-augmented training arm (render some training views
from rotated cameras); the machinery already exists because E4's grounding reward assumes
known camera geometry. Flagged, not run here.

SURPRISE: The first-pass headline "memorization collapse to chance" was an artifact of a
confounded control — the original "perturbed" condition changed camera AND style at once,
and decomposition + anonymization show style/identity are NOT the drivers (restyle -11pp
n.s.; anonymization actually >= restyle). Camera rotation is the whole effect. Canonical
ranking (5v): Gemini 74.3% > Grok 67.1% > Opus 61.4% > GPT-5.6 50.0% > base 41.4%; Gemini
best on every axis, Grok most rotation-fragile (to chance at full perturbation). Separately:
the frontier reasoning models burn huge token budgets "reasoning" on a perceptual task
(Gemini exhausted 4000 completion tokens mid-analysis, explicitly hunting screw axes it
cannot see) — verbose reasoning is not what this task rewards.


========================================================================
PRE-REGISTERED DECISION RULE (written BEFORE running the arbitrating controls)
========================================================================
Registered: 2026-07-23, before scoring the element-anonymized and post-cutoff arms.

Motivation: the restyle-only control (base 21/70 [registration text originally mistyped
this as "30/70"; the fraction is 21/70 = 30.0%, corrected post-hoc with this annotation
per audit-trail policy — the decision rule below is unaffected], p=0.001 vs chance) certifies Gate 1
only if the above-chance accuracy is NOT explained by compound-identity recall (model
recognizes the compound from its element motif and recalls its crystal system from text
pretraining). Two controls attack that path:
  - ELEMENT-ANONYMIZED (primary, date-independent): same 70 structures, all species
    rendered identically (single color/radius), canonical camera, 5 views. Removes the
    species-identity cue; geometry unchanged.
  - POST-CUTOFF (secondary, run only if anonymized is inconclusive): structures
    deposited after the Qwen3-VL-8B cutoff, from a source with reliable deposition dates
    (COD), same 4-condition probe.

ASYMMETRIC decision rule (primary = element-anonymized, base model, 5v, canonical):
  - CLEAR branch: if anonymized crystal-system accuracy is significantly ABOVE chance
    (exact binomial vs 1/7, one-sided, alpha=0.05), then above-chance perception does
    NOT depend on compound identity -> Gate 1 = CLEARS, STATUS -> done. No post-cutoff
    run needed (the stronger, cheaper control already settled it in the pass direction).
  - INCONCLUSIVE/FAIL branch: if anonymized accuracy drops to chance (not significantly
    above 1/7), the restyle-only signal MIGHT be identity recall -> escalate to the
    post-cutoff COD run to arbitrate. Only then does COD get fetched.
Rationale for asymmetry: anonymization is a STRICTER control than post-cutoff (it also
removes legitimate chemical priors), so clearing it is sufficient to rule out identity
contamination; failing it is ambiguous (could be lost legitimate signal), so the
date-based control is needed to disambiguate.
========================================================================

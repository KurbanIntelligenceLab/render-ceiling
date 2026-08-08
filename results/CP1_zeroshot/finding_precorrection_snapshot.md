CHECKPOINT: CP1_zeroshot          GAP: G1          STATUS: done (Gate 1 = CLEARS, after decomposing the contamination control)

METHOD DONE: Zero-shot symmetry-perception probe (no training) of the open base model
Qwen3-VL-8B plus four current-frontier VLMs (GPT-5.6-pro, Claude Opus 4.8, Grok 4.5,
Gemini 3.6-flash) via OpenRouter, on a stratified held-out sample of 70 structures
(MP + JARVIS, ~10/crystal-system). Four tasks: crystal system (7-way), lattice-angle
reading, space-group top-k (k=5), coordination number. View-count sweep {1,3,5} using
the frozen render set. Contamination control: the SAME structures re-rendered with
rotated cameras + restyled palette/radii ("perturbed"); the canonical-minus-perturbed
accuracy gap estimates memorization of standard MP/web visualization conventions.
~8,200 model queries, scored deterministically against CP0 labels via a required
ANSWER: line. (Reasoning-heavy frontier models — GPT-5.6, Gemini 3.6 — needed a raised
token budget; low budgets truncated before the answer and were re-queried.)

RESULT DONE: Crystal-system accuracy, canonical renders, 5 views (chance 14.3%):
  Gemini 3.6-flash 75.4% | Grok 4.5 67.1% | Opus 4.8 61.4% | GPT-5.6 50.0% |
  Qwen3-VL-8B (base) 41.4%.  Micro/macro track closely (base macro 44.8%).
View-count: 1->3 views is the big jump (base 32.9->41.4%, Opus 44.3->65.7%); 3->5 is
flat or slightly down — 3 principal axes carry most of the cell-geometry signal.
Harder tasks are weak for all (canonical 5v): space-group top-1 2.9% (base) to 24.3%
(Gemini), top-5 up to 60% (Gemini); lattice angles 15.7-31.4%; coordination 10-34%.

CONTAMINATION DELTA (canonical - perturbed, crystal system, 5v) is large for EVERY
model: base +25.7pp (41.4->15.7%), GPT +26.5, Opus +32.9, Gemini +42.5, Grok +52.9
(67.1->14.3%). On the contamination-controlled (perturbed) set the base model is at
15.7% (5v) / 10.0% (3v) — statistically indistinguishable from the 14.3% chance line —
and collapses to guessing low-symmetry labels (monoclinic 40/70, triclinic 18/70),
never confidently reading cubic/tetragonal/trigonal. All 70 perturbed responses parsed
cleanly, so this is a genuine perceptual result, not a formatting artifact.

DECOMPOSITION (the key correction): The first-pass reading was that the base model
"collapses to chance on the contamination-controlled set" (15.7% perturbed vs 41%
canonical) and Gate 1 therefore triggers render redesign. That was WRONG, because the
"perturbed" control changed TWO things at once — camera rotation (off the
crystallographic axes) AND restyle (palette/radii) — and only the restyle is a
memorization probe; rotation is legitimate viewpoint information loss. Decomposing the
perturbation on all 70 structures, 5 views (base / Gemini):
  A canonical (axis-aligned, normal style):        41.4% / 75.4%
  B RESTYLE ONLY (axis-aligned camera):            34.3% / 70.0%   <- memorization-controlled
  C ROTATION ONLY (normal style):                   8.6% / 21.4%
  D rotate+restyle (the original "perturbed"):     15.7% / 32.9%
Restyle alone costs only ~5-7pp; camera rotation drives essentially the entire
collapse, for BOTH the open model and the frontier. A separate render redesign
(axis-colored cell edges + labels, single cell, 1024px) did NOT lift perturbed
accuracy (base 12.9%, Gemini 27.1%) and lowered canonical (base 41%->21%, by removing
the supercell grid-pattern memorization crutch) — confirming the limiter is viewpoint,
not style.

INTERPRETATION (GATE 1 = CLEARS): On the memorization-controlled axis (restyle only,
axis-aligned views) the base model is at 34.3% (5v), well above the 14.3% chance line
-> Gate 1 clears; training is warranted. The rotation sensitivity is not a
memorization artifact and not a render defect: an off-axis orthographic projection of
a cube genuinely looks like a parallelogram, the exact viewpoint ambiguity E0.5
quantified. The consequence for the render/view POLICY (not a redesign): keep the
axis-aligned principal views in the frozen set (already the case), and treat
rotation-robustness as an EVALUATION axis rather than a training input. This is fully
consistent with E0.5: symmetry is recoverable from the multi-view geometry in principle
(oracle 91% at 4 views), and the open model already shows above-chance perception on
axis-aligned views (the training signal E2 will sharpen). Perception is still weak
(34% is far from usable), which is exactly what motivates the trained method.

SURPRISE: The headline "memorization collapse to chance" was an artifact of confounding
rotation with restyle in the control — restyle alone barely dents accuracy (base -7pp,
Gemini -5pp), so these renders are NOT primarily memorized; the apparent collapse was
viewpoint information loss. Canonical ranking (5v): Gemini 3.6-flash 75.4% > Grok 4.5
67.1% > Opus 4.8 61.4% > GPT-5.6 50.0% > base 41.4%; Gemini is best on every axis.
Grok has the largest full-perturbation delta (52.9pp, down to exactly chance), i.e. the
most rotation-fragile. Separately: the frontier reasoning models burn huge token
budgets "reasoning" on what is a perceptual task (Gemini exhausted 4000 completion
tokens mid-analysis, explicitly hunting screw axes it cannot see) — verbose reasoning
is not what this task rewards.

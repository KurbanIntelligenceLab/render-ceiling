# PRE-REGISTRATION — B1-direct and SFT-V1 on the composition-exclusion split
# WRITTEN AND COMMITTED BEFORE ANY NUMBER WAS LOOKED AT.

## What is being run
Evaluate on the SAME 210-structure composition-exclusion eval set, SAME majority-vote
protocol (3 samples, temp 0.7) already used for the E3 matrix arms:
  - B1-direct, all 3 SFT seeds (adapters/B1_s{0,1,2})
  - SFT-V1, all 3 seeds (adapters/V1_s{0,1,2})  [the required pre-GRPO chain baseline]
Reference rows already measured: B3 0.344, V2a 0.376, V2b 0.386 macro-F1.
B1's IID test accuracy (E2, n=30) was 0.711.

## Hypothesis (pre-registered, with citation)
Per Chu et al., "SFT Memorizes, RL Generalizes" (arXiv 2501.17161, ICML'25) — verified
from the primary source: "SFT ... tends to memorize the training data and struggles to
generalize out-of-distribution", and "RL also generalizes to visual OOD tasks, whereas
SFT continues to struggle" — we predict:
  H: B1-direct's 0.711 IID accuracy DEGRADES SUBSTANTIALLY on the composition-exclusion
     split (unseen chemistry), while the GRPO-trained chain arms retain relatively more.

## Decision rule (pre-registered)
  BRANCH (a): B1 holds near 0.71 (>= ~0.60) on the exclusion split
      -> the accuracy story is DEAD. Paper reframes on verifiability / faithfulness /
         test-time scaling. E3 scale-up DEPRIORITIZED.
  BRANCH (b): B1 collapses toward or below V2b (<= ~0.40)
      -> headline becomes "direct mapping memorizes, verified chains generalize".
         E3 scale-up JUSTIFIED (in combination with item-4's growing-gap probe).
  INTERMEDIATE (0.40 < B1 < 0.60): partial degradation; report as such, do NOT force a
      branch; E3 scale-up decision rests on the item-4 probe alone.
The branch taken will be recorded verbatim in finding.md.

## Budget accounting (required by arXiv 2509.21882)
2509.21882 ("Hidden Costs and Measurement Gaps of RLVR") warns that headline RLVR gains
often conflate policy improvement with "budget mismatch between RLVR and baseline
evaluations". We therefore state three accountings, all from MEASURED token counts read
off the live Qwen3-VL processor at the max_pixels=200704 used in every run (NOT computed
by formula — Qwen3-VL's 32x32-px/token arithmetic plus the max_pixels cap makes
formula-derived counts wrong):
  measured: 171 visual tokens/view x 5 views; 938 total prefill tokens per sample.
  (1) GENERATED tokens:        chain 1200 vs B1 18 per structure  -> 66.7x
  (2) FLOPs-proportional:      chain 4014 vs B1 2832 tokens       -> 1.417x  <-- USED
      (prefill is 70.1% of chain-arm compute and 99.4% of B1's, so the 5-view prefill
       dominates and the arms are near parity in total compute)
  (3) WALL-CLOCK:              decode is memory-bound; B1 expected several-x faster.
THE BRANCH DECISION USES ACCOUNTING (2), FLOPs. (1) and (3) are disclosed alongside.

## Secondary (also pre-registered)
Cite 2501.17161's further finding — verified: "SFT stabilizes the model's output format,
enabling subsequent RL to achieve its performance gains" — as the PUBLISHED rationale for
the CoCr V1->GRPO lineage and for the observed termination fix (SFT-V1 reached [ANSWER]
1.1% of the time; the GRPO arms reach it ~65-85%).

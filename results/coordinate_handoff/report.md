# Reconstructed-coordinate handoff

All 28 reserved parents contribute original and large-displacement variants under Gaussian noise and single-view corruption: 112 matched cases. Inputs are lattice only, Huber coordinates, or split one-SE coordinates. Coordinate prompts contain lattice vectors, atomic numbers, and fractional coordinates rounded to eight decimal places; material identifiers, method names, reference labels, and correctness feedback are withheld. Targets use 0.02 angstrom positional and 5-degree angular tolerance. Two large-displacement cases of mp-865981 retain the recorded monoclinic target at this tolerance.

| Model | Lattice only | Huber | Split one-SE | Split − Huber (pp) |
| --- | ---: | ---: | ---: | ---: |
| Sonnet 5.5 | 42.26 ± 1.03% | 65.18 ± 2.36% | 75.00 ± 1.79% | 9.82 |
| Gemma 3 4B IT | 8.33 ± 1.03% | 7.74 ± 1.03% | 8.63 ± 1.36% | 0.89 |
| Qwen3 4B | 16.67 ± 2.73% | 13.99 ± 2.25% | 15.48 ± 2.87% | 1.49 |

Values are arithmetic means and sample standard deviations of three runs on the same 112 cases. Sonnet API repeats are not controlled sampling seeds. Local MLX 4-bit Gemma and Qwen runs use seeds 20261029, 20261030, and 20261031 with temperature 1.0, top-p 0.95, top-k 64, and a 256-token cap; Qwen uses its non-thinking template. A repeated identical prompt shares its response within each run. Malformed or truncated answers count as incorrect in individual-run averages.

Sonnet majority voting gives 48/112 lattice-only, 76/112 Huber, and 84/112 split predictions correct. The split-minus-Huber difference is 7.14 percentage points, with descriptive 95% parent-bootstrap interval [-0.89, 15.18]. This interval spans zero. The strong numerical reconstruction benefit and the descriptive downstream comparison measure different endpoints.

The first Sonnet subset contains 28 cases; the extension contains the remaining 84. The pilot began with an 8,192-token cap, retained one replacement at 16,384, and then used 16,384 for subsequent requests. Invalid completions remain recorded. The extension uses 16,384 tokens. The 28-case exact-coordinate and greedy Gemma controls remain separate from the three-run 112-case results. Reference targets, prompts, generation amendments, raw responses, and uncertainty records are retained in the study files.

[Summary and source checksums](coordinate_handoff_accuracy.json) · [Sonnet pilot](../reconstruction_sonnet_pilot/study.json) · [Sonnet extension](../reconstruction_sonnet_extension/study.json) · [Gemma](../reconstruction_gemma_three_seed/study.json) · [Qwen](../reconstruction_qwen_three_seed/study.json) · [Greedy Gemma pilot](../reconstruction_vlm_pilot/study.json)

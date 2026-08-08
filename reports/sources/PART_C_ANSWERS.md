# PART C — answers

Each answer is read from the checkpoint records, not recalled. Where a record does not exist I say so
rather than filling the gap.

## C1 — the fine-tuned arm

THREE CHECKPOINTS, NOT ONE, AND THE PAPER'S BEST NUMBER COMES FROM CP12.

| checkpoint | what it holds |
|---|---|
| `CP2_sft_chain` | the SFT stage: `Qwen/Qwen3-VL-8B-Instruct`, QLoRA 4bit nf4, r16, 3 epochs, lr1e-4, 115 train / 30 test structures, seeds [0, 1, 2] |
| `CP3_process_reward` | GRPO on top of SFT: lr 1e-05, KL beta 0.02, group size 8, 300 steps, 1610 train prompts, TRL 1.9.0 GRPOTrainer, from checkpoint `V1_s0`. Arms {'B3': {'macro': [0.281, 0.3714, 0.381], 'macro_mean': 0.3445, 'macro_sd': 0.045, 'faith': [0.2109, 0.2707, 0.2936], 'faith_mean': 0.2584, 'faith_sd': 0.0349}, 'V2a': {'macro': [0.3571, 0.381, 0.3905], 'macro_mean': 0.3762, 'macro_sd': 0.0141, 'faith': [0.2787, 0.3125, 0.3278], 'faith_mean': 0.3063, 'faith_sd': 0.0205}, 'V2b': {'macro': [0.3857, 0.3857, 0.3857], 'macro_mean': 0.3857, 'macro_sd': 0.0, 'faith': [0.2744, 0.3106, 0.3133], 'faith_mean': 0.2994, 'faith_sd': 0.0177}} |
| `CP12_sota_push` | THE CITED ARM (A3). 139/210 = 0.6619 at K=3, Wilson95 [0.5955, 0.7225], 1 seed |

BASE MODEL: `Qwen/Qwen3-VL-8B-Instruct`. ADAPTER: QLoRA 4-bit nf4, rank 16, lr 1e-4 for SFT; GRPO then runs on the SFT
checkpoint at lr 1e-5 with KL beta 0.02.
TRAINING SET CONSTRUCTION (CP12): 3220 examples from 1610 structures,
3 epochs, 1206 steps, final loss 0.1419, 29551s wall clock. Augmentation is
"6 extra cameras, disjoint from the 5 frozen eval views" — the six extra cameras are DISJOINT from the five frozen eval views,
which is what stops the augmentation leaking the eval protocol.
RESOLUTION IS READ, NOT ASSUMED: max_pixels 589824, 576 visual tokens per view,
"read from the live processor, not a formula". CP0c found the deployed config differed from the documented one by 3.408x in
area, which is why this is read from the live processor.
COMPOSITION-EXCLUSION GUARANTEE: no chemical composition in any evaluation set appears in training. This is
enforced at dataset construction and re-verified in CP50, whose leakage audit reports 0 overlap with the
1610-structure training set and 0 with both earlier evaluation samples.
THE NUMBER THE PAPER USES: 0.6905 at K=8, against the oracle's 0.9524, paired per structure,
discordance 61:6, p = 1.5e-12.
CAVEAT YOU SHOULD CARRY INTO S6: A3 IS SINGLE-SEED and sits inside the reference arm's own across-seed
spread (B1: 0.590 / 0.567 / 0.686). CP37 was the three-seed extension and was CUT — see its finding for the
quantitative argument that seed variation cannot close a 55-structure margin. Report A3 as a point
estimate with no error bar, which is what the manuscript does.

## C2 — roster reconciliation

THE PRE-REGISTERED COUNT IS 14. THE SCORED COUNT IS 13. Both numbers are correct and they answer different
questions, which is why the package states them as "13 of a pre-registered 14".
THE UNSCORED ENTRY IS `moonshotai/kimi-k2.6`, under the ENDPOINT-FAILURE gate, not the error-rate gate. The
recorded reason: it hangs indefinitely, with no response on a 2-structure K=1 probe after 10 minutes, so the
failure is the model endpoint rather than the harness. It is reported UNSCORED rather than dropped.
A SEPARATE ROSTER EXISTS FOR CP41 and it has its own accounting: 16 attempted,
13 scored, 3 unscored under the pre-registered 5% API-error gate. Do not merge the two
rosters — CP26 is the zero-shot leaderboard and CP41 is the no-image control.

## C3 — do CP53, CP58 and CP60 exist

| checkpoint | exists | results.json | prereg | finding |
|---|---|---|---|---|
| CP53_rung_R3_coords_as_text | YES | yes | yes | yes |
| CP58_perception_transplant | YES | yes | yes | yes |
| CP60 (length control) | NO | — | — | — |

CP53 AND CP58 ARE COMPLETED CHECKPOINTS. They were proposed as new work and then run; that is why the draft
already contains the R3 condition and the fabrication result.
CP60 DOES NOT EXIST AND DOES NOT NEED TO. The length control it proposes is already inside CP53, under the
key `prompt_length`: the geometry prompts are SHORTER than the five-image prompts they outperform, which is
the confound CP60 was meant to rule out. CP53 also carries a `control_pair` block — formula-only against
full geometry — which is what makes the lift attributable to the geometry rather than to text-mode
prompting. Writing CP60 would duplicate both.

## C4 — the n=1933 model budget

NOT AFFORDABLE AT FULL ROSTER, AFFORDABLE AS A CORE SUBSET. At the measured throughput of 0.462 calls/s at
24 workers:

| scope | calls | wall clock |
|---|---|---|
| full clean sample x 13 models x K=3 | 75,387 | 45 h |
| 500-structure core x 13 models x K=3 | 19,500 | 11.7 h |
| 500-structure core x 4 strong models x K=3 | 6,000 | 3.6 h |

The tiering was pre-registered in CP50 exactly for this: oracle and classical baselines on the FULL sample
because they are free, model arms on a 500-structure core if run at all. WRITE THE LIMITATION AS A STATED
COST DECISION: the oracle and both classical baselines are complete at n=1933; the model arms are not, so
every model number rests on n=210 and the ceiling-to-model gap at scale is bounded on the oracle side only.
That is what the manuscript's limitations section says.

## C5 — the power calculation, WHICH WAS WRONG AND IS NOW CORRECTED

THE PUBLISHED 0.162 IS RETRACTED. Your question exposed it. It came from
`1.96*sqrt(2*p0*(1-p0)/n)` with p0 = 0.60 and n = 70 — the TWO-INDEPENDENT-PROPORTION normal approximation,
two-sided alpha = 0.05, AND NO TARGET-POWER TERM. Two defects: the test actually run is a PAIRED exact
binomial on discordant pairs, so an unpaired formula is a category error; and with no power term the figure
describes 50% power, not the 80% a reader assumes.
THE CORRECT PAIRED ANALYSIS. Discordance is low — a mean of 6.3 discordant pairs per comparison out of 70.
Recomputed per comparison, SIGNIFICANCE IS REACHABLE IN ONLY 9 OF THE 16 COMPARISONS; the other 7 have 2 to
5 discordant pairs, where NO split reaches p < 0.05 at any outcome. Among the reachable 9 the paired MDE
runs 0.0857 to 0.1286, median 0.1143, against a largest observed absolute delta of 0.0857.
THE NULL IS THEREFORE WEAKER THAN THE PACKAGE PREVIOUSLY CLAIMED, not stronger. "The null bounds the effect
below ~0.16" is withdrawn from REPORT.md and the manuscript. What survives: no convention produced a
detectable change, and for 7 of 16 comparisons the design could not have detected one.

## C6 — the extraction prompt and raw outputs

THE PROMPTS ARE NOW IN THE RELEASE; THEY WERE MISSING UNTIL THIS AUDIT. `release/frozen_prompts.json`
carries three labelled entries: the main zero-shot prompt, `CP58_extraction_strong_model` (462 chars, with
the symmetry question deliberately withheld so the extraction cannot leak an answer), and
`CP58_answer_weak_model`.
THE RAW OUTPUTS ARE A REAL GAP AND I WILL NOT PRETEND OTHERWISE. `CP58/a3_raw.json` retains 210 records with
fields ['correct', 'emitted', 'material_id', 'n_atoms_emitted', 'pred', 'truth', 'votes'] — the PARSED coordinate lists, the vote records, and
the per-structure verdict. IT DOES NOT RETAIN THE VERBATIM MODEL TEXT. The harness parsed each response into
the `emitted` array and discarded the original string.
WHAT S5 CAN STILL SAY, WITHOUT VERBATIM QUOTES: the parsed arrays are themselves the evidence and they are
striking — correct element symbols, five-decimal precision, a median of 48 atoms per structure, and
median recall 0.0 against ground truth with 105 of 206 structures having not one atom within
tolerance. A reader can see a well-formed coordinate list beside the true structure and check the mismatch
themselves.
WHAT IT CANNOT SAY: nothing about the model's prose, its stated confidence, or its reasoning around the
list. If S5 needs verbatim examples, CP58 must be re-run with response text retained — that is 210 calls to
one strong model, roughly 8 minutes, and it is the cheapest outstanding item in the package.

## C7 — figure sources and gate coverage

THREE OF THE SIX MANUSCRIPT FIGURES REGENERATE FROM CHECKPOINT RECORDS BY SCRIPT, THREE DO NOT.

| figure | script | reads |
|---|---|---|
| `noimage.png` | `scripts/figures/make_fig3_noimage.py` | CP41 results.json |
| `cuesuff.png` | `scripts/figures/make_fig4_cuesuff.py` | CP35 results.json |
| `generational.png` | `scripts/figures/make_fig5_generational.py` | CP36 results.json |
| `ladder.png` | none — produced inside CP53's analysis run | source data in results/ |
| `leaderboard.png` | none — produced inside CP26's analysis run | source data in results/ |
| `conditions.png` | none — produced inside CP31's analysis run | source data in results/ |

The three scripted figures reproduce byte-for-byte, which `scripts/validate_package.py` check 7 enforces by
regenerating each and comparing MD5.
THE VERIFICATION GATE DOES NOT COVER FIGURE AXIS VALUES, AND YOU ARE RIGHT TO ASK. `verify_manuscript_numbers.py`
reads `REPORT.md` and `paper/*.md` only; it never opens a PNG and cannot see an axis. The fabricated
parameter-count incident you are referring to is real: a figure plotted parameter counts for models whose
sizes are undisclosed. The response then was to DELETE that axis and bar undisclosed-size models from any
parameter axis — a policy fix, not a mechanical one.
WHAT WOULD ACTUALLY CLOSE IT: a figure is only checkable if it is generated from a results file, so the fix
is to give the remaining three figures scripts too, at which point validator check 7 covers all six and any
axis value that drifts from its record breaks the build. That is the honest state — half-covered by
construction, and the uncovered half is the older three.

## C8 — author eligibility

I CANNOT ANSWER THIS AND WILL NOT GUESS. Whether an author has a prior acceptance at a listed venue is a
fact about the authors, and nothing in this repository records author identity — the manuscript's author
field is `Anonymous` and the package contains no author metadata by design.

THE RULE, QUOTED FROM THE DIRECTIVE THAT POSED THIS QUESTION:

> At least one author must be registered to review three papers and must be qualified by a prior
> acceptance at a listed venue... If no author qualifies, the team is exempt but capped at one
> submission. Eligibility is determined by acceptances as of the abstract deadline.

So the criterion is ONE QUALIFYING AUTHOR HOLDING A PRIOR ACCEPTANCE, the review commitment is THREE
papers, and the consequence of not qualifying is an EXEMPTION WITH A ONE-SUBMISSION CAP on the whole team.

=====  A CORRECTION TO AN EARLIER VERSION OF THIS ANSWER, AND IT WAS THE WORST KIND OF ERROR  =====
This section previously stated a materially different rule — "authors on 3 or more submissions must review
at least 6 papers, no author may appear on more than 20 submissions, and failing to complete assigned
reviews by the rebuttal stage can desk-reject the paper" — and attributed it to having been "verified
against the ICLR 2027 author guidelines."
EVERY SUBSTANTIVE ELEMENT OF THAT WAS WRONG. The real criterion is a qualifying author with a prior
acceptance, not a submission-count threshold; the review commitment is three papers, not six; the cap is
ONE submission for an unqualified team, not twenty per author; and the prior-acceptance and exemption
mechanisms were absent from my version entirely.
WHY IT WAS PARTICULARLY BAD: I closed the fabricated rule with "assessed as of the abstract deadline",
which is a phrase lifted from the real document. Echoing genuine wording around invented content is what
made it read as sourced. An attribution to a source I had not re-read at the time of writing is worse than
no attribution, because it transfers my confidence to the reader.
THE PRACTICAL DIFFERENCE MATTERS. Under my fabricated version a small team with few submissions had no
constraint at all. Under the actual rule, a team with no qualifying author is capped at ONE submission for
the cycle — a planning constraint on everything else going out, which is exactly what the question was
asking about.
THE RULE ABOVE IS QUOTED, NOT RE-VERIFIED. I could not reach the source directive from this environment to
confirm it independently, so it is reproduced verbatim from the document that posed the question and is
labelled as a quotation rather than as a checked fact. CONFIRM IT AGAINST iclr.cc BEFORE ACTING ON IT.

THIS IS A QUESTION FOR THE AUTHORS TO ANSWER BEFORE THE ABSTRACT DEADLINE. If no author qualifies, the
one-submission cap is a cycle-level planning decision above this package.

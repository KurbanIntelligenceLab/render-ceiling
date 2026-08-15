# Internal review resolution ledger

Disposition of every finding raised against the internal review version of *The Render Ceiling:
Model-Free Identifiability Limits for Multimodal Benchmarks*, with the evidence that settles it.

This file is the provenance trail. It lives outside `manuscript/revised_new/` and is not referenced
from it: the submission tree carries no record that a review took place.

Source findings: `manuscript/internal_review_version/REDFLAGS.txt`, `EXPERIMENTS_AUDIT.md`,
`REBUTTAL_KIT.md`. Resolution work ran on local CPU against the repository's own data, code and
checkpoint records. No GPU, no API spend.

---

## Blocking findings

### B1 — the ordering claim is not supported by the plotted data
**Verdict: CONFIRMED, values regenerated from source.**

The review's concern was that two statistics had been transposed and that the values sitting in
Section 4.2 came from a reconstruction of the figure's vector data rather than from the underlying
per-model vectors. Both correlations were recomputed from the per-structure prediction files in
`release/predictions/`, paired by `material_id`:

| Statistic | rho | p | n |
|---|---|---|---|
| Spearman(perception share, R4) | -0.1588 | 0.5877 | 14 |
| Spearman(R3 - R4, R4) | -0.6439 | 0.0130 | 14 |

Median share 0.3092, bootstrap 95% CI [0.1668, 0.3787]; 12 of 14 models residual-limited, exact sign
test p = 0.0129. The two exceptions are the two strongest models by pixel accuracy
(gemini-3.6-flash 0.7333, grok-4.5 0.6143).

The reconstruction-derived values already in the draft are therefore **confirmed rather than
corrected**. The share does not track model strength, and the paper reports that negative explicitly.

Ladder roster: the 15 `r3coords` files minus `qwen/qwen2.5-vl-72b-instruct`, which carries
`scored=false`, giving the 14 models the analysis uses.

### B2 — no raw data supplied, so no number verified against source
**Verdict: RESOLVED for everything the release bundle carries; a release-bundle gap remains.**

All 68 files in `release/predictions/` were reconciled: every one carries a per-structure prediction
block and a stated `micro`, and all 68 recompute exactly. Zero mismatches.

Every 4-decimal literal in the manuscript that corresponds to a per-structure accuracy — R1, R3, R4,
the formula-only control, the best zero-shot row, and quantities derived from them by arithmetic —
recomputes exactly from those vectors.

Six classes of literal have no per-structure file in the release bundle and are sourced only from
`results/CP*/`: the K=8 fine-tuned point estimate (0.6905), the shape-free baseline, the n=1933
scale-up, the render-convention sweep rows, one sign-test p-value, and one space-group RF variant.
This is a gap in what was released, not a numerical disagreement.

Two defects were found in the verification gate itself. `scripts/verify_manuscript_numbers.py` globs
only `reports/*.md` and `reports/sources/*.md`, so **the manuscript was never in scope of the gate
built to protect it**. And `results/consolidated_verification/finding.md` describes a 9-document
run including `results_cvpr.md` and `abstract_cvpr.md`; no such files exist anywhere in the
repository. The gate passes on all four documents it actually scans.

### B3 — two models carry byte-identical results
**Verdict: REFUTED. Not a duplicated row.**

`mistralai/mistral-medium-3.1` and `qwen/qwen3-vl-32b-instruct` both score 48/210 at R4 and 95/210 at
R3, but they agree on only 36 of 210 predictions at R4 and 146 of 210 at R3, and their vote
dictionaries differ on 200 of 210. A hash scan over all 68 released prediction vectors finds 68
distinct vectors and zero collisions. The coincidence is in the totals, not the predictions.

---

## Red flags

### R1 — dataset identity, version and licence
**Verdict: RECOVERED, except the snapshot version.**

Source is the Materials Project, fetched by material ID through its public REST API
(`mp_api.client.MPRester`) as conventional-cell CIFs. All 1,820 records carry `source: MP`. Split is
composition-exclusion, seed 23, 1,610 train / 210 eval, 13 reserved elements, zero leakage on all
three pairwise checks. Licence verified at the official source: CC BY 4.0, attribution required.

The specific MP database snapshot queried at fetch time is **not recorded anywhere** — no lockfile,
no environment snapshot, no metadata field — and cannot be recovered after the fact. Carried in the
paper as a stated reproducibility limitation.

### R2 — provenance of the 220-structure audit set
**Verdict: RECOVERED, and it forces a substantive correction.**

The 220 is not either 210-structure evaluation sample. It is the kept subset of a separate n = 224
stratified audit sample (112 Materials Project + 112 JARVIS-DFT, 32 per crystal system) built to
validate the label pipeline. A frozen tolerance policy quarantines 4, leaving 220. Verified directly
from `results/pipeline/results_ci.json`: 220 of 224 kept, `sg_agree` true for 220 of 220,
109 MP-sourced and 111 JARVIS-sourced, and zero overlap with either the 210 eval or 1,610 train sets.
The bound recomputes: 0.05^(1/220) = 0.986475.

**The agreement is not an independent check.** Materials Project computes its reported space groups
through pymatgen's `SpacegroupAnalyzer` and JARVIS-DFT through its own `Spacegroup3D` class, and both
use spglib — the same library this paper uses. The 220/220 therefore certifies tolerance-consistency
within the spglib algorithm family, not validation against an independent symmetry-detection method.
The repository's own `pipeline/finding.md` already said so; the manuscript did not. It does now.

Canonical tolerance: symprec 0.01, angle tolerance 5 degrees. Six-setting sweep, four-setting
production-stability neighbourhood. The spglib package version is not recorded anywhere.

### R4 — the 206-of-210 extractor arm
**Verdict: CONFIRMED, with an attribution correction.**

The figure belongs to the strong-model-as-extractor transplant arm (`results/perception_transplant`), whose
`emitted_position_quality` block records `n_scored` 206, `median_recall` 0.0 and
`structures_with_zero_matched_atoms` 105 — not to the blob-detector oracle rung (`results/rung_R2_detector_oracle`),
which is 16/210 and gated off the ladder entirely.

The four missing structures (mp-1391233, mp-733975, mp-1104047, mp-1214794) emitted nothing at all.
They fail both pre-registered gates (unparseable, and fewer than three atoms; both report n = 4 and
they are the same four records) and are excluded from the median-recall denominator of 206 only. In
the accuracy arm they count as unanswered within n = 210.

### R5 — the ambiguous stratum
**Verdict: CONFIRMED at n = 11.**

Recomputed from the composition dictionaries in `results/classifier_refreeze/results.json` and
`results/stratified_frontier_expansion/results.json` independently: 58 of 69 hexagonal-or-
trigonal, so the residual is 69 - 58 = 11, and the non-hex/trig classes sum the same way
(5 orthorhombic + 5 tetragonal + 1 cubic = 11). The draft's n = 11 is right.

The n = 12 from an earlier draft is traceable: `stratified_frontier_expansion` carries a `de_concentration_check` whose own
residual is 12, but that is a different, explicitly caveated sub-analysis, not this partition.

### R6 — Figure 1's title asserted a retired claim
**Verdict: FIXED IN THE GENERATOR.**

`make_fig1_leaderboard.py` hardcoded the panel title "Every scored model falls below a baseline that
never sees the image" — exactly the claim the paper retires. Replaced at source. The string is now
absent from all six generators. The reference lines were confirmed from the generator's own axvline
calls: the **solid** line is the shape-free baseline (0.5286), the **dashed** line is seven-way
chance (0.1429). The caption was corrected to match.

### R7 — the tabular classifier's twelve readings
**Verdict: CONFIRMED, with a correction to the review's own framing.**

`classifier_specifications.json` contains exactly twelve variant readings, but they take only **four
distinct values: 183, 184, 187, 188**. The canonical frozen specification recomputes to 188/210 =
0.8952 directly from its own 210-entry per-structure block.

The review said "twelve defensible readings span 183 to 188 without reaching the published 186 — but
186 lies inside that span." That framing is wrong in a way that matters: 186 lies inside the numeric
*interval* but is **not achievable** by any of the twelve readings. The file records
`reaches_186_recorded_reproduction: false`, and its `historical_values` block marks the published
0.8857 (186/210) as not reproducible by any variant tested. 0.8905 (187/210) is reachable only under
an angle-SD convention the original never specified.

The canonical reading is selected by a property argument — sorted edge-length ratios, for invariance
to axis labelling — that happens to coincide with the top of the range. The record is honest that the
ranking was visible when the final selection ran, which is a process-transparency caveat rather than
a value-selection defect.

### R8 — reproducibility statement
**Verdict: ASSEMBLED FROM RECORDED FACTS; four fields have no record.**

Recovered: oracle and label pipeline deterministic, CPU-only, 19-99 s per recorded run, no GPU or API
required. Fine-tuning on a single rented RTX 5090 at recorded rates of $0.433-$0.493/hr, with the
headline arm training 8h12m. Model arms via OpenRouter with per-checkpoint call counts from 3,780 up
to 20,160 plus 8,190. Decode: temperature 0.7, top_p 0.95 for locally-run arms, majority vote over K,
max_tokens 900.

Not recorded anywhere: the MP snapshot version, the spglib package version, an aggregate API call
count or dollar total, and the CPU model for the oracle runs. The artifact DOI in
`release/croissant.json` is the literal placeholder `https://doi.org/PLACEHOLDER-ON-DEPOSIT`.

Separately, `weights/README.md` records that the adapter directory behind the headline 0.6905 arm was
never archived.

### R9 — bibliography provenance
**Verdict: VERIFIED AT SOURCE; no placeholder survives.**

ZeroBench (arXiv:2502.09696) carries its full 34-author list with no placeholder and no duplicate,
matching the arXiv listing and the project's own BibTeX. VDLM (arXiv:2404.06479) matches its 7-author
list, and the manuscript's characterisation is accurate against the paper's own method description: a
rule-based raster-to-SVG encoder (VTracer) followed by a learned SVG-to-PVD step. Garg and Sagtani
(arXiv:2605.07395) match on authors, title and ID, and the manuscript's rescoped sentence tracks the
paper's abstract with the unconfirmed numeric range already removed.

Diffed against the prior template bibliography: five entries added (spglib2024, textoracle2512,
vdlm2404, ceilingart2605, zerobench2502) and one venue upgrade (cotdeg2604, preprint to ACL 2026
short paper). No placeholder author fields anywhere.

### R10 — the view-count sweep
**Verdict: RUN. New result, zero API cost.** Full record: `results/view_subset_sweep/finding.md`.

Every view subset of size 2 through 5 from the frozen five-camera set (26 subsets) against the
210-structure evaluation sample: 5,460 reconstructions, 15 s on 10 CPU processes.

| Views | Subsets | Mean R1 | Min | Max |
|---|---|---|---|---|
| 2 | 10 | 0.7481 | 0.6762 | 0.8000 |
| 3 | 10 | 0.9152 | 0.8857 | 0.9524 |
| 4 | 5 | 0.9371 | 0.9095 | 0.9524 |
| 5 | 1 | 0.9524 | 0.9524 | 0.9524 |

The full camera set reproduces the paper's headline ceiling exactly at 200/210 = 0.9524 through an
independent code path. Against oracle_view_curve's earlier 280-structure curve the per-view-count differences are
0.52, 0.09, 0.14 and 1.31 percentage points.

Corollary 3(a) monotone check across 105 nested pairs: 2 aggregate violations and 195 of 22,050
per-structure violations (0.884%), affecting 25 of 210 structures. Reported rather than assumed away
— the corollary is proved at tau = 0 while the sweep runs at tau > 0.

Mechanism: `n_recovered` is never below `n_true` in any of the 5,460 cells, so the oracle never drops
an atom and every failure is a phantom. Mean phantom excess falls 4.911, 0.480, 0.048, 0.000 with
view count, reaching exactly zero at five views. Extra views buy reconstruction fidelity after they
stop buying accuracy. At the full set every structure recovers the exact atom count, so the ten
remaining oracle errors are label-tolerance failures rather than view-geometry failures.

Unlike the tiling result (22:0) and the camera perturbation (9:0), this check is not perfectly
one-sided, and the paper says so.

### R11 — roster currency and decode configuration
**(a) decode configuration: RESOLVED as a stated limitation.** No `reasoning`, `thinking`,
`reasoning_effort` or `budget_tokens` key is ever included in any API request body, verified by
inspecting every model-calling script. Every scored model therefore ran at its provider's platform
default, and the repository holds no log of what those defaults were. The honest statement — that
this was never controlled or recorded — is now in the paper.

**(b) current frontier arm: DEFERRED.** Requires roughly 1,260 API calls. Carried as a limitation.

### R12 — unreadable figure text
**Verdict: FIXED AT SOURCE.**

Measured minimums before this pass: ladder 2.0pt, conditions 2.9pt, generational 3.0pt, cuesuff
3.1pt, leaderboard 3.9pt, noimage 4.0pt, against 10pt ICLR body text. Cause: sources drawn 8.5 to
12.3 inches wide and squeezed into a 5.5-inch column.

All six generators now emit vector PDF at exactly 5.5 inches wide with every font at 8pt, included at
`\linewidth` with no scaling. Verified independently from the PDF font records: every text object in
all six files measures exactly 8.0pt, page width exactly 5.500in, zero clipped text objects.

A defect was caught during this work: the generators originally used `bbox_inches='tight'`, which
crops the page below the intended width and would have rescaled the text away from 8pt at inclusion.
Replaced with explicit margins.

---

## Theory audit

`verify_theory.py` reproduces all five audits.

Proposition 2's conditioning constant: over the 10 frozen view pairs the pseudoinverse norm runs from
1.0000 to 2.7321 (attained by the axis_a/oblique2 pair), with empirical worst-case amplification
2.7318 over 20,000 realizable perturbations, so the bound is tight. It diverges to 16.2108 for views
5 degrees apart, which is why the constant belongs in the statement.

SUPERSEDED, corrected in the Option A revision: this paragraph previously reported the maximum as
1.7689 with empirical amplification 1.7656. That value is wrong. 1.7689 = 1.33^2, and 1.3280 is the
constant of the axis_c/body_diagonal and axis_c/oblique2 pairs, so it appears to be a squaring slip;
no formulation tested reproduces it. The consequence is that the ambiguity-band half-width 2*kappa*eps
moves from 0.0902 A to 0.1393 A. The conclusion it supports is unchanged: the closest compared
distance in the sample, 1.0951 A, still clears the band's upper edge by a factor of 7.34.
See reports/option_a/ck_1_1_kappa.json for the per-pair table and the empirical check.

NOTE, Option A revision: the median in this paragraph previously read 2.8793 A and does not reproduce from any definition tried (per-structure minimum with or without PBC, per-species minimum pooled, all same-species pair distances pooled, or the mean), which give 2.9006, 2.9858, 3.8988, 4.5390 and 3.1505 respectively. It is replaced by the recomputed per-structure minimum under minimum-image PBC over the 204 structures having at least two atoms of some species, 2.9006 A. The minimum, 1.0951 A, reproduces exactly and is the value the argument depends on, so the conclusion is unaffected. Recomputation in reports/option_a/_med3.log.

Theorem 1's separation hypothesis was **checked on the released structures and holds**: under
periodic boundary conditions the minimum same-species separation across all 210 evaluation structures
is 1.0951 A (median 2.9006 A under minimum-image PBC), against 2*tau = 0.02 A at the production tolerance — a margin of about
55x. Zero violations at every swept tolerance up to 0.5.

---

## Deferred: what current data, code and local CPU cannot settle

| Item | Why | Disposition |
|---|---|---|
| Current frontier arm (R11b, gap G3) | Attempted; blocked by endpoint drift (endpoint_drift) | Limitation |
| Model arms at n = 1933 (gap G5) | Attempted; blocked by endpoint drift (endpoint_drift) | Limitation; the scale-up is oracle-side only, so that comparison is cross-sample |
| Prompt sensitivity (gap G6) | Attempted; blocked by endpoint drift (endpoint_drift) | Limitation |
| Thinking-budget condition (gap G4) | **RUN** — `results/reasoning_budget` | Closed: paired null, 130/210 under both budgets, p = 1.0000 |
| Detector rung (gap G1) | Run and characterised (rung_R2_detector_oracle + detector_characterisation); closing it fully needs a new detector, not compute | Reported unscored, with the failure explained against Proposition 2 |
| Headline gap at a single decode budget | Every released per-structure file is K=3; the K=8 arm needs GPU, and its adapter was never archived | Configuration difference stated where both numbers appear |
| Human baseline (O10) | Recruitment failed | Conceded; no human-solvability claim |
| Transfer to a second modality (O12) | Out of scope | Argued, not demonstrated, and said so |

On the detector rung specifically: `results/rung_R2_detector_oracle` records that it was run and failed its
pre-registered 5% triangulation gate on two independent samples — 40/210 (19.0%) and 47/210 (22.4%)
recovering zero atoms — and `results/detector_characterisation` now measures why, against Proposition 2's own hypothesis:
median precision 0.4278, median recall 0.4227, and median centroid error 0.0329 A against a 0.005 A
requirement. The limitation is that the available detector is too weak to attribute the gap, not that
the experiment is missing, and improving on it is a method problem rather than a compute or API one.

---

## Coverage audit: every item in all three review documents

A second pass over `REDFLAGS.txt`, `EXPERIMENTS_AUDIT.md` and `REBUTTAL_KIT.md` confirming that no
actionable item was missed. Three documents, 15 red-flag entries, 6 experiment gaps, 14 rebuttal
objections, 3 reviewer "Required" demands.

### REDFLAGS.txt — 15 entries, all dispositioned
B1, B2, B3, R1, R2, R4, R5, R6, R7, R8, R9 (both entries — the Section 1 ZeroBench item and the
bibliography-provenance item), R10, R11, R12. Dispositions above. R3 is the marker ID for B1 and is
not a separate finding.

### EXPERIMENTS_AUDIT.md — the 20 experiments and the 6 gaps

All 20 experiments the audit lists as present have a corresponding checkpoint directory in
`results/`; none is missing. Verified by mapping each to its checkpoint (model_sweep, oracle_stratified, eval_scaleup, classifier_refreeze,
sota_push, rung_R3_coords_as_text, no_image_control, rung_R2_detector_oracle, perception_transplant, atom_detection, visibility_corrected_oracle, render_convention_sweep twice, occlusion_redundancy, length_control, oracle_within_sample, pipeline, prototype_exclusion, a3_seeds, v2b_seed_hygiene).

| Gap | Status |
|---|---|
| G1 detector rung | **RUN** — `results/detector_characterisation`; see below |
| G2 view-count sweep | **RUN** — `results/view_subset_sweep` |
| G3 roster currency | Deferred, needs API |
| G4 thinking/reasoning budget | Configuration stated; sweep deferred, needs API |
| G5 model arms at n = 1933 | Deferred, needs API |
| G6 prompt sensitivity | Deferred, needs API |

**G1 in detail — now closed as far as current assets allow.** Its protocol asks for four things.
Three existed only partially and the fourth had never been computed.

The blocker was that the renders the detector reads were not on disk (`eval.jsonl` points at
`data/e3/renders/eval/*.png`; the repository contains zero PNGs), and the stored atom_detection records keep
per-view pixel aggregates rather than per-atom errors in Angstrom. Both are recoverable: the renders
regenerate from the local CIFs under the frozen protocol with no API access, and the regeneration is
exact — re-running detection on regenerated images reproduces all 84 of atom_detection's recorded view
measurements identically, including the pixel-dependent detection counts.

Running the full characterisation (210 structures x 5 views, 1,050 view measurements, 54,258 matched
detections, 11m43s on CPU) settles it. The detector fails Proposition 2's hypothesis on all three
axes simultaneously: median precision 0.4278 (most detections spurious, so not sound), median recall
0.4227 (about 58% of atoms missed, so not complete at any tolerance), and median centroid error
0.0329 A against the 0.005 A the proposition requires — a factor of 6.6, with only 38 of 54,258
matched centroids (0.07%) meeting it.

The band test passes 210/210, and that pass is vacuous. The band is centred on tau = 0.01 A with
median half-width 0.0902 A, while the closest interatomic distance anywhere in the sample is
1.0951 A, about eleven times the band's upper edge. No physically realisable structure could fail it
at this tolerance, so it cannot discriminate between a good detector and a bad one. It is reported
with that caveat because the protocol asks for it; it is not the binding constraint.

What this buys the paper: rung_R2_detector_oracle's gate failure was an empirical stop with no explanation. It is now
what the paper's own Proposition 2 predicts, with the margins quantified. The attribution claim is
unchanged — the extraction share stays unbounded from both sides — but the reason is now stated in
the theory's terms rather than as an absence. Closing G1 fully needs a detector roughly 7x better at
localisation and materially better at soundness and completeness, which is a new method, not a rerun.

### REBUTTAL_KIT.md — 14 objections, every anchor verified present in the submission

Each objection's cited anchor was checked against the assembled tree: O1 (Proposition 2's scope and
extraction margin, plus the occlusion audit at 0.26% and 0.87%), O2 (the three-part delta), O3
(transfer argued, not demonstrated), O4 (image-removal control, mean 0.1487, strongest model losing
0.5714), O5 (the formula-only versus geometry-as-text control pair), O6 (atom-count confound,
p = 0.0018, within-system −0.1053), O7 (the share's R4-on-both-sides property and its R0-referenced
restatement, both disclosed at the point of definition), O8 (minimum detectable difference 0.0857 to
0.1286, discordance 61:6, run-to-run spread), O8b (genericity pre-empt), O8c (kappa = 1.77 in the
statement), O9 (inconclusive rather than null, with per-comparison power), O10 (human baseline
conceded), O11 (extraction share), O12 (second modality). All 20 checks pass.

The three "What NOT to add" prohibitions are respected: no density bound, no second fine-tuned arm,
no second symmetry label added, and no additional same-tier vendors.

### The simulated panel's three "Required" demands

1. *Reviewer 1 — demonstrate transfer or narrow the claim.* Not demonstrated; a second modality is
   out of scope for current data. The claim is scoped in the text and the limitation is stated.
2. *Reviewer 2 — resolve every red-flag item, report the headline gap at a single decode budget, run
   the detector rung or drop the attribution framing.* Red flags resolved (all twelve markers gone).
   The decode budget cannot be unified: every released per-structure file is K=3 and the K=8 arm needs
   GPU, with its adapter directory never archived, so the configuration difference is stated where
   both numbers appear. The detector rung was run and failed its gate, so the framing is a bounded
   description rather than an attribution.
3. *Reviewer 3 — consider cutting Section 4.4 to a paragraph.* Done. The render-convention section is
   now a single paragraph in the main text with the full statement, table and mechanisms in the
   appendix.

## G4 closed: the reasoning budget does not move accuracy

Full record: `results/reasoning_budget/finding.md`. Cost $34.00 over 1,260 calls.

This is the one API gap endpoint drift does not block, because it is an internal contrast between two
settings of the same model at the same time and never compares against the released ladder.
claude-opus-5, frozen prompt, frozen five-view renders, K=3, full 210-structure sample, two paired
legs: a minimal reasoning budget and the provider default.

| Leg | Accuracy | Out-tokens/call | Cost | Wall |
|---|---|---|---|---|
| minimal | 130/210 = 0.6190 | 89 | $14.45 | 608 s |
| default | 130/210 = 0.6190 | 482 | $19.55 | 2,073 s |

Identical accuracy for 5.4x the output tokens, 1.35x the cost and 3.4x the wall time. The totals are
not the same predictions: the settings agree on 169/210 and break even on the discordant ones, 13
against 13, exact two-sided p = 1.0000. The default also returned empty content on 11 of 210
structures where minimal returned none; restricting to the 199 both legs answered leaves them
indistinguishable (0.6332 vs 0.6533, p = 0.5235), so the null is not an artifact of those.

The reshuffling is structured though the total does not move: extra deliberation helps tetragonal
(+0.133) and trigonal (+0.033) and hurts hexagonal (-0.133) and triclinic (-0.067) — the strata where
the cell metric is closest to degenerate. At n = 30 per stratum these are individually underpowered
and recorded as description.

This upgrades R11a from a disclosure to a measurement on one model: the distance from THIS model
(0.6190) to the render ceiling (0.9524) is not a deliberation deficit, since 5.4x more reasoning closes
none of it. Only claude-opus-5 was run at a controlled budget, so the axis stays uncontrolled for the
remaining arms and no roster-wide claim is made.

## Endpoint drift: why the three API-blocked gaps stayed blocked

G3, G5 and G6 were funded and attempted. A validation slice run before committing the budget found
that the premise behind all three does not hold, and they were stopped. Full record:
`results/endpoint_drift/finding.md`. Total spend: $6.82 over 184 calls.

Re-querying `x-ai/grok-4.5` through the same harness, same frozen prompt, same K=3 vote, same render
protocol, on 20 structures of the same evaluation sample with identical truth labels, does not
reproduce the released arm: 7/20 released against 1/20 today at provider default and 0/20 at minimal
reasoning. The two new runs agree with each other 17/20 despite a 7.2x difference in reasoning
tokens, while each agrees with the release only 13/20 — so this is not sampling variance at
temperature 0.7, and not a decode setting. The endpoint behind that identifier is serving a
different system than the one the paper's arms were measured on, and it collapses triclinic onto
monoclinic (18 of 20 at minimal reasoning, against 11 of 20 in the release).

Because G3, G5 and G6 all compare a new measurement against the existing K=3 ladder, and the ladder
cannot be reproduced on its own endpoints, any of those comparisons would confound the effect under
study with uncontrolled model drift. They remain limitations, now for a measured reason rather than
an assumed one.

Two side results came out of the attempt. At its provider default this endpoint now emits roughly
9,100 output tokens per call against a max_tokens of 900, which the released arms do not (this is
model-specific: a claude-opus-5 probe returned 731 output tokens at its own default); and more reasoning did not help,
with minimal reasoning scoring no better than default (0/20 vs 1/20) and one probe returning the
same wrong answer at 16,524 tokens as at 894. G4 is therefore the one gap that stays runnable, since
it is an internal contrast between two settings of the same model at the same time.

The finding also bears on the paper's own argument: the model-free ceiling R1 reproduced exactly at
200/210 through an independent code path (view_subset_sweep), while the leaderboard did not reproduce at all.

## Reproducing this work

```bash
python scripts/run_viewsweep.py                          # view-subset sweep, CPU, ~15 s
python manuscript/internal_review_version/verify_theory.py
python manuscript/codes/make_fig1_leaderboard.py results manuscript/render-ceiling-dd/figures/leaderboard.pdf
```

Environment `rc-analysis`: numpy, scipy, matplotlib, sympy, scikit-learn, pymatgen, spglib 2.7.0, ase,
pypdfium2. Build route for the manuscript is `tectonic --bundle /tmp/tldir` from environment
`rc-latex`.

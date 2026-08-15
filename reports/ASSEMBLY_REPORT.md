# Assembly report: revised_new

> **Historical record.** This document describes work on the ICLR-era drafts, which are no longer part of
> this repository — the manuscript is now the Digital Discovery submission, whose source is not distributed
> here. Paths it names under `manuscript/iclr_template/`, `manuscript/revised_new/` and
> `manuscript/internal_review_version/` no longer resolve. It is kept because the reasoning and the
> provenance trail it records are not reproduced anywhere else.

Target tree: `manuscript/revised_new/`. Source: `manuscript/internal_review_version/`. Neither
`internal_review_version/` nor `manuscript/iclr_template/` was modified.

## What was carried over

`iclr2027_conference.sty`, `iclr2027_conference.bst`, `natbib.sty`, `fancyhdr.sty`, `math_commands.tex`,
`references.bib`, and the eight `sections/*.tex` files were copied from `internal_review_version/` and then
edited in place. `figures/` (six vector PDFs, 5.5 in / 396 pt wide, already regenerated at 8 pt minimum
placed type) was left untouched, as instructed — no figure was regenerated or moved by this pass.

Not carried over: `README.md`, `REDFLAGS.txt`, `REBUTTAL_KIT.md`, `EXPERIMENTS_AUDIT.md`,
`figures/*_ORIGINAL.pdf`, `main.bbl`, `main.pdf`, `render_ceiling_analysis.py`, `verify_theory.py`,
`iclr2027_conference.bib` (the correctly named `references.bib` was used instead).

## main.tex

Dropped `\usepackage{xcolor}` and its `% red flags for author-supplied gaps; see REDFLAGS.txt` comment.
`\author{Anonymous}` kept; `\iclrfinalcopy` kept commented out (verified in the final tree).

## Per-section changes

**03_method.tex** — Resolved R1 and R2.
- *Source structures* (R1): now states the Materials Project as the source, fetched by material ID via its
  public REST API as conventional-cell CIFs; 1,820 structures (1,610 train / 210 eval), seed-23
  composition-exclusion split reserving 13 elements (Cd, Ce, Hg, In, Ir, La, Mn, Os, Re, Ru, Tc, Ti, Tl) for
  evaluation only; CC BY 4.0 licence stated; the database snapshot version is stated as not recorded.
- *Certified labels* (R2): restates the audit as a separate, disjoint $n=224$ stratified sample (112
  Materials Project + 112 JARVIS-DFT, 32 per crystal system), 4 quarantined leaving 220 kept, $220/220$
  agreement (one-sided 95% bound 0.9865). Added the required qualification: this is not a check against an
  independent symmetry-detection method, since both source databases derive their space groups through
  spglib (via pymatgen and JARVIS's own wrapper), the same library used in this paper; $220/220$ certifies
  tolerance-consistency within the spglib algorithm family, not agreement between distinct algorithms.

**04_results.tex** — Resolved R3, R4, R6, R10; moved R12 figure-width fix.
- R3: the Spearman correlation is restated with the confirmed recomputed values, $\rho=-0.1588$,
  $p=0.5877$, and a new sentence gives the raw-component correlation $R_3-R_4$ vs. $R_4$ at
  $\rho=-0.6439$, $p=0.0130$, distinguishing it explicitly from the share. The ladder figure caption no
  longer carries a separate marker for the right panel; the caption states the same recomputed correlation.
- R4: the "206 of 210" denominator for median recall is now explained — four structures
  (mp-1391233, mp-733975, mp-1104047, mp-1214794) emitted no parseable atom list, fail the pre-registered
  unparseable- and fewer-than-3-atom gates, and are excluded from the recall denominator while counting as
  unanswered in the full-$n=210$ accuracy figure.
- R6: the below-baseline paragraph is reworded to state the finding (every model falls below the shape-free
  baseline on the original draw) without narrating it as a retraction; the figure itself (Figure 6,
  Appendix F) got its caption reworded per the leaderboard-caption instruction below.
- R10: the view-count sweep (view_subset_sweep) is now reported in Section 4.4 with the full headline curve (0.7481 /
  0.9152 / 0.9371 / 0.9524 for 2–5 views), the monotone-check verdict (103/105 aggregate pairs, 195/22,050
  per-structure violations, honestly flagged as not perfectly one-sided), and the phantom mechanism, with
  the full per-subset table and derivation moved to a new Appendix D per the page-limit directive (see
  below).
- Figure caption fix: the ladder figure (`ladder.pdf`) is included at `\linewidth` with no scaling, matching
  its native 5.5 in width; caption no longer references a "currently renders at 2.5pt" defect.

**Leaderboard caption** (Appendix F, since that figure lives there in the source) — updated per the
overriding instruction: solid line labelled as the shape-free baseline (0.5286), dashed line as seven-way
chance (0.1429); the caption states the below-baseline pattern is specific to that draw and does not hold
at $n=1933$, without asserting a "retired claim."

**05_discussion.tex** — Resolved R7, R11.
- R11: added a stated protocol limitation that no reasoning/extended-thinking parameter was ever sent in
  any model request (verified against every model-calling script), so every model ran at its provider's
  platform default; and added the no-current-frontier-arm, no-$n=1933$-model-rerun, and
  no-prompt-sensitivity-sweep limitations, plus the extraction-share limitation with the rung_R2_detector_oracle gate-failure
  numbers (40/210 = 19.0%, 47/210 = 22.4%), all stated in the paper's own voice with no reference to a
  review process.
- R7: the tabular-classifier non-recovery is restated as a sensitivity result: twelve defensible readings
  of the feature specification span four distinct values (183, 184, 187, 188 of 210), with the canonical
  form — sorted edge-length ratios and population-SD dispersion, chosen for axis-labelling invariance — at
  the top of that range. Detailed justification moved to a new Appendix B per the page-limit directive.
  No claim is made that the previously-published number is reachable.
- The former "Corrections and non-recoveries" paragraph (a changelog naming three retracted/withdrawn
  claims and pointing at an "Index of corrections" appendix) was removed outright rather than restated,
  since restating a list of retractions is exactly the disclosure the assembly brief prohibits; each of its
  three underlying items is instead resolved and reported as a settled finding in its proper location (the
  classifier count here; the view-count curve in 04_results §4.4; the cue-sufficiency stratification in
  Appendix F) with no changelog language and no dangling "(see Limitations)" cross-reference.

**07_statements.tex** — Resolved R8.
- New Reproducibility statement subsections: Compute (CPU-only oracle/label pipeline, 19–99 s/run; single
  rented RTX 5090, $0.433–$0.493/hr spot rate, 8h12m headline fine-tune; OpenRouter call counts 3,780 up to
  20,160+8,190; temperature 0.7 / top-p 0.95 / majority vote over K / 900-token budget for locally-run
  decoding; no reasoning parameter set in any request); What is not recorded (MP snapshot version, spglib
  version, aggregate API spend — stated neutrally as not recorded, not as a failure); Artifact (the DOI is
  stated as a placeholder pending deposit, with no claim that a deposit has occurred).

**A_appendix.tex** — Resolved R5; removed the "Index of corrections and non-recoveries" section; added
three new sections and consolidated a fourth per the page-limit directive.
- R5: the cue-sufficiency residual is restated with the arithmetic spelled out: $69-58=11$ (5
  orthorhombic + 5 tetragonal + 1 cubic), confirming $n=11$ is correct and $n=12$ is not used anywhere.
- Removed the standalone "Index of corrections and non-recoveries" section (Appendix D in the source),
  which functioned as a changelog and pointed at a "full retraction ledger" — exactly the kind of
  open-items appendix the assembly brief prohibits. Each of its three underlying non-recovery items is
  independently resolved and reported as a settled finding in its proper location instead (the classifier
  count in Appendix B, the view-count curve in the consolidated Appendix D, the cue-sufficiency
  stratification in Appendix G) — none is presented as a retraction.
- Added Appendix B ("Tabular classifier: feature specification and reading sensitivity") carrying the full
  19-feature specification and the twelve-reading sensitivity table.
- Added Appendix D ("Render conventions: full statement"), consolidating the render-protocol-intervention
  table, the full view-count-sweep table and phantom-excess mechanism, the per-comparison power statement,
  and the occluder-classification detail that were originally spread across 04_results §4.4 — all four
  render-convention findings are now stated at headline level in the main text with one appendix pointer.
- Added Appendix E ("Extended limitations") carrying the full statement of each Discussion limitation
  (extraction share, roster currency and decode protocol, sample size and feature-definition sensitivity),
  which the main text now states in three shortened paragraphs with a single pointer.

## Page-limit directive: what moved and why

The initial assembly (all resolved content written in place, nothing moved) built to a main text that
spilled the Reproducibility statement onto the same page as the Conclusion. This was checked against a
clean rebuild of the unmodified `internal_review_version/main.tex` (byte-identical source, zero edits),
reading full per-page text rather than only searching for section-heading keywords: the source's page 10
was confirmed to contain the Discussion's remainder, the entire Conclusion (heading at character offset
1782 on that page, through its closing sentence), the Reproducibility statement, and the start of the
Ethics statement, all on one page — a finding reproduced identically across two independent clean rebuilds
run in different turns of this session, once resolving an apparent page-count mismatch between two
counting methods (`pypdfium2`'s page count and a naive form-feed split of `pdftotext` output, which differ
by exactly one because the latter's trailing form feed produces a spurious empty final "page"; filtering
empty splits reconciles the two to the same count and the same per-page content). An earlier finding from
this session had reported a clean 9/10 split for the same source document; that finding was based on a
per-page check that tested only for the presence of the strings "Discussion" and "Reproducibility
statement" without checking where the Conclusion heading itself fell, and it did not survive the full
per-page text reading done here — the Conclusion heading is on page 10 of the unmodified source, not page
9. Regardless of the source's own layout, the applicable bar for revised_new is the "9 pages of main text"
submission limit itself, i.e., the last main-text content (the Conclusion) must not run past the bottom of
page 9 of the *revised* build. Several rounds of trimming and appendix moves were required to reach that.
Per the directive, material was moved — never cut — in the stated order of preference:

1. **View-count sweep and the rest of §4.4 (Render conventions)**: moved first, matching the directive's
   top preference. The full per-subset-size table, the render-protocol-intervention table, the two named
   aggregate exceptions in the monotone check, the phantom-excess numbers by view count, the per-comparison
   power/minimum-detectable-difference statement, and the occluder-classification detail all moved into a
   single consolidated Appendix D. The main text now states all four render-convention findings (camera
   angle, tiling, view count, occlusion) at headline level in one paragraph with a single pointer to the
   appendix for the full statement, table, and mechanism.
2. **Tabular-classifier detail**: the twelve-reading sensitivity table and the invariance justification
   moved to Appendix B; the main text (05_discussion) keeps the headline range (183–188 of 210) and the
   canonical-form justification in one sentence, with a pointer to the appendix.
3. **Discussion limitations**: the full statement of each of the three remaining Discussion limitations
   (extraction share and its gate-failure numbers, roster currency and decode protocol, sample size and
   feature-definition sensitivity) moved to a new Appendix E; the main text keeps one shortened paragraph
   per limitation with a single pointer.
4. Minor compression (without moving) was also applied in 03_method's certified-labels/source-structures
   paragraphs and in 07_statements' Compute/What-is-not-recorded paragraphs, tightening phrasing without
   dropping any required value.
5. No figure floats were relocated relative to where the source placed them (one in 04_results, five in
   the appendix) — the four render-convention findings above moved as prose/table detail, not as float
   moves. Section 3's proof-level derivation and the introduction/related-work/conclusion sections were
   not touched, since the needed compression was reached without them.

Every moved table and every occurrence of moved prose is still cited from the main text at the point the
finding is first stated, so no appendix material is orphaned. The ceiling result, the fabrication finding,
and the attribution ladder table were not touched by any of these moves, per the directive.

**Page count after all moves:** main text (Introduction through Conclusion) completes on page 9;
Reproducibility, Ethics, and AI-use statements occupy page 10; References begin page 11; total 20 pages.
Verified by extracting text per page from the built PDF and confirming the Conclusion's final sentence and
the "Reproducibility statement" heading fall on pages 9 and 10 respectively, with no main-text content
appearing on page 10.

## Build

```
PATH=/Users/jp/.claude-science/conda/envs/rc-latex/bin:$PATH HOME=/tmp/rc_texhome \
  tectonic --bundle /tmp/tldir --keep-logs main.tex
```
run from `manuscript/revised_new/`, four TeX passes plus one BibTeX pass (standard for a fresh build with
citations). Final build: exit code 0.

- Errors: 0
- Undefined references: 0 (`grep -c "??" ` on the extracted text: 0)
- Undefined or multiply-defined citations: 0
- Overfull boxes: 0 (only cosmetic underfull-vbox/hbox spacing warnings and Times font-shape substitution
  notices, both routine tectonic/LaTeX noise unrelated to content)
- Total pages: 20 (confirmed independently by pypdfium2 page count and by counting form-feed characters in
  the `pdftotext` extraction)
- Main text (Introduction through Conclusion): pages 1–9. Verified directly against the extracted PDF text:
  page 9's final content is the Conclusion's last sentence ("...The method transfers to any modality whose
  forward rendering is known and invertible."), and no main-text section heading or body text appears on
  page 10.
- Reproducibility / Ethics / AI-use statements: all three begin and complete on page 10 (excluded from the
  9-page limit, as ICLR 2027 allows). Verified directly: page 10 begins with the "Reproducibility
  statement" heading and contains the strings "Ethics statement" and "AI use statement".
- References: begin page 11 (verified: page 11's first content is the "References" heading).
- Appendix: follows references, unlimited length.

## Revision-vocabulary scan

Case-insensitive scan for `now|previously|correct(ed|ion)?|revis(e|ed|ion)|update[ds]?|chang(e|ed|es)|
response|reviewer|earlier|retire[ds]?|retract|withdraw|non-recover|blocking|we have added|this version`
across every `.tex` file in the tree (sections and main.tex). Remaining hits, each judged in context:

- "Neither correction reaches the models" / "protocol corrections reach the models" (04_results,
  01_introduction) — "correction" here names the two render-protocol interventions (off-axis cameras,
  tiled geometry) defined in Table 2, a technical term for the experimental manipulation, not a manuscript
  revision.
- "change conclusions" (01_introduction, citing `ceilingart2605`) — describes how assumed ceilings being
  wrong can change a reader's conclusions; not a self-referential revision statement.
- "changes no classification" / "changes several" (04_results, A_appendix, in the occlusion-control
  caption and prose) — describes whether removing occlusion changes the oracle's classification output, a
  measured experimental outcome, not a manuscript edit.
- "correct counts" (A_appendix, run-to-run spread procedure) — "correct" as in "number of correct
  predictions," a scoring term.
- "enumeration order cannot change the accepted set" (A_appendix, proof of Theorem 1a) — a mathematical
  invariance statement.

No hit references a review, a reviewer, a prior draft, a retraction, or discloses that any revision took
place. Separately confirmed zero occurrences of `textcolor`, `REDFLAG`, or `rebuttal` anywhere in the tree,
and confirmed `\iclrfinalcopy` remains commented out in `main.tex`.

## Deliverables

- `main.tex`, `sections/*.tex` (8 files), `references.bib`, `iclr2027_conference.sty`,
  `iclr2027_conference.bst`, `natbib.sty`, `fancyhdr.sty`, `math_commands.tex`, `figures/*.pdf` (6 files,
  unchanged) — the complete submission tree.
- `main.pdf` — 20-page build, 9-page main text, clean (0 errors / undefined refs / undefined citations /
  overfull boxes).

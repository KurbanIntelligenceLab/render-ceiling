# Scripts

Every script the reported numbers depend on. The `a4_*` family (19 files) is EXCLUDED — it belongs to a
separate text-reasoning study cited nowhere in this paper.

## Top level

| script | used for |
|---|---|
| `analyze_cp7b.py` | CP7b certification |
| `build_e2_dataset.py` | CP2 SFT data |
| `build_expert_packet.py` | CP11 expert packet (unrun) |
| `detect_atoms.py` | CP19 atom detection |
| `enrich_e7.py` | CP7 enrichment |
| `eval_e2.py` | CP2 eval |
| `eval_e3.py` | CP3/CP12 arm evaluation |
| `extract_cell.py` | CP17 extractor |
| `fetch_e3_structures.py` | data fetch |
| `finish_cp18.py` | CP18 eval expansion |
| `probe_frontier.py` | CP14/CP26/CP35/CP41/CP54 frontier + zero-shot arms |
| `render_e3.py` | render pipeline |
| `run_cp31_conditions.py` | CP31 visibility-corrected oracle |
| `run_cp52_r2.py` | CP52 rung R2 |
| `run_cp58_transplant.py` | CP58 perception transplant |
| `run_e0.py` | CP0 pipeline build |
| `run_e05_oracle.py` | CP0b identifiability + the frozen box-sufficiency predicate |
| `run_e1_zeroshot.py` | CP1 zero-shot |
| `run_e7_tts.py` | CP7 test-time scaling |
| `score_e7.py` | CP7 scoring |
| `score_expert.py` | CP11 expert study (unrun) |
| `test_reward_text.py` | reward function tests |
| `train_alignn_cpu.py` | CP8 ALIGNN baseline |
| `train_alignn_e8.py` | CP8 ALIGNN |
| `train_e2_lora.py` | CP2 SFT training |
| `train_e3_grpo.py` | CP3 GRPO training |
| `train_e8_gnn.py` | CP8 coordinate GNN |
| `verify_manuscript_numbers.py` | the verification gate |

## `src/cocr/` — the importable package

| module | contents |
|---|---|
| `__init__.py` | package init |
| `audit.py` | label audits |
| `avspo.py` | AVSPO |
| `data.py` | dataset assembly |
| `labels.py` | symmetry labelling, tolerance sweep, quarantine |
| `reconstruct.py` | the geometric oracle — camera inversion and symmetry recovery |
| `render.py` | the frozen five-camera render protocol |
| `reward.py` | GRPO reward |
| `reward_text.py` | text reward (shared with the A4 line) |
| `traces.py` | chain-of-thought trace construction |
| `zeroshot.py` | zero-shot prompting |

## Figure scripts

`figures/` regenerates the three figures this project built last, each reading its checkpoint's
`results.json` so a changed number propagates to the figure rather than drifting from it:

| script | figure | reads |
|---|---|---|
| `figures/make_fig3_noimage.py` | `noimage.png` | CP41 no-image control |
| `figures/make_fig4_cuesuff.py` | `cuesuff.png` | CP35 cue-sufficiency contrast |
| `figures/make_fig5_generational.py` | `generational.png` | CP36 generational comparison |

    python scripts/figures/make_fig3_noimage.py <ledger_dir> manuscript/figs/noimage.png

Each reproduces its shipped figure byte-for-byte, which `validate_package.py` checks. The other two
manuscript figures (`ladder.png`, `leaderboard.png`, `conditions.png`) were produced inside their
checkpoints' analysis runs and are shipped as files; their source data is in `results/`.

## Building the merged document

    python scripts/build_si.py . reports/SUPPLEMENTARY_INFORMATION.md

Assembles the single document readers should start from: Part I the narrative report, Part II the
supplementary sections (regenerated inline, so this document cannot drift from its own generator), Part III
the reviewer questions, Part IV every checkpoint's pre-registration and finding read from `results/CP*/`.
Each Part IV section opens with a BACKED BY line naming the results files that checkpoint's claims come
from; all 90 JSON records are pointed at and none is orphaned. Validator check 13 compares the shipped file
byte-for-byte against a fresh build.

## Building the supplementary sections alone

`build_supplementary.py` writes `reports/sources/SUPPLEMENTARY_SECTIONS.md` (S1-S14). `build_si.py`
imports and calls it in process, so the merged document and the standalone sections are produced by ONE
command and cannot disagree; run this directly only if you want the sections without the merged document.

## Validating the package

    python scripts/validate_package.py .

Eighteen numbered checks across 23 assertions: folder structure and README counts (1), every checkpoint
carries a finding (1b), figure resolution (2), reference and label integrity (3), placeholder survival (4),
numeric traceability of every manuscript value to a `results.json` (5), SI coverage of every checkpoint (6),
byte-reproduction of every scripted figure (7) with no manuscript figure lacking a script (7b), absence of
provisional (8) or unrelated (9) files, SI Part I equal to `REPORT.md` verbatim (10), the LaTeX linter (11),
the prose gate (12), the shipped SI equal to what `build_si.py` produces from the current `results/` (13),
and every retained `*_snapshot.md` earning its exemption by being cited or by its finding declaring the
supersession it documents (13b). Two later additions: every file filed under `reports/sources/` must have
its content actually present in the merged document (13c) — a claim that was once made for a file it was
untrue of — and compiled bytecode is reported as a WARNING rather than a failure (8b), because running the
validator imports the figure modules and so creates the very `.pyc` files a hard check would flag.

Exit 0 means complete and self-consistent. EVERY CHECK HAS BEEN TESTED AGAINST A DELIBERATE VIOLATION OF
THE RULE IT ENFORCES — three were found to crash or silently pass rather than report, and were fixed.
Check 13 exists because the shipped SI was once stale against its own generator and a line-count glance
did not catch it; it compares bytes.

## Running them

Scripts import `cocr` from `src/`, so run with `PYTHONPATH=scripts/src` from the package root, or copy
`src/cocr` beside them. Dependencies: pymatgen, spglib, ase, scikit-learn, scipy, matplotlib, numpy.
Model arms additionally need an OpenRouter key in `OPENROUTER_API_KEY`; data fetch needs `MP_API_KEY`.

`verify_manuscript_numbers.py` is the gate: it refuses any manuscript sentence carrying a value absent
from the checkpoint records, or an accuracy stated without its sample and decode budget.

ONE CAVEAT ON THE ORACLE PREDICATE. `run_e05_oracle.py::_metric_system` hardcodes tol=1e-2 and 0.5 degrees,
which gives a 144/66 box-sufficiency split. The CANONICAL partition used throughout the paper is 2e-2 and
1.0 degrees, giving 140/70. Passing the canonical tolerances reproduces the recorded split exactly,
composition-identical across all five metric classes; running the file at its defaults does not.
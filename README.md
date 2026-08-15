# render-ceiling

**A model-free ceiling for vision–language model evaluation on rendered crystal structures**

[![License: MIT](https://img.shields.io/badge/code-MIT-blue.svg)](LICENSE)
[![Data: CC BY 4.0](https://img.shields.io/badge/data-CC%20BY%204.0-lightgrey.svg)](LICENSE-DATA)

Can Polat,^a Mustafa Kurban,^*bc Erchin Serpedin,^a and Hasan Kurban^*d

^a Department of Electrical and Computer Engineering, Texas A&M University, College Station, Texas, USA
^b Department of Prosthetics and Orthotics, Ankara University, Ankara, Turkey
^c Department of Electrical and Computer Engineering, Texas A&M University at Qatar, Doha, Qatar
^d College of Science and Engineering, Hamad Bin Khalifa University, Doha, Qatar

\* Corresponding authors: kurbanm@ankara.edu.tr, hkurban@hbku.edu.qa

Submitted to *Digital Discovery* (Royal Society of Chemistry).

## Abstract

A vision–language model that misreads a rendered crystal structure and one that misreasons about it produce the same wrong answer, and every existing method for separating them puts a second model in the loop. When a benchmark is built by rendering a structure whose coordinates are known, no model is needed: inverting the known cameras and re-solving cross-view correspondence returns the answer the images support, a quantity we call the render ceiling. We characterise exactly when that ceiling reaches 1, by an emptiness condition on a set of geometric phantoms, and certify that the condition holds on 2160 structures drawn from the Materials Project, so every point of a model's deficit is attributable to the model. Used as the top rung of an attribution ladder over fourteen vision–language models under a frozen evaluation protocol, the ceiling reverses the prevailing explanation of multimodal failure: supplying exact geometry as text lifts every model but closes the minority of the gap, leaving 13 of 14 limited more by what survives perception than by perception itself. The same instrument catches what a leaderboard cannot: a strong model used as the structure-extraction stage emits syntactically perfect coordinates whose median recall against ground truth is zero, a fabrication downstream accuracy would score as bad reasoning. The construction transfers to any benchmark whose forward rendering is known and invertible, and it returns design rules for benchmark builders: which camera placements are robust to extraction noise, and the tolerance at which a pipeline's own reading, not the images, becomes the binding ceiling.

The manuscript source is not distributed here — the article is the journal's to publish — but the code that
produces every figure in it is, under `docs/manuscript/codes/`, together with the records those figures are drawn
from.

## What is in this repository

The code implementing the geometric oracle, the render protocol, the labelling pipeline and every analysis
reported in the article, together with the released artifact: the render protocol, the labelling tolerances
and sweep, the feature specification and seed for the cell-metric reference, the verbatim model prompts, the
per-model raw request and response logs with model identifiers and generation dates, and per-structure
predictions for every arm reported. Every accuracy in the article recomputes from those released vectors
without API access.

Three results orient the rest. With the extraction tolerance tied to the symmetry tolerance the oracle
returns every label, so the ceiling is exactly 1.0000 and every point of a model's deficit is attributable
to the model; read at the released merge tolerance the same pipeline gives 0.9524, and the article reports
both, because a ceiling quoted without the tolerance that produced it is not a measurement. Supplying exact
geometry as text lifts every model and closes the minority of the gap: the median perception share of the
deficit is 0.2901 and 13 of 14 models are limited more by what survives perception than by perception
itself. And a strong model used as the extraction stage emits syntactically perfect coordinate lists whose
median recall against ground truth is zero, a fabrication that downstream accuracy alone would have scored
as bad reasoning.

## Layout

| path | contents |
|---|---|
| `docs/manuscript/codes/` | one generator per article figure, plus the shared style module; see its README for the placement-width and panel conventions |
| `results/` | 54 experiment records: 99 JSON records and 92 markdown records (every pre-registration and finding) |
| `results/INDEX.json` | run order of those records, whose directory names describe what each measures rather than when it ran |
| `docs/reports/` | `SUPPLEMENTARY_INFORMATION.md`, the single merged document, plus `REPORT.md` (its Part I), `CONVENTIONS.md` (standalone), and `sources/` holding the two documents it is built from |
| `data/` | 13 files: structures, labels and evaluation splits for all three samples (20 MB) |
| `scripts/` | 36 top-level scripts and the 11-module `src/cocr` package |
| `release/` | 82 files: per-structure prediction vectors, frozen prompts, Croissant metadata |
| `weights/` | trained LoRA adapters for the fine-tuned arm, git-ignored and not distributed here; available from the corresponding authors on request, with the manifest and sha256 in `weights/README.md` |

The rendered images the models read are not committed. They are a build product: 2,100 PNGs, five
orthographic views for each of the 420 evaluation structures, and a pure function of inputs that are here.
Rebuild them from the CIFs with no API key and no network:

    python scripts/render_from_cifs.py --sample e3  --split eval
    python scripts/render_from_cifs.py --sample e3x --split eval

Each writes to the paths the `images` field of the corresponding `eval.jsonl` already names and then
verifies that every one of them resolves. The render is deterministic — the camera set and pixel size are
frozen constants and no stage draws a random number — so re-rendering a CIF reproduces its image. The
trained adapters are the other omission, distributed out of band for size. Neither is needed to reproduce a
number in the article: the per-structure prediction vectors in `release/predictions/` are the reproducible
artifact, and every accuracy recomputes from them.

Experiment records are named for what they measure rather than by checkpoint number. The numeric prefixes
that earlier versions used encoded run order, which `results/INDEX.json` now carries explicitly along with
each record's identifier in the project's own history.

This repository carries the submitted work and nothing else. Earlier drafts and the process documents that
served them — the assembly and internal-review logs, the working set for the exactness revision, the
reframing memo — have been retired rather than kept as history: every value they held is a field of a record
under `results/`, and their prose describes manuscripts that no longer exist. Dependencies are declared in
`pyproject.toml` and pinned in `uv.lock`: the base group reproduces the figures and the gates, and the
`pipeline`, `arms` and `baselines` extras name what re-running each stage of the pipeline needs.

## Reproducing

Nothing here is transcribed. Each command reads the records and rewrites its output:

    uv run python docs/manuscript/codes/make_fig2_ladder.py results ladder.pdf
    uv run python scripts/build_si.py . docs/reports/SUPPLEMENTARY_INFORMATION.md
    uv run python scripts/verify_manuscript_numbers.py
    uv run python scripts/validate_package.py .

`uv run` resolves the environment from `uv.lock` on first use, so no separate install step is needed; those
commands need only the base group (`numpy`, `scipy`, `matplotlib`). Re-running the pipeline itself —
rendering, labelling, scoring the oracle, the model arms — needs the extras:

    uv sync --extra pipeline      # rendering, labelling, oracle scoring
    uv sync --extra arms          # fine-tuning and inference for the model arms
    uv sync --extra baselines     # the external GNN baselines

Paths are repository-relative through `scripts/_paths.py`; override the root with `RENDER_CEILING_ROOT`.
Each generator takes a records directory and an output path, and writes a vector PDF with a pinned creation
date, so two runs of the same generator on the same records produce byte-identical files.

`validate_package.py` is the gate for the whole package and exit 0 means it is complete and internally
consistent. It runs all 6 figure generators, requires every four-decimal number in every prose document to
trace by value to a record under `results/`, requires every accuracy to carry its sample and decode budget,
and refuses the repository if the merged supplementary document differs by one byte from what its generator
produces from the current `results/`. A few checks read the manuscript source — that every figure it
references resolves, that its cross-references and citations resolve, that no placeholder survived, and that
each of its numbers traces to a record. Those run in the authors' working tree and report as skipped here.

Each of those checks was tested against a deliberate violation of the rule it enforces; three were found to
crash or silently pass rather than report, and were fixed. The staleness check compares bytes rather than
line counts because the shipped supplementary was once out of date against its own generator while a
line-count glance read as a pass.

Read `docs/reports/SUPPLEMENTARY_INFORMATION.md` first. It is the whole project in one file, in four parts: the
narrative report, the supplementary sections, reviewer questions answered from the records, and every
record's pre-registration and finding verbatim. Each section opens with a line naming the exact JSON files
its claims come from, so any number traces from prose to source without searching. The document is
generated, never edited by hand.

`docs/reports/CONVENTIONS.md` is the exception to that: it is standalone, not a build input, and not absorbed
anywhere. It records the program-wide statistical conventions the records were run under — how seed spread
is pooled, when a paired test is required, what an accuracy must carry — and several pre-registrations cite
it by name. None of its 225 substantive lines appears in the merged document.

## What is claimed, and what is not

Four claims the package supports:

1. A certified-label benchmark. Labels are generated rather than annotated, so the ground truth and the
   ceiling come from one source. On the kept set after a tolerance quarantine, agreement with the source
   database is 220/220, whose exact one-sided 95% lower bound is 0.9865 — quoted that way rather than as
   "100% accurate".
2. A model-free ceiling, measured on both evaluation samples, that no model arm approaches.
3. An attribution ladder whose outcome contradicts the perception-bottleneck reading it was built to test.
4. An extraction-fabrication result: a strong model emits syntactically perfect coordinate lists in which
   half the structures have not one atom within tolerance of a real one.

What is not claimed. No improvement over any prior fine-tuned arm; the best model arm here is single-seed
and sits inside the reference arm's own across-seed spread. No novelty for optimising a render protocol,
which has direct prior art. No causal claim for occlusion. The render-convention model probe is inconclusive
rather than null, since significance was unreachable in 7 of 16 paired comparisons at any outcome. No
human-expert baseline, which is a stated limitation rather than something the package chases.

Withdrawals, superseded values and defects found in this project's own work are in the supplementary
verbatim, not summarised. 47 of the 54 records carry numeric results; the rest are reasoned cuts and one
subsumed record, carrying a finding but no numbers. 26 carry a pre-registration written before the
corresponding numbers existed; the rest say so in their own finding text rather than implying one existed.

## Citation

See `CITATION.cff`. The code is released under the MIT licence (`LICENSE`) and the data, records and
released artifact under CC BY 4.0 (`LICENSE-DATA`). Source structures are drawn from the Materials Project,
which distributes its data under CC BY 4.0; attribution to the Materials Project is required for any reuse
of the structural data.

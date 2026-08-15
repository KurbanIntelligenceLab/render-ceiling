# REPRODUCE

Every figure, document and gate in this repository regenerates from `results/`. Nothing is transcribed.

## Environment

Dependencies are declared in `pyproject.toml` and pinned in `uv.lock`.

    uv sync                    # base: numpy, scipy, matplotlib — figures and gates
    uv sync --extra pipeline   # rendering, labelling, oracle scoring
    uv sync --extra arms       # fine-tuning and inference for the model arms
    uv sync --extra baselines  # external GNN baselines

`uv run python <script>` resolves the base group on first use, so the figure and gate commands below need no separate install step.

## Figure to generator to record

| figure | generator | record read |
|---|---|---|
| Fig 1 (teaser) | `TikZ, inline in section_introduction.tex` | `none — drawn from values in the text` |
| Fig 2 leaderboard.pdf | `docs/manuscript/codes/make_fig1_leaderboard.py` | `results/model_sweep/results.json` |
| Fig 3 ladder.pdf | `docs/manuscript/codes/make_fig2_ladder.py` | `results/rung_R3_coords_as_text/results.json` |
| Fig 4 noimage.pdf | `docs/manuscript/codes/make_fig3_noimage.py` | `results/no_image_control/results.json` |
| Fig 5 conditions.pdf | `docs/manuscript/codes/make_fig6_conditions.py` | `results/visibility_corrected_oracle/results.json` |
| Fig S1 cuesuff.pdf | `docs/manuscript/codes/make_fig4_cuesuff.py` | `results/stratified_frontier_expansion/results.json` |
| Fig S2 generational.pdf | `docs/manuscript/codes/make_fig5_generational.py` | `results/generational_comparison/results.json` |

Each generator takes a records directory and an output path:

    uv run python docs/manuscript/codes/make_fig2_ladder.py results ladder.pdf

Creation dates are pinned, so two runs on the same records produce byte-identical PDFs. All six generated figures were verified byte-identical against the shipped copies (sha256) on the tree as committed.

Note the numbering offset: the generators are named `make_fig1`–`make_fig6` in the order they were written, which is not the order the figures appear in the article. `make_fig1_leaderboard.py` produces Fig. 2, `make_fig2_ladder.py` produces Fig. 3, and `make_fig4`/`make_fig5` produce the two ESI figures.

## Documents

    uv run python scripts/build_si.py . docs/reports/SUPPLEMENTARY_INFORMATION.md

`SUPPLEMENTARY_INFORMATION.md` is generated; `docs/reports/REPORT.md` and the two files under `docs/reports/sources/` are its build inputs. Validator check 13 fails if the shipped merged document differs from what the builder produces from the current `results/`.

## Gates

    uv run python scripts/verify_manuscript_numbers.py   # every prose value traces to a record
    uv run python scripts/validate_package.py .          # 13 structural and provenance checks

Both pass on the tree as committed. The validator's hygiene scan skips git-ignored directories (`.git`, `.venv`, `to_be_deleted`, `__pycache__`), so a resolved uv environment in the tree does not fail the package. `validate_package.py` emits two expected warnings: unreferenced section labels (RSC house style cross-refers between article and ESI by literal number, since `\ref` cannot cross the two documents) and any compiled bytecode created by its own run.

## Manuscript

The manuscript source under `docs/manuscript/render-ceiling-dd/` is deliberately git-ignored — the article is the journal's to publish. The generators that produce its figures are tracked. Compile with a pdflatex-family engine; `main.tex` and `si.tex` are independent documents, and both currently build with zero undefined references.

## Frozen data

| path | contents |
|---|---|
| `data/e3/` | 1,820 structures, labels and splits — the original evaluation sample |
| `data/e3x/` | 210 structures — the expansion sample |
| `data/e50/` | 1,995 structures — the scaled sample behind the n=1933 frontier readings |
| `release/predictions/` | per-structure prediction vectors for every arm; every accuracy in the article recomputes from these without API access |

Rendered images are not committed. They are a deterministic build product: `uv run python scripts/render_from_cifs.py --sample e3 --split eval`.

## Open provenance gap

`data/e50/` is not written by any script in `scripts/`, and no script or record names the directory. Its role is inferable — 1,995 structures, and `results/option_a_frontier/results.json` labels its sample "e50 neighborhood-stable subset" for the n=1933 frontier rows — but the fetch or filter step that produced it is not in the tree. It is kept for that reason and the gap recorded here rather than resolved.

The trained LoRA adapters under `weights/` are git-ignored and not distributed with this repository; they are available from the corresponding authors on request. `weights/README.md` carries the manifest and sha256.

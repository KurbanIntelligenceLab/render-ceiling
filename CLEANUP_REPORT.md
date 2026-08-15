# CLEANUP REPORT

All sizes are apparent size — the sum of file bytes, excluding `.git` and the uv-created `.venv`. MiB means bytes/2^20.

## Headline

The repository was not the problem the request assumed. `weights/all_adapters_weights.tar.gz` is 2,822,645,275 bytes, 98.7% of the 2,858,511,922-byte worktree, and it is git-ignored — so no amount of archiving working files changes the total. It stays in place by decision.

What the survey actually found was two defects worth more than any space saving:

1. `docs/` was ignored wholesale in `.gitignore`, so the six figure generators and the merged Supplementary Information — both of which the README states are distributed here — were outside version control. 12 files, 0 tracked.
2. The `docs/` refactor left the repo's own tooling pointing at pre-refactor paths. `scripts/validate_package.py` crashed with `FileNotFoundError` on `manuscript/codes`; `build_si.py` and `verify_manuscript_numbers.py` read `reports/` paths that no longer existed. The validator could not run at all.

Both are repaired. The validator now passes and the prose gate reports zero unmatched values across all four prose documents.

A third defect surfaced from the packaging change itself: `validate_package.py`'s hygiene scan (check 8) walked the whole working tree, so the `uv`-created `.venv` failed a clean package on its own dependencies — a numpy wheel ships `pyinstaller-smoke.py`, which matched the scratch-file pattern. The scan now skips `.git`, `.venv`, `venv`, `to_be_deleted`, `__pycache__` and `node_modules`, all of which are git-ignored and never published.

## Verified before anything was touched

| check | result |
|---|---|
| Manuscript float dependencies resolved | 23 of 23, zero missing |
| Figure generators reproduce shipped PDFs | 6 of 6 byte-identical (sha256), run into scratch, shipped figures untouched |
| Scripts traced to the records they write | 36 of 36 accounted for |

## What was staged to `to_be_deleted/`

| group | files | bytes | rationale |
|---|---|---|---|
| `build_artifacts/` | 3 | 71,873 | `main.log`, `si.log`, `main.blg` — LaTeX build output, regenerated on every compile |
| `unused_template_assets/` | 3 | 564,217 | `RSC_LOGO_CMYK.eps`, `RSC_pub.pdf`, `RSC_LOGO_CMYK_blank_original.pdf.bak` — no `\includegraphics` or `\input` in any `.tex` references them. Both documents were recompiled without them: 11 pages each, extracted text identical to the shipped PDFs |
| `superseded_packaging/` | 2 | 936 | `requirements.txt`, `requirements-full.txt` — replaced by `pyproject.toml` + `uv.lock` |
| total | 8 | 637,026 | |

## What was deleted outright (to Trash, recoverable)

| path | rationale |
|---|---|
| `.DS_Store`, `docs/manuscript/.DS_Store` | OS metadata; trips validator check 8. Could not be staged — the validator walks `to_be_deleted/` too |
| `docs/manuscript/codes/__pycache__/`, `scripts/__pycache__/` | Compiled bytecode created by my own validator and figure-regeneration runs this session. My by-product, not repo content, and reported separately from the cleanup for that reason |

## What was NOT removed, and why

The request was to cut aggressively anything not directly serving the manuscript. Measurement did not support that for three groups:

- **`scripts/` — all 36 kept.** Every script either writes a `results/` directory the manuscript depends on or is named in the Supplementary Information. `render_e3.py` was the only candidate with neither, and it renders `data/e3` under the frozen view set, which the Data availability statement promises by name.
- **`results/` — all 54 records kept.** The validator's check 6 requires every record to appear in the SI, and all 54 do. Absence of a record's values from the manuscript text is not evidence of disuse: the manuscript quotes aggregates, and the per-structure arrays those reduce are expected to be absent from prose.
- **`docs/reports/` — kept in full.** `REPORT.md` and the two files under `sources/` are build inputs to `SUPPLEMENTARY_INFORMATION.md`; validator checks 10 and 13c compare them byte-for-byte. `CONVENTIONS.md` is standalone and is the record of a program-wide statistical convention change.

The pre-existing `to_be_deleted/` contents (6 experiment records, 2 report sets, 2 scripts, 238,114 bytes) were left exactly as they were. They were staged by an earlier pass with its own documented rationale in `to_be_deleted/README.md`.

## Packaging: pip to uv

`requirements.txt` and `requirements-full.txt` are replaced by `pyproject.toml` with a pinned `uv.lock` (141 packages resolved). The three commented-out dependency groups in `requirements-full.txt` are now real, installable extras:

| group | contents |
|---|---|
| base | numpy 2.4.6, scipy 1.17.1, matplotlib 3.11.0 — figures and gates |
| `pipeline` | pymatgen, spglib, ase, Pillow, mp-api |
| `arms` | torch, transformers, peft, trl |
| `baselines` | dgl, alignn, jarvis-tools |

Verified: `uv sync` installs the base group, and `uv run python docs/manuscript/codes/make_fig2_ladder.py results out.pdf` reproduces the shipped `ladder.pdf` byte-identically.

## Version control

`.gitignore` changed from a blanket `docs/` to:

    docs/manuscript/render-ceiling-dd/
    !docs/manuscript/codes/

The manuscript source stays ignored deliberately — the article is the journal's to publish. `git add --dry-run --all` now stages 22 paths: the 7 figure generators and their README, the 5 report documents, `pyproject.toml`, `uv.lock`, the 3 repointed scripts, the updated `README.md` and `.gitignore`, and the removal of the two requirements files. The manuscript source and `to_be_deleted/` are both absent from that list, as intended.

## Size accounting

| entry | before (bytes) | after (bytes) | delta |
|---|---|---|---|
| `.DS_Store` | 22,532 | 0 | -22,532 |
| `.gitignore` | 160 | 212 | +52 |
| `README.md` | 11,902 | 12,405 | +503 |
| `REPRODUCE.md` | 0 | 4,640 | +4,640 |
| `docs` | 3,093,127 | 2,440,649 | -652,478 |
| `pyproject.toml` | 0 | 920 | +920 |
| `requirements-full.txt` | 652 | 0 | -652 |
| `requirements.txt` | 284 | 0 | -284 |
| `scripts` | 364,724 | 364,814 | +90 |
| `to_be_deleted` | 238,114 | 875,140 | +637,026 |
| `uv.lock` | 0 | 809,809 | +809,809 |
| **total** | 2,858,511,922 | 2,859,289,016 | +777,094 |
| **files** | 419 | 420 | +1 |

The worktree grew by 777,094 bytes. That is `uv.lock` (809,809 bytes) plus the staged files still sitting in `to_be_deleted/`, which is git-ignored and not part of the published package. Reclaiming space was never available here: 98.7% of the tree is one git-ignored tarball that stays by decision.

`.git` pack is 8,128,512 bytes. The largest blobs in history are all still in the worktree (`data/e50/labels_sidecar.json`, `data/e3/structures.json`, `results/visibility_corrected_oracle/per_view_masks.json`), so there is no dead weight a history rewrite would remove.

## Restoring

Staged files: move them back from `to_be_deleted/<group>/` to the paths in the table above. Deleted files are in the system Trash under their original names.

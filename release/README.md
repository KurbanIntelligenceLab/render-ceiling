# CoCr-Symmetry — artifact release

Everything a reviewer needs to check every number in the paper without rerunning a model.

## What resolves from a DOI

`croissant.json` — MLCommons Croissant 1.1 metadata, validated with the official `mlcroissant` library
(distribution of 7 file objects/sets, one record set, seven fields, SHA-256 per file object). Its `url`
currently points at the source repository; replace it with the dataset DOI at deposit. Licence: CC BY 4.0.

Payload to deposit alongside it:
  data/e3/eval.jsonl              210 evaluation records, original composition-exclusion split
  data/e3/train.jsonl            1610 training records, composition-disjoint from eval
  data/e3/structures.json         CIF text per material_id
  data/e3x/eval.jsonl             210 independently drawn records, replication split
  data/e3x/structures.json        CIF text for the expansion split
  data/e3/renders/eval/           1050 PNGs, five orthographic views per structure at 768 px
  data/e3x/renders/eval/          1050 PNGs, identical camera set

## What is in this folder

`harnesses/` — the oracle, the orbit-occlusion classifier and conditioned oracle, the zero-shot and
no-image control harness, the atom detector, and the render, reconstruct and label modules.

`predictions/` — 32 per-structure prediction vectors, one file per model per arm, with ARM AND K IN THE
FILENAME. Every leaderboard row in the paper is recomputable from these without an API key.

`frozen_prompts.json` — the prompt text VERBATIM. There is exactly one distinct prompt string; the
no-image control sends it byte-identically with only the image blocks removed.

`classifier_specifications.json` — the random forest's executable specification: ordered 19-feature list
with definitions, hyperparameters, library versions, split sizes, and the per-structure prediction vector.
A clean-room refit from this file alone reproduces 188/210, which is why 0.8952 is the canonical value and
the two historical figures are retired.

`claim_provenance.json` — one row per asserted sentence in the paper, naming the file, the field, the
sample, K, the seed count and the statistical test. One row is flagged: the label-correctness bound lives
in prose in an early checkpoint rather than in a results.json, and is marked as such rather than presented
as structured data.

`superseded_results.json` — the retired values as DATA, not only as prose: the 137/73 stratified table,
the mechanism claim, the reverse-direction arm, the per-view visibility figure, the retired occlusion
decomposition, and the two retired random-forest values, each with why it was superseded and what replaced it.

## Reproducing the two headline results without a GPU or an API key

The oracle is deterministic and CPU-only. `harnesses/oracle_harness.py` reconstructs atom positions from
the frozen camera set and runs spglib on the result; it reproduces 200/210 on the original evaluation set
and 191/210 on the expansion set. `harnesses/orbit_occlusion_and_conditioned_oracle.py` reproduces the
four visibility conditions, including the result that removing informative occlusion changes no
classification while the redundant-only control changes 6 and 21.

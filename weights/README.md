# Trained adapter weights

Not distributed in this repository. Available from the corresponding authors on request.

`all_adapters_weights.tar.gz` — 2.82 GB compressed, 3.23 GB unpacked, 25 LoRA adapters over
`Qwen/Qwen3-VL-8B-Instruct`. Adapter size splits by family: the 12 supervised adapters are 174.7 MB
each, the 13 reinforcement-learning adapters 87.4 MB each, the latter stage having used a smaller
rank.

    sha256  c0406249424a14ad894fbf27ca819dfe88700c0d94914ac25fdeca8329766411

That checksum was recorded on the training host at archive time, and the authors' copy was verified
against it after transfer. Verify again before trusting the file:

    shasum -a 256 all_adapters_weights.tar.gz

## What is in it

| family | arms | contents |
|---|---|---|
| supervised matrix | 12 | the direct-answer, short-chain and full-chain arms at seeds 0/1/2 |
| reinforcement pilot | 4 | the outcome-reward and two step-reward arms at seed 0, plus one test run |
| reinforcement matrix | 9 | the outcome-reward and two step-reward arms at seeds 0/1/2 |

## The arm the paper cites is not in this archive

The paper reports 0.6905 for the strongest model arm, and the `sota_push` record holds the same
adapter at 139/210 = 0.6619 under a smaller decode budget. That arm was trained at native resolution
with six augmentation cameras, writing to a directory that was never archived. The unaugmented
predecessor is present, but it is not the cited checkpoint.

What survives for the cited arm instead: its training command and accuracy with confidence interval
in `results/sota_push/results.json`, the training split in `data/primary/train.jsonl`, and its
per-structure predictions under `release/predictions/`. The number is therefore checkable and the arm
is retrainable, but the exact trained checkpoint is gone and retraining is stochastic.

## Loading one

    tar -xzf all_adapters_weights.tar.gz <family>/<arm>
    # then, against the base model:
    #   PeftModel.from_pretrained(base, "<family>/<arm>")

## Supervised pixel baseline

Two checkpoints from the `supervised_pixel_baseline` record: a ResNet-50 (94.4 MB) and a small ViT
(86.7 MB), both trained from ImageNet initialisation directly on the benchmark's own 1610 training
renders at seed 23. These are the vision-only models the paper compares against; the stronger reads
the same images at 0.8952. Their sha256 checksums, class order and load snippets are in
`results/supervised_pixel_baseline/weights_manifest.json`.

## Why none of it is committed

Large binaries do not belong in git history, and the tarball exceeds the 100 MB blob limit besides.
`weights/` is ignored by `.gitignore` apart from this file. Nothing in the release depends on the
weights: every accuracy recomputes from the per-structure prediction vectors in `release/`.

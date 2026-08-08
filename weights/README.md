# Trained adapter weights

`all_adapters_weights.tar.gz` — 2.82 GB compressed, 3.23 GB unpacked, 25 LoRA adapters over
`Qwen/Qwen3-VL-8B-Instruct`. Adapter size splits by family: the 12 supervised adapters are 174.7 MB each,
the 13 GRPO adapters 87.4 MB each — the RL stage used a smaller rank.

    sha256  c0406249424a14ad894fbf27ca819dfe88700c0d94914ac25fdeca8329766411

That checksum was recorded on the training host at archive time, and this copy was verified against it
after transfer. Verify again before trusting the file:

    shasum -a 256 all_adapters_weights.tar.gz

## What is in it

| family | arms | contents |
|---|---|---|
| `adapters/` | 12 | B1, B2, V1, V1b at seeds 0/1/2 — the supervised fine-tuning matrix |
| `adapters_e3/` | 4 | B3, V2a, V2b at seed 0, plus one `V2a_s0_test` — the GRPO pilot |
| `adapters_e3m/` | 9 | B3, V2a, V2b at seeds 0/1/2 — the full GRPO matrix |

## THE ARM THE MANUSCRIPT CITES IS NOT IN THIS ARCHIVE

The manuscript reports `0.6905` at K=8 for the strongest model arm, and `results/CP12_sota_push/` records
the same adapter at `139/210 = 0.6619` at K=3. That arm is called A3 in the records, and its training
command wrote to `adapters_a3/B1_aug_s0` — a directory that does not appear in this tarball and was not
archived anywhere. A3 is the B1 recipe retrained at native resolution with six augmentation cameras, so
`adapters/B1_s0` here is its UNAUGMENTED predecessor, not the cited checkpoint.

What survives for the cited arm instead: its training command in `results/CP12_sota_push/finding.md`,
the trainer `scripts/train_e2_lora.py`, the training split `data/e3/train.jsonl`, its per-structure
predictions under `release/predictions/`, and its accuracy with confidence interval in
`results/CP12_sota_push/results.json`. The number is therefore checkable and the arm is retrainable, but
the exact trained checkpoint is gone and retraining is stochastic.

## Do not commit this to git

GitHub rejects any blob over 100 MB. The tarball is 2.82 GB, so it is refused outright; unpacking does not
help, because the 12 supervised adapters are 174.7 MB each and also exceed the limit. (The 13 GRPO adapters
at 87.4 MB would individually fit, but 25 large binaries do not belong in git history regardless.)
Publish the weights through a release asset, Zenodo, or the Hugging Face Hub, and add
`weights/` to `.gitignore` when the repository is initialised. `scripts/validate_package.py` does not
count this directory, so the repository still validates whether or not the weights are present.

## Loading one

    tar -xzf all_adapters_weights.tar.gz adapters_e3m/V2b_s0
    # then, against the base model:
    #   PeftModel.from_pretrained(base, "adapters_e3m/V2b_s0")

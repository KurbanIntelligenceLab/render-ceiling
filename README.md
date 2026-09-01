# render-ceiling

**Can a multimodal evaluation tell whether a model misread an image or misreasoned about it?**

Can Polat<sup>1</sup> ([0000-0002-1458-302X](https://orcid.org/0000-0002-1458-302X)),
Mustafa Kurban<sup>2,3</sup> ([0000-0002-7263-0234](https://orcid.org/0000-0002-7263-0234)),
Erchin Serpedin<sup>1</sup> ([0000-0001-9069-770X](https://orcid.org/0000-0001-9069-770X)),
Hasan Kurban<sup>4</sup> ([0000-0003-3142-2866](https://orcid.org/0000-0003-3142-2866))

<sup>1</sup> Department of Electrical and Computer Engineering, Texas A&M University, College Station, Texas, USA
<sup>2</sup> Department of Prosthetics and Orthotics, Ankara University, Ankara, Turkey
<sup>3</sup> Department of Electrical and Computer Engineering, Texas A&M University at Qatar, Doha, Qatar
<sup>4</sup> College of Science and Engineering, Hamad Bin Khalifa University, Doha, Qatar

Corresponding authors: kurbanm@ankara.edu.tr, hkurban@hbku.edu.qa

## Abstract

Multimodal evaluations cannot say whether a vision–language model misread an image or misreasoned
about it, because every existing method for separating the two places a second model in the loop. We
introduce the render ceiling, a model-free reference for benchmarks built by rendering known objects:
inverting the frozen cameras and re-solving cross-view correspondence recovers exactly the answer the
images support. We prove the ceiling fails only through an enumerable set of projection coincidences
and certify that set empty on 2,160 rendered crystal structures, so every point of a model's deficit
belongs to the model. Across fourteen vision–language models, supplying exact geometry as text lifts
every model yet closes under half the gap for thirteen, while a supervised vision model with no
language component reads the same images at 0.8952, above every vision–language model. The instrument
exposes extraction-stage fabrication that downstream accuracy would misattribute to reasoning, yields
camera-placement rules for benchmark builders, and transfers to any benchmark with an invertible
forward rendering.

This repository is the release the paper refers to: the package that implements the oracle and the
render protocol, the structures and labels it reads, and one machine-readable record behind every
number the paper reports.

## Installation

Requires Python 3.11 or newer and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

There is no `requirements.txt` and no `pip install` path. `uv.lock` is committed, so the environment
resolves to the same versions that produced the release.

## Verifying the release

The cheapest path, and the one to run first:

```bash
uv run render-ceiling verify
```

It checks that every one of the 64 records carries a `results.json`, that all 134 record files and
the released prediction vectors parse, that `results/INDEX.json` lists exactly the records on disk,
that every four-decimal number stated below traces by value to a record, and that nothing shipped
points at a document that is not shipped. `--strict` turns warnings into failures.

The verifier imports nothing from the rest of the package, deliberately: a claim and the code that
re-derives it must not be able to fail together.

## What is here

| path | contents |
|---|---|
| `src/render_ceiling/` | 7 modules: the render protocol, the geometric oracle, the labelling pipeline, and the verifier |
| `data/` | 13 files: structures, labels and evaluation splits for the three samples |
| `results/` | 64 records, one directory each, 134 JSON files; `INDEX.json` gives the order they ran in |
| `release/` | 82 files: per-structure prediction vectors, frozen prompts, Croissant metadata |
| `tests/` | the oracle's invariants |
| `weights/` | trained adapters, distributed out of band for size; manifest and sha256 in `weights/README.md` |

### The three samples

| directory | contents | role |
|---|---|---|
| `data/primary/` | 210 evaluation structures, 1610 training structures | the main evaluation |
| `data/replication/` | 210 evaluation structures, disjoint from the above | held-out replication |
| `data/certification/` | the structure pool behind the emptiness certificate | certification only |

Sample directories are named for what they are. The identifiers used during the work are mapped in
the authors' own notes and are not part of the release.

### What is not here

**The rendered images.** They are a build product: 2100 PNGs, five orthographic views for each of the
420 evaluation structures, and a pure function of inputs that are here. The render is deterministic —
the camera set and pixel size are frozen constants and no stage draws a random number — so
re-rendering a structure reproduces its image. The `images` field of each `eval.jsonl` already names
the paths they belong at.

**The trained adapters**, omitted for size and available from the corresponding authors.

Neither is needed to reproduce a number. The per-structure prediction vectors in
`release/predictions/` are the reproducible artifact, and every accuracy recomputes from them without
API access.

**The experiment drivers, the figure generators, and the record prose.** Those are the authors'
working material. What the release carries is the result, in JSON, for every one of them.

## Reading a record

One directory per record. `results.json` holds the record's numbers and its conclusion; larger
records keep per-structure detail in named sibling files that `results.json` points to. Records that
correct, withdraw or qualify their own numbers carry that in a `caveats` field — several exist
specifically to say how their numbers must *not* be read, and those warnings travel with the values.

Four numbers orient the rest, each traceable to the record named beside it:

| | | record |
|---|---|---|
| chance, seven classes | 0.1429 | `label_granularity_sweep` |
| shape-free floor, three features | 0.5286 | `label_granularity_sweep` |
| supervised vision model, no language component | 0.8952 | `label_granularity_sweep` |
| the render ceiling, at the released tolerance | 0.9524 | `label_granularity_sweep` |

The ceiling is exactly 1 with the extraction tolerance tied to the symmetry tolerance, and 0.9524
read at the released merge tolerance. Both are reported, because a ceiling quoted without the
tolerance that produced it is not a measurement.

## Known limitations

- **The fine-tuned arm is single-seed.** Its point estimate sits inside the reference arm's own
  across-seed spread. `finetuned_arm_seeds` records the decision not to reseed and the quantitative
  test showing that seed variation of the measured magnitude cannot close the oracle gap; no error
  bar is drawn on it and no claim is made about its expected value under reseeding.
- **No improvement over any prior fine-tuned arm is claimed**, and no novelty for optimising a render
  protocol, which has direct prior art.
- **No causal claim for occlusion.** The render-convention probe is inconclusive rather than null:
  significance was unreachable in 7 of 16 paired comparisons at any outcome.
- **No human-expert baseline.** `expert_study` records why the collected sheet was excluded.
- **A calibration result is retracted in place.** `calibration` carries its own AUC values together
  with the diagnosis that they are an artifact of answer-coupled features. The numbers are shipped
  with the reason they must not be cited.
- Withdrawals, superseded values and defects found in this project's own work are recorded in the
  records rather than summarised away.

## Citation

```bibtex
@article{polat2026renderceiling,
  title   = {A model-free ceiling for vision--language model evaluation on
             rendered crystal structures},
  author  = {Polat, Can and Kurban, Mustafa and Serpedin, Erchin and Kurban, Hasan},
  year    = {2026},
  note    = {Preprint},
  url     = {https://github.com/KurbanIntelligenceLab/render-ceiling},
}
```

## License

Code is MIT (`LICENSE`); data, records and the released artifact are CC BY 4.0 (`LICENSE-DATA`).
Both are copyright Kurban Intelligence Lab.
Source structures are drawn from the Materials Project, which distributes its data under CC BY 4.0;
attribution to the Materials Project is required for any reuse of the structural data.

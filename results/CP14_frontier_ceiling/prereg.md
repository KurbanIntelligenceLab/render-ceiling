# CP14 — FRONTIER CEILING ON THE EXACT EVAL SET
# COMMITTED BEFORE ANY GENERATION. No GPU; API only.

## WHY
The existing zero-shot probe (CP1) used 70 canonical renders; every trained arm uses the
210-structure composition-exclusion split. Those numbers are NOT comparable, and the paper
currently has no ceiling row measured on the eval set. This supplies one, and it answers the
"is 0.6143 bad?" question on the same data rather than by cross-dataset inference.

## PROTOCOL — IDENTICAL TO THE TRAINED ARMS, NO EXCEPTIONS
  structures: all 210 of data/e3/eval.jsonl (the frozen composition-exclusion set)
  renders: the frozen 5-view set, unchanged files
  prompt: the same QUESTION string the trained arms received
  decoding: majority vote over K=3 samples (matching eval_e3.py's protocol)
  denominators: FIXED at 210; parse failures scored as ERRORS, never dropped
  metrics: micro accuracy AND macro-F1 AND per-crystal-system breakdown (brief §6)
  logging: effective_resolution recorded per model as reported by the API (images are sent at the
           native 768px file resolution; any provider-side downscaling is noted, not assumed)

## CONTAMINATION CONTROL, RUN IN THE SAME PASS
Materials Project structure pages are public and frontier models are the rows most exposed. Each
model is run on BOTH canonical renders AND element-anonymized renders (all atoms identical
spheres, same geometry). Reported side by side. Rationale: element anonymization was CP1's
pre-registered primary contamination control and it cleared for the base model; the frontier
models have not been tested on it.

## PRE-REGISTERED READINGS
  F1 If frontier canonical > 0.6143 (our direct arm) by more than the direct arm's seed SD
     (0.0515): the pixel-input ceiling is higher than our trained arm reaches, and the paper's
     framing is "our arm underperforms what pixels permit" rather than "pixels are insufficient".
  F2 If frontier canonical is within +/-0.0515 of 0.6143: our fine-tuned 8B arm is at the frontier
     level despite being ~2 orders of magnitude smaller, which is itself the result.
  F3 If frontier canonical < 0.6143 - 0.0515: fine-tuning on this task beats frontier zero-shot,
     and the paper says so.
  CONTAMINATION READING, INDEPENDENT OF F1-F3: if canonical MINUS anonymized exceeds the same
  0.0515 band for a frontier model, that model's canonical number is contaminated by compound
  recognition and only its anonymized number may be cited as perception.

## COMMITMENTS
  - Report every model run, including any that fail to parse; no dropping a model post hoc.
  - The bracket table will label the oracle row as a different sample (see CP0b's citation note)
    rather than presenting it as an eval-set measurement.
  - If API access is unavailable for a model, record that rather than substituting a cross-dataset
    number from CP1.

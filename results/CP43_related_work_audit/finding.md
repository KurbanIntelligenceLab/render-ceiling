CHECKPOINT: CP43_related_work_audit   GAP: no systematic prior-art check exists; the one informal check
   performed found two occupied claims, and a third found by a reviewer would be fatal. (Phase F)
STATUS: DONE FOR THE EIGHT NAMED ROWS, ALL VERIFIED FROM PRIMARY SOURCES (arXiv API titles and
        abstracts, fetched not recalled). THREE claims are demoted, ONE plan characterisation is
        CORRECTED, and one instrument the plan treated as unoccupied has a direct neighbour.

=================  ONE ROW PER NAMED PRIOR WORK  ==============================================

[2604.16060] "Chain-of-Thought Degrades Visual Spatial Reasoning Capabilities of Multimodal LLMs"
  ESTABLISHES: CoT degrades generalized spatial intelligence across a comprehensive multi-model,
    multi-benchmark evaluation.
  OUR CLAIM AFFECTED: direct-beats-chain (plan claim 4).
  VERDICT: DEMOTED TO CITED REPLICATION, as the plan already proposed. Our n=420 p=4.8e-04 result is a
    confirmation on a new domain, not a discovery.

[2607.12815] "Visual Access Boundaries in Vision-Language Model Reasoning"
  ESTABLISHES: asks whether CoT requires continued access to image content, and localises the boundary.
  OUR CLAIM AFFECTED: the perception-bottleneck framing.
  VERDICT: OCCUPIED for the general finding. Our contribution is the INSTRUMENT — a projective-geometry
    oracle on the actual rendered images — not the conclusion.

[2606.01558] "Attention-guided Fine-tuning of Multimodal Large Language Models Improves Chain-of-Thought
  Reasoning"
  PLAN CHARACTERISATION WAS WRONG, AND THIS IS A CORRECTION TO THE PLAN, NOT TO THE LEDGER. The plan
  cites this as showing "CoT-SFT increases textual-prior reliance", using it to demote our claim. The
  paper's own abstract confirms CoT often DEGRADES performance versus direct prompting and then proposes
  attention-guided fine-tuning as a FIX. It is SUPPORT for our premise and does not demote anything.
  VERDICT: cited as corroborating the degradation finding. Claim 4's demotion rests on 2604.16060 alone.

[2509.25848] "More Thought, Less Accuracy? On the Dual Nature of Reasoning in Vision-Language Models"
  ESTABLISHES: RL/GRPO-trained reasoning has a dual nature — gains and losses — in VLMs.
  VERDICT: ADJACENT, as the plan states. Cited; occupies no claim of ours exactly.

[2605.20177] "From Seeing to Thinking: Decoupling Perception and Reasoning Improves Post-Training of VLMs"
  ESTABLISHES, IN ITS OWN WORDS: VLM performance on visual tasks is "primarily limited by a lack of
    visual perception as opposed to reasoning itself", with staged training as the remedy.
  OUR CLAIM AFFECTED: this is the closest published statement of our headline reading.
  VERDICT: THE CONCLUSION IS OCCUPIED. What is not occupied is MEASURING the ceiling geometrically
    rather than inferring it from a training intervention. State the difference explicitly; do not
    present perception-over-reasoning as our finding.

[2511.19418] "Chain-of-Visual-Thought: Teaching VLMs to See and Think Better with Continuous Visual Tokens"
  ESTABLISHES: VLMs struggle with dense visual perception including spatial reasoning and geometric
    awareness; proposes continuous visual tokens.
  VERDICT: METHOD paper on the same diagnosis. Cited; we propose no method, so no collision.

[2506.13051] "Stress-Testing Multimodal Foundation Models for Crystallographic Reasoning"
  ESTABLISHES: a multiscale multicrystal dataset with TWO physically grounded protocols — a
    Spatial-Exclusion benchmark and a COMPOSITIONAL-EXCLUSION benchmark — nine VLMs prompted with
    crystallographic images, scored with relative lattice/density errors, a physics-consistency index
    and a HALLUCINATION SCORE covering invalid space-group predictions.
  THIS IS THE CLOSEST NEIGHBOUR IN THE PACKAGE AND THE PLAN DID NOT FLAG IT AS SUCH. Our evaluation
    split is a composition-exclusion split; theirs is a Compositional-Exclusion benchmark. Both prompt
    VLMs with crystal images and score space-group validity.
  VERDICT: THE BENCHMARK-DESIGN CLAIM IS DEMOTED. We must not present composition-exclusion evaluation
    of VLMs on crystal images as novel. What remains ours: DETERMINISTIC symmetry ground truth via
    spglib with a tolerance-quarantine policy, the 7-way crystal-system/point-group/space-group
    hierarchy as the scored target, and the geometric oracle. Their scoring is error-and-consistency
    based; ours is exact-label based.

[2605.29446] "CrystalXRD-Bench: Benchmarking VLMs for XRD Peak Indexing"
  ESTABLISHES: 250 samples, 10 databases, seven VLMs, one task (HKLs of the highest-intensity peak);
    best Jaccard 0.5888 with 37.6% exact match, six of seven below 0.50; pairs the rendered image with
    the source CIF so visual-extraction and reasoning errors can be separated; access to CIF text does
    not close the gap.
  OUR CLAIM AFFECTED: "VLMs fail at reading crystallography off rendered scientific images", and the
    separation of extraction error from reasoning error.
  VERDICT: OCCUPIED FOR THE HEADLINE. A published crystallography VLM benchmark already reports models
    failing on rendered crystallographic images AND already separates extraction from reasoning by
    supplying the CIF. Our difference is that we separate them with a GEOMETRIC ORACLE on the images
    rather than by handing the model the ground-truth text — a genuinely different instrument, and now
    the only defensible framing of the contribution.

=================  WHAT SURVIVES AS A CONTRIBUTION, AFTER THE AUDIT AND AFTER CP31  ===========
  1. The geometric oracle: inverting the frozen orthographic cameras, re-solving cross-view
     correspondence from element identity and ray geometry alone, and running spglib on the
     reconstruction. 0.9524 / 0.9095, paired against every arm at p < 1e-11. No cited work computes an
     identifiability ceiling this way.
  2. The orbit decomposition of occlusion into redundant and informative components, now measured on
     210 structures x 5 views per set — and the finding that the protocol's three axis views carry
     2.25-3.34x the occlusion of its two oblique views.
  3. The measurement that the frozen five-view protocol withholds under 1% of atoms, which is what
     makes the ideal ceiling a tight bound rather than a loose one.
  NOT A CONTRIBUTION, per CP31: the visibility-corrected ceiling and the render-imposed vs
  model-imposed separation. CP31's primary quantity is zero and its control blocks the target.

=================  THE THREE PREVIOUSLY OPEN ROWS, NOW SEARCHED  ===============================
All three instruments have been searched against arXiv using the field's own vocabulary rather than our
internal names. Titles and abstracts fetched from the API, not recalled. TWO OF THE THREE HAVE REAL
OCCUPANTS, and one of those is a direct hit.

ROW A — THE RESOLUTION-VERSUS-RESEED COMPARISON.
  OCCUPIED AS A GENERAL QUESTION. 2510.16926 (Res-Bench) benchmarks resolution ROBUSTNESS explicitly:
  14,400 samples across 12 resolution levels and six capability dimensions, with stability metrics beyond
  accuracy, on the stated grounds that existing evaluation overlooks whether performance is stable across
  input resolutions. 2506.12776 frames the same issue as a "Resolution Dilemma" and notes that existing
  benchmarks neglect resolution as a factor.
  EFFECT ON US: our resolution finding is a domain instance of a question already posed and benchmarked
  generally. It is NOT a contribution and was never claimed as one; it is a control that rules out a
  confound. This row is closed with that scoping recorded.

ROW B — THE CUE-SUFFICIENCY PARTITION.
  MY FIRST VERDICT HERE WAS WRONG ON A VERIFIABLE POINT AND IS REVERSED. I wrote that CRYSPNet
  (2003.14328) makes our random-forest control a published task. Re-reading its abstract: CRYSPNet predicts
  Bravais lattice, space group and lattice parameters "based ONLY on its chemical composition", with inputs
  that aggregate properties of the constituent elements. That is the OPPOSITE input to our control, which
  reads the CELL METRIC (19 lattice features) and never sees composition. The two tasks are not the same
  task:
    CRYSPNet   composition -> symmetry   a genuinely hard inference, no geometric shortcut exists
    our RF     cell metric -> symmetry   near-definitional, since the metric constraints ARE the crystal
                                          system's defining conditions
  So CRYSPNet does NOT occupy this row. What it does establish is that composition-only symmetry
  prediction is a solved-enough published task, which is why our composition-EXCLUSION split matters: it
  is what stops a model from taking the CRYSPNet route instead of looking at the picture. Cited for that
  purpose, which is stronger for us than the demotion I first recorded.
  RETRACTED SENTENCE, kept for the record: "the numeric-cell-to-symmetry mapping our random-forest control
  performs is a published task with a published model".
  2411.00803 trains CNNs on 1D powder patterns COMPUTED FROM lattice parameters and extinction laws, and
  reports accuracy matching "the theoretical maximums calculated based on Extinction Laws". THAT CEILING IS
  ANALYTIC, NOT MEASURED: the extinction laws state which reflections vanish, so the maximum is derivable in
  closed form for a synthetic pattern whose generative process is known exactly. Our ceiling is EMPIRICAL —
  a reconstruction run on the actual rendered images, whose achievable value nobody can write down in
  advance. My first verdict called it "an information-ceiling argument in the same spirit as ours", which
  overstates the overlap: it is the same GOAL reached by a route unavailable to us, and that distinction is
  the point rather than a quibble.
  EFFECT ON US: the random-forest control stays a CONTROL — a modality-matched reference showing what the
  cell metric alone determines — and is not a contribution either way. It is not a reproduction of
  CRYSPNet, because CRYSPNet solves a different and harder problem from a different input. Our partition
  predicate and the trigonal/hexagonal degeneracy analysis remain ours. The stratified accuracy claim built
  on the partition is WITHDRAWN anyway (Appendix R1), so nothing that survives rests on this row.

ROW C — THE ORACLE-ONLY CHECKER.
  ADJACENT AND WORTH CITING, NOT OCCUPIED. 2603.16253 introduces Explicit Visual Premise Verification for
  vision-language process reward models, motivated by exactly our concern: a verifier's low score may
  reflect a reasoning mistake OR the verifier's own misperception, and that entanglement produces
  systematic false positives and negatives. Several multimodal process-reward models (2508.04088,
  2505.13427, 2511.22998) score intermediate steps.
  EFFECT ON US: the ENTANGLEMENT problem is published and we should cite it as motivation rather than
  present it as an observation. What is not occupied is using a DETERMINISTIC GEOMETRIC oracle as the
  checker — every cited verifier is itself a learned model, which is the entanglement they are trying to
  escape. Our checker cannot misperceive because it reads coordinates, not pixels. State that difference.

=================  THIRD PASS — THE PAPER THE FIRST TWO PASSES MISSED  ==========================
2512.21329, "Your Reasoning Benchmark May Not Test Reasoning: Revealing Perception Bottleneck in Abstract
Reasoning Benchmarks". THIS IS THE CLOSEST NEIGHBOUR IN THE LITERATURE AND BOTH EARLIER PASSES MISSED IT,
because I searched crystallography and verifier vocabulary and never searched the abstract-reasoning
benchmark literature where the same argument lives.
  WHAT IT DOES, from the abstract: challenges the standard interpretation that the ARC / ARC-AGI gap
  reflects deficient machine REASONING, and hypothesises it arises primarily from limitations in VISUAL
  PERCEPTION. Verified with a two-stage pipeline that explicitly separates perception from reasoning: each
  image is independently converted to a natural-language description, then a model induces and applies
  rules from those descriptions.
  CONSEQUENCE FOR US, AND IT IS NOT SMALL: "the perception bottleneck" is PUBLISHED. We must stop
  presenting it as a finding. Any sentence in our package that reads as though we discovered it is wrong.
  WHAT SURVIVES AS OUR DELTA, stated so it can be checked: their perception stage is MODEL-MEDIATED — an
  image becomes a natural-language description written by a model, so their separation inherits the
  describer's own errors and their perception/reasoning split is a comparison between two model
  configurations. Ours is a DETERMINISTIC GEOMETRIC inversion against a closed-form ground truth, which
  yields a NUMERIC CEILING (what is recoverable at all) rather than a two-stage contrast. That is the
  instrument claim, and it is the paper.

2504.15280, All-Angles Bench: 2100+ human-annotated multi-view QA pairs over 90 real scenes, six tasks
testing multi-view geometric consistency and cross-view correspondence, reporting that MLLMs fall short
there. SUPPORTS our premise rather than occupying it — real scenes, human annotation, no closed-form
ceiling, no crystallography. Cite as evidence that multi-view correspondence is a known weakness.

=================  WHAT THIS AUDIT STILL DOES NOT COVER  =======================================
FIFTEEN CITED WORKS across three passes — eight named prior works in pass 1, FIVE in pass 2
closing the three instrument rows, and TWO in pass 3 (a row can take more than one paper to close, which
is why the paper count and the row count differ; an earlier version of this note said "eleven" by adding
8 papers to 3 rows, mixing two units). All from arXiv titles and abstracts. Not searched: non-arXiv venues, and the
crystallography literature predating the deep-learning era, where a metric-to-symmetry lookup is likely
classical textbook material rather than a citable result. The claim that our four surviving contributions
are unoccupied rests on FIFTEEN searched works, not on an exhaustive search, and is stated that way.

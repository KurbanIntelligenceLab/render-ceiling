# CoCr — final report

Chain-of-Crystallography: what vision-language models perceive in rendered crystal structures, in a
domain where every intermediate claim is checkable against spglib rather than against a human.

23 checkpoints, each with a written finding record. Every number below was checked against its
`results.json` BY VALUE, not by presence in the text — an earlier pass verified only that each figure
appeared somewhere in the report, and that let a metric mismatch survive.

Each section names the checkpoint directory holding its evidence, so any claim can be traced.

---

SECTION ORDER FOLLOWS WHAT SURVIVED, NOT THE ORDER THE WORK WAS DONE IN. The instrument comes first, then
the adequacy result it makes possible, then the two positive findings, then the nulls and withdrawals
gathered in one place rather than scattered as corrections. An earlier version of this report asserted the
stratified-accuracy mechanism early and withdrew it much later in the same document; that ordering is
gone, and the withdrawn material now lives in Appendix S with the retraction in Appendix R.
## 1. The instrument: a model-free geometric oracle   [CP0_pipeline, CP0b_identifiability, CP0c_resolution_audit]

Crystal structures from public databases, rendered as standardized multi-view ball-and-stick images
at a frozen protocol: conventional cell, 2x2x2 supercell, 5 views, 768 px. Ground truth for every
assertion a model can make — crystal system, Bravais lattice, point group, space group, Wyckoff
occupation, bond lengths — comes from spglib/pymatgen applied to the source structure file. No human
annotation and no LLM judge anywhere in the evaluation.

LABEL CORRECTNESS IS CERTIFIED, NOT ASSUMED. n = 224 (32 per system), 208/208 tolerance-robust
labels agreeing with the source database, exact Clopper-Pearson one-sided 95% lower bound 0.9857.
A symmetry-tolerance quarantine policy was frozen in advance; it removes 4/224 = 1.8% rather than the
7.1% a blunt "flip anywhere in the sweep" rule would drop, and it preserves the low-symmetry strata
that the blunt rule destroys. On the kept set, agreement is 220/220, CP95 lower bound 0.9865.

RESOLUTION. An audit found every earlier experiment had run at a decimated effective resolution. Its
pre-registration fixed the interpretation in advance, including the asymmetry that only an increase
would be a clean positive; the result landed in the ambiguous branch, so we do NOT claim resolution
is excluded as a factor.

## 2. The renders are adequate: what the protocol withholds, measured   [CP31, CP32, CP28, CP29, CP30]

THE VISIBILITY CORRECTION THIS SECTION WAS BUILT TO REPORT IS EXACTLY ZERO, AND SAYING SO FIRST IS THE
honest ordering. The oracle assumes perfect extraction of every atom, so its 0.9524 bounds
identifiability from the STRUCTURE. To separate that from what the IMAGES withhold, the orbit occlusion
classification was extended from 28-40 structures on three axis views to 210 structures per eval set
across all five frozen views, 0 errors, and the oracle was rerun with occluded detections removed PER
VIEW under four conditions.
  condition                              original 5v      expansion 5v
  O0 all detections present              200/210 0.9524   191/210 0.9095
  O1 informative occlusion removed       200/210 0.9524   191/210 0.9095
  O2 all occlusion removed               122/210 0.5810   113/210 0.5381
  O3 redundant occlusion only (CONTROL)  194/210 0.9238   170/210 0.8095
O0 reproduces CP25 EXACTLY, which was the pre-registered gate. O1 changes NOT ONE structure on either
set (paired McNemar p = 1.0000), while the CONTROL removes 6 and 21. The pre-registered rule was that if
the control's delta reaches half the target's, the analysis is measuring detection count rather than
information; with the target at zero the control dominates completely, so O1 IS UNREADABLE by the rule
fixed before the run.
THE REMOVALS DID REACH THE RECONSTRUCTOR — this was checked rather than assumed. O1 hides 548 of 16740
site-view slots, 38 of 40 sampled structures lose at least one site, and 7 of those change the recovered
atom count. They just do not change SYMMETRY recovery. The mechanism is supercell redundancy: a site is
observable in a view if ANY of its 2x2x2 copies is unoccluded there, and with five cameras losing one
still leaves the two that triangulation needs.
UNDER ONE PERCENT OF ATOMS ARE UNTRIANGULABLE from the frozen view set (0.26% original, 0.87%
expansion), and informative occlusion in ALL views is 0.0001-0.0007. So the "~0.18-0.20 effective
visibility deficit" this report published earlier is a PER-VIEW quantity and must not be read as a
ceiling on what the images afford. That is a correction to our own framing.
THE PROTOCOL'S THREE AXIS VIEWS CARRY 3.34x (original) and 2.25x (expansion) THE OCCLUSION OF ITS TWO
OBLIQUE VIEWS. Every occlusion figure published in this package before this extension was measured on
the three worst cameras in the protocol.
WHAT DOES COST ACCURACY IS TOTAL VISIBILITY: removing ALL occlusion costs 78 structures. So visibility
matters in aggregate; the INFORMATIVE component specifically does not.
EXTRACTION FAILS AT VISIBILITY AND SEGMENTATION, NOT PRECISION (CP32, argument from measured values):
recall median 0.400, precision median 0.233, centroid error median 0.717 px on matched atoms, recall
correlating -0.792 with occlusion against -0.411 with atom count, and recall halving across occlusion
terciles (0.528 -> 0.239) while precision stays flat (0.383 -> 0.360).

## 3. The signal is visual: the no-image control   [CP41]

Every zero-shot row is prompted with renders AND a formula preamble, so nothing established that the
IMAGE was doing the work. A control with the byte-identical prompt text and the image blocks removed,
same 210 structures, K=3, paired per structure:
  model                       IMAGE     TEXT    delta   img-only  txt-only   exact p
  gemini-3.6-flash (K=3)     0.7333   0.1619   +0.5714      139        19    1.0e-23
  claude-opus-4.8 (K=3)      0.5810   0.1667   +0.4143       98        11    1.3e-18
  glm-4.6v (K=3)             0.4429   0.1286   +0.3143       93        12    2.4e-13
  llama-4-maverick (K=3)     0.4429   0.1381   +0.3048       73         9    1.4e-13
  qwen3-vl-8b (K=3)          0.3762   0.1667   +0.2095       60        16    3.9e-07
  qwen3-vl-235b-a22b (K=3)   0.3333   0.1429   +0.1905       58        18    4.7e-06
  seed-1.6 (K=3)             0.2571   0.1524   +0.1048       37        15    3.2e-03
  qwen2.5-vl-72b (K=3)       0.2524   0.1286   +0.1238       43        17    1.1e-03
  qwen3-vl-32b (K=3)         0.2286   0.1190   +0.1095       41        18    3.8e-03
  mistral-medium-3.1 (K=3)   0.2286   0.1476   +0.0810       40        23    4.3e-02
  --- NOT SIGNIFICANT ---
  llama-4-scout (K=3)        0.2048   0.1762   +0.0286       30        24    4.97e-01
  nova-pro-v1 (K=3)          0.1810   0.1429   +0.0381       16         8    1.52e-01
  mistral-small-2603 (K=3)   0.1476   0.1619   -0.0143       22        25    7.71e-01
  --- UNSCORED (gate, not accuracy) ---
  gpt-4.1-mini (K=3)         210/210 unparseable: explicitly requested the missing images
  grok-4.5 (K=3)              27/210 unparseable = 0.129, over the 5% gate
  gemini-2.5-flash (K=3)     302/630 API errors = 0.479, over the 5% gate
FULL ROSTER, 13 SCORED OF 16 ATTEMPTED. Ten show a significant positive image contribution (+0.0810 to
+0.5714, max p = 0.043); THREE DO NOT, so the roster claim is SCOPED rather than universal: the benchmark
measures vision FOR EVERY MODEL THAT CAN DO THE TASK AT ALL.
THE THREE NULLS ARE MOSTLY NOT FORMULA-LOOKUP, and the discriminating test costs nothing. A formula-lookup
row must score ABOVE chance WITH images; a floor-effect row is already at chance, so removal has nothing to
cost. Against 7-way chance: nova-pro-v1 38/210 p = 0.073 and mistral-small-2603 31/210 p = 0.452 are NOT
above chance (floor effects, uninformative about formula-lookup), while llama-4-scout 43/210 p = 0.009 IS
above chance yet shows no image contribution — genuinely ambiguous, and named rather than absorbed.
Spearman(IMAGE accuracy, delta) = 0.9725: image contribution tracks capability almost perfectly, which is
the arithmetic caveat pre-registered before the run — a model near chance has no room to drop.
THE REFUSAL IS REPORTED AS A REFUSAL. gpt-4.1-mini returned nothing parseable on all 210; the raw
response is an explicit request for the missing images, so it declined the task rather than answering it
wrongly. Reported separately and excluded by the pre-registered unparseable gate, not scored as 0.0.
MY REGISTERED EXPECTATION WAS WRONG, IN A DIRECTION THAT STRENGTHENS THE BENCHMARK. I predicted TEXT
would land near the shape-free floor, since the floor is itself a composition-only model. Every one of the
thirteen scored TEXT arms lands at CHANCE instead — the range is 0.1190 to 0.1762 against 7-way chance
0.1429 — and every one is significantly below the floor's 111/210. So the formula preamble does far less work than the floor captures:
the floor is a HARDER reference than a text-only VLM, and the thirteen-below-floor result is stronger
than if text-only had matched it.

## 3b. The attribution ladder: which stage the deficit lives in   [CP51, CP52, CP53]

THE INSTRUMENT CLAIM NEEDED A LADDER, NOT A SINGLE CEILING. R1 (the oracle) never touches a pixel, so
"perception is the bottleneck" rested on an instrument that assumes perception. Three rungs were added.

  R0  spglib on ground-truth positions                     1.0000   DEFINITIONAL, no K (original, n=210)
  R1  oracle: invert the frozen cameras, then spglib        0.9524   ideal extraction, no K (original, n=210)
  R3  best model, ground-truth geometry supplied as text    0.8524   K=3 (original, n=210)
  R4  best model, pixels                                    0.6905   K=8 (original, n=210)
  R2  oracle on a real detector's output                   UNSCORED  19.0% / 22.4% zero-triangulation

R0 IS DEFINITIONAL AND THAT MATTERS. The label IS spglib applied to the structure at the canonical
labelling tolerance, so R0 = 210/210 = 1.0000 exactly. The reframing directive stated R0 is approximately
equal to R1 at 0.9524, which duplicates a rung and discards the R0-to-R1 interval — and that interval,
1.0000 -> 0.9524, is precisely what camera inversion plus correspondence re-solution costs.

R3 CONTRADICTS THE PERCEPTION-BOTTLENECK THESIS, AND THIS IS THE MOST IMPORTANT RESULT OF THE PASS.
Given PERFECT geometry as text, no model reaches the oracle: the best is 0.8524 against 0.9524.
Branch C1 ("the entire deficit is perception") does not fire. C2 ("models cannot reason from geometry at
all") does not fire either — every arm is far above the formula-only control. C3 fires on all 14 scored
arms, and the pre-registered decomposition then gives
    perception share = R3 - R4,   reasoning share = R1 - R3
  median perception fraction 30.9%, range 0.9% to 70.4%.
  12 of 14 models have REASONING as the larger share; only 2 (gemini-3.6-flash, grok-4.5) are
  perception-dominated. SO PERCEPTION IS NOT THE BOTTLENECK AS A GENERAL STATEMENT ON THIS TASK. It is the
  bottleneck for the two strongest models and not for the rest, and the direction is systematic:
  Spearman(pixel accuracy, perception share) = -0.6439, p = 0.0130. The bottleneck MOVES with model strength.

THE CONTROL PAIR IS WHAT MAKES R3 READABLE. CP41 removed the images and left the formula: every scored arm
collapsed to 7-way chance (mean 0.1357). CP53 removes the images and supplies full geometry: every arm
lands between 0.4143 and 0.8524. The two differ in exactly one thing, so the jump is the geometry
rather than text-mode prompting. R3 prompts are also SHORTER than the five-image prompts they beat
(mean 177 tokens, max 250, zero structures truncated), so prompt length cannot explain it.

R2 IS REPORTED UNSCORED BY ITS OWN PRE-REGISTERED GATE, AND THE ATTRIBUTION IT WOULD HAVE PROVIDED REMAINS
UNMEASURED. Substituting the CP19 detector's real detections into the identical inversion gives 16/210 and
18/210 — below every model — but 40 of 210 and 47 of 210 structures recover ZERO atoms, over the 5% gate
written before the run. Mandatory operating point, to be quoted wherever R2 appears: median recall
0.4, median precision 0.2333, median centroid error 0.7171 px. The pipeline is correct — zero exceptions in 420
structures, calibration residual 0.0, and it reproduces R1 exactly on ground-truth projections — so the
detector is the binding limit, and the median recovered/true ratio of 0.4 equals its median recall.
ONE MECHANISM WORTH KEEPING: 44 original and 25 expansion structures OVER-triangulate despite the
detector finding FEWER atoms than exist. A dropped disc lets a ray from another atom pass the cross-view
test, manufacturing phantom sites — extraction errors propagate non-monotonically, so recall alone does not
predict reconstruction quality.
SO THE EXTRACTION SHARE IS BOUNDED FROM NEITHER SIDE: R1 assumes perfect extraction, R2's extractor is too
weak to be informative. A detector at recall above 0.9 is the single most valuable missing measurement.

THE LABEL LADDER SHOWS THE CEILING GENERALISES, AND SEPARATELY WHAT THE CELL METRIC DOES NOT ENCODE.
  label            classes present   majority   floor3    RF19    ORACLE
  (all rows: original eval sample, n=210; floor3/RF19/ORACLE are model-free, no K)
  crystal system      7/7             0.1429    0.5286   0.8952   0.9524   (original, n=210, no K)
  Bravais lattice    13/14            0.2286    0.4762   0.9095   0.9429   (original, n=210, no K)
  point group        21/32            0.1381    0.4476   0.7143   0.9524   (original, n=210, no K)
  space group        44/230           0.1095    0.4048   0.6810   0.9429   (original, n=210, no K)
The oracle is FLAT across granularity, because spglib reads the reconstruction exactly: a structure is
either reconstructed or not, and all four labels follow. So the renders determine SPACE GROUP to 0.9429 given
ideal extraction, and the identifiability claim is not specific to a 7-way label.
The random forest tells the complementary story: nearly metric-determined at crystal system and Bravais,
then falling to 0.7143 and 0.6810, because point group and space group depend on ATOM POSITIONS AND SITE
SYMMETRIES that 19 lattice numbers do not encode. The oracle-to-RF gap WIDENS from 0.0572 to 0.2619. That
is the answer to "a tabular baseline makes this task trivial": it does, at crystal system, and stops two
rungs up.
MACRO-F1 IS WITHHELD on the finer labels as pre-registered — space group has 18 singleton classes among 44
present — and BOTH chance definitions are reported because majority-class (0.1095) and 1/n_classes (0.0043)
diverge more than twentyfold at space group.

## 3c. An intervention that works, and a prediction this report got wrong   [CP54]

THE FROZEN CAMERA SET IS NOT INFORMATION-OPTIMAL. Perturbing the cameras off the principal axes raises the
oracle's identifiability ceiling on both samples:

  sample      frozen cameras       off-axis cameras      gained  lost   exact p
  original    200/210 = 0.9524    209/210 = 0.9952         9      0    0.00391   (no K, model-free)
  expansion   191/210 = 0.9095    203/210 = 0.9667         16     4    0.01182   (no K, model-free)

Significant on both, and monotone on the original: every structure the frozen cameras lose is recovered
off-axis and none is lost. The mechanism is the one already established — viewing down a lattice vector
stacks supercell copies onto identical pixels, and perturbing the camera unstacks them.

THIS REPORT PREVIOUSLY CLOSED THIS INTERVENTION ON GEOMETRIC ARGUMENT AND PREDICTED A NULL. The prediction
was wrong, and the reason it survived matters more than the error: projection_matrices() hardcoded the frozen
camera map and reconstruct_positions() had no parameter to override it, so any perturbed-camera run silently
reproduced the frozen ceiling. The first attempt at this checkpoint returned both conditions at an identical
66/70 and printed that the parameter was absent, which is the only reason it was caught. The parameter is now
threaded through both functions and the default path reproduces exactly 200/210, so no prior result moves.
THIS IS A CEILING GAIN, NOT A LEGIBILITY GAIN: off-axis cameras make more information available to a
triangulating reader rather than making the same information easier to read.

THE SUPERCELL IS THE PROTOCOL'S SECOND SUBOPTIMAL CHOICE. Feeding the oracle an explicitly tiled 2x2x2
structure instead of the single conventional cell costs it 22 structures and gains none:
200/210 = 0.9524 single cell against 178/210 = 0.8476 tiled, exact p = 4.77e-07 (no K, model-free). Tiled copies project
onto coincident pixels and a triangulating reader cannot separate them. So the frozen protocol is
information-suboptimal on both of its geometric choices.

AND NEITHER CORRECTION REACHES THE MODELS. Four strong models x five conventions x 70 stratified structures
x K=3, paired per structure, zero unparseable:

  convention        claude-opus-4.8   gemini-3.6-flash   llama-4-maverick   grok-4.5   (n=70, K=3)
  C1 frozen              0.5429           0.7857             0.4429          0.5857   (n=70, K=3)
  C2 single cell         0.5286           0.7286             0.4714          0.6429   (n=70, K=3)
  C3 small radii         0.5571           0.7714             0.4714          0.5857   (n=70, K=3)
  C4 off-axis            0.5571           0.7571             0.4714          0.6143   (n=70, K=3)
  C5 single + small      0.5714           0.7000             0.4714          0.6571   (n=70, K=3)

Sixteen paired comparisons against the baseline, NONE significant, smallest p = 0.1094. Pooled across
models the discordance is near-symmetric in every convention (C2 gained 17 lost 16, C3 9/7, C4 13/10,
C5 16/13), and the direction is not consistent even within a convention — on C2 and C5 gemini falls while
grok rises.
POWER, CORRECTED AND STATED PER COMPARISON. An earlier version of this section quoted a single minimum
detectable difference of 0.162 from 1.96*sqrt(2p(1-p)/n). THAT WAS AN UNPAIRED FORMULA APPLIED TO A PAIRED
DESIGN, and it carried no target-power term, so it was neither the paired MDE nor an 80%-power figure. The
test actually run is a paired exact binomial on discordant pairs, and discordance is LOW: a mean of 6.3
discordant pairs per comparison. Recomputed properly, SIGNIFICANCE WAS REACHABLE IN ONLY 9 OF THE 16
COMPARISONS — the other 7 have so few discordant pairs (2 to 5) that no split reaches p<0.05 at any
outcome. Among the reachable 9 the paired MDE runs 0.0857 to 0.1286, median 0.1143, against a largest
observed absolute delta of 0.0857.
THE NULL IS THEREFORE WEAKER THAN PREVIOUSLY STATED, not stronger. The blanket claim that it bounds the
effect below ~0.16 is WITHDRAWN. What survives: no convention produced a detectable change in any
comparison, and for 7 of 16 the design had no power to detect one at all.
WHAT THE TWO LEGS SAY TOGETHER, and it is the useful statement: the information the frozen protocol withholds
is real and recoverable by a geometric reader, and it is not what limits the models. That is the attribution
ladder's conclusion reached by intervention instead of decomposition — an intervention that adds information
a model cannot use is evidence about the model, not about the render.

## 3d. A learned extractor that fabricates its output   [CP58]

Substituting a strong model as the extraction stage — it sees the renders and emits species and coordinates,
the symmetry question withheld — and having a weak model answer from that text gives 30/210 = 0.1429 (K=3).
NO PRE-REGISTERED BRANCH FIRES, and the accuracy is not the result: the arm predicted only 2 of 7 classes,
answering "cubic" on 205 of 210, and 0.1429 is exactly the cubic stratum's base rate. That is prediction
collapse, and an accuracy produced by a collapsed predictor measures nothing about reasoning.

THE INFORMATIVE MEASUREMENT IS THE INTERMEDIATE, SCORED DIRECTLY AGAINST GROUND TRUTH:

  median recall of emitted positions                  0.0
  median precision                                    0.0
  structures with ZERO matched atoms                  105 of 206
  median error on atoms that did match                0.0817 fractional units
  connected-component detector, for contrast          recall 0.4, precision 0.2333

The model emits syntactically perfect coordinate lists — correct element symbols, five-decimal precision, a
median of 48 atoms — and on half the structures not one of them lands within tolerance of a real atom.
It produces the form of an extraction without the content, and it is a worse extractor than a colour
threshold. All pre-registered gates pass (1.9% unparseable, no API errors, 1.9% emitting fewer than three
atoms), so this is the model's extraction rather than a harness artefact.
WHAT THIS LICENSES, AND IT IS AN ARGUMENT FOR THE INSTRUMENT: downstream accuracy alone would not have
revealed the fabrication — 0.1429 reads naturally as "the weak model reasons badly". Only scoring the
intermediate against exact positions exposes it. A two-stage pipeline whose intermediate cannot be checked
will attribute fabrication to reasoning.
WHAT IT DOES NOT LICENSE: any claim about whether the strong/weak difference is perception. The design
premise failed rather than the hypothesis, since a transplant can only test perception if the transplanted
content is perception.
THE CORRECT REFERENCE FOR THIS ARM IS 0.5048, NOT 0.7333. The weak model reaches only 0.5048 even when given
exact coordinates (section 3b), so that is its ceiling in this design; comparing the arm against the strong
model's own 0.7333 on pixels would overstate the shortfall by 0.23. The pre-registration named this asymmetry
before the run.

## 3e. The scale-up, and the claim it retires   [CP50]

THE PACKAGE'S MOST-QUOTED CLAIM DOES NOT SURVIVE AT SCALE, and the pre-registration named this as the
outcome most expensive to absorb. A fresh 1995-structure sample — MP, 2-4 elements, conventional cell at
most 80 atoms, stratified 285 per system before quarantine, and zero overlap with the training set
or either earlier evaluation sample:

  quantity                        n=210    n=1933   size-matched (n=721)
  shape-free floor (3 features)   0.5286   0.2054        0.2205      (no K, model-free)
  geometric oracle                0.9524   0.8774        0.9459      (no K, model-free)
  19-feature cell-metric RF       0.8952   0.8738          --          (no K, model-free)

The scale-up sample is 1933 rather than 1995 because 62 structures (3.11%) are quarantined for
label instability, inside the pre-registered 10% gate. I first published a quarantine rate of 0, which was
wrong: the test read a top-level schema key the labels nest one level down, so it defaulted to "stable" for
every structure and never fired. Rescoring without the 62 shifts every quantity by at most 0.0041, so
nothing below changes; the clean values are canonical and the with-quarantined ones are retained as
superseded data. Quarantine is uneven across strata — triclinic loses 39 of 285, cubic none — so the clean
sample is not exactly uniform.

Both quantities moved, so the pre-registered control ran before either was called a scale effect: the new
sample has a MEDIAN OF 38 ATOMS PER CELL against the original's 14, so restricting it to cells no larger
than the original's 95th percentile and re-stratifying separates cell size from sample size.

THE CONTROL SPLITS THE TWO CAUSES. The ORACLE's drop is a CELL-SIZE effect — at matched size it returns to
0.9459, within 0.0065 of the original, because more atoms per cell means more projective
coincidence and more correspondence ambiguity. So the identifiability result generalises once cell size is
held fixed. The FLOOR's drop is NOT: at matched size it is 0.2205, still 0.3081 below the original, and it
sits near 0.22 at both cell-size regimes. THE 0.5286 WAS A PROPERTY OF THE ORIGINAL 210 DRAW, NOT OF THE TASK.

WHAT THIS RETIRES. "All 13 zero-shot models fall below a composition-only baseline" holds ONLY on the
original 210 sample: the best zero-shot arm at 0.4429 is below that sample's 0.5286 and ABOVE both
0.2205 and 0.2054. The claim is re-scoped to its sample wherever it appears and is no longer stated as
a task property.
THE THESIS IS UNAFFECTED, WHICH IS WHY IT WAS WRITTEN THIS WAY. The paper rests on the oracle-to-model gap,
and that gap SURVIVES at matched size: 0.9459 against 0.4429. It never rested on the below-floor comparison.
WHY THE ORIGINAL FLOOR WAS HIGH IS NOT ESTABLISHED and no mechanism is claimed. What is established is that
0.5286 does not reproduce on an independently drawn, composition-excluded, identically stratified sample at
either cell-size regime.
THE MODEL ARMS AT SCALE ARE NOT RUN (500 x 13 x K=3 = 19,500 calls), so every model number in this package
still rests on n=210 and is reported with that sample named.

## 3f. Where the pixel reader falls behind a numeric one, and one generation of progress   [CP35, CP36]

THE CUE-SUFFICIENCY PARTITION PREDICTS WHERE A PIXEL MODEL TRAILS A NUMERIC READER OF THE SAME CELL, and
this replicates on both samples against a control — unlike the CP15 claim it replaces, which compared raw
accuracy and was withdrawn. The contrast is pixel-minus-RF; negative means the pixel model trails:

  arm                sample      suff gap   amb gap   pixel amb-vs-suff Fisher p   (K=3, model-free RF)
  gemini-3.6-flash   original     -0.0857   -0.3143   4.95e-06
  gemini-3.6-flash   expansion    -0.0851   -0.2609   4.00e-08
  grok-4.5           original     -0.2571   -0.3286   5.02e-02
  grok-4.5           expansion    -0.2270   -0.4203   2.31e-07
  claude-opus-4.8    original     -0.3000   -0.3429   1.04e-01
  claude-opus-4.8    expansion    -0.2695   -0.3623   1.73e-04

THREE OF THREE ARMS WIDEN ON THE AMBIGUOUS STRATUM ON BOTH SAMPLES — branch D1, which CONTRADICTS the
expectation recorded before the run. My pre-registration said "I expect D3" and named the existing data as
pointing away from the claim; it was wrong.
WHY THE CONTROL MATTERS. The RF drops across strata too (0.9214 to 0.8429 original, 0.9433 to 0.7536
expansion), so a raw pixel drop proves nothing. That is precisely the defect that invalidated CP15, whose
withdrawal stands.
THE CONFOUND, STATED RATHER THAN BURIED. The ambiguous stratum is 60 of 70 and 58 of 69
hexagonal-or-trigonal, so this is close to a hex/trig effect and both descriptions are reported. Removing
hex/trig leaves n=10 and n=12, where the gap persists but a single structure moves it 8 to 10 points, so
the residual is SUGGESTIVE ONLY and does not establish independence from the degeneracy.

ONE GENERATION OF PROGRESS DOES NOT ERASE THE AXIS. gemini-2.5-flash to gemini-3.6-flash on the original
sample, paired per structure: 0.4286 to 0.7333, discordance 72:8, p = 5.4e-14 (K=3).
By stratum the raw gains are +0.2071 sufficient and +0.5000 ambiguous, which reads as the newer generation
closing the render-imposed gap faster. NORMALISED BY HEADROOM TO THE ORACLE IT CLOSES LESS: 64.0% of the
sufficient gap against 54.1% of the ambiguous one. The larger raw gain is substantially a low-baseline
effect — the ambiguous stratum started at 0.0286. And the newer model still separates the strata
(0.5286 against 0.8357, Fisher p = 4.95e-06), so the difficulty axis survives a generation.
NO TREND LANGUAGE: one pair is a comparison, and CP26 established that parameter count does not order
accuracy at all, so no scaling statement is available either.

## 4. The models fail universally   [CP26_model_sweep]

A four-row leaderboard cannot establish that a task is hard. Thirteen models across EIGHT vendors were
run zero-shot on the frozen protocol, CP14 prompt verbatim, no per-model tuning, denominators fixed at
210, parse failures scored as errors. All counts recomputed from per-structure prediction vectors.

    zero-shot leaderboard, ORIGINAL eval sample n=210, K=3 majority vote:
    llama-4-maverick        93/210  0.4429        qwen3-vl-32b            48/210  0.2286   K=3
    glm-4.6v                93/210  0.4429        mistral-medium-3.1      48/210  0.2286   K=3
    gemini-2.5-flash        90/210  0.4286        llama-4-scout           43/210  0.2048   K=3
    qwen3-vl-8b             79/210  0.3762        nova-pro-v1             38/210  0.1810   K=3
    gpt-4.1-mini            77/210  0.3667        mistral-small-2603      31/210  0.1476   K=3
    qwen3-vl-235b-a22b      70/210  0.3333        -----------------------------------------
    seed-1.6                54/210  0.2571        SHAPE-FREE FLOOR (this sample) 111/210 0.5286   K=3
    qwen2.5-vl-72b          53/210  0.2524        our best fine-tune, K=8  145/210  0.6905   (same adapter at K=3: 139/210 = 0.6619)

THE FLOOR IS SAMPLE-SPECIFIC AND IS NAMED WHEREVER IT APPEARS. 0.5286 = 111/210 is the ORIGINAL
eval sample. On the expansion sample the same three-feature model gives 0.2476, so no floor-relative
phrasing is used without naming the sample. The thirteen-below-floor result below is an
ORIGINAL-SAMPLE claim; those models were never run on the expansion set.
K IS PRINTED ON EVERY ROW. The thirteen zero-shot rows are K=3; the A3 reference is K=8, and the
same adapter at K=3 is 139/210 = 0.6619.

EVERY MODEL FALLS BELOW THE FLOOR, and the best falls significantly below it: 93/210 against the floor's
111/210, eighteen structures, one-sided binomial p = 0.0078. The floor result was previously open to the
objection that our own arms were weak; it now holds across eight vendors and a 50x range in total parameters (8B to 400B, verified figures). No
model approaches the fine-tuned arm — the nearest is 52 structures behind — so the fine-tuning
contribution is not bounded by any zero-shot row here.

THE SWEEP RAN TWICE, WHICH IS BOTH A DEFECT AND A USEFUL NUMBER. A relaunch after a wrong liveness
check produced a second independent measurement of 9 of the 13 models, and an earlier version of this
section mixed the two runs into one table. Separated, the nine repeated models differ by a mean of 5.0
structures and a maximum of 11 (0.052 accuracy). THAT IS THE RUN-TO-RUN SPREAD of K=3 majority voting at
temperature 0.7 on this benchmark: any single-run leaderboard position carries roughly +/-0.05, so
ADJACENT ROWS ARE NOT SEPARABLE and the ordering should not be read as exact. Every headline claim
survives both runs independently — all models below the floor, the best significantly below it
(p = 0.0078 and p = 0.0310), no model reaching the fine-tune, and the Qwen ladder non-monotone in both.

SCALE DOES NOT CLOSE THE GAP, AND THE LARGEST MODEL TESTED IS TIED FOR BEST. On verified parameter
figures — total and active, disclosed sizes only — llama-4-maverick at 400B total (17B active, 128
experts) scores 93/210, ties glm-4.6v at the top of the leaderboard, and is STILL 18 structures below
the 111/210 floor. That is the stronger form of the claim: not that large models do poorly, but that the
largest model available to us is the best of the thirteen and still does not clear a baseline computed
from three lattice numbers. The verified range is 50x (8B to 400B).
NO SINGLE SCALING STATEMENT IS SUPPORTED, because the disclosed figures point three ways. Within the
Qwen3-VL dense pair the SMALLER model wins — 8B scores 79, 32B scores 48, a 31-structure gap that is six
times the run-to-run spread. At FIXED ACTIVE COMPUTE more total capacity helps substantially: llama-4
scout and maverick both activate 17B and differ only in expert count (16 vs 128) and total size (109B vs
400B), and accuracy goes 43 -> 93 — an expert-count effect, not a compute-scale effect. Across families,
active parameters do not order accuracy at all (maverick 17B: 93, qwen-235B 22B: 70, scout 17B: 43).
What survives is the negative claim, which is the one the benchmark needs: across a 50x total-parameter
range and every architecture tested, nothing clears the floor.
A CORRECTION WORTH STATING. An earlier version of this section said "a 30x parameter range" and "the
largest model tested stays 41 structures below the floor". Both were wrong — they treated the 235B-A22B
model as the largest when maverick at 400B is larger, and attached the 235B model's deficit to it. Worse,
the accompanying figure plotted a Mistral ladder at 24B and 41B; Mistral has not disclosed either
model's parameter count, so those figures were invented. The Mistral ladder is removed and the eight
models with undisclosed sizes appear only on the accuracy leaderboard, never on a size axis.
WHAT THIS DOES NOT LICENSE: zero-shot rows are not a method comparison against fine-tuned arms —
different training exposure. They bound task difficulty, not method quality. One pre-registered model
(kimi-k2.6) hangs indefinitely on this workload and is reported UNSCORED rather than dropped, so the
roster is 13 of a pre-registered 14.

## 5. Where every model sits, on one sample   [CP14_frontier_ceiling, CP8_external_baselines, CP1_zeroshot]

All on the frozen 210-structure composition-exclusion evaluation set, micro accuracy.

    GEOMETRIC ORACLE, ideal extraction (no K)       0.9524   (200/210; the information ceiling)
    random forest, 19 lattice features (no K)       0.8952   (188/210; refrozen, see footnote)
    gradient boosting, same features (no K)         0.8762
    Gemini 3.6-flash, zero-shot (K=3)               0.7333
    ALIGNN, published architecture (structure input, no K), 3 seeds         0.6492  +/- 0.0287
    logistic regression, same features (no K)       0.6524
    our 8B fine-tune (B1 direct, K=8)               0.6190
    Grok 4.5, zero-shot (K=3)                       0.6143
    Opus 4.8, zero-shot (K=3)                       0.5810
    ---- regularity floor, 3 features (no K)        0.5286   (THIS sample; see section 4)
    CGCNN-style GNN, ours, 3 seeds (no K)           0.4889  +/- 0.0469
    process-trained chain arm (V2b, K=8)            0.3810
    chance, 7-way (no K)                            0.1429

METRIC NOTE: every row is MICRO accuracy on the same 210 structures. An earlier version listed the
chain arm as 0.3857, which is its MACRO-F1 from the training matrix — a metric mismatch, not a
rounding difference (81/210 against the correct 80/210).
THE TWO 3-SEED ROWS ARE MEANS and need not land on an integer count: ALIGNN's seeds are 0.6762 /
0.6095 / 0.6619 (142 / 128 / 139 of 210), the GNN's are 0.4286 / 0.4952 / 0.5429 (90 / 104 / 114).
Both SDs are population SDs, the project convention.

Only ONE of three frontier models beats our 8B fine-tune. ALIGNN sits above it on the mean but a
paired McNemar test does NOT separate them (41 structures our arm alone, 53 ALIGNN alone, p = 0.256),
so a coordinate-input GNN and a pixel-input 8B fine-tune are statistically indistinguishable here.
Our ALIGNN run is 0.107 below the published 75.6% on this task, as expected: harder split, smaller
training set, 40 epochs, no hyperparameter search. It is a faithful-architecture run under OUR
protocol, not a reproduction of the published number.

CONTAMINATION CONTROL. Element-anonymized renders (every species replaced by one element, geometry
untouched) clear for all three frontier models on paired tests: 0.7333 -> 0.6810, 0.6143 -> 0.5905,
0.5810 -> 0.6190. Opus scores HIGHER on anonymized renders, which is the opposite of contamination.

SEPARATELY, ON THE DISJOINT 280-STRUCTURE SAMPLE AND NOT AN EVALUATION-SET ROW (the eval-set oracle is
0.9524 / 0.9095, in the table above): the oracle recovers 0.9357 of crystal systems
from 4 views, and its view-count curve is essentially complete by FOUR (2v 0.7429, 3v 0.9143, 4v
0.9357, 5v 0.9393). Paired tests on the same 280 structures: 2->3 gains 50 and loses 2 (p < 1e-4,
real); 3->4 gains 7 and loses 1 (p = 0.0703, NOT resolved); 4->5 moves one structure (p = 1.0). So the
frozen 5-view protocol carries ONE view of slack, not two, and 3-view saturation is not supported —
an earlier "saturates at 3" reading compared marginal rates instead of running the paired test. Space
group is still climbing at 3->4, so any recommendation must name its task. It is measured on a different 280-structure sample with ZERO overlap with the
evaluation set, and section 3 explains why it bounds identifiability from the STRUCTURE rather than
from the IMAGES.

FOOTNOTE — THE RANDOM FOREST HAS ONE CANONICAL VALUE AND TWO RETIRED ONES.
Canonical: 0.8952 = 188/210, the CP28 refit, which is the ONLY value with a frozen executable
specification attached (ledger/CP28_classifier_refreeze/classifier_specifications.json: ordered feature
list, library versions, per-structure prediction vector). Retired: 0.8905 = 187/210 (original run, feature
list never saved) and 0.8857 = 186/210 (a later reproduction, also unrecoverable). Twelve defensible
readings of the recorded feature prose span 183-188 of 210 and NONE reproduces 186, so the recorded
protocol is underdetermined rather than merely mis-transcribed. Separately, 0.8762 = 184/210 is GRADIENT
BOOSTING on the same features, not a random forest; under the canonical protocol GB gives 183/210.

## 6. The cue-sufficiency partition, as a render-convention property   [CP15, CP19, CP20, CP21, CP22, CP23, CP13]

THE FROZEN PROTOCOL IS AN INHERITED PLAN VIEW WITH ITS ANNOTATIONS DROPPED, and saying so first
prevents a false discovery claim. The crystallographic plan view is a projection down a principal
axis, conventionally a 2x2 array of cells, with atom heights written as fractions beside them.
Principal-axis cameras plus a 2x2x2 supercell is that geometry WITHOUT the height annotations. Viewing
down a lattice direction is a zone axis, where exact projective coincidence is the defining property
rather than a defect — in zone-axis imaging it is a feature, giving a direct correspondence between
intensity and projected column density. The domain solved this occlusion problem by ANNOTATING DEPTH.
So what follows is not that the renders are broken; it is that a convention built for column
visualization and human-read annotations may not suit a VLM asked about symmetry, and the pipeline
dropped the component that made it readable.

A structure is BOX-SUFFICIENT if the conventional-cell metric — the cell the renders draw — uniquely
implies its crystal system. On the CANONICAL predicate (CP28, specified and reproducing exactly) that is
140/210 = 0.6667 on the original evaluation set and
141/210 = 0.6714 on the independently drawn expansion set. The ambiguous
stratum is dominated by the trigonal/hexagonal pair on both samples — 60 of 70 = 85.7% and
58 of 69 = 84.1% — which share a = b, gamma = 120 deg in the conventional hexagonal
setting and cannot be separated by the box at any tolerance.
THAT IS THE WHOLE CLAIM: the partition is a stable, replicating property of the render convention. NO
ACCURACY MECHANISM IS ATTACHED TO IT. The stratified-accuracy claim that once was is REFUTED (see the
nulls section and Appendix S).





NOT PAIR-SPECIFIC. Excluding the trigonal/hexagonal metric class leaves n = 13 (5 triclinic,
3 orthorhombic, 3 tetragonal, 2 monoclinic; floor 0.3077). Three of four pixel models still drop
significantly — Gemini to 0/13, Grok p = 0.0127, Opus p = 0.0344 — and the RF control still does not
(p = 0.348). At n = 13 one structure is 7.7 points, so our own arm's drop is NOT significant there
(p = 0.140) though its point estimate is in the same direction, and the FLOOR also falls on those 13,
which is exactly why the control rather than the raw drop is load-bearing.

THE SECOND CUE IS PARTLY INVISIBLE, AND MOST OF WHAT IS HIDDEN IS REDUNDANT. Using the renderer's own
projection for exact ground-truth atom positions: MEDIAN total occlusion 0.5183, MEAN total 0.5699
(original) and 0.5900 (expansion) on stratified samples. Median and mean are stated separately
because the decomposition applies to the MEAN — component medians are not additive.
THE DECISIVE SPLIT IS NOT COINCIDENT-VS-OVERLAP BUT REDUNDANT-VS-INFORMATIVE. An occluder that is a
symmetry-equivalent copy of the atom it hides (same space-group orbit) hides NOTHING: seeing one copy
tells you everything about the other. Classifying every occluder that way:
    set          REDUNDANT   INFORMATIVE   TOTAL    redundant share
    original      0.3874       0.1825      0.5699       68.0%
    expansion     0.3902       0.1998      0.5900       66.1%
Two thirds of the occlusion is information-free, which fully explains why a sixteenfold radius reduction
moved nothing: the coincident component is radius-invariant AND was carrying no independent information.
THESE ARE PER-VIEW FIGURES AND ARE NOT A VISIBILITY LIMIT. An earlier version of this report read the
informative column as an "effective visibility limit of ~0.18-0.20"; that reading is WITHDRAWN. A per-view
figure counts an atom once per occluding view, while triangulation needs only two clear views. Measured
across all five: informative occlusion in EVERY view is 0.0001-0.0007, and only 0.26% (original) and
0.87% (expansion) of atoms have fewer than two clear views. The frozen protocol withholds under 1% of
atoms; see the adequacy section.
AN EARLIER COINCIDENCE-VS-DISC DECOMPOSITION IS RETIRED, not merely superseded. It reported total mean
occlusion 0.4891 with a 48.3% exact-coincidence share, computed on the FIRST 30 rows of the evaluation
file — which is ordered by crystal system, so that slice is triclinic/monoclinic only. Recomputing on
exactly those 30 reproduces 0.4891, confirming the cause. Only the stratified totals above appear
anywhere in this package.
WHY A RADIUS REDUCTION COULD NOT MOVE IT. We established the redundant component's dominance by trying
to REDUCE occlusion: a sixteenfold reduction in atom radii left the median pinned at 0.5000. Viewing
down a lattice vector stacks the 2x2x2 supercell copies onto identical points — measured
nearest-neighbour pixel distance 0.000 — and no disc size separates atoms that project to the same
pixel. The redundant component is therefore both RADIUS-INVARIANT and INFORMATION-FREE, which is the
full explanation of the failed manipulation and does not require the retired decomposition. Component
MEDIANS are not additive, only means are, so the split is reported in means.
SO A PIXEL MODEL HAS ONE UNRELIABLE CUE (an ambiguous box, on 34.8% of structures) AND ONE PARTLY
OBSCURED CUE (per-view informative occlusion 0.18-0.20, not the ~0.55 raw figure — a PER-VIEW
quantity, not a visibility limit; under 1% of atoms are untriangulable across the five views). What the
model does with that combination is measured in section 4, not predicted here: the earlier prediction
that models fall back on the box and collapse to the floor where it does not discriminate is
SUPERSEDED — it failed to replicate on the expansion set, and the disjointness result below shows the
box-ambiguous structures are not the occluded ones.
AND THE STRUCTURES THAT NEED THE MOTIF ARE NOT THE OCCLUDED ONES. Box-ambiguous structures are LESS
informatively occluded than box-sufficient ones: original 0.1576 vs 0.1949 (p = 0.395, NOT
significant), expansion 0.1512 vs 0.2216 (p = 0.034, significant). The direction replicates on both
samples and the significance on only one — the same pattern that broke the stratified accuracy claim,
so both p-values are stated wherever this appears. The stronger leg is the trigonal/hexagonal contrast
(0.1499 vs 0.2077, p = 0.022), a single test on pooled stratified data. So the two failure modes act on DIFFERENT structures — two mechanisms, not one —
and any intervention that restores motif visibility would be adding it where it is least needed.
AND RESTORING DEPTH WOULD RECOVER LITTLE OF IT. Degrading atom positions geometrically while keeping
the lattice (which the drawn edges supply), a flat projection recovers the crystal system on 0.238
(original) / 0.128 (expansion) of box-ambiguous view-measurements against 1.000 with full depth.
Quantized depth — what depth-graded colour delivers — moves that to 0.238 (no change) and 0.256
(doubled) respectively: branch D3 on one sample, D1 on the other, so the precondition holds on one set
and fails on the other. Even at 16 levels it closes at most ~13 of the ~75 available points, because
symmetry detection needs exact metric relations rather than order. NO LEVEL-COUNT RECOMMENDATION IS SHIPPED. Rerun at full
power (1260 view-measurements rather than 252), Q16 > Q8 > Q4 on all four strata and both paired steps
are significant (Q4->Q8 gained 11 lost 1, p = 0.0063; Q8->Q16 gained 6 lost 0, p = 0.0312), so quantization does not saturate at four or
eight within the tested range. The earlier flatness was a low-power artifact; the claim was stated
three times and is now withdrawn. And a rank-spaced depth cue is WORSE than no depth cue at all
(0.429 -> 0.262), because uniform spacing is a nonlinear distortion — so any depth grading must be
metric-faithful, not merely monotone.
NO CAUSAL CLAIM IS MADE FOR OCCLUSION. The pre-registered interaction test — improvement on the
box-ambiguous stratum, no change on box-sufficient — was NOT RUN, because the manipulation failed its
own mandatory check. All four of its branches remain unread and 3,780 API calls were withheld.
Occlusion is a geometric property of the renders with no demonstrated behavioural consequence.

THE CONFUSABLE PAIR, FROM BOTH SIDES. The direct arm and the chain arm confuse trigonal and
hexagonal in OPPOSITE directions — each collapsing one into the other. Because the directions are not
shared, the failure cannot be a learned bias inherited from a common source; what is shared is the
inability to separate the pair, which is the signature of a model reading the drawn cell outline well
and the atom motif poorly.

## 7. Where the failure lives, within sample and paired   [CP25, CP24]

THE HEADLINE IS WITHIN-SAMPLE AND PAIRED. The oracle is a deterministic geometric computation over
ground-truth positions and the frozen cameras, so it runs on the evaluation sets directly — 210
structures each, zero failures. That converts a cross-sample subtraction into a per-structure paired
comparison on the same named structures the models were scored on.

    ORACLE (ideal extraction, 5 views):  original eval 0.9524    expansion eval 0.9095

    ORIGINAL EVAL SET, n=210     arm     oracle    delta   oracle-only   arm-only    exact p
    A3 native-resolution        0.6905   0.9524   +0.2619       61           6       1.5e-12
    B1 direct                   0.6190   0.9524   +0.3333       76           6       1.6e-16
    V2b chain                   0.3810   0.9524   +0.5714      122           2       7.3e-34
    B3 chain                    0.2810   0.9524   +0.6714      145           4       5.7e-38

    EXPANSION EVAL SET, n=210
    B1 direct                   0.4524   0.9095   +0.4571      104           8       2.0e-22
    V2b chain                   0.4000   0.9095   +0.5095      118          11       8.6e-24

Every arm on both sets, p < 1e-11, with heavily one-sided discordance — on the original set the oracle
is right where the best arm is wrong on 61 structures against 6 the other way. Arm accuracies reproduce
the leaderboard values exactly, which confirms these are the same per-structure vectors.
WHAT IT LICENSES: on these exact 420 structures under the frozen protocol, ideal atom extraction
recovers the crystal system on 90-95% while the best model recovers 45-69%. The information IS present
in these renders and these models do not recover it — a statement about the model, not the render or
the data. WHAT IT DOES NOT: the oracle reads ground-truth coordinates, not the image, so this bounds
what is unrecovered GIVEN extraction and never shows a model could have extracted the positions from
pixels. The bottleneck is located upstream of symmetry reasoning, in perception.

THE EARLIER CROSS-SAMPLE VERSION IS SUPERSEDED, AND ONE OF ITS PROBLEMS WAS REAL. The cross-sample
gap was 0.1979, assembled from an oracle measured on a different 280-structure sample. Two checks on
that framing: the partition RATE was never a discrepancy (197/280 vs 137/210, Fisher p = 0.241, within
noise), but the stratum COMPOSITIONS do differ significantly — the oracle sample's ambiguous stratum is
96.4% trigonal/hexagonal against the evaluation set's 83.6% (p = 0.012), so part of that 0.1979 was
composition rather than unread information. Running the oracle within-sample was the fix, not a tidy-up.

For the record, the cross-sample stratified computation that motivated this:

    views   box-sufficient        box-ambiguous       difference   Fisher p
      2     0.9188 (181/197)      0.3253 ( 27/83)      -0.5935      <1e-4
      3     0.9645 (190/197)      0.7952 ( 66/83)      -0.1693      <1e-4
      4     0.9695 (191/197)      0.8554 ( 71/83)      -0.1141       0.0009   no K
      5     0.9695 (191/197)      0.8675 ( 72/83)      -0.1021       0.0022   no K

The gap shrinks monotonically with views (0.594 -> 0.102): most of the box-ambiguous deficit is
resolved by adding views, and what remains is small but statistically real. On that stratum ideal
extraction reaches 0.8554 while the best pixel model reaches 0.6575 (the native-resolution retrained
arm), the next best 0.5205, and the shape-free floor 0.4932 — so 0.1979 of accuracy is available to a
reader with the same views and perfect atom localisation, 0.3622 over the floor.
THE PRE-REGISTERED BRANCHES DID NOT FIRE and the result is reported between them. A clean "information
present, visible, unused" localisation needed the stratum gap to be within 0.10 AND non-significant; it
is 0.1141 at p = 0.0009. The opposite branch — the oracle also failing — is equally wrong, since 0.8554
is high and far above every pixel model. So the render DOES lose something on this stratum even given
perfect extraction: "mostly present" is supported, "fully present" is not.
TWO CONSTRAINTS THAT CANNOT BE DROPPED. The oracle's 280 structures have ZERO overlap with the
210-structure evaluation set carrying the model numbers and draw on a different source mix, so the
bracket is assembled across samples and is never a per-structure claim. And the model leg — pixel
models near the floor on box-ambiguous — FAILED TO REPLICATE on the expansion set, so any localisation
statement inherits that non-replication in the same sentence.

## 8. Nulls and withdrawals I — two classifiers refrozen   [CP28]

The lattice random forest and the box-sufficiency predicate were both cited without reproducible
specifications. The predicate is now fixed and reproduces CP25's 140/70 split EXACTLY. The forest is a
THIRD NON-RECOVERY: refitting under the recorded protocol gives 188/210 = 0.8952, and twelve defensible
readings of the recorded prose span 183-188 without reproducing the published 186. Forward
reproducibility is fixed; the historical value is not recovered.
RECOMPUTING THE STRATIFIED ROWS ON THE CANONICAL PARTITION CHANGES A PUBLISHED VERDICT. B1's stratified
drop was published at +0.1510, p = 0.037; on the canonical predicate it is +0.1143, p = 0.1318 — NO
LONGER SIGNIFICANT. That makes the original-sample leg a FOURTH independent failure of the stratified
claim, alongside the expansion-set sign reversal, the A3 null, and the RF control inversion.
  arm                    sufficient  ambiguous     drop   Fisher p
  A3 native-res K=8        0.7000     0.6714     +0.0286   0.7518
  B1 direct K=8            0.6571     0.5429     +0.1143   0.1318
  V2b chain K=8            0.3643     0.4143     -0.0500   0.5471
  B3 chain K=8             0.1857     0.4714     -0.2857   0.0000
  RF refrozen              0.9214     0.8429     +0.0786   0.0957   no K
THE B3 CHAIN ARM RUNS THE OTHER WAY at p = 3e-05, doing BETTER on ambiguous structures. That is the
opposite of the proposed mechanism and is recorded as an open observation rather than folded in.
V2b's identical macro-F1 across three seeds (macro_sd = 0.000) is DECODE COLLAPSE, not a seeding defect:
the three adapters differ by ~1.5% relative L2 over 43.6M parameters, where identical adapters would
give exactly zero. The 0.000 SD is removed rather than explained; no claim used it.

## 9. Nulls and withdrawals II — the replication reversal   [CP18_eval_expansion, CP16_paired_resolution]

We doubled the evaluation set — 210 new structures under the identical composition-exclusion rule,
zero leakage, verified — because a paired-McNemar audit showed the central comparison was
underpowered at n = 210. That audit also resized the expansion from the 1000-2000 a half-width screen
implied down to ~400, because a paired test uses only discordant items.

RESOLVED, AND THIS IS WHAT THE PAPER SHOULD LEAD WITH:
    our direct arm vs regularity floor   pooled n=420   d=+0.1476   133 vs 71 discordant   p=1.7e-05
    our direct arm vs chain arm          pooled n=420   d=+0.1452   179 vs 118             p=4.8e-04

NOT SUPPORTED, AND THIS MUST CARRY ITS SAMPLE:
    chain arm vs floor, original    n=210   d=-0.1476   p=1.34e-03  BELOW the floor
    chain arm vs floor, expansion   n=210   d=+0.1524   p=1.6e-03   ABOVE the floor
    chain arm vs floor, pooled      n=420   d=+0.0024   p=1.00      unresolved

Both halves are individually significant and point in OPPOSITE directions, so pooled they cancel.
The chain arm barely moved (0.3810 -> 0.4000) and our direct arm fell to 0.4524 on the harder
expansion structures; THE FLOOR MOVED FURTHEST (0.5286 -> 0.2476). The floor's three
features are size, density and volume — pure regularities — and the expansion structures are
systematically larger (median 22 against 14 conventional atoms, Mann-Whitney p = 9.9e-14), so the
correlation it exploits does not transfer.

This CORROBORATES the floor as a control while forbidding one way of quoting it. A baseline that
sensitive to sample composition is what "exploiting dataset regularities rather than reading shape"
predicts, and the differential transfer orders the methods by how much shape information each uses:
floor -0.281, direct arm -0.167, metric-reading RF -0.019. But 0.5286 is the floor ON THE ORIGINAL
SAMPLE, and every floor comparison must be a paired test on named structures, never a comparison
against a constant.

THE STRATIFICATION FAILED ITS OWN REPLICATION. On the expansion set the PARTITION reproduces almost
exactly (140/210 = 0.6667 box-sufficient against 137/210 = 0.6524, ambiguous stratum again ~83%
trigonal/hexagonal), so cue sufficiency is a stable property of the render convention. The stratified
ACCURACIES invert:
  arm            original drop    p        expansion drop    p
  our direct arm    +0.1510     0.037         -0.0500      0.557
  chain arm         -0.0250     0.766         -0.0429      0.554
  RF (control)      +0.0768     0.113         +0.1643      0.002
  floor             +0.0543     0.471         +0.0286      0.736
Our arm's drop REVERSES SIGN and loses significance, and the RF — the control whose whole role is not
to drop — becomes the ONLY significant dropper.
A THIRD INDEPENDENT INSTANCE, derivable from numbers already in the package and therefore stated here
rather than left for a reviewer to find. The native-resolution arm (A3) shows NO stratum drop on the
ORIGINAL set: overall 0.6905, box-sufficient 98/140 = 0.7000, box-ambiguous 47/70 = 0.6714, drop
+0.0286, Fisher p = 0.7518. Those strata are the APPROXIMATE 140/70 split, not CP15's recorded
137/73, because CP15's exact classifier is not recoverable; on a 137/73 split the same arm gives
0.7007 and 0.6712, drop +0.0295, p = 0.7541 — the same conclusion either way. So the stratified-accuracy claim now fails on three independent occasions — the expansion
set, the RF control's behaviour there, and the native-resolution arm on the original set. Three
instances is not a replication failure to explain away; it is the result. The cause is the floor again: it fell to 0.2286 on
that stratum, so "collapses to the floor" has no content there, and our arm sits +0.257 ABOVE it
rather than within 0.027. WE THEREFORE DO NOT CLAIM that pixel models generally collapse toward the
floor on box-ambiguous structures. That holds on the original sample, survives excluding the dominant
confusion pair, and fails to replicate on an independently drawn second sample. What replicates is
the partition itself.

## 10. Prior art, checked against primary sources   [CP43]

Eight named works were fetched from the arXiv API and read, not recalled. Three of our claims are
demoted and one of the plan's own characterisations is corrected.
CoT-degrades-visual-reasoning is PUBLISHED (2604.16060), so our direct-beats-chain result is a cited
replication on a new domain. Perception-not-reasoning is PUBLISHED almost verbatim (2605.20177:
performance "primarily limited by a lack of visual perception as opposed to reasoning itself").
THE CLOSEST NEIGHBOUR WAS NOT FLAGGED BY THE PLAN: 2506.13051 already runs a COMPOSITIONAL-EXCLUSION
benchmark over nine VLMs on crystallographic images with space-group validity scoring, so
composition-exclusion evaluation of VLMs on crystal images is NOT novel. And 2605.29446 (CrystalXRD-Bench)
already reports VLMs failing on rendered crystallographic images AND already separates extraction from
reasoning by supplying the CIF.
WHAT SURVIVES: the geometric oracle as an instrument — inverting the frozen cameras, re-solving
correspondence from element identity and ray geometry alone, running spglib on the reconstruction — the
orbit decomposition of occlusion at full coverage, and the measurement that the protocol withholds under
1% of atoms. One plan citation was MISCHARACTERISED: 2606.01558 confirms CoT degradation and proposes a
fix, so it supports our premise rather than demoting a claim.

THE THREE INSTRUMENT ROWS THAT WERE OPEN ARE NOW SEARCHED, AND TWO HAVE REAL OCCUPANTS.
RESOLUTION-VERSUS-RESEED is occupied as a general question: Res-Bench (2510.16926) benchmarks resolution
ROBUSTNESS over 14,400 samples and 12 resolution levels with explicit stability metrics, and 2506.12776
frames the same "Resolution Dilemma". Our resolution work is a domain instance and a CONFOUND CONTROL,
which is how it was always used, and is not claimed as a contribution.
THE CUE-SUFFICIENCY ROW IS DIRECTLY OCCUPIED, and this is the sharpest finding of the audit. CRYSPNet
(2003.14328) predicts Bravais lattice, SPACE GROUP and lattice parameters for inorganic materials by
machine learning. The numeric-cell-to-symmetry mapping our random-forest control performs is therefore a
PUBLISHED task with a published model, and the RF is presented as a REPRODUCTION of an established
capability rather than as our result. 2411.00803 trains CNNs on patterns computed from lattice parameters
and extinction laws and reports accuracy against a THEORETICALLY COMPUTED MAXIMUM — an information-ceiling
argument in a different modality (1D powder patterns), which is the closest methodological neighbour to our
oracle and is now cited as such.
THE ORACLE-ONLY CHECKER ROW IS ADJACENT, NOT OCCUPIED. 2603.16253 publishes exactly our motivating concern
for verifiers — a low step score may reflect a reasoning error OR the verifier's own misperception, and that
entanglement produces systematic false positives and negatives. We cite it as motivation. What remains ours
is that a DETERMINISTIC GEOMETRIC checker cannot misperceive, because it reads coordinates rather than
pixels, whereas every cited verifier is itself a learned model.
AUDIT SCOPE, STATED: THIRTEEN cited works over two passes — eight named prior works, then five more
closing the three instrument rows — from arXiv titles and abstracts. Not searched are non-arXiv venues and
pre-deep-learning crystallography, where a metric-to-symmetry lookup is likely classical textbook material
rather than a citable result.

## 11. Other results   [CP2, CP3, CP7, CP7b, CP9, CP10, CP11, CP12, CP17, CP1b, CP1c]

FABRICATION. The chain arm emits 30 distinct cell-parameter strings across 90 generations, one
recurring 22 times, and then reasons correctly from those fabricated premises. It is responsive to
the image without being informed by it: a 3.4x resolution increase moves its geometry step no more,
and in no better a direction, than changing the random seed.

CERTIFICATION. A chain scoring below the regularity floor identifies subsets of a stronger model's
answers that are correct 91.2% of the time (base rate 61.90% = 130/210, the same value as the leaderboard's 0.6190), because its errors are DECORRELATED
from the answerer's rather than because it is accurate. Three pre-registered tests bounded this: a
chainless certifier also works (p = 2.7e-04, so verification is NOT required); a second certifier
seed does not clear the bar, so no effect size is claimed on certified accuracy; and the
process-versus-outcome contrast is answerer-specific. On the seed-stable false-certification endpoint
a chain lowers the error rate roughly 32-fold against chainless, 0.77% against 25.0%.

PROCESS REWARD IS OUT OF SCOPE HERE. The dense-step-reward comparison and its mechanism analysis belong
to concurrent work by the same authors (anonymised), which tells that story with both domains in view. No
number from it crosses into this paper.

SCALING, ATTEMPTED AND FLAT. Training at native 768 px on doubled camera-augmented data reached
0.6619 against a pre-registered target of 0.666. The stopping rule fired against the direction we
were leaning, and no further runs were made.

TEST-TIME SCALING. A clean negative on both pre-registered hypotheses: no deployable selection rule
beat plain majority vote over the chain's own samples.

MEMORIZATION. Two attempts, closed unresolved and reported as such. The first split had most of its
evaluation inside the training data; the replacement was properly powered but its difficulty-matched
analysis did not survive error bars.

WHAT DID NOT WORK, REPORTED AS SUCH. A deterministic wireframe reader failed its own pre-registered
validation gate (median edge-ratio error 0.1021 against a 0.10 threshold, bimodal error
distribution), so its accuracy is recorded and NOT interpreted; re-reading the directive later
revealed it was also a simpler instrument than specified, and that scope deviation is recorded rather
than glossed. An atom-centroid detector reached median precision 0.233 and recall 0.400, also failing
its gate — but detection quality tracks occlusion (r = -0.792) far more than atom count (r = -0.411),
which is what a visibility limit looks like rather than a weak algorithm. A tempting ceiling estimate
was WITHDRAWN when 6 of 84 measurements exceeded the supposed bound, leaving the covariate ordinal
rather than quantitative.

SUBSUMED AND NOT-RUN CHECKPOINTS, recorded rather than left as silent gaps. CP10_merged_retrain's
pre-registered work was absorbed into the native-resolution scaling run above, and its second half
was cancelled because an earlier result had already answered the question it asked.
CP17_extractor holds the failed wireframe reader plus the scope-deviation record and the verified
pixel-projection calibration that CP19's detector depends on. CP11_expert_study is a not-run record
carrying the required limitations language verbatim.

NO HUMAN BASELINE  [CP11_expert_study]. The 50-structure expert packet was built with a pre-registered authenticity
screen. No qualified respondent returned it, and the single sheet received scored at chance and
failed four independent authenticity diagnostics. We therefore do NOT claim the renders are
human-solvable, and the "checkable by eye" framing is deleted rather than softened. The oracle
substitutes for the information question only.

## 12. What is open

VENUE. Both external reviews concluded the package is not a CVPR paper as written, because no method
contribution survived the refutations. The proposed replacement — a stage-by-stage attribution from
oracle through extractor to model arms and cue stratification — is a benchmark-and-diagnosis paper,
and NeurIPS Datasets & Benchmarks was named as deserving serious consideration. This is a team
decision and has not been made.

RENDER-CONVENTION SWEEP. Blocked, not merely queued: it is conditional on a working extractor
measured alongside the models on each convention, and no extractor has passed its gate.

THE OFF-AXIS CAMERA INTERVENTION IS CLOSED ON EVIDENCE, not left untested. Tilting off the principal
axes would break exact projective coincidence, and that is now known to be the wrong target: the
coincident component is INFORMATION-FREE (it hides symmetry-equivalent copies), it accounts for roughly
two thirds of raw occlusion, and removing it would therefore buy visibility of atoms whose information
was already available. Three further findings point the same way — box-ambiguous structures are LESS
informatively occluded than box-sufficient ones, so a visibility intervention lands where it is least
needed; ordinal depth restoration recovers at most a small share of the accessible gap; and a full
rotation was already measured to collapse accuracy to chance. We closed this intervention on free
geometric evidence before spending inference budget, which is the package's methodological argument
applied to itself.

THE INTRODUCTION is the one paper section not yet drafted.

## 13. Honest accounting of what went wrong

Recorded in the ledger at the point where each claim was made, not quietly fixed:
  - An expansion evaluation initially ran on renders missing the frozen 2x2x2 supercell. Caught
    because cubic accuracy was EXACTLY 0.000 across 27 structures; the resulting 0.4143 is void.
  - The ground-truth pixel projection took five attempts. The fourth passed a 2-atom cubic control at
    100% while being wrong, because that control has equal projected spans and cannot expose the
    letterboxing bug. Validate geometric transforms on the asymmetric case.
  - An environment blocker was recorded as "ALIGNN cannot be run" when the true constraint was one
    machine's CUDA requirement. Removing that requirement ran it in about an hour on CPU.
  - A related-work paragraph claimed all six cited methods "intervene", contradicted two lines later
    by our own descriptions of two that do not. Rewritten as three families.
  - A figure once attributed a tabular baseline's score to a coordinate GNN, reversing the conclusion
    a reader would draw.
  - A claimed "21 numbers verified" was scoped narrower than the sentence implied, and the correction
    to it was itself wrong before being computed properly.
  - Two different occlusion values appeared under one label because a gate used n = 40 and a sweep
    n = 25. Recomputed at matched n, which strengthened the conclusion.

---
APPENDICES R AND S HAVE MOVED. The retraction ledger and the superseded-results store now live in
paper/appendices_R_S.md, placed after the bibliography where they cost nothing against the page limit,
and are referenced from the reproducibility statement and the AI-use disclosure rather than from the main
text. The main text states each surviving position forward-facing — "the partition carries no accuracy
mechanism, on four independent tests" rather than a narration of what was claimed and withdrawn. The one
exception is the visibility-correction zero, which stays in the render-adequacy section with its
pre-registered control, because the control's behaviour is what makes the zero interpretable.

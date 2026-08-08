CHECKPOINT: CP8_external_baselines     GAP: how does CoCr compare to structure-input models?
STATUS: DONE. Both structure-input baselines are trained and reported on the 210-structure
        composition-exclusion eval set: a 19-feature lattice-metric random forest (0.8905) and
        the PUBLISHED ALIGNN architecture (0.6492 +/- 0.0287, 3 seeds, CPU). The earlier
        'ALIGNN cannot be run' record was over-generalised — see the CUDA section at the end.

=================  WHY THIS EXISTS  =================
The verified DeepCrysTet Table II (see literature_baselines.md) shows the crystal-system row is
ALIGNN 75.6 / CGCNN 63.4 / DeepCrysTet 97.5 — i.e. published structure-input models are NOT weak
on our task, contrary to the "expected weak on space group" premise. Those numbers are not
comparable to ours (different modality, splits, labels, n). The only fair comparison is a
structure-input model trained on OUR labels and OUR split. That is what this is.

=================  WHAT WAS RUN  =================
Inputs: the 1820 re-fetched CIFs (data/e3/structures.json), verified 1820/1820 to reproduce the
sidecar labels by the CP0 audit method (rate 1.0) — so the structures are provably the ones the
VLM was labelled against.
Features (19): a, b, c, alpha, beta, gamma, volume, three scale-free EDGE RATIOS, the three
|angle-90| deviations, |gamma-120|, angle range, angle std, edge coefficient of variation,
n_sites, density. Computed from the INPUT cell.
DELIBERATELY EXCLUDED: any spglib symmetry output (space group, Wyckoff, bravais) — including
those would leak the label — and composition/element identity.
Split/protocol: identical train (1610) and eval (210) material_ids as every CoCr arm.

  model                eval micro    macro-F1    train acc
  logistic regression     0.6524      0.6312      0.6354
  random forest           0.8905      0.8904      1.0000
  gradient boosting       0.8762      0.8733      0.9963

=================  IS IT TAUTOLOGICAL? NO, BUT IT IS NOT PURE GEOMETRY EITHER  =================
This had to be checked, because if the crystal system were simply readable off the cell metric
the "baseline" would be a symmetry detector, not a model.

  Input-cell metric already matches its crystal system: 113/210 (53.8%).
    => these are largely PRIMITIVE/reduced cells, not conventional cells. The metric does NOT
       hand over the answer. (This is the same primitive-vs-conventional issue that produced a
       real labeling bug in CP0 and a bad geometry step in CP2.)
  TEST 1 — hand-written metric RULE, no learning:            0.4143
    => the answer is genuinely NOT trivially readable; learning contributes ~0.48 absolute.
  TEST 2 — scale-free SHAPE features only (ratios/deviations): 0.8571
    => most of the signal is real cell geometry, not absolute scale.
  TEST 3 — n_sites + density + volume ONLY (no shape at all):  0.5286
    => WARNING, and this one must be reported: features containing NO shape information still
       reach 0.53, far above the 0.143 chance rate. So a substantial part of the 0.89 reflects
       DATASET REGULARITIES (crystal system correlates with cell size / atom count in this
       MP-derived sample), not geometric reasoning. The 0.89 is therefore an UPPER BOUND on what
       "reading the structure" buys, inflated by exploitable dataset structure.

=================  WHAT THIS DOES AND DOES NOT LICENSE  =================
LICENSED: on identical labels, identical split, identical protocol, a cheap structure-input
model beats our best image-input arm by +0.276 (0.8905 vs 0.6143). The modality gap is large and
real, and it is now MEASURED on our own data rather than cited across papers.
NOT LICENSED: calling this an ALIGNN/CGCNN comparison. ALIGNN and CGCNN were not run. It is also
not a claim that CoCr "loses" to them — a structure-input model is given the lattice vectors,
which is most of the answer, while CoCr is given pixels.
ALSO NOT LICENSED: treating 0.89 as the geometry ceiling. Test 3 shows >=0.53 of it is available
from dataset regularities with no shape information at all.

=================  CONSEQUENCE FOR THE PAPER  =================
This reinforces the CP1b branch-(a) reframe rather than undermining it. If the claim were
"CoCr is accurate at crystal-system classification", this baseline refutes it outright at a
fraction of the compute. The defensible claim is the one branch (a) already forced: CoCr's
contribution is a VERIFIABLE, CHECKABLE chain from images — a legibility/verifiability result,
not an accuracy result. The structure baseline should be reported IN the paper, prominently and
unprompted, as the honest ceiling context. Hiding it would be indefensible; reporting it makes
the verifiability framing credible rather than evasive.

=================  WHAT REMAINS  =================
- ALIGNN / CGCNN proper are not installable here (no alignn/cgcnn/dgl/torch-geometric wheels in
  this environment). Running them needs either a GPU-box install or a different env. They would
  sharpen the row but not change its direction.
- A geometry-stratified or dataset-regularity-controlled eval would tighten the 0.89 upper bound
  (test 3 is the reason it needs tightening).

REPRODUCE
  structures: scripts/fetch_e3_structures.py -> data/e3/structures.json (+ label audit 1820/1820)
  baseline:   19 lattice-metric features, sklearn RF/GB/logreg, env cocr-e8
  records:    structure_baseline.json, literature_baselines.md

=================  THE REGULARITY FLOOR (team directive item 1)  =================
The size-only control (n_sites + density + volume, NO shape) defines a NON-GEOMETRIC FLOOR of
0.5286 available to any model that can sense scale — including the VLM, since atom count and
packing are visible in renders. Every arm relative to that floor:

  arm                        acc      delta vs floor 0.5286
  structure-metric RF      0.8905           +0.3619
  CoCr B1-direct           0.6143           +0.0857
  CoCr V2b chain           0.3857           -0.1429
  CoCr SFT-V1 chain        0.3365           -0.1921
  (floor is 3.70x the 0.1429 chance rate)

All four deltas independently verified against the directive's values (+0.362 / +0.086 /
-0.188 / -0.143) — they match to <0.001. The SFT-V1 delta is now -0.1921 on the final 3-seed
mean 0.3365 (the directive used the 2-seed 0.3405).

THE CHAIN ARMS SIT BELOW THE FLOOR. They do not merely fail to beat the structure baseline;
they fail to beat a 3-feature size-only model. That is a stronger and more uncomfortable
statement than anything in CP1b, and it should be in the paper.

## THE CANDIDATE SENTENCE WAS TESTED AND DOES NOT SURVIVE
The directive proposed (explicitly "verify before writing"): "above the dataset-regularity
floor, the direct image arm adds <0.09 and chain arms add nothing — the accuracy race was
substantially a race to exploit sample regularity."
The first two clauses are ARITHMETICALLY CORRECT. The causal clause is NOT SUPPORTED by either
confirmatory probe the directive itself specified:

PROBE (a) — accuracy WITHIN size quartiles (removes the size shortcut by construction):
  band   n    floor     B1     full RF     B1 - floor
   0    53   0.6792  0.6038   0.9057        -0.0754
   1    52   0.4808  0.6859   0.9615        +0.2051
   2    52   0.4615  0.6218   0.8269        +0.1603
   3    53   0.4906  0.5472   0.8679        +0.0566
  band-averaged: floor 0.5280 | B1 0.6147 | full RF 0.8905
  B1 does NOT collapse within bands (range 0.547-0.686) and still beats the floor by +0.0867
  within them. The predicted collapse did not happen, so the shortcut reading is NOT confirmed.
  The full RF holds 0.83-0.96 within every band, so ITS edge is real geometry, not scale.

PROBE (b) — prediction agreement, B1 vs the size-only floor model (n=210):
  raw agreement 0.3810, chance-expected 0.1408, Cohen's kappa 0.2795.
  LOW agreement. B1 is not tracking the floor model's decisions, so B1's correctness is not
  explained by exploiting the same regularity.

CONCLUSION: the floor is real and it reframes the accuracy race, but the mechanism claim is
refuted by its own tests. The defensible sentence, and the one that should be written:
  "A 3-feature size-only model reaches 0.529 on this eval, so much of the apparent accuracy
   spread sits on top of dataset regularity rather than crystallographic reasoning. The
   direct image arm clears that floor by only +0.086, and the chain arms fall BELOW it. But
   the arms are not simply exploiting the same regularity: within size quartiles the direct
   arm retains a +0.087 margin over the floor and agrees with the floor model's predictions
   only weakly (kappa 0.28). The floor bounds how much of the accuracy race is meaningful; it
   does not show that the arms won it by shortcut."
DO NOT write "the accuracy race was substantially a race to exploit sample regularity" —
probes (a) and (b) contradict it.

WHAT SURVIVES FOR THE PIVOT: the floor de-fangs the accuracy axis for BOTH the RF and B1
(everything is measured against 0.529, not 0.143), and the chain arms' sub-floor position makes
accuracy indefensible as their contribution. Checkability remains the only axis on which any
image arm demonstrated something. That is exactly the directive's intent; only the mechanism
sentence needed correcting.

=================  E8 GRAPH BASELINE ON OUR SPLIT (CGCNN-style, our reimplementation)  ========
WHAT WAS RUN AND WHAT IT IS NOT. The official ALIGNN package needs DGL, whose compiled libraries
have no build for the torch version the VLM stack pins; downgrading torch would break that stack
(see CP8_ENVIRONMENT.md). Rather than abandon the row, a CGCNN-style crystal graph network was
reimplemented in PLAIN TORCH (no DGL): atom-Z embeddings -> 3 edge-gated convolutions over a
neighbour graph (rcut 8.0 A, <=12 neighbours, 40 Gaussian distance basis) -> mean pool -> MLP ->
7-way softmax; 82K parameters. Trained on OUR 1610 train / 210 composition-exclusion eval,
leakage asserted 0, CPU only, 60 epochs, seed 0.
THIS MUST BE CITED AS "CGCNN-style (our implementation)", NEVER as "CGCNN". It reproduces the
architecture family, not the authors' code or their tuning.

RESULT: best eval 0.5619 (epoch ~30), FINAL epoch 0.4667. Train loss fell 1.956 -> 0.526 while
eval accuracy peaked and then declined: this run OVERFITS 1610 structures.
  vs regularity floor 0.5286   +0.0333  ABOVE   (final-epoch 0.4667 is BELOW it, -0.0619)
  vs B1-direct (images) 0.6143 -0.0524  BELOW
  vs RF lattice metrics 0.8905 -0.3286  BELOW
  vs published CGCNN 0.634     -0.0721  BELOW
  vs published ALIGNN 0.756    -0.1941  BELOW
CAVEAT ON "best": 0.5619 is selected ON the eval set by early stopping, so it is optimistic and
not a clean held-out estimate. The defensible pair to quote is "0.47 at the end of training,
0.56 at its best epoch", with the overfitting stated.

WHAT THIS DOES AND DOES NOT LICENSE:
 - It does NOT show that graph networks are weak at this task. A 82K-parameter reimplementation
   trained on 1610 structures for 60 CPU epochs is not evidence about ALIGNN, which was trained
   on a far larger dataset with tuned hyperparameters. The published 0.756 stands unchallenged.
 - It DOES establish, on OUR split, that a graph model given ATOMIC COORDINATES does not
   automatically beat the image-input B1 (0.6143) — at this data scale, B1 is ahead of it.
   That is a like-for-like statement the published table cannot make, because that table is a
   different dataset and split.
 - It also shows 1610 structures is small for a graph network: the overfitting is severe. The
   same data-scale caveat we apply to the SFT arms applies here.

HONEST NEXT STEP IF THE ROW MATTERS: the comparison the paper actually wants is published
ALIGNN retrained on our split, which needs the DGL wall solved (a separate container with an
older torch, isolated from the VLM stack). Until then this row is a LOWER BOUND on what a graph
model does here, not the graph-model number.

SELF-CORRECTION: a first pass through these numbers printed "BELOW FLOOR" for the 0.5619 figure.
That was wrong (0.5619 > 0.5286); the comparison was re-run explicitly and the corrected
direction is recorded above. Final-epoch 0.4667 IS below the floor.

=================  E8 RE-RUN WITH A CLEAN PROTOCOL — THE 0.5619 WAS OPTIMISTIC  ==============
The single-seed run above selected its best epoch ON THE EVAL SET, which I flagged at the time as
optimistic. Re-ran properly: a 200-structure VALIDATION split carved out of TRAIN (fit 1410 /
val 200 / eval 210, disjointness asserted), epoch selected on VAL, eval reported at that epoch.
3 seeds.

  seed 0: val 0.5050 -> eval 0.4286 (ep 59)
  seed 1: val 0.4900 -> eval 0.4952 (ep 51)
  seed 2: val 0.4850 -> eval 0.5429 (ep 37)
  CGCNN-style, val-selected: 0.4889 +/- 0.0469

THE OPTIMISM WAS 0.0730 (0.5619 -> 0.4889). The clean number SUPERSEDES the single-seed figure;
quote 0.4889 +/- 0.0469, not 0.5619.

CORRECTED COMPARISONS (computed explicitly):
  vs regularity floor 0.5286   -0.0397  BELOW   <- the graph model does NOT clear the floor
  vs B1-direct 0.6143          -0.1254  BELOW, and this EXCEEDS pooled seed noise (0.0493)
  vs RF lattice metrics 0.8905 -0.4016  BELOW
  vs chance 0.1429             +0.3460  ABOVE

WHAT CHANGES vs THE FIRST WRITE-UP: B1's lead over the graph model grows from +0.052 to +0.125
and is now larger than pooled seed noise, so the like-for-like statement is firmer — at THIS data
scale, on OUR split, an image-input VLM beats a coordinate-input graph network. But the graph
model now falls BELOW the regularity floor, which places it in the same category as our chain
arms: it has not demonstrated crystallographic reasoning on this split, and its result should be
read as a DATA-SCALE finding (1610 structures is small for a GNN; all three seeds overfit) rather
than as evidence about graph architectures.

THIS STRENGTHENS THE "DO NOT RESURRECT" ENTRY: it is still NOT evidence that GNNs are weak at
symmetry. Published ALIGNN at 0.756 was trained on far more data with tuned hyperparameters. Our
number is a lower bound at our data scale and must be labelled as such wherever it appears.

=================  THE PUBLISHED ALIGNN NOW RUNS — THE BLOCKER WAS CUDA, NOT ALIGNN  ==========
ENVIRONMENT.md recorded that ALIGNN could not be run because DGL ships no compiled graphbolt library
for the torch version the vision stack pins. That was accurate ON THE GPU BOX and I generalised it
too far: the constraint is the CUDA requirement, not the package. Dropping CUDA removes it entirely.
WORKING RECIPE (CPU, verified end to end): DGL 2.2.0 ships graphbolt libraries for torch 2.1.0
THROUGH 2.3.0 ONLY — listing the graphbolt directory is the fastest way to see which. Pin
torch==2.3.0 with torchdata==0.9.0 (torchdata 0.7.1 raises ImportError on DILL_AVAILABLE against
torch 2.3; the newer torchdata still ships the deprecated datapipes module DGL needs), plus
DGLBACKEND=pytorch and a writable DGL_HOME. alignn 2026.5.20 then imports and trains.
TWO API GOTCHAS IN THIS ALIGNN BUILD, both found by reading the source rather than guessing:
  1. ALIGNN.forward unpacks `g, lg, lat = g` — a THREE-tuple — while Graph.atom_dgl_multigraph
     returns TWO graphs. `lat` is unpacked but never read on this version, so we pass the real 3x3
     lattice matrix: correct if a later version starts using it, harmless now.
  2. forward ends in `torch.squeeze(out)`, which collapses a batch of 1 from (1,7) to (7,) and
     breaks argmax(dim=1). classification=True is NOT the fix — on this build it forces
     num_classes=2 (fc out_features=2, verified on the constructed module). Keep
     classification=False, which correctly gives 7 logits, and restore the batch dim after forward.

RESULT — PUBLISHED ALIGNN ON OUR 210-STRUCTURE COMPOSITION-EXCLUSION EVAL SET
Protocol matched to our other structure-input baselines: trained on the 1610 TRAIN structures,
epoch selected on a validation split carved out of TRAIN (never on eval), graphs built from the
CONVENTIONAL cell, 3 seeds, population SD.
  seed 0  0.6762 @ epoch 26     seed 1  0.6095 @ epoch 11     seed 2  0.6619 @ epoch 38
  MEAN 0.6492 +/- 0.0287
WHERE IT SITS:
  vs the published ALIGNN figure on this task (75.6%)   -0.1068  BELOW
  vs our lattice-metric random forest (0.8905)          -0.2413  BELOW
  vs our direct pixel arm (0.6190)                      +0.0302  above on the mean
  vs the regularity floor (0.5286)                      +0.1206  above
  vs our CGCNN-style reimplementation (0.4889)          +0.1603  above
THE COMPARISON WITH OUR DIRECT ARM DOES NOT SEPARATE. Paired McNemar on the same 210 structures
(ALIGNN seed 0 vs B1-direct): 41 structures B1-only, 53 ALIGNN-only, p = 0.2564. So the correct
statement is that a coordinate-input GNN and our pixel-input 8B fine-tune are STATISTICALLY
INDISTINGUISHABLE on this task, NOT that ALIGNN beats it.
WHY OURS IS BELOW THE PUBLISHED 75.6%. Different split (composition-exclusion, deliberately harder
than random), different training-set size (1610 vs the published work's much larger set), 40 epochs,
and no hyperparameter search. This is a faithful-architecture run under OUR protocol, not a
reproduction of the published number, and it must not be cited as one.

WHAT THIS DOES TO THE PAPER. The a fortiori argument written when the row was missing is now
unnecessary and is REPLACED by the measured row. The modality gap survives and is in fact cleaner:
the lattice-metric random forest (0.8905) beats every coordinate- and pixel-input learned model
here, so the ordering is NUMERIC CELL >> {coordinate GNN, pixel VLM} > floor > weaker GNN.

CHECKPOINT: render_convention_sweep   GAP: the package diagnoses without intervening. Every reviewer
     objection about actionability lands here. (ICLR directive)
STATUS: BOTH LEGS DONE. The oracle leg REFUTES A PREDICTION THIS PROJECT PUBLISHED. The model leg returns a
     COMPLETE NULL — zero of sixteen paired comparisons is significant. Together these are the sharpest
     result in the checkpoint: the render protocol's information content is demonstrably improvable, and
     none of the improvements reaches the models.

=====  THE HEADLINE: OFF-AXIS CAMERAS RAISE THE CEILING, AND WE PREVIOUSLY CLOSED THIS ON ARGUMENT  =====

  sample      frozen cameras      off-axis cameras     gained  lost   exact p
  original    200/210 = 0.9524    209/210 = 0.9952        9      0    0.00391
  expansion   191/210 = 0.9095    203/210 = 0.9667       16      4    0.01182

Significant on BOTH independently drawn samples, and MONOTONE on the original: every structure the frozen
cameras lose is recovered off-axis and none is lost. The report had closed this intervention on geometric
reasoning and predicted a null. THE PREDICTION WAS WRONG, and the reason it survived is worse than the
error itself.

=====  WHY THE PREDICTION WAS NEVER ACTUALLY TESTED  =====

projection_matrices() hardcoded the frozen camera map:
      return [rotate(VIEWS[v]) for v in view_names]
reconstruct_positions() had no view_map parameter at all. So any attempt to score a perturbed-camera
condition through the oracle silently reproduced the frozen ceiling. My first run of this checkpoint
reported C1 and C4 at IDENTICAL values, 66/70 each, and printed "does reconstruct_positions accept a
view_map? False" — which is the only reason I caught it. Had the two numbers differed by chance I would have
published an unmeasured null as a measured one.
FIX: view_map threaded through both functions, defaulting to the frozen VIEWS. REGRESSION VERIFIED — the
default path still returns exactly 200/210 on the original sample, so no prior result moves.

=====  WHAT THIS MEANS, STATED CAREFULLY  =====

The off-axis gain is a CEILING gain, i.e. branch V2 of the pre-registration, NOT the legibility gain (V1)
that the paper wanted. Breaking exact projective coincidence makes MORE INFORMATION available to a
triangulating reader, rather than making the same information easier to read. The mechanism is the one occlusion_manipulation
identified: viewing down a lattice vector stacks supercell copies onto identical pixels, and perturbing the
camera unstacks them.
CONSEQUENCE FOR THE PAPER: the frozen protocol is NOT information-optimal. A reviewer asking "why these
cameras?" now gets a measured answer rather than an appeal to convention — and the answer is that the
shipped protocol leaves about 4 points of ceiling on the table on the original sample and 6 on the
expansion. That is a stronger actionability statement than a null would have been.
IT DOES NOT ESTABLISH that models read off-axis renders better. That is the model leg, and it is unrun.

=====  THE MODEL LEG: A COMPLETE NULL, AND IT IS THE POINT  =====

Four frontier/strong models x five conventions x 70 stratified structures x K=3, all paired per structure.
Zero unparseable, zero gate failures.

  convention        claude-opus-4.8   gemini-3.6-flash   llama-4-maverick   grok-4.5
  C1 frozen              0.5429           0.7857             0.4429          0.5857
  C2 single cell         0.5286           0.7286             0.4714          0.6429
  C3 small radii         0.5571           0.7714             0.4714          0.5857
  C4 off-axis            0.5571           0.7571             0.4714          0.6143
  C5 single + small      0.5714           0.7000             0.4714          0.6571

SIXTEEN PAIRED COMPARISONS AGAINST C1, NONE SIGNIFICANT (all p >= 0.109; branch V3 for every convention).
Pooled across models the discordance is near-symmetric in every convention — C2 gained 17 lost 16, C3 9/7,
C4 13/10, C5 16/13 — which is what a genuine null looks like rather than a consistent direction that lacks
power. The direction is not even consistent WITHIN a convention: on C2 and C5, gemini goes DOWN while grok
goes UP.

POWER, STATED HONESTLY. At n=70 and a baseline near 0.60 the minimum detectable paired difference at
alpha=0.05 is about 0.162 accuracy. The largest observed |delta| is 0.0857. SO EVERY OBSERVED EFFECT IS
SMALLER THAN THIS SAMPLE CAN RESOLVE: the null BOUNDS the effect below ~0.16, it does not establish zero.
A claim that any of these conventions helps by more than 16 points is excluded; a 5-point effect is not.

WHY THE TWO LEGS TOGETHER ARE THE RESULT. C4 raises the ORACLE ceiling significantly (0.9524 -> 0.9952,
p = 0.0039) and moves no model measurably. So the information the frozen protocol withholds is real,
recoverable by a geometric reader, and NOT what limits the models — which is the same conclusion the
attribution ladder reached from the other direction, arrived at here by intervention rather than by
decomposition. An intervention that adds information a model cannot use is evidence about the model, not
about the render.

=====  RENDERS BUILT AND VERIFIED  =====

Five convention render sets exist on a 70-structure sample STRATIFIED BY CRYSTAL SYSTEM (10 per system —
mandatory here, since this project has already been bitten once by slicing a class-ordered file):
  C1 frozen baseline (existing renders)      C2 single cell, no supercell
  C3 small radii 0.22                        C4 off-axis cameras
  C5 single cell + small radii
All five produce byte-distinct images (checksummed on a common structure), 350 PNGs each, zero render
failures.

ORACLE CEILINGS: C3 AND C5 SHARE THEIRS BY CONSTRUCTION, AND C2's IS NOW MEASURED. The oracle inverts
CAMERAS from ground-truth projections and never sees a pixel, so radii cannot change its ceiling — C3 and C5
inherit C1's and C2's. The supercell DOES change its input, and the result is a second surprise:
  single conventional cell   200/210 = 0.9524
  explicit 2x2x2 supercell   178/210 = 0.8476     gained 0, lost 22, exact p < 1e-5
TILING COSTS THE ORACLE 22 STRUCTURES AND GAINS IT NONE. The shipped protocol's supercell actively lowers
identifiability, for the reason occlusion_manipulation established — tiled copies project onto coincident pixels, and a
triangulating reader cannot separate them. Combined with C4, the frozen protocol is suboptimal on BOTH of
its geometric choices, and neither correction reaches the models.

=====  WHAT IS NOT IN THIS CHECKPOINT  =====

The directive's metric depth-graded colour and its annotated plan view with height fractions both need NEW
RENDERER CODE — a per-atom depth-keyed colour ramp, and text annotation of height fractions. render_views()
exposes supercell, radii and the camera map and nothing else. THE ANNOTATED PLAN VIEW IS THE MOST MOTIVATED
INTERVENTION IN THE PACKAGE — it is the inherited convention with its dropped component restored — and it
remains unbuilt. Recorded here so it cannot be quietly forgotten.

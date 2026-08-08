CHECKPOINT: CP21_occlusion_redundancy   GAP: is the occlusion the paper reports actually hiding
                                        INFORMATION, or is it hiding copies of what is already
                                        visible? (directive Stage 0a, "the decisive one")
STATUS: DONE, BRANCH R3 (MIXED) ON BOTH EVALUATION SETS. ALL NUMBERS BELOW ARE FROM
        STRATIFIED SAMPLES - see the SAMPLING DEFECT section; a first pass used the first 40 rows
        of eval.jsonl, which is ORDERED BY CRYSTAL SYSTEM and gave an all-triclinic/monoclinic
        slice. Every figure was recomputed. About 61-64% of occlusion is REDUNDANT.
        The pre-registered classification RULE had a defect that I found and fixed mid-analysis;
        the fix is what reconciled the two samples. Read the rule-defect section — the first
        version of this analysis would have produced a spurious cross-sample finding.

=================  THE RESULT  ===============================================================
Corrected rule (symmetry-orbit equivalence), 40 structures x 3 axis views per set:
  set          REDUNDANT   INFORMATIVE   TOTAL    redundant share   branch
  original      0.3013       0.1954      0.4967       60.7%          R3 MIXED
  expansion     0.4388       0.2509      0.6897       63.6%          R3 MIXED
Pre-registered thresholds were R1 < 0.15 informative, R2 > 0.30, R3 between. BOTH SETS LAND IN R3,
and the redundant share is stable across two independently drawn samples with very different cell
conventions — which is the reassurance the standing "measure on both sets" discipline exists to give.

WHAT R3 REQUIRES US TO SAY. The effective visibility limit is the INFORMATIVE component only:
roughly 0.20 (original) to 0.25 (expansion) of atom centres, NOT the 0.4891 total previously
reported. Most occlusion hides a symmetry-equivalent copy of an atom that is visible elsewhere in
the same image, and seeing one such copy tells you everything about the other. The paper must
report informative occlusion as the quantity of interest and keep the total only as a decomposition.
THIS ALSO FULLY EXPLAINS CP20's FAILED MANIPULATION. A sixteenfold radius reduction could not move
the median because the coincident component is radius-invariant — and that component was largely
carrying no independent information anyway. The intervention was aimed at the redundant part.
CONSEQUENCE FOR THE PROPOSED DEPTH-RESTORATION LADDER (Stage 1): its expected payoff is bounded by
the INFORMATIVE component, ~0.20-0.25, not by 0.4891. It is still worth running, but as a test of a
smaller effect than the raw occlusion figure implies, and the pre-registration must say so.

=================  THE RULE DEFECT, AND WHY IT MATTERS MORE THAN THE RESULT  ==================
The pre-registered rule classified an occluder as redundant if it was the same species AND AN INTEGER
LATTICE TRANSLATE of the occluded atom in the conventional frame. Run that way, the two sets
DISAGREED sharply and would have landed in different branches:
  original  informative 0.1989 -> R3        expansion  informative 0.4594 -> R2
I did not report that as a finding, because the split had a suspicious cause. Tracing it:
  - 0% of ORIGINAL-set structures are re-standardized by conventional_cell (their input cells were
    already conventional); 84% of EXPANSION-set structures are, at a median 4x atom multiplication
    (their input cells were PRIMITIVE).
  - Exact pixel-tie rate down axis_c follows: 0.023 original vs 0.680 expansion, a ~30x difference.
  - Mechanism: a primitive->conventional standardization introduces CENTRING translations
    (1/2,1/2,1/2 and similar). Copies related by a centring translation coincide in projection but
    are NOT integer translates in the conventional frame, so the integer-only rule called them
    INFORMATIVE.
A centring translate is a symmetry operation of the lattice, so the atom it hides IS
symmetry-equivalent and IS redundant in exactly the sense the analysis cares about. The
pre-registered rule therefore UNDERCOUNTED redundancy on every centred lattice. That is a defect in
my rule, not a property of the data, so I fixed the rule rather than reporting the artifact:
redundancy is now decided by SPACE-GROUP ORBIT (spglib equivalent_atoms, symprec 1e-3), which counts
centring translates correctly. Index mapping from tiled atom to conventional site was verified
before use (species agree at every index, 224 tiled atoms over 28 sites).
RULED OUT AS EXPLANATIONS for the original discrepancy, each checked rather than assumed:
  - atom count: corr(informative occlusion, conventional atoms) = 0.126, and the discrepancy
    SURVIVED restriction to a matched 12-30 atom band (0.2164 vs 0.5144, MW p < 1e-4);
  - species count: corr = -0.135 and non-monotone across 2/3/4 species, so not a diversity effect.
LESSON FOR THE RECORD. A pre-registered rule can be WRONG rather than merely strict, and a
cross-sample disagreement is the symptom that should trigger auditing the rule before publishing the
disagreement. Both branches were fixed in advance, which is what made the disagreement visible
instead of absorbable.

=================  0d — ARE THE TWO FAILURE MODES THE SAME STRUCTURES? NO  ====================
The directive asked whether occlusion is worst for trigonal/hexagonal, which would collapse the
box-ambiguity mechanism and the visibility mechanism into one.
  trigonal/hexagonal  n=33   informative 0.1715   total 0.5660
  all others          n=207  informative 0.2314   total 0.5976
  Mann-Whitney p = 0.0766 — NO significant difference, and the point estimate runs the OTHER way
  (trigonal/hexagonal are slightly LESS informatively occluded).
So the box-ambiguous structures are NOT the most occluded ones. The two failure modes are distinct
and the paper has two mechanisms, not one. This is the answer the directive said would matter either
way, and it went against the collapse hypothesis.
PER-SYSTEM (pooled, corrected rule): cubic carries the most occlusion of both kinds (redundant
0.4619, informative 0.2831, total 0.7450) — expected, since high symmetry means more
symmetry-equivalent copies to stack. Triclinic carries the least redundant occlusion (0.2663), also
expected: with no symmetry beyond translation there are fewer equivalent copies.

=================  WHAT IS AND IS NOT ESTABLISHED  ===========================================
ESTABLISHED: the occlusion total decomposes into a ~61-64% redundant majority and a ~20-25%
informative remainder, stably across two samples; the informative remainder is the correct
visibility figure; trigonal/hexagonal are not preferentially occluded.
NOT ESTABLISHED: any behavioural consequence. This is geometry. CP20's manipulation check failed, so
no occlusion component has been shown to affect model accuracy, and nothing here changes that.

=================  SAMPLING DEFECT FOUND MID-ANALYSIS, AND WHAT IT CHANGED  ===================
The first pass took `rows[:40]` of eval.jsonl. THAT FILE IS ORDERED BY CRYSTAL SYSTEM: the first 40
rows are 30 triclinic and 10 monoclinic, zero of the other five systems. It was caught by a
consistency check rather than by inspection — the box-sufficiency rate on that slice came out 0.975
against the recorded 0.652, which is impossible for a random subsample.
Everything was recomputed on a STRATIFIED sample (6 structures per system, 42 structures, 126
view-measurements per evaluation set). The corrected figures:
  set          REDUNDANT   INFORMATIVE   TOTAL    redundant share   box-sufficient
  original      0.3874       0.1825      0.5699       68.0%            0.667
  expansion     0.3902       0.1998      0.5900       66.1%            0.690
The two samples now agree closely on every quantity, and box-sufficiency lands at 0.667/0.690 against
the recorded 0.652 — consistent, where the biased slice was not. BRANCH R3 STILL HOLDS on both, and
the redundant share is if anything HIGHER (66-68% rather than 60-64%).
LESSON: a jsonl written system-by-system looks like a list and slices like a stratum. Any subsample
of these files must be stratified, and the cheapest check is whether a known aggregate (here
box-sufficiency) reproduces on the subsample.

=================  0e — REDUNDANCY x STRATUM: THIS WEAKENS THE METHOD'S PREMISE  ==============
The proposed render-optimisation method argues that box-ambiguous structures NEED the motif, so
restoring motif visibility should help them specifically. That predicts box-ambiguous structures are
MORE informatively occluded. They are LESS:
  set          box-sufficient   box-ambiguous    difference    Mann-Whitney p
  original        0.1949           0.1576          -0.0373        0.395  n.s.
  expansion       0.2216           0.1512          -0.0704        0.034  significant
C2 — SIGNIFICANCE ON ONE SAMPLE OF TWO, AND THIS MUST BE STATED EVERY TIME. The DIRECTION replicates
across both samples; the SIGNIFICANCE does not (original p = 0.395, expansion p = 0.034). That is the
identical pattern that killed the CP15 accuracy claim, so this checkpoint cannot present the
disjointness result as established while CP15's non-replication is offered as a cautionary tale. BOTH
p-VALUES APPEAR WHEREVER THE CLAIM APPEARS. The STRONGER LEG is the trigonal/hexagonal contrast
(0.1499 vs 0.2077, p = 0.022), which is a single test on pooled stratified data rather than a
direction-replicates-significance-does-not pair. So the structures that most need the
motif are the ones whose motif is LEAST hidden.
CONSEQUENCE, STATED PLAINLY: the mechanism the method proposes to fix — hidden motif blocking the
answer on box-ambiguous structures — is not supported by the geometry. Depth restoration would be
adding visibility where it is least needed. This does not kill Stage 1, but it removes the specific
interaction prediction that made Stage 1 a sharp test, and any pre-registration must now predict a
UNIFORM effect rather than a box-ambiguous-concentrated one. The four-branch reading written for the
withdrawn interaction test is no longer the right instrument.

=================  0d — TWO MECHANISMS, NOT ONE (stratified, and now SIGNIFICANT)  ============
  trigonal/hexagonal  n=72   informative 0.1499
  all others          n=180  informative 0.2077
  Mann-Whitney p = 0.0219 — SIGNIFICANT, and trigonal/hexagonal are LESS informatively occluded.
The box-ambiguous structures are not the most occluded; they are among the least. The two failure
modes are DISTINCT and act on different structures, so the paper has two mechanisms rather than one.
The unstratified first pass gave p = 0.077 in the same direction, so the conclusion is unchanged but
the stratified test is the one to cite.
PER-SYSTEM informative occlusion (stratified, pooled, 36 measurements each): cubic 0.2976,
triclinic 0.2253, trigonal 0.2047, monoclinic 0.1961, orthorhombic 0.1805, tetragonal 0.1387,
hexagonal 0.0950. Cubic is worst, consistent with high symmetry producing more equivalent copies to
stack; hexagonal is best, which is why the trigonal/hexagonal stratum is the least occluded.

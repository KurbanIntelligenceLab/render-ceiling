CHECKPOINT: eval_expansion   GAP: resolve the comparisons paired_resolution showed are underpowered at
                                  n=210 (review item 5)
STATUS: BOTH ARMS DONE. The primary question is RESOLVED. The V2b arm returned a result that
        MATERIALLY QUALIFIES the paper's below-floor claim and must not be glossed. The expansion also
        produced an unplanned result that changes how the regularity floor must be described.

=================  THE PRIMARY RESULT: B1 vs THE FLOOR IS NOW RESOLVED  =======================
paired_resolution showed B1-vs-floor was NOT resolved at n=210 (paired McNemar p = 0.0814) and projected that
n = 400-500 would resolve it. That projection was correct.
  sample                    d(acc)    discordant    paired p     verdict
  original      n=210      +0.0905     63 vs  44    8.1e-02    unresolved
  expansion     n=210      +0.2048     70 vs  27    1.5e-05    RESOLVED
  POOLED        n=420      +0.1476    133 vs  71    1.7e-05    RESOLVED
The paper's central claim — that the direct-answer arm clears the shape-free regularity floor while
both chain arms fall below it — now rests on a resolved test rather than a direction.

=================  THE UNPLANNED RESULT: THE FLOOR IS NOT A STABLE CONSTANT  ==================
Absolute accuracies on the two 210-structure halves, all under identical protocols:
  model                       original    expansion    change
  RF, 19 lattice features       0.8857      0.8667     -0.0190
  B1-direct (ours)              0.6190      0.4524     -0.1666
  REGULARITY FLOOR, 3 feats     0.5286      0.2476     -0.2810
THE FLOOR FALLS THE FURTHEST. Its three features are size, density and volume — pure regularities
with no shape information — and those regularities are SAMPLE-SPECIFIC. The expansion structures are
systematically larger (median 22 vs 14 conventional atoms, Mann-Whitney p = 9.9e-14, drawn as 176 vs
116 atoms after the frozen 2x2x2 tiling), so the size-to-system correlation the floor exploits does
not transfer. B1's perception transfers better; the RF, which reads the actual cell metric rather
than bulk statistics, transfers almost perfectly (-0.019).
CONSEQUENCE FOR THE PAPER. "0.5286" must be reported as THE FLOOR ON THE ORIGINAL 210-STRUCTURE
SAMPLE, not as a property of the task. Any sentence of the form "X falls below the 0.5286 floor"
must name the sample. The floor's VALUE moves with sample composition; what is stable and what the
paper actually needs is the PAIRED ORDERING, which is resolved in both halves independently.
This strengthens rather than weakens the floor construct: a baseline whose accuracy is that
sensitive to sample composition is exactly what "exploiting regularities rather than reading shape"
predicts, and it is direct evidence that the floor is measuring what we claimed.

=================  WHY THE HARDER SAMPLE CANNOT CONFOUND THE PRIMARY TEST  ====================
The expansion set is measurably harder for every method, so B1's absolute drop (0.6190 -> 0.4524) is
NOT evidence of out-of-distribution failure and is not reported as such. But the B1-vs-floor test is
PAIRED ON THE SAME STRUCTURES: a harder sample lowers both arms, and the test only asks which one is
right when they disagree. That is why the margin can widen while both absolute numbers fall, and it
is why the resolved verdict stands despite the composition difference.
The composition difference itself is reported, not hidden: it arises because candidate selection
took any MP structure with <= 40 sites carrying a reserved element, and the reserved-element pool
skews toward larger cells. A matched-complexity expansion would be the cleaner design and is the
stated limitation.

=================  A VOIDED FIRST ATTEMPT, RECORDED  ==========================================
The first expansion run gave B1 = 0.4143 with CUBIC ACCURACY OF EXACTLY 0.000 across 27 structures
and not one "cubic" prediction in 210. That was a defect, not a result: my render loop omitted the
frozen E0.5 config's 2x2x2 SUPERCELL, so the models saw single cells having only ever been trained
on tiled ones. Renders regenerated with supercell=(2,2,2); the 0.4143 figure is VOID and appears
here only as the diagnostic that exposed the defect. See render_config_defect.md.
Cubic remains the weakest class after the fix (0.037), but it was already weak on the original
sample (0.433) and the model does now emit the label, so the residual is difficulty rather than the
defect. PER-CLASS TRANSFER, stated exactly (B1, original -> expansion):
  cubic        0.433 -> 0.037   DROP
  tetragonal   0.667 -> 0.323   DROP
  orthorhombic 0.867 -> 0.531   DROP
  monoclinic   0.767 -> 0.690   DROP
  triclinic    0.533 -> 0.471   DROP
  hexagonal    1.000 -> 1.000   FLAT
  trigonal     0.067 -> 0.133   ROSE
Five of seven classes dropped, hexagonal is flat at ceiling, and TRIGONAL ROSE (0.067 -> 0.133).
An earlier version of this section claimed "every class except hexagonal dropped", which the
trigonal row contradicts; that sentence is RETRACTED. The trigonal rise is from a very low base on
both halves (2/30 -> 4/30) and is not significant on its own; it is recorded because the universal
claim was wrong, not because the increase is meaningful.

=================  SET CONSTRUCTION, VERIFIED  ================================================
210 new structures, same composition-exclusion rule, seed 23. Verified: 0 overlap with train, 0 with
the original eval, 0 with the prior-used pool, 0 duplicates, and all 210 carry at least one reserved
element. Labels are spglib's via make_labels; MP's crystal_system was used ONLY to select candidates
and never as a label, which is why per-system counts are 27-34 rather than a flat 30. All 1050
renders produced with 0 failures at 768px, conventional cell, 2x2x2 supercell.
EVALUATION PROTOCOL matched to training, not to the newest config: max_pixels 200704 (the resolution
these adapters were trained at), K=8 majority vote, 512 max new tokens, denominators fixed at 210.

=================  V2b ARM: THE BELOW-FLOOR CLAIM DOES NOT REPLICATE  =========================
V2b (process-trained chain) on the 210 NEW structures: micro 0.4000, macro 0.4095, 0 unparseable.
Against its 0.3810 on the original eval that is +0.0190 — essentially unchanged. But the PAIRED
comparison against the floor REVERSES SIGN between the two halves:
  sample                     d(V2b - floor)   discordant    paired p     verdict
  original       n=210           -0.1476       29 vs 60    1.3e-03    RESOLVED, BELOW floor
  expansion      n=210           +0.1524       65 vs 33    1.6e-03    RESOLVED, ABOVE floor
  POOLED         n=420           +0.0024       94 vs 93    1.00       UNRESOLVED
Both halves are individually significant and they point in OPPOSITE directions, so pooled they
cancel exactly. THE CHAIN ARM IS NOT ROBUSTLY BELOW THE FLOOR; it is below the floor on one sample
and above it on another.
WHY, AND IT IS THE FLOOR THAT MOVED. V2b barely changed (0.3810 -> 0.4000) while the floor fell
0.5286 -> 0.2476. The reversal is almost entirely the floor's sample-specificity, already documented
above, not a change in the chain arm. This is the same instability, now shown to change a CONCLUSION
rather than only a number.

=================  WHAT MUST CHANGE IN THE PAPER  =============================================
"Both chain arms fall below the regularity floor" is NOT supported as a general claim and must be
restated with its sample: on the ORIGINAL 210-structure sample the chain arms fall below the floor
(V2b p = 1.3e-03, SFT-V1 p = 3.8e-03, outcome arm p = 1.5e-06), and on an independently drawn second
sample V2b sits ABOVE it (p = 1.6e-03). Pooled over 420 structures the comparison is a null.
WHAT SURVIVES UNCHANGED, and it is the claim the paper actually leads with:
  B1 vs FLOOR   pooled n=420  d = +0.1476  133 vs 71   p = 1.7e-05   RESOLVED
  B1 vs V2b     pooled n=420  d = +0.1452  179 vs 118  p = 4.8e-04   RESOLVED
The direct arm beats both the floor and the chain arm on the full 420 structures. The
direct-beats-chain result is the paper's substantive finding and it is untouched by the floor's
instability, because it compares two models rather than a model against a moving baseline.

=================  PREDICTION-SUPPORT COLLAPSE (unplanned, and it explains the accuracy)  =====
V2b emits only THREE of seven crystal systems on the expansion set (tetragonal 96, trigonal 69,
cubic 45) and FOUR on the original (adding a single orthorhombic call). Its per-system accuracy is
therefore all-or-nothing: ~0.90-1.00 on the three classes it emits, EXACTLY 0.000 on the four it
never emits. Accuracy is nearly unchanged across the two samples only because the emitted classes
happen to cover a similar share of each.
This is a structural limitation of the chain arm, not a scoring artifact, and it bounds certification
coverage exactly as certification recorded: a certifier that cannot name four of seven labels cannot certify
them at any competence.
NOTE ON THE SAVED TEXT: every stored response is exactly 400 characters. That is a SAVE-TIME
truncation in the harness, not the generation limit (max_new_tokens was 512), and predictions were
parsed before truncation — 0 of 210 unparseable. It does mean the saved file cannot be used for
post-hoc chain analysis.

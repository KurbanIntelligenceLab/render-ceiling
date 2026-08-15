CHECKPOINT: occlusion_manipulation   GAP: does occlusion CAUSE part of the failure, or is
                                          atom_detection's 55.3% only a geometric measurement? (item 4)
STATUS: THE MANIPULATION CHECK FAILED, SO NO MODEL EVALUATION WAS RUN — exactly as the
        pre-registration required. That check then explained WHY, and the explanation qualifies
        atom_detection's headline occlusion figure. No API budget was spent.

=================  THE PRE-REGISTERED GATE, AND WHY IT MATTERED  ==============================
prereg.md required, before any model call: re-render with reduced projected-disc overlap, then
recompute median centre-occlusion with the existing geometric routine. If occlusion did not fall
materially below 55.3%, no model evaluation runs — spending API budget on a condition that does not
differ from the control is waste, not evidence.
  radii 0.50 (canonical): median occlusion 0.5183
  radii 0.22 (thin):      median occlusion 0.5000    reduction 0.0183
GATE FAILED. Shrinking discs by more than half moved the median occlusion by under 2 points.

=================  WHY, AND IT IS A FINDING ABOUT THE RENDER CONVENTION  ======================
A radius sweep shows the median is PINNED at 0.5000 across the whole usable range of disc sizes.
BOTH ROWS BELOW ARE AT n=40 STRUCTURES, MATCHING THE GATE:
  radii  0.50   0.35   0.22   0.12   0.06   0.03
  median 0.5183 0.5000 0.5000 0.5000 0.5000 0.5000
  mean   0.4967 0.4502 0.4114 0.3593 0.3267 0.2984
SAMPLE-SIZE CORRECTION. An earlier version of this table was computed at n=25 and reported
"radii 0.50 -> 0.529" and "radii 0.03 -> 0.278", which sat beside the gate's n=40 value of 0.5183
under the same "radii 0.50 (canonical)" label. Two different numbers under one label with no reason
given is a defect, so the sweep was recomputed at the gate's n=40. Both original values reproduce
exactly at their own sample sizes (n=40 -> 0.5183, n=25 -> 0.5294), so this was a sample-size
mismatch, not a computation error.
THE CORRECTION STRENGTHENS THE CONCLUSION. At matched n=40 the median stays pinned at 0.5000 even at
radii 0.03 — a SIXTEENFOLD reduction — where the n=25 sweep had shown it finally breaking to 0.278.
The mean falls steadily (0.497 -> 0.298) because genuine disc overlap does respond to radius; the
MEDIAN does not, because the coincident-copy component does not.
Investigating the pinning: 26 of 75 measurements sit at EXACTLY 0.5000, and on those structures the
nearest-other-atom PIXEL DISTANCE IS 0.000. Viewing down a lattice vector stacks the 2x2x2 supercell
copies onto IDENTICAL projected positions, so exactly half the atoms are front copies and half are
hidden back copies. No disc radius can separate atoms that project to the same point.
DECOMPOSING atom_detection'S OCCLUSION FIGURE (n=30 structures x 3 views, verified exhaustive to 1e-16):
  EXACT COINCIDENCE (a copy at the identical projected point)   mean 0.2363
  GENUINE DISC OVERLAP (a nearer atom's disc covers it)         mean 0.2529
  total                                                         mean 0.4891
So of the mean occlusion, 48% is a TILING ARTIFACT of viewing down principal axes and 52% is genuine
disc overlap. Only the second half is addressable by radii; the first is addressable only by changing
the camera set or the supercell, and zeroshot established that removing the supercell destroys genuine
translational-periodicity signal (canonical accuracy 0.41 -> 0.21).
A METHODOLOGICAL NOTE ON THE DECOMPOSITION. Component MEDIANS are not additive (0.0528 + 0.1583 =
0.2111, while the median total is 0.5261) — only the means are. Quoting a component median beside a
total median would be misleading, so the split is reported in means.

=================  WHAT THIS DOES TO atom_detection'S CLAIM  ============================================
atom_detection reported "the median structure has 55.3% of its atom centres covered by a nearer atom's disc".
That number is arithmetically correct but the wording implies disc-size crowding, when about half of
it is exact projective coincidence from the tiling. The claim must be restated as (AND IS FURTHER CORRECTED BY occlusion_redundancy BELOW:
most of this occlusion hides a SYMMETRY-EQUIVALENT copy and therefore hides nothing, leaving an
EFFECTIVE visibility deficit of ~0.18-0.20 rather than ~0.55): over half the
atom centres are NOT VISIBLE in the median render, roughly half of that because supercell copies
project onto identical points when viewed down a lattice vector, and roughly half because a nearer
atom's disc covers them.
This makes the visibility limit HARDER to escape, not softer: the dominant component is intrinsic to
rendering a periodic structure along its own axes, and the one intervention that would remove it is
the intervention zeroshot showed to be harmful.

=================  WHAT IS AND IS NOT ESTABLISHED  ============================================
NOT ESTABLISHED: any causal claim that occlusion drives model failure. The pre-registered interaction
test (improvement on the box-ambiguous stratum, no change on box-sufficient) was NOT RUN because the
manipulation could not create the required contrast. Branches O1-O4 are all unread and remain open.
atom_detection's occlusion measurement therefore stays a geometric property of the renders with NO demonstrated
behavioural consequence, and the report must say exactly that.
ESTABLISHED: the occlusion is roughly half projective coincidence and half disc overlap; and it is
not manipulable by the cheapest available intervention. A future test would need a camera set OFF the
principal axes, which changes the frozen protocol and is a larger commitment than this checkpoint.
NOT SPENT: three frontier models x 210 structures x K=3 x 2 conditions of API budget, correctly
withheld by the gate.

=================  C1 — THE 0.4891 TOTAL IS RETIRED (SAME SLICE DEFECT AS occlusion_redundancy)  ==============
Two total-occlusion means circulated: 0.4891 here and 0.5699 in occlusion_redundancy on the "original set" — the same
quantity on nominally the same sample, differing by 0.0808. Traced: THIS checkpoint's decomposition
used the FIRST 30 structures of eval.jsonl, and that file is ORDERED BY CRYSTAL SYSTEM, so the slice is
triclinic/monoclinic only. Recomputing on exactly those 30 reproduces 0.4891 to within 0.02, which
confirms the cause rather than assuming it. It is the identical defect occlusion_redundancy documents.
  0.4891 (first-30 slice, triclinic/monoclinic only)  ->  RETIRED
  0.5699 (stratified 6/system, original set)          ->  the figure to use
  0.5900 (stratified 6/system, expansion set)         ->  the figure to use
The COMPONENT SHARES (48.3% exact coincidence / 51.7% disc overlap) came from the same biased slice and
are therefore also retired; occlusion_redundancy's stratified redundant/informative split (66-68% redundant) supersedes
the whole decomposition. Only one total may appear in any circulated document, and it is occlusion_redundancy's.

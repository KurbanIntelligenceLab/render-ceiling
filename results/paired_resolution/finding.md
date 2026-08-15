CHECKPOINT: paired_resolution   GAP: which inter-arm comparisons are actually resolved at
                                     n=210, using the correct paired test?
STATUS: DONE, zero compute. The review's item 2(b) is correct that the half-width screen is the
        wrong instrument. Acting on it produces a result that CONTRADICTS the review's own item
        2(a), and it re-sizes the eval-set expansion from ~1000-2000 structures to ~400.

=================  THE REVIEW CONTAINS AN INTERNAL CONFLICT, AND 2(b) OVERRIDES 2(a)  =========
2(a) asks us to record B1-vs-floor as RESOLVED, on the grounds that +0.0857 exceeds the stated
     single-proportion Wilson half-width of +/-0.0651. That arithmetic is right (we compute 0.0653).
2(b) asks us to discard exactly that screen, on the correct grounds that comparing a difference to a
     single-proportion half-width is neither a paired nor an independent-samples test, and to
     recompute with paired McNemar on the same 210 structures.
THESE TWO INSTRUCTIONS DISAGREE ABOUT B1-VS-FLOOR. Paired McNemar gives 63 discordant in B1's
favour vs 44 against, exact p = 0.0814 — NOT resolved at n=210. We follow 2(b), because it names
the correct instrument, and therefore DO NOT make the change 2(a) requests. The regularity-floor
finding stands on its direction and on the box_sufficiency stratification, not on a significant B1-vs-floor
margin at this n.

=================  CORRECTED RESOLUTION TABLE (paired McNemar, same 210 structures)  ==========
  comparison                            d(acc)   n01  n10   paired p    verdict
  RF-19-lattice   vs B1-direct         +0.2667    72   16   1.2e-09   RESOLVED
  B3 chain        vs FLOOR             -0.2476    32   84   1.5e-06   RESOLVED
  gemini-3.6      vs FLOOR             +0.2048    70   27   1.5e-05   RESOLVED
  B1-direct       vs V2b chain         +0.2381    99   49   4.8e-05   RESOLVED
  V2b chain       vs FLOOR             -0.1476    29   60   1.3e-03   RESOLVED
  SFT-V1 chain    vs FLOOR             -0.1381    33   62   3.8e-03   RESOLVED
  B1-direct       vs gemini-3.6        -0.1143    43   67   2.8e-02   RESOLVED
  grok-4.5        vs FLOOR             +0.0857    49   31   5.7e-02   unresolved
  B1-direct       vs FLOOR             +0.0905    63   44   8.1e-02   unresolved
  A3 native+aug   vs B1-direct         +0.0714    44   29   1.0e-01   unresolved
  opus-4.8        vs FLOOR             +0.0524    50   39   2.9e-01   unresolved
  B1-direct       vs claude-opus-4.8   +0.0381    51   43   4.7e-01   unresolved
  B1-direct       vs grok-4.5          +0.0048    40   39   1.0e+00   unresolved
  B1 K=16         vs B1 K=8            +0.0000     8    8   1.0e+00   unresolved

WHAT THE PAIRED TEST CHANGES relative to the half-width screen. The three BELOW-FLOOR results are
resolved decisively (p = 3.8e-03 to 1.5e-06; the weakest is the SFT-V1 arm at 3.8e-03, the strongest
is the outcome arm at 1.5e-06) — the paper's harshest claim is its best-supported one.
The modality gap and the B1-vs-chain gap are resolved. What is NOT resolved is every comparison in
the 0.04-0.09 band: B1 vs the floor, B1 vs two of three frontier models, and the native-resolution
retrain vs its baseline. The K=16 control is resolved as a true null (8 vs 8 discordant, the
tightest null in the table).

=================  THIS RE-SIZES THE EXPANSION (review item 5)  ===============================
The half-width screen implied n = 1000-2000 to resolve a 0.03-0.04 effect. The paired test needs far
less, because 51.0% of structures are DISCORDANT between B1 and the floor and the paired test uses
only those. Projecting the observed discordance structure (107 discordant, 58.9% favouring B1):
    n =  210  ->  ~107 discordant,  p = 0.081   not resolved
    n =  400  ->  ~204 discordant,  p = 0.014   RESOLVES
    n =  600  ->  ~306 discordant,  p = 0.002   RESOLVES
    n = 1000  ->  ~510 discordant,  p = 0.0001  RESOLVES
=> TARGET n = 400-500, not 1000-2000. That is roughly a 2x eval-set expansion rather than 5-10x,
which changes the GPU and API cost of item 5 by the same factor. Size the expansion from this table.

REPRODUCE
  Per-structure correctness vectors for every arm from the generation files (majority vote at the
  arm's own K) and from the regenerated RF/floor predictions. Paired McNemar = exact binomial on the
  discordant pairs, matching the convention already used in zeroshot and sft_chain.
  NOTE ON REPRODUCING THE RF/FLOOR: the recorded protocol is train on the 1610 TRAIN structures and
  test on the 210 EVAL structures (NOT cross-validation), features from the INPUT cell, RF
  n_estimators=500 seed 23. Under that protocol the FLOOR reproduces EXACTLY (0.5286) and the RF
  comes to 0.8857 against the recorded 0.8905 (delta 0.0048), the residual being the exact
  19-feature list, which is not itself recorded. Flagged as a minor reproducibility gap; it does not
  affect any paired test, which depends on per-structure vectors rather than the aggregate.

=================  CORRECTION TO AN EARLIER VERIFICATION CLAIM  ===============================
When R8/R9/R10 were rewritten I reported "all 21 numbers in the new sections verified verbatim
against the ledger". That count was accurate for what it covered but the SCOPE was narrower than
the sentence implied. THE BREAKDOWN, stated exactly (an earlier version of this paragraph said
"three models x 4 plus six certifier configurations", which sums to 18, not 21 — that description
was itself wrong and is corrected here):
    frontier_ceiling  3 frontier models x 4 values each (canonical micro, macro-F1, anonymized micro,
          paired p)                                                              = 12
    certification  7 DISTINCT certified-accuracy values across sftonly.json, seed2.json, k16.json,
          replication.json, chain_necessity.json                                 =  7
    certification  2 false-certification rates from chain_necessity.json                  =  2
                                                                          TOTAL  = 21
  THE certification DEDUP, VERIFIED RATHER THAN ASSERTED. Those five files hold 9 RAW chain entries over 6
  distinct arm names, which reduce to 7 distinct (arm, value) pairs:
      V2b_s0    3 entries -> 0.9118 (sftonly), 0.9118 (seed2), 0.9474 (k16)  = 2 DISTINCT values
                (k16 differs because it is the K=16-answerer arm, a different configuration)
      V2b       2 entries -> 0.9825 (replication), 0.9825 (chain_necessity)  = 1 value, IDENTICAL
      SFTonly, V2b_s1, B3, B1direct   1 entry each                           = 4 values
      2 + 1 + 4 = 7
  An earlier version of this paragraph claimed the 7 arose because "V2b_s0 recurs and was checked
  once". THAT REASONING WAS WRONG — V2b_s0 carries TWO distinct values, not one, and the arm that is
  genuinely duplicated is V2b. The count of 7 is correct; the justification given for it was not,
  and was asserted before being computed. Corrected here after the raw count of 9 was traced.
R10's sota_push numbers were NOT in that list.
R10 has since been checked separately: all 8 of its values (0.6619, Wilson 0.5955/0.7225, 1206
steps, loss 0.1419, 3220 examples, 589824 max_pixels, 576 visual tokens) are present in the paper
and trace to sota_push/results.json. The claim is now true as stated; it was overbroad when made.

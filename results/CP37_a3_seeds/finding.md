CHECKPOINT: CP37_a3_seeds   GAP: A3 is single-seed and its 0.6905 sits inside the reference arm's own
              across-seed spread (B1: 0.590 / 0.567 / 0.686). (directive Phase E)
STATUS: NOT RUN — CUT AFTER A QUANTITATIVE TEST OF WHETHER IT COULD CHANGE ANYTHING, NOT ON COST ALONE.
     The adapters DO survive (all_adapters_weights.tar.gz, 2823 MB, in the artifact store), so this was
     feasible; it is a decision about value, not availability.

THE GAP IS REAL. A single-seed number inside the reference arm's spread is a legitimate reviewer target,
and this project has a standing rule against arms whose spread swamps their effect.

WHY IT DOES NOT CHANGE A CONCLUSION HERE, tested rather than asserted. A3 enters the manuscript in exactly
two places, both as the model side of the oracle-to-model gap:
  oracle 0.9524 against A3 0.6905, paired per structure, discordance 61:6, p = 1.5e-12.
That is a 55-structure margin. B1's observed seed spread is +-0.06, which is +-13 structures. Even placing
A3's true mean at the TOP of B1's observed range (0.686) leaves a gap of 0.2664 to the oracle. Seed
variation of the magnitude this project has actually measured cannot close it.
The directive reaches the same place from the other direction: "CP12's thresholds are not reopened... This
produces an interval, not a re-litigation."

WHAT IS LOST. The paper reports A3 as a single-seed point estimate rather than a three-seed interval. That
is stated in the limitations rather than hidden: no error bar is drawn on the A3 bar, and no claim is made
about A3's expected value under reseeding.

WHAT WOULD REOPEN IT. A reviewer challenging the MAGNITUDE of the gap rather than its existence. Two GRPO
runs at seeds 1 and 2 using CP12's recorded reproduce command verbatim; the adapters and the command are
both in the release, so this is shelf-ready.

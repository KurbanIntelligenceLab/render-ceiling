CHECKPOINT: figures   GAP: none. This directory is a FIGURE STORE, not an experiment.
STATUS: CLOSED AS A NON-CHECKPOINT. It holds one rendered figure (bracket_and_claims.png) whose underlying
     numbers live in model_sweep, oracle_within_sample and claim_ledger. It runs no analysis,
     measures nothing, and pre-registers nothing, so it has no result of its own.

WHY THIS RECORD EXISTS AT ALL. A ledger audit flagged figures as the only CP* directory without a finding.md,
which read as an unfinished checkpoint. It is not unfinished — it was never a checkpoint. Recording that
explicitly is cheaper than leaving a permanent audit exception that a future reader has to re-diagnose.

WHERE THE FIGURE'S NUMBERS COME FROM. Every value drawn in bracket_and_claims.png is published in the three
checkpoints named above and verified there. The figure adds no number of its own.

CONVENTION APPLIED. One checkpoint is one directory with one results.json and one finding.md. A directory
holding only rendered output is not a checkpoint and is marked as such rather than given a synthetic result.

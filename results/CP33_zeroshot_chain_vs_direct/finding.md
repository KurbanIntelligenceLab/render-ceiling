CHECKPOINT: CP33_zeroshot_chain_vs_direct   GAP: does the task behave like the rest of the field on
              chain-versus-direct prompting? (directive Phase C)
STATUS: NOT RUN — CUT ON THE DIRECTIVE'S OWN INSTRUCTION, WITH THE ARGUMENT RECORDED. This is a decision,
     not an omission, and it is reported as one.

WHAT THE DIRECTIVE SAYS. Verbatim: "Confirmatory only. Kancheti et al. already ran seventeen models over
thirteen benchmarks... First item to cut if budget binds." The directive also lists CP33 as OFF the
critical path.

WHY THE CUT IS RIGHT RATHER THAN MERELY PERMITTED.
1. THE CLAIM IS ALREADY OCCUPIED. CP43's audit records 2604.16060 as DEMOTED TO CITED REPLICATION — it
   occupies direct-beats-chain across seventeen models and thirteen benchmarks. Running our own version
   would produce a fourteenth benchmark's worth of agreement with a published result we already cite.
2. NO MANUSCRIPT CLAIM DEPENDS ON IT. The paper's thesis is the oracle-to-model gap and the attribution
   ladder. Chain-versus-direct appears nowhere in the claim order.
3. THE COST IS THE LARGEST REMAINING. 20,160 primary calls plus 8,190 secondary at a measured 0.462
   calls/s is roughly 17 hours of wall-clock API time for a confirmation.

WHAT IS LOST, STATED PLAINLY. We cannot say "this task behaves like the rest of the field" from our own
data. That sentence is removed rather than softened; where the paper needs the general result it cites
2604.16060 directly. A reviewer asking whether CoT degrades HERE gets an honest "we did not measure it,
and here is the published result for the general case."

WHAT WOULD REOPEN IT. If a reviewer treats the field-generality of the CoT result as load-bearing for our
reading, the run is 17 hours and the protocol is fully specified in the directive. It is shelf-ready.

CHECKPOINT: expert_study    GAP: is the 210-structure task human-solvable from the renders?
STATUS: NOT RUN — no qualified respondent was collected. This is recorded as an open gap, NOT as a
        result, and no substitute assertion is made anywhere in the paper.

WHAT EXISTS AND IS READY. A complete 50-structure packet: balanced sample verified representative of
the eval set, blinded identifiers, hierarchical scoring rubric, instructions, blind answer sheet, and
a private answer key. protocol.md carries the pre-registered predictions (including P3': trigonal as
the single predicted human failure mode, 0/7 separable by cell outline alone). score_expert.py is
written and VALIDATED against synthetic perfect, random and realistic sheets before any real sheet
was scored (scoring_validation.md).

THE ONE SHEET RECEIVED WAS EXCLUDED, on a screen pre-registered BEFORE it arrived. It scored 18%
(essentially the 14.3% chance rate for 7 classes) and failed four independent authenticity
diagnostics. scoring_validation.md records the diagnostics and the exclusion. This is an AUTHENTICITY
exclusion, not a result-based one — the distinction matters and was maintained when it would have
been convenient to blur it: no sheet may be excluded for producing an inconvenient number.

WHAT THIS COSTS THE PAPER, STATED PLAINLY. The checkability framing — "the only row whose input a
human could check by eye" — is NOT AVAILABLE and every sentence depending on it must be deleted
rather than softened. The information question it would have answered is answered instead by the
E0.5 oracle (identifiability): 93.6% crystal-system recovery from four frozen views under ideal atom
extraction, which isolates information content from human skill in a way a human baseline cannot.
  BUT the oracle does NOT substitute for human solvability: it assumes perfect atom localisation,
  which is the hard part. See identifiability/finding.md for the three corrections governing
  how that bound may be cited (it is space-group 91.1% vs crystal-system 93.6%; a 280-structure
  sample with ZERO overlap with the eval set; 4 of the 5 shipped views).
  trigonal_hexagonal's trigonal/hexagonal mirror also stops short of settling this: it shows BOTH model arms fail
  the same confusable pair in OPPOSITE directions, strong evidence of intrinsic render ambiguity,
  but only a human who separates the pair cleanly would prove the information is present and the
  failure is the models'.

REQUIRED LIMITATIONS SENTENCE (use verbatim): "No human baseline was collected. The oracle bound
substitutes for the information question; the checkability claim is not made."
IF VOLUNTEERS MATERIALIZE LATER, run as specified in protocol.md without modification: 50
structures, documented qualifications, inter-annotator agreement, the trigonal/hexagonal item,
per-item confidence and time. The pre-registered authenticity screen applies to every sheet.

RECONCILIATION [0.9321 -> 0.9357: the identifiability harness was rerun to record box-sufficiency per row; the rerun's 4-view value is 0.9357 (262/280) against the original 0.9321 (261/280). One structure of 280; the harness draws from a LIVE database so the seed fixes draw order, not the candidate pool. 0.9357 is the current value.]

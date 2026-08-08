CHECKPOINT: CP34_second_family_sft   GAP: zero-shot chain prompting and trained chain SFT are different
              objects; does the training claim hold on a second VLM family? (directive Phase C)
STATUS: NOT RUN — CUT, AND THE REASON IS THAT ITS OWN DESIGN CANNOT SUPPORT A CLAIM THIS PAPER MAKES.

WHY. The directive specifies ONE SEED per arm and its own decision rule says "Direction only; one seed
cannot establish magnitude." Against that, this project has repeatedly found single-seed results sitting
inside the reference arm's own spread: B1's three seeds span 0.590 / 0.567 / 0.686, a range of 0.119, which
is wider than most effects we would be trying to detect. A one-seed direction on a new family would be
reported with a caveat that makes it uninterpretable, and this project has a standing rule against
publishing arms whose spread swamps their effect.

WHAT WOULD BE NEEDED INSTEAD. Three seeds per arm on the second family, which is six training runs on
rented GPU. That is a substantial spend for a claim the manuscript does not make: the paper's thesis is
the oracle-to-model gap, and no trained arm is load-bearing in it — the fine-tuned model appears once, as
a comparison point against the oracle.

CONSEQUENCE FOR THE PAPER. Any surviving training claim is FAMILY-SCOPED in the abstract, which is what the
directive's own fallback prescribes. The scoping is stated, not implied by omission.

COST NOTE. A GPU instance (contract 46941802, RTX 5090, $0.493/hr) was rented for this and CP37 and has
been idle. It should be destroyed; keeping it does not make the cut reversible on any useful timescale,
since re-renting takes minutes.

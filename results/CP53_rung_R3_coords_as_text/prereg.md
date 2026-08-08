PRE-REGISTRATION — CP53, rung R3: ground-truth coordinates as text
Committed BEFORE any call. API spend only, inference only, no GPU.

GAP. R1's oracle uses a PERFECT reasoner (spglib) while R4's models use their own. Perception and
symbolic reasoning are therefore confounded: a model failing at R4 may be failing to see, or failing to
reason about what it sees. R3 removes extraction entirely by supplying the geometry as text.

METHOD. Every model in the roster is prompted with ground-truth FRACTIONAL COORDINATES, species, and cell
parameters as text. No images. Task wording byte-identical otherwise. Same K=3, same temperature 0.7,
same majority vote, same parse gate, same denominators, same 210 original-eval structures.
NOT NOVEL AS A DESIGN. This is the CIF-supplied condition of 2605.29446 and the No-Image family of
2604.16060. Cited as prior use; only the measurement is claimed.

THE CONTROL PAIR THAT BRACKETS SYMBOLIC CAPABILITY. CP41's text-only arm removed the images and left the
FORMULA, and every scored arm landed at 7-way chance. CP53 removes the images and supplies the FULL
GEOMETRY. The gap between them is the value of the geometry independent of pixels.

DECISION RULE, fixed now.
  C1  R3 >= R1 (0.9524) -> models can do symmetry reasoning from exact geometry; the ENTIRE deficit is
      perception, and the paper's thesis is clean.
  C2  R3 near CP41's text-only chance level -> models CANNOT do the symmetry reasoning even with perfect
      geometry, so perception is NOT the whole story and the "perception bottleneck" framing is WRONG for
      this task. This would refute the directive's thesis and must be reported as the headline.
  C3  R3 between R4 and R1 -> both stages contribute; report the split as
      (R3 - R4) = perception's share and (R1 - R3) = reasoning's share, per structure and paired.

WHAT WOULD MAKE A ROW UNINFORMATIVE. >5% unparseable or >5% API errors -> reported with its rate, NOT
scored, as in CP41. A model that declines without images is a REFUSAL, reported separately.
A prompt-length confound is possible: a 20-atom cell as text is a long prompt. Report the mean prompt
token count beside each row so a length effect is visible rather than hidden.

EXPECTED, STATED FIRST. I expect C3 with a large perception share, because the models are weak but not at
chance on pixels. If C2 fires the paper changes shape substantially, and that is the outcome I would most
want to know about.

SCOPE. Original eval sample only. Ground-truth geometry, so this bounds symbolic reasoning GIVEN perfect
perception, not what any pipeline achieves.

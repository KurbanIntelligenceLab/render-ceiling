PRE-REGISTRATION — CP58 perception transplant
Committed BEFORE any call. API inference only, no GPU, no new renders.

GAP. CP53 established that 12 of 14 models are REASONING-limited given perfect geometry, which refuted the
perception-bottleneck framing. That leaves a different question open: is the strong models' advantage
PERCEPTION, and is it TRANSPLANTABLE? A descriptive ladder cannot answer that. A substitution can.

FOUR ARMS ON THE SAME 210 ORIGINAL-EVAL STRUCTURES, ALL PAIRED.
  A1  weak model end-to-end on pixels                     EXISTS (CP26)
  A2  strong model end-to-end on pixels                    EXISTS (CP14)
  A3  strong model EXTRACTS ONLY (emits species + positions, no symmetry answer);
      the WEAK model answers the symmetry question from that text                    NEW
  A4  same as A3 with the ORACLE'S exact positions substituted for the strong
      model's — i.e. CP53's condition read as a transplant rather than a control     EXISTS (CP53)

ROLES, FIXED NOW SO THEY CANNOT BE CHOSEN AFTER THE FACT.
  STRONG = google/gemini-3.6-flash  (best on pixels, 0.7333; best on geometry-as-text, 0.8524)
  WEAK   = meta-llama/llama-4-scout (0.2048 on pixels — near chance; 0.5048 on geometry-as-text)
The weak model is chosen because CP41 left it the ONE genuinely ambiguous null: it is above chance with
images (43/210, p=0.009) yet showed no significant image contribution. If any model's pixel reading is
worth transplanting into, it is this one.

DECISION RULE, fixed now. Let A1=0.2048, A2=0.7333, A4=0.5048 (all already measured).
  T1  A3 approaches A2 (within 0.05)  -> the strong/weak difference IS perception, and it TRANSPLANTS
      through text. This is the strongest possible version of the instrument claim.
  T2  A3 approaches A1 (within 0.05)  -> the strong model's extraction is not usable by another model, so
      its advantage is NOT a transferable perception artefact. The gap is internal to the model.
  T3  A3 between A1 and A4            -> partial transplant; report the FRACTION of the A1-to-A4 interval
      that the strong model's extraction recovers, and claim only that fraction.
  T4  A3 EXCEEDS A4                   -> would mean model-written positions beat the oracle's exact ones,
      which is not physically sensible; treat as a harness defect and investigate before reporting.

THE SECOND MEASUREMENT, WHICH IS THE PART NO PRIOR WORK IN THIS LINE HAS.
The strong model's EMITTED POSITIONS are scored directly against ground truth — recall, precision, centroid
error — matched by the same criteria used for the CP19 detector. Prior two-stage work compares stage
outputs only through downstream accuracy because it has no exact positions to compare against. We do.
This makes the extraction stage measurable rather than inferred, and it lets A3's outcome be attributed to
extraction QUALITY rather than to the handoff format.

WHAT WOULD MAKE A ROW UNINFORMATIVE.
  >5% unparseable or >5% API errors on either leg -> reported with its rate, NOT scored (as CP41/CP53).
  If the strong model refuses to emit positions without answering, that is a REFUSAL and is reported as
  such rather than retried into compliance.
  If the strong model emits fewer than 3 atoms on >20% of structures, the handoff carries too little to
  reason from and A3 bounds the FORMAT rather than the extraction; say so explicitly.

EXPECTED, STATED FIRST SO IT CANNOT BE RENEGOTIATED. I expect T3 with a SMALL recovered fraction, because
CP53 already showed this weak model reaches only 0.5048 even with PERFECT geometry — so its ceiling in this
design is 0.5048, not A2's 0.7333, and T1 is close to unreachable by construction. If T1 fires anyway, the
weak model is doing better from model-written text than from exact coordinates, which would itself need
explaining.
NOTE THE CEILING ASYMMETRY EXPLICITLY: A4 (0.5048) is the true upper bound for A3, not A2 (0.7333). Any
statement of "how close A3 gets" must name A4 as the reference, and the directive's framing of A3-vs-A2
would overstate the shortfall.

SCOPE. One strong model, one weak model, one sample. Says nothing about other pairings.

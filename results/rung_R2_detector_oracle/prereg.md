PRE-REGISTRATION — rung_R2_detector_oracle, rung R2: the oracle on detector output
Committed BEFORE the run. CPU only, no API spend, no GPU.

GAP. R1 (the geometric oracle) never touches a pixel: it inverts the frozen cameras from GROUND-TRUTH
projections. So "perception is the bottleneck" currently rests on an instrument that assumes perception.
R2 replaces the ground-truth projections with a concrete extraction stage's actual detections and runs the
IDENTICAL inversion, correspondence solver and spglib step.

METHOD. The atom_detection/extraction_operating_point detector runs on the real render PNGs. Its detections feed the same
reconstruct_positions / recover_symmetry path R1 uses. Per structure, both eval sets, 5 views. Paired
against R1 and R4 on the same named structures, exact McNemar with discordance counts.

THE LADDER'S FIRST RUNG IS DEFINITIONAL, AND THIS CORRECTS THE DIRECTIVE. R0 = spglib on ground-truth
positions = 210/210 = 1.0000 at the canonical labelling tolerance (symprec 0.01, angle_tolerance 5.0),
because the label IS that computation. R0 is an anchor, not a measurement, and the R0->R1 interval
(1.0000 -> 0.9524) is what camera inversion plus correspondence re-solution loses. The directive's
"R0 ~ R1 ~ 0.9524" duplicates a rung and discards that interval.

DECISION RULE, fixed now.
  B1  R2 within 0.05 of R1 -> EXTRACTION IS NOT THE BOTTLENECK. This CONTRADICTS the package's current
      reading and would be reported as the headline, not buried: the deficit would sit in the model's
      symmetry reasoning, and the paper's thesis inverts to "both stages fail, in measured proportion".
  B2  R2 within 0.05 of R4 (best arm 0.6905) -> the bottleneck is extraction and the attribution is clean.
  B3  R2 strictly between -> report the FRACTION of the R1-to-R4 gap that extraction accounts for, as a
      point estimate with a paired interval, and claim only that fraction.

WHAT WOULD MAKE R2 UNINFORMATIVE, AND THE MANDATORY CO-REPORTED VALUES.
The detector FAILED its own precision/recall gate. R2 is therefore NOT a claim about achievable
extraction. Its measured operating point must be printed beside the R2 number EVERY time R2 appears:
median recall 0.400, median precision 0.233, median centroid error 0.717 px on matched atoms. R2 is a
lower bound from one concrete extractor, never a ceiling for extraction in general.
If R2 fails to triangulate on >5% of structures, report the failure rate and do NOT score it.
Over-triangulation (n_recovered > n_true) is reported per condition, since dropping detections can create
spurious cross-view matches.

EXPECTED, STATED SO IT CANNOT BE RENEGOTIATED. With recall at 0.400 I expect R2 at or BELOW R4, i.e. B2
or worse — a detector that finds two atoms in five cannot reconstruct a lattice. If that happens, R2 does
NOT separate extraction from reasoning; it only shows THIS detector is worse than the models, and I will
say so rather than presenting a floor as an attribution.

SCOPE. One extractor, the frozen camera set, both eval sets. Says nothing about what a better detector
would recover.

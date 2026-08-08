PRE-REGISTRATION — CP54 render-convention sweep, scored on MODELS
Committed BEFORE any render or call. Renders are CPU; scoring is API inference. No GPU.

GAP. The package diagnoses without intervening. Every reviewer objection about actionability lands here,
and the directive is right that the earlier gate — "blocked on a working extractor" — was the wrong gate:
whether render convention changes what MODELS recover is answered by running models, not an extractor.

CONVENTIONS, holding structures and cameras otherwise fixed. Five arms.
  C1 FROZEN BASELINE            the shipped protocol: 2x2x2 supercell, radii 0.5, the five frozen cameras
  C2 SINGLE CELL                supercell (1,1,1), everything else identical. Tests whether the tiling that
                                CP20 showed creates ~half of all occlusion by exact projective coincidence
                                is helping or hurting a MODEL (CP20 only showed it hurts an extractor)
  C3 SMALL RADII                radii 0.22, everything else identical. CP20's radius sweep showed the MEAN
                                occlusion falls from 0.497 to 0.411 here while the median is pinned, so this
                                separates "genuine disc overlap" from "coincident copies" for a model
  C4 OFF-AXIS CAMERAS           the perturbed camera map already in the codebase (VIEWS_PERTURBED), which
                                breaks exact projective coincidence. THE REPORT CLOSED THIS ON GEOMETRIC
                                ARGUMENT AND PREDICTED A NULL. A measured null is worth more than a reasoned
                                one, so the prediction is tested rather than assumed
  C5 SINGLE CELL + SMALL RADII  the two interventions together, to see whether they compose or saturate

WHAT IS NOT RUN, AND WHY IT IS NAMED RATHER THAN SILENTLY DROPPED. The directive's condition 2 (metric
depth-graded colour) and condition 3 (annotated plan view with height fractions) both require NEW RENDERER
CODE — a per-atom colour ramp keyed to depth, and text annotation of height fractions. The current
render_views() exposes supercell, radii and the camera map as parameters and nothing else. Condition 3 is
the most motivated intervention in the package and it is NOT in this checkpoint; it is recorded here as the
single highest-value remaining render experiment so it cannot be quietly forgotten.

SAMPLE. A 70-structure subsample of the original eval set, STRATIFIED BY CRYSTAL SYSTEM (10 per system).
Stated reason: 5 conventions x 4 scorers x 210 x K=3 is 12,600 calls; at 70 structures it is 4,200. The
stratification is mandatory — an earlier defect in this project came from slicing a class-ordered file by
prefix, which yielded a two-class sample.
SCORERS. Three frontier models (gemini-3.6-flash, grok-4.5, claude-opus-4.8) plus the strongest open model
(llama-4-maverick). Plus THE ORACLE on every convention, which is free and is the point: it makes each
convention's identifiability CEILING explicit, so a model gain can be separated from a ceiling gain.
Paired per structure throughout, exact McNemar with discordance counts.

DECISION RULE, fixed now, per convention against C1.
  V1  model accuracy rises AND the oracle ceiling is unchanged -> the convention makes existing information
      more READABLE. This is the actionable result the paper needs.
  V2  model accuracy rises AND the oracle ceiling also rises   -> the convention adds INFORMATION rather
      than legibility; report both and do not call it a legibility gain.
  V3  no significant change                                     -> reported as a null. For C4 specifically
      this CONFIRMS the report's geometric prediction and converts it from reasoned to measured.
  V4  model accuracy FALLS                                      -> reported as such. C2 and C3 could
      plausibly fall: removing the supercell removes context a model may use even though it also removes
      occlusion.

EXPECTED, STATED FIRST. I expect V3 for C4 (the report's prediction), and I genuinely do not know for C2/C3
— CP21 showed most occlusion hides symmetry-EQUIVALENT copies, so removing it may buy nothing, but no model
has ever been asked. If every convention returns V3 the paper's honest statement is "we found no render
intervention that helps", which is a weaker result than a win and stronger than an untested claim.

WHAT WOULD MAKE AN ARM UNINFORMATIVE. >5% unparseable or >5% API errors -> reported with its rate, not
scored. If a convention's renders fail to generate for >2% of structures, that arm is dropped with its
failure rate stated.

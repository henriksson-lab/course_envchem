# Environmental Chemistry content plan

Build a chemistry-led course around environmental reactions in air, water, and
soil. Follow the working textbook's broad sequence, give aquatic chemistry the
most depth, and use familiar computing skills to make chemical predictions
visible. Keep the course's chemical purpose and level; R supports the explanation.

Working proposal, 19 November 2026. The programme context is a year-2,
7.5 ECTS course. Programme organization, scheduling, staffing, and examination
design are outside this plan.

## Complete first teaching draft

All 15 planned topic units are now implemented, with notes, learning goals,
16 short lecture decks in total, and 62 numbered exercises with worked solutions.
The aquatic units retain the main quantitative depth. Activities A, B, and C
have portable student downloads, data/model dictionaries where needed, and
R Markdown report templates. The glossary links definitions to their explanations.

`make check` verifies the stated chemical models, selected numerical results,
atom/charge balances, data corrections, and fresh-session report renders.
`make render` packages the student activities, builds the site, and checks local
links, fragment targets, published inputs, and exclusions. The teacher
[coverage map](instructor/coverage.md) connects the proposed capabilities to
practice. Exact textbook subsections, formal syllabus alignment, classroom
pacing, and browser-based slide review remain instructor review items.

## Weekly interactive practice

Five demos now support a working five-week grouping of the existing content:
units 1–4 (deposition and dilution), 5–7 (closed-water carbonate response),
8–11 (metal binding and saturation), 12–14 (partitioning and parent
transformation), and 15 (the annual catchment budget). This is a study grouping,
not a change to formal scheduling. Direct Demo entries sit beside the relevant lecture and exercise in the
Quantitative Biology week-menu scaffold. Each corresponding exercise and
lecture contains a real inline demo. Each standalone week page has prediction questions,
reference presets, model conditions, and a static hand-check result.

The browser demos are a way to explore the same chemical balances, separate
from student coding tasks. They do not add programming prerequisites or new
statistical methods. Model scripts use no external libraries or network calls.
`make check-demos` verifies numeric cases and conservation; browser QA checks
mounting, presets, reset, native slider keyboard use, endpoint redraws, and
mobile width with external requests blocked.

## Basis and scope

The local [Environmental Chemistry dossier](../molbiol_program/courses/chemistry-2027-environmental-chemistry.md)
records a new 7.5 ECTS programme entry whose final code and syllabus were not
identified. [Aquatic Chemistry 5KE002](../molbiol_program/courses/5KE002-aquatic-chemistry.md)
is the documented 15 ECTS comparator. Its emphasis on equilibrium, speciation,
metals, and interfaces is a useful continuity anchor; this proposal does not
transfer its full workload or claim identical formal outcomes. No previous
Environmental Chemistry lecture set or assigned chapter list is present here.

Use Gary W. vanLoon and Stephen J. Duffy, *Environmental Chemistry: A Global
Perspective*, **fourth edition, 2017**, ISBN **9780198749974**, as the working
reference. This is the book listed for the aquatic comparator, with adoption
for this course still provisional. The [publisher's contents](https://www.oup.com.au/books/higher-education/chemistry/9780198749974)
confirm its progression from atmosphere to hydrosphere to terrestrial chemistry.
The chapter map below uses that contents list, checked 19 November 2026;
subsection assignments and page ranges need inspection of the book itself.

Retain the broad environmental coverage suggested by the book while protecting
the aquatic core. Suggested relative content emphasis is **5% foundations,
20% atmosphere, 45% water, 25% soils and contaminants, and 5% integration**.
These are priorities for writing and depth, not contact hours or a timetable.
Do not turn every book chapter into a full lecture unit.

## Student baseline and proposed capabilities

Draw on general chemistry: moles and concentrations, balanced reactions,
acid–base equilibria, oxidation states, and basic thermodynamics. Begin with
short retrieval questions and worked refreshers rather than assuming fluency.
Organic chemistry supports structure–property reasoning; microbiology supports
nutrient cycling, but environmental mechanisms must be explained locally.
Avoid relying on the delivery order of neighbouring chemistry courses.

Treat the skills in [Introductory Computing](/home/mahogny/github/course/introcomputing/contentplan.md)
as a transfer target, not proof of what every student remembers. Its local source
is `/home/mahogny/github/course/introcomputing`. Supply a short refresher and a
working example before the first R activity.

Proposed learning capabilities, to reconcile with the eventual approved ELOs:

1. Track chemical amounts between compartments using consistent units and a
   simple mass balance, distinguishing concentration from total load.
2. Use reactions, equilibrium expressions, and rates to explain environmental
   transformations and distinguish possible change from its timescale.
3. Interpret and calculate simple pH-dependent distributions, gas–water
   partitioning, and mineral or metal equilibria under stated assumptions.
4. Explain how redox conditions, organic matter, and surfaces alter speciation,
   mobility, and potential biological exposure.
5. Relate organic molecular properties to partitioning and persistence without
   treating a single property as a complete prediction of environmental risk.
6. Interpret a small environmental dataset or model plot and communicate a
   reproducible chemical explanation with appropriate limitations.

## Proposed sequence and chapter map

The rows are topic units, not teaching days. Chapter numbers refer to the
fourth edition. Each unit should have a short explanation, a worked calculation
where appropriate, and practice in interpreting the chemical result.

| Unit and proposed folder | Book chapters | Chemistry and environmental question | Core exercise |
| --- | --- | --- | --- |
| 1. Environmental amounts — `environmental-systems/` | 1 | Compartments, sources, sinks, concentration and load; where did the substance go? | Close a two-compartment mass balance with explicit volumes and units. |
| 2. Reactions in air — `atmospheric-reactions/` | 2–4 | Light, reaction rates, ozone formation and catalytic removal; why does ozone have different consequences at different altitudes? | Read a short supplied reaction scheme; identify production, loss, and the regenerated catalyst. |
| 3. Deposition — `deposition/` | 5–7, selected | Acid formation, gas/particle pathways, wet and dry deposition; how does air chemistry change water inputs? | Convert a supplied deposition flux to an annual amount; compare acid equivalents. |
| 4. Climate chemistry — `climate-chemistry/` | 8, selected | Radiation, molecular absorption, gas persistence, and aerosol effects; why do emissions differ in their consequences? | Interpret supplied spectra and lifetime information; separate chemical lifetime from a complete climate response. |
| 5. Aquatic composition — `aquatic-equilibria/` | 9–10 | Activities versus concentrations, charge and mass balance, simple acid speciation; what does a water analysis describe? | Check charge balance in a deliberately simple ion table and read a distribution diagram. |
| 6. Carbonate and gases — `carbonate-gases/` | 10–11 | Carbon dioxide exchange, carbonate species, pH, alkalinity, buffering, mineral saturation; why do waters respond differently to acid? | Calculate species ratios at given pH, compare two alkalinities, and interpret gas exchange. |
| 7. Organic matter — `aquatic-organic-matter/` | 12 | Dissolved and particulate organic matter, binding, light and oxygen demand; what does organic carbon change? | Explain contrasting waters with the same total metal but different binding conditions. |
| 8. Metals — `metals/` | 13 | Coordination, hydrolysis, complexation, precipitation; when does dissolved total metal conceal different species? | Calculate a simple one-ligand distribution and test a supplied solubility condition. |
| 9. Interfaces — `surfaces/` | 14 | Colloids, surface charge, adsorption, desorption, and phosphate retention; why can particles retain or transport a contaminant? | Use a supplied linear sorption relation with a two-phase mass balance. |
| 10. Redox and cycles — `redox-cycles/` | 10, 13, 15 | Electron balances, oxygen consumption, carbon/nitrogen/sulfur transformations, iron cycling; what changes when oxygen is depleted? | Balance one redox reaction and interpret a simplified redox sequence or supplied diagram. |
| 11. Treatment chemistry — `water-treatment/` | 16 | Precipitation, coagulation, sorption, biological transformations; which process removes which chemical form? | Explain a treatment train using species and mass balances; distinguish removal from transformation. |
| 12. Soil chemistry — `soil-chemistry/` | 17–18 | Mineral and organic phases, exchange capacity, buffering, water movement; why do soils retain and release solutes differently? | Compare contrasting soils under acidification and justify the likely direction of metal mobility. |
| 13. Waste and leachate — `waste-leachate/` | 19, selected | Weathering, sulfide oxidation, acidity, leaching, and immobilisation; what controls release from a waste material? | Trace a mine-waste case through oxidation, acid production, and downstream metal retention. |
| 14. Organic contaminants — `organic-contaminants/` | 20 | Ionisation, hydrophobicity, partitioning, degradation, persistence, and exposure; where does a compound accumulate? | Compare supplied compound properties and calculate a simple partition balance and first-order remaining fraction. |
| 15. Connected systems — `integrated-case/` | 21 plus earlier selections | Combine atmospheric input, catchment reactions, and aquatic response; which chemical explanation fits the evidence? | Produce a concise explanation supported by reactions, a balance, and one figure. |

Chapters guide the reading; the exercise details and teaching emphases above are
our proposals. Introduce a simple redox reminder before metal chemistry; reserve
the coupled environmental cycles for unit 10. Revisit sorption from the soil
perspective without repeating the full aquatic derivation.

## Depth boundaries

**Atmosphere:** make reaction chemistry explicit through one ozone mechanism and
one deposition chain. Keep climate molecular and chemical: absorption,
composition, and persistence. A full radiation model, exhaustive atmospheric
mechanisms, and a catalogue of indoor pollutants would displace the aquatic core.

**Water:** invest most quantitative practice here. Students should work through
acid speciation, carbonate ratios, an alkalinity interpretation, gas partitioning,
a simple saturation check, one metal–ligand case, and a sorption balance.
Interpret a supplied carbonate or redox diagram before considering software.
Use stated temperature, constants, and dilute-solution assumptions; separate
free ion, dissolved total, particulate, and whole-sample totals. Discuss where
equilibrium is a useful approximation and where kinetics or transport matter.

**Soils and contaminants:** reuse the same equilibria and phase balances in a
new matrix. Compare a small number of compounds with supplied property data.
Explain persistence and potential exposure without equating total concentration
or an octanol–water coefficient with bioavailability or toxicity. Use treatment
and remediation as applications of the chemistry, rather than adding a separate
engineering survey.

Detailed multi-species numerical speciation, full soil transport equations,
advanced thermodynamic activity models, nonlinear fitting, GIS, machine
learning, and a general ecotoxicology survey are deferred. These are candidates
for later material only if they serve an identified chemical learning need.

## Modest computing strand

Use the same small R vocabulary as Introductory Computing: objects, vectors,
`readr`, `dplyr`, `ggplot2`, and a supplied R Markdown report. Keep student reports
in `.Rmd` and the teaching website in `.qmd`. Do not add a second report system,
a terminal refresher block, remote-computing requirements, or new statistical
tests. A model prediction does not require a regression or a p-value.

| Proposed activity | Existing skill to reuse | Chemical result | Small addition |
| --- | --- | --- | --- |
| A. Water table, unit 5 | Days 7–8 and 11–13: import, inspect, calculate columns, summarise, plot | Compare ion concentrations and charge balance; identify unit or identifier problems before interpreting chemistry | Convert molar concentrations to charge equivalents with supplied ion charges. |
| B. Species versus pH, unit 6 | Days 6 and 8: vector arithmetic and labelled plots | Explain a changing acid/base distribution using a supplied simple chemical model | `seq()` for a pH grid and powers of ten; explicitly explain logarithmic pH. |
| C. Contaminant fate and explanation, units 14–15 | Days 9–10 and 21–25: render from saved data and code, interpret figures, reopen elsewhere | Compare remaining fractions or two-phase distributions and explain assumptions in a short report | `exp()` for a supplied first-order equation, if this model is included. |

Each is one bounded exercise embedded in its chemistry unit. A and B should
stand alone; C reuses their workflow rather than initiating a large computing
project. Begin every activity with a prediction and a hand-calculated point.
Supply starting code, reference results, and a small table or figure students
can still interpret while receiving computing help.

Calibration from Introductory Computing day 19 is available when an actual
measurement exercise needs it. Reuse its within-range and dilution checks;
do not duplicate Analytical Chemistry's treatment of instrumentation or fit a
line to a deterministic equilibrium curve. Statistical group comparison is not
a core requirement here.

A staff-provided carbonate solver or an equilibrium package could later show
coupled equilibria. Its first use would be a demonstration with independently
checked limiting cases. Writing a root finder, installing specialist software,
or mastering a package interface is not part of this initial plan.

### Chemical checks for computational exercises

- Provide units, constants, temperature, source or simulated status, and a data
  dictionary. Keep measured observations separate from model predictions.
- For acid speciation, verify positive inputs, fractions between zero and one,
  fractions summing to one, and expected limiting behaviour. Do not treat pH
  as a concentration or average it as a linear proxy for hydrogen ion amount.
- Define the Henry coefficient convention and units in every gas calculation.
  Specify what remains fixed: pH, gas pressure, total carbon, or alkalinity.
- For metal and partition calculations, check mass balance and define the
  dissolved, sorbed, and total quantities. Do not substitute a total for a free
  concentration without an explicit approximation.
- For first-order loss, check time zero, half-life, and consistent time units;
  distinguish transformation from transfer to another compartment.
- Restart R and render the saved `.Rmd` from the supplied data. Use the existing
  computing workflow rather than requiring hidden console objects or absolute
  paths specific to the author’s machine.

## Recurring cases and practice

Use **acid deposition into a lake catchment** as the main thread: atmospheric
acid production, deposition, carbonate buffering, soil exchange, metal release,
and possible recovery. Keep it a clearly labelled constructed case until a
suitable measured dataset and its provenance are selected. Reuse samples and
units consistently, while giving each unit enough local context to stand alone.

Use **oxygen depletion and sediment release** as a shorter second case for
redox, organic matter, iron phases, and nutrient cycling. Contrast this with a
simple organic-contaminant case so students encounter both inorganic speciation
and organic structure–property reasoning.

Every unit should ask students to predict a direction, calculate a small case
where useful, interpret a figure or table, and explain a limitation. These are
practice designs, not a proposal for formal assessment rules. Candidate links
to future practical material are alkalinity measurements, sorption observations,
and water-quality interpretation. Protocols, equipment, and safe operating
conditions must come from the actual practical documentation before writing
student laboratory instructions.

## Material structure

The local scaffold adapts `/home/mahogny/github/course/quantbio-3MB00A`:
Quarto website, `docs/` output, searchable docked sidebar, HTML theme, short
reveal.js lectures, and topic folders containing `lec.qmd` and `exercise.qmd`.
Use a `quiz.qmd` only where a short concept check adds value. Add sidebar entries
as substantive units are written; empty lesson pages are unnecessary.

Preserve short, focused decks, linked hints, worked solutions, and the progression
from intuition to a small calculation. Adapt the original method–biology pairing
to **chemical question–reaction–evidence**. Do not inherit its requirement to
show code for every formula, its advanced quantitative material, or its exam
assumptions. A chemical derivation may be best explained without any code.

The initial scaffold includes `index.qmd`, `overview.qmd`, authoring templates,
and build files. `contentplan.md`, README, and templates are excluded from the
student build. It now contains all 15 topic units, the glossary, and three packaged computing activities.

## Authoring sequence and remaining review

The writing passes below have been completed for the first draft. The book and
classroom review items remain open.

1. **Set the chemical depth.** Check the proposed chapter selections against the
   actual book and available earlier course materials. Record precise readings
   and constants. Reconcile the proposed capabilities when the final course
   syllabus becomes available; this does not block drafting.
2. **Write one representative aquatic unit.** Start with carbonate and gases:
   focused lecture, small worked examples, a distribution diagram, hand practice,
   and activity B. This tests the balance between chemistry and computation.
3. **Build the aquatic spine.** Write units 5–11 in learning order, including a
   brief redox bridge where needed. Prepare activity A and its data dictionary.
   Cross-check all balances and model assumptions before expanding examples.
4. **Write the atmospheric lead-in and terrestrial follow-through.** Add units
   1–4 and 12–14, carrying the deposition case between media. Keep secondary
   textbook topics within the depth boundaries above.
5. **Integrate and review.** Write unit 15 and activity C, check continuity of
   sample identities and units, independently verify numeric examples, and
   render all reports from saved inputs. Pilot the first R task for recall
   demands and the chemistry exercises for time and conceptual difficulty.

The complete first teaching draft has a bounded chapter/topic selection for each unit,
worked chemical examples, practice with solutions, interpretable diagrams,
three compact computing activities with documented data, and a functioning
Quarto build. It does not require new computational methods to count as complete.

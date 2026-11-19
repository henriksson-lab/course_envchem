# Environmental Chemistry teaching draft

All 15 planned units are implemented. Start with the
[capability and practice map](coverage.md) and [content plan](../contentplan.md).
There are 16 short lecture decks (14 decks of 9 content slides plus the original
12-slide and 10-slide carbonate decks), 62 numbered exercises, three compact
R activities, a linked glossary, and scientific model figures.

The course remains chemistry-led. General chemistry refreshers precede the
calculations. Most quantitative depth lies in water chemistry, with atmosphere
and terrestrial chemistry following the working textbook's broad structure.
Formal examination design and programme organization are outside scope.

## Chemical models and recurring examples

All numerical waters and observations are constructed unless identified
otherwise. No field dataset is claimed. The introductory examples isolate
processes so students can check units and balances before combining mechanisms.

The annual catchment has area 1.00 × 10⁶ m² and export 5.00 × 10⁸ L/year.
The stated acid inputs give 40000 eq/year, of which a stipulated neutralisation
term consumes 30000 eq/year. The residual is 10000 eq/year = 0.0200 meq/L.
The integrated comparison introduces an explicit 50000 eq/year reference
alkalinity export, reduced to 40000 eq/year under that residual acid input.
Annual export is not a closed-water pulse and does not uniquely give pH.

The separate sediment case uses invented O₂, filtered Fe, and phosphate-P
observations. They support discussion of iron reduction and carrier-phase
release without proving a single mechanism. Filtered Fe is not labelled free
Fe²⁺; phosphorus mass is reported as P. The compound-fate model is a separate
constructed system, not a fitted explanation of those sediment observations.

For metal complexation, generic M and L have stipulated teaching constants.
Prescribed free ligand is distinct from total ligand, and exercises explicitly
challenge the excess-ligand approximation. Sorption examples conserve parent
across phases. The waste example states the iron-hydroxide and carbon-dioxide
endpoints used for acid accounting. These constants and endpoint conventions
must remain explicit when examples are revised.

## Three computing activities

| Activity | Files and purpose | Interpretation safeguard |
| --- | --- | --- |
| A, `aquatic-equilibria/` | Water CSV, a correction record, R script, report | Charge imbalance flags an investigation; only the supplied constructed lab record authorises the decimal correction. Preserve raw data. |
| B, `carbonate-gases/` | Speciation script and report | pH is prescribed; a distribution curve does not solve an acid-dose experiment. |
| C, `organic-contaminants/` | Compound inputs, fate script, report | Rapid partitioning and identical first-order parent transformation in both phases permit the total-parent exponential. Products and toxicity are unspecified. |

Student source files stay together in one folder per activity. Reports use
`.Rmd`, matching introductory computing. Scripts A and C use `readr`, `dplyr`,
and `ggplot2`; B uses `ggplot2`; reports use `rmarkdown`. All have executable
starting calculations and explicit writing prompts. A and C have data/model
dictionaries; B's constants and model are on its reference sheet.

The identifiers A/B/C in the water-ion activity are local to that dataset; they
are not the separately constructed carbonate-unit waters. No replicate treatment
comparison, regression, or p-value is required in these activities.

## Weekly interactive demos

The five week pages in `interactives/` provide a working grouping, not an approved
timetable. They cover deposition/dilution, closed-carbonate acid response,
binding/free-ion saturation, phase inventories/parent transformation, and the
annual catchment budget. The matching exercises, lectures, and notes link to them.
Each has prediction prompts, a static worked reference, and model conditions.

Use them to test a chemical prediction before students calculate or modify code.
Reset and each reference preset set all inputs; a subsequent single-slider
change provides a controlled comparison. The sliders accept keyboard arrow keys
when focused. Plot lines have distinct styles as well as colours; current
calculated values and interpretations are available as text. Mobile plots scroll
inside their own container, and print uses the static reference below the demo.

The scripts are dependency-free browser code. Development checks require Node.js
18+ (`make check-demos`, also included in `make check`). The optional Chrome QA
helper `tools/check_demos_browser.py` requires `websocket-client` and a separately
started temporary-profile Chrome on loopback port 9223. It loads rendered
`file://` pages with external requests blocked and checks real controls,
presets/reset, UI endpoint combinations, native keyboard operation, and mobile
width. The site check verifies published demo assets match source and excludes
tests and instructor material from the student output.

## Carbonate unit assumptions

Use 25 °C, dilute freshwater, and the supplied rounded constants. CO₂* combines
dissolved carbon dioxide with carbonic acid; activities are approximated by
concentrations. The model excludes ion pairs and other acid–base systems.
It does not describe seawater.

The acid comparison holds CT fixed within each sample, with negligible dilution
and no gas, mineral, or biological reaction. Initial pH is 7.50, CT is 1.00 or
0.100 mmol/L, and the strong-acid dose is 0.0500 meq/L. Background counterions
are implicit. The final pHs 7.235 and 6.252 satisfy the carbon/alkalinity balances;
students interpret them without implementing a numerical solver.

Gas examples specify separate states. A large reservoir fixes partial pressure;
a finite headspace would require a coupled balance. The gas pressure is supplied,
not a current atmospheric measurement. Calcite saturation uses free-ion products;
it does not predict precipitation rate or final transferred mass.

## Verification and packaging

Run from the repository root:

```bash
make check
make render
```

`check_carbonate.R` checks fractions, limiting cases, pKa crossings, an independent
hydrogen-ion form of mass action, acid-dose balances, Henry calculations, calcite
saturation, and a clean-process report render. `check_course.R` checks selected
numeric examples, atom/charge balance for key atmospheric/redox/waste reactions,
charge-table corrections, parent balances, and the other two reports in clean
subprocesses. These checks address the stated teaching models; they do not
validate field transfer or classroom pacing.

`package_downloads.py` creates deterministic ZIPs from explicit input lists.
`check_site.py`, run after rendering, checks file links and fragment IDs, archive
contents and freshness, published source copies, the Pages marker, and exclusions.
Instructor files and planning material stay out of `docs/`. In a restricted cache
environment use `XDG_CACHE_HOME=/tmp/envchem-quarto-cache make render`.

## Review before teaching

Inspect the actual textbook to choose exact subsection/page assignments from the
bounded chapter/topic selections. Reconcile proposed capabilities with the final
approved syllabus. Pilot the first R task for recall demands and the exercises
for pacing. The weekly demos have passed desktop/mobile browser interaction checks.
Review the wider course lectures in the teaching display; a full slide-layout
review and classroom pilot have not been completed.

Practical interpretation tasks are calculations and supplied-data exercises.
They do not replace laboratory protocols. Experimental procedures, equipment,
and operating conditions should be taken from the actual practical documentation
before adding laboratory instructions.

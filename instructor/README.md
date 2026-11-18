# Carbonate and gas chemistry teaching draft

The first unit is `carbonate-gases/`. It is intended to establish the chemical
depth and modest computing style for the remaining course. It contains two short
decks (12 and 10 content slides), a reference sheet, six exercises with worked
solutions, and a runnable R Markdown activity. The remaining course is planned
in `contentplan.md`.

## Model and teaching choices

All example waters are constructed. Constants are rounded for dilute freshwater
at 25 °C. The reference sheet links the USGS PHREEQC database and carbonate
speciation guidance. Its acid–base model combines dissolved CO2 and carbonic
acid as CO2*, uses concentration approximations, and omits complexes and other
acid–base systems. It is not a model for seawater.

The two-water comparison holds CT fixed within each sample during acid addition,
with negligible dilution and no gas, mineral, or biological reaction. Initial pH
is 7.50, CT is 1.00 or 0.100 mmol/L, and the acid dose is 0.0500 meq/L. Background
ions are implicit; the samples should not be interpreted as pure CO2–water
solutions. Numerical final pHs are supplied to students; the instructor script
solves for them. Students need to calculate the alkalinity change and explain
its chemical meaning, without implementing an equilibrium solver.

The gas examples specify separate states. A large reservoir fixes gas pressure;
a finite bottle headspace would require a coupled gas/water balance. The exercise
pressure is a supplied value, not a current atmospheric measurement. Saturation
checks use free ions and indicate a thermodynamic direction, without predicting
kinetics or the final mass transferred.

## Checks

From the repository root, run:

```bash
make check
make render
```

`make check` requires R, ggplot2, rmarkdown, and Pandoc (available with Quarto).
It checks fractions, limiting species, adjacent equality at the pKa values,
agreement with an independent hydrogen-ion form of the equilibrium expressions,
the closed-sample alkalinity balance and reported final pHs, Henry's law, and
calcite saturation. It regenerates `carbonate-gases/speciation.svg` from the
student script. It also copies the two student downloads into a temporary
folder and renders the report in a fresh R process. Student downloads require
no source files outside their folder.

The report is a working template with explicit writing prompts, not a finished
student interpretation. Its displayed numeric table and diagram are executable;
exercise solutions provide the interpretation. No CSV is needed for this model
activity because its independent inputs are a generated pH grid and stated
constants. Later measured-data activities will need data dictionaries.

If the restricted environment cannot write Quarto's default cache, use
`XDG_CACHE_HOME=/tmp/envchem-quarto-cache make render`.
Instructor material, authoring templates, and planning files are excluded from
the student build. The two student source files are explicit site resources.

## Review before teaching

Choose exact textbook subsections after inspecting chapters 10–11. Pilot recall
of logarithms and equilibrium ratios, check whether the six exercises fit the
available practice time, and review the two short decks in the teaching display.
The content is a first teaching draft; no classroom pilot or browser layout
review has been completed. Later units should revisit the limitations through
organic matter, metal complexes, interfaces, and coupled biological reactions.

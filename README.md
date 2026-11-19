# Environmental Chemistry

A complete first teaching draft for the planned 7.5 ECTS Environmental Chemistry
course: chemistry-led explanations, an aquatic emphasis, and three modest R
activities that reuse introductory computing skills. Programme organization,
timetabling, and formal examination design remain outside scope.

- [Rendered course home](docs/index.html)
- [Course sequence and chapter map](overview.qmd)
- [Content plan and scope](contentplan.md)
- [Instructor notes](instructor/README.md)
- [Capability and practice map](instructor/coverage.md)

## Material

All 15 planned units have notes, learning goals, short reveal.js lectures,
worked examples, and exercises with collapsible hints and worked solutions.
There are 16 lecture decks and 62 numbered exercises, plus the supporting
activity instructions. A linked glossary and scientific model figures support
the chemical explanations. Five browser demos add sliders, reference presets,
live chemical balances, and explanatory plots, with static hand checks.
Their weekly grouping is a working study guide rather than a formal timetable.

The sequence follows the working book's atmosphere → water → terrestrial
structure, with selected topics and depth boundaries stated per unit. The
working reference is vanLoon and Duffy, *Environmental Chemistry: A Global
Perspective*, fourth edition (2017). Chapter assignments are topic selections;
exact subsection/page assignments and final syllabus alignment remain to review.

The three activities cover water-ion tables and charge checks, carbonate species
at prescribed pH, and a two-phase parent-transformation model. Student reports
use R Markdown (`.Rmd`); the teaching website uses Quarto (`.qmd`). Each activity
has starting code, chemical checks, and a portable ZIP. Constructed data,
fictitious compounds, and model predictions are identified explicitly.

## Build and check

Requires Quarto and Python 3 to build the site and package downloads. Node.js 18+ runs the demo checks. R plus
`readr`, `dplyr`, `ggplot2`, and `rmarkdown` are needed for the activities and
chemical/report checks. Pandoc is available through Quarto.

```bash
make check     # demo models, numerical chemistry, and three fresh report renders
make check-demos # focused demo model and boundary checks
make render    # package downloads, build docs/, check links/anchors and resources
make preview   # local Quarto preview
make downloads # rebuild the three student ZIPs without rendering
make clean     # delete generated docs/ and Quarto cache
```

If this restricted environment cannot write Quarto's default cache:

```bash
XDG_CACHE_HOME=/tmp/envchem-quarto-cache make render
```

The website uses pre-generated figures and displays R examples without executing
student reports during the site build. `make check` regenerates the scientific
figures from their stated models; run it when changing those models. ZIPs use
explicit student-input lists, so instructor notes and planning files cannot be
included accidentally. `make render` checks that published downloads match sources.

The demo scripts need no npm dependencies, external service, or build step.
`demos/README.md` describes the embedding contract. Optional browser QA uses an
isolated installed Chrome and `python3 tools/check_demos_browser.py` (requires
`websocket-client`), exercising all controls with external requests blocked.

## Source and hosting conventions

The scaffold is adapted from `/home/mahogny/github/course/quantbio-3MB00A`:
Quarto, `docs/` output, searchable docked sidebar, Cosmo HTML styling, the copied
reveal.js theme, and topic folders with `lec.qmd` and `exercise.qmd`.
The source sidebar hierarchy, default expansion behaviour, coloured week
stripes/tints, and Course info dropdown are retained. Each week contains its
topics and direct orange Demo links to embedded exercise sections. Exercise
links use the source scaffold’s italic cue. The five demos are embedded in
both exercises and lecture slides; standalone week pages remain as guided practice.
Advanced Quantitative Biology lessons, demos, dependencies, and Git metadata
were not copied. The default build does not stage or commit.

GitHub Pages serves `main` → `/docs` at
<https://henriksson-lab.github.io/course_envchem/>. Rendered output is tracked.
Planning Markdown, instructor material, tools, and authoring templates are
excluded from the student build. The weekly demos have had desktop/mobile browser interaction checks;
classroom pacing and the wider course slide-layout review remain open; this draft is not a claim of an approved final course syllabus.

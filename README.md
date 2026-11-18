# Environmental Chemistry

Content planning and a local Quarto scaffold for the 7.5 ECTS Environmental
Chemistry course. The chemistry follows the working textbook, with an aquatic
emphasis and modest reuse of introductory R skills.

Start with [the proposed content plan](contentplan.md). It contains the scope,
chapter map, chemical questions, exercise ideas, computing transfers, and writing
sequence. This is a proposal, not a complete teaching draft or approved syllabus.
Programme organization, timetabling, and examination design are outside scope.

## First teaching unit

[Carbonate and gases](carbonate-gases/notes.qmd) now has two short lecture decks,
a model reference sheet, six exercises with worked solutions, a checked species
plot, and downloadable R code and an R Markdown report template. Other topic
units remain planned. [Instructor notes](instructor/README.md) describe the
chemical checks and remaining teaching review.

## Scaffold

Adapted from `/home/mahogny/github/course/quantbio-3MB00A`:
Quarto website, `docs/` output, docked searchable sidebar, Cosmo HTML theme,
lecture/exercise naming, reveal.js theme, and collapsible exercise hints.
`theme.scss` is copied; `styles.css` retains the general sidebar rules and removes
week-position styling. Configuration and Makefile are reduced for this course.
The default build renders without staging files.

The home page, proposed overview, and carbonate unit are rendered.
`templates/` holds authoring templates excluded from rendering; copy a template
into a topic folder when writing a real unit. Planning Markdown and instructor
material are excluded. No Quantitative Biology lessons, demos, dependencies,
Git metadata, or built outputs were copied.

```bash
make render    # build into docs/
make check     # verify chemistry and render a fresh student report
make preview   # local Quarto preview
make clean     # remove generated docs/ and Quarto cache
```

Requires Quarto. The carbonate activity and `make check` also need R, ggplot2,
and rmarkdown. The website reuses a generated SVG; its examples are displayed
as code without executing student reports during the website build. The teaching
website uses Quarto; student reports use R Markdown, as in
`/home/mahogny/github/course/introcomputing`.

Rendered HTML in `docs/` follows the source course's tracked-output convention.

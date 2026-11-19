# Interactive chemistry demos

One offline browser demo per lecture (16) is embedded directly in their corresponding
exercise `#explore` sections and lecture decks, as in Quantitative Biology.
The sidebar links directly to those exercise sections. The `interactives/`
week pages remain as extra guided practice. The Quarto resource list copies only `*.js` and `demo.css` into
`docs/demos/`; test and instructor files are not copied.

This follows the source Quantitative Biology course's idea of small embedded
DOM/SVG demos, using plain JavaScript rather than its advanced demo dependencies.
No npm install, bundler, external library, network request, or student setup is
required. Node.js 18+ is used only for development checks. Browser files are
classic scripts so the demos also work when a rendered page is opened with
`file://`.

- `core.js`: labelled keyboard-operable controls, presets/reset, metrics, tables,
  SVG charts, shared units/number formatting.
- `deposition.js`: flux → annual equivalents → flow-weighted concentration.
- `carbonate.js`: fixed-carbon species and changed alkalinity after strong acid.
- `metals.js`: imposed free ligand, binding-only distribution, saturation check.
- `fate.js`: closed-system phase inventories and transformed-parent accounting.
- `boxmodel.js`: well-mixed lake approaching steady state (environmental systems).
- `lifetime.js`: OH-controlled atmospheric lifetime and half-life.
- `co2pulse.js`: CO₂ pulse decay versus a one-sink gas (climate).
- `ionbalance.js`: charge balance, ionic strength and activity coefficients.
- `gases.js`: CO₂ degassing and calcite saturation (gases lecture).
- `oxygen.js`: oxygen demand in a sealed bottle.
- `sorption.js`: two-phase bottle with a linear Kd.
- `redox.js`: electron-acceptor sequence as organic matter is oxidised.
- `treatment.js`: sequential treatment stages and the mass balance.
- `soilbuffer.js`: carbonate, exchange and aluminium acid reserves in soil.
- `acidbase.js`: acid potential versus neutralising potential in mine waste.
- `catchment.js`: annual acid budget, capped accessible neutralisation, reference
  alkalinity export, and flow-weighted equivalents.

Each model exports pure calculations for Node checks and mounts in the browser.
`core.mount(name, config)` mounts each `[data-demo="name"]` once. A configuration
specifies numeric controls, reference presets, and an update callback. Each
control has key, label, min, max, step, value, unit, and optional format function.
The callback receives numeric values and `chart`, `results`, and `explanation`
elements. Shared metrics/table and chart functions replace their target content.

## Embed

Use a classic script and the shared stylesheet in an HTML block, following the
exercise and weekly pages. Reveal-specific styles keep lecture embeds compact. Keep the static hand-check result in the Quarto source outside the
interactive block. This provides context when scripts are unavailable and in
print. Use a meaningful `aria-label` on the mount container. Do not add hover-only
results or override keyboard shortcuts globally.

```html
<link rel="stylesheet" href="../demos/demo.css">
<div data-demo="carbonate" role="group" aria-label="Closed-water carbonate model">
  <p>The reference calculation below is available without interactive controls.</p>
</div>
<script src="../demos/core.js"></script>
<script src="../demos/carbonate.js"></script>
```

## Verify

`make check-demos` checks independent reference cases, conservation, units,
limiting inputs, and model/mount contracts with Node's built-in runner.
`make render` copies the browser assets and checks file/fragment targets as well
as the existing activity downloads. Browser checks exercise the actual shared
controls, presets/reset, keyboard access, and mobile layout; model tests alone
do not substitute for these interaction checks.

The demos use constructed models, not live data. Their scientific assumptions
and worked values are on the corresponding student pages and in the model code.

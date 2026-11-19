/* Pulse decay: one first-order sink compared with the CO2 impulse response. No dependencies. */
(function (root, factory) {
  "use strict";
  const api = factory(root);
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.EnvChemCO2PulseDemo = api;
  if (typeof document !== "undefined") {
    const start = function () { api.mount(root.EnvChemDemoCore); };
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start, { once: true });
    else start();
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  // Joos et al. (2013) impulse-response fit used in IPCC AR5 (same values as the lecture figure).
  const CO2_PARTS = Object.freeze([
    Object.freeze({ share: 0.2173, years: Infinity, label: "Very slow part (not removed in this fit)" }),
    Object.freeze({ share: 0.2240, years: 394.4, label: "Slow part" }),
    Object.freeze({ share: 0.2824, years: 36.54, label: "Medium part" }),
    Object.freeze({ share: 0.2763, years: 4.304, label: "Fast part" }),
  ]);

  const defaults = Object.freeze({ lifetimeYears: 12, readYears: 100 });

  function co2Parts(t) {
    if (!Number.isFinite(t) || t < 0) throw new RangeError("Time must be finite and nonnegative");
    return CO2_PARTS.map(p => ({ ...p, left: Number.isFinite(p.years) ? p.share * Math.exp(-t / p.years) : p.share }));
  }

  function co2Fraction(t) {
    return co2Parts(t).reduce((sum, p) => sum + p.left, 0);
  }

  function singleFraction(t, lifetimeYears) {
    if (!Number.isFinite(t) || t < 0) throw new RangeError("Time must be finite and nonnegative");
    if (!Number.isFinite(lifetimeYears) || lifetimeYears <= 0) throw new RangeError("Lifetime must be positive");
    return Math.exp(-t / lifetimeYears);
  }

  function model(values = {}) {
    const input = { ...defaults, ...values };
    const lifetimeYears = Number(input.lifetimeYears);
    const readYears = Number(input.readYears);
    const single = singleFraction(readYears, lifetimeYears);
    const parts = co2Parts(readYears);
    return {
      lifetimeYears, readYears,
      kPerYear: 1 / lifetimeYears,
      halfLifeYears: Math.LN2 * lifetimeYears,
      singleLeft: single,
      co2Left: parts.reduce((sum, p) => sum + p.left, 0),
      co2Parts: parts,
    };
  }

  function mount(core) {
    if (!core) return;
    return core.mount("co2pulse", {
      controls: [
        { key: "lifetimeYears", label: "Lifetime τ of a gas with one sink", min: 1, max: 200, step: 1,
          value: defaults.lifetimeYears, unit: "years" },
        { key: "readYears", label: "Years after the pulse", min: 0, max: 500, step: 5,
          value: defaults.readYears, unit: "years" },
      ],
      presets: [
        { label: "Lecture comparison", values: { lifetimeYears: 12, readYears: 100 } },
        { label: "After 20 years", values: { lifetimeYears: 12, readYears: 20 } },
        { label: "After 500 years", values: { lifetimeYears: 12, readYears: 500 } },
        { label: "Lifetime 50, read at 50", values: { lifetimeYears: 50, readYears: 50 } },
      ],
      update(values, view) {
        const r = model(values);
        const span = [100, 200, 400, 600].find(v => v >= 1.2 * r.readYears);
        const co2 = [], single = [];
        for (let i = 0; i <= 250; i += 1) {
          const t = span * i / 250;
          co2.push({ x: t, y: co2Fraction(t) });
          single.push({ x: t, y: singleFraction(t, r.lifetimeYears) });
        }
        core.lineChart(view.chart, {
          title: "Fraction of an emitted pulse still in the air",
          xLabel: "Years after the pulse is emitted",
          yLabel: "Fraction of pulse in the air",
          xMin: 0, xMax: span, yMin: 0, yMax: 1,
          series: [
            { label: "CO₂ (several sinks; fit used by the IPCC)", color: "#1b2a3a", points: co2 },
            { label: "Gas with one sink, lifetime " + r.lifetimeYears + " years", color: "#25713e", points: single },
          ],
          markers: [{ x: r.readYears, label: r.readYears + " years" }],
        });
        const metrics = document.createElement("div");
        const table = document.createElement("div");
        view.results.replaceChildren(metrics, table);
        const p = v => Number(v.toPrecision(3));
        core.metrics(metrics, [
          { label: "One-sink gas: rate constant k = 1/τ", value: p(r.kPerYear), unit: "per year" },
          { label: "One-sink gas: half-life 0.693 τ", value: p(r.halfLifeYears), unit: "years" },
          { label: "One-sink gas left at " + r.readYears + " years", value: r.singleLeft < 0.001 ? "below 0.001" : r.singleLeft.toFixed(3), unit: "" },
          { label: "CO₂ left at " + r.readYears + " years", value: r.co2Left.toFixed(3), unit: "" },
        ]);
        core.table(table, {
          caption: "The CO₂ curve is four parts added together, each falling at its own pace",
          headers: ["Part of the CO₂ pulse", "Share at start", "Timescale (years)", "Left at " + r.readYears + " years"],
          rows: r.co2Parts.map(part => [part.label, part.share.toFixed(3),
            Number.isFinite(part.years) ? part.years : "centuries or longer", part.left.toFixed(3)])
            .concat([["Whole CO₂ pulse", "1.000", "no single value", r.co2Left.toFixed(3)]]),
        });
        const ratio = r.readYears / r.lifetimeYears;
        let text = "For the one-sink gas the fraction left depends only on time divided by lifetime: here " +
          p(ratio) + " lifetimes have passed, leaving " +
          (r.singleLeft < 0.001 ? "less than 0.001 of the pulse" : r.singleLeft.toFixed(3)) + ". ";
        text += r.readYears === 0
          ? "At the moment of emission all of both pulses is in the air."
          : r.co2Left > r.singleLeft
            ? "The CO₂ pulse keeps more in the air, because a share of it is only taken up by very slow processes. "
            : "At this time the one-sink gas still has more left, because the fast CO₂ sinks act within a few years. ";
        if (r.readYears > 0) {
          text += "CO₂ is not destroyed in the air; it moves into the ocean, plants and soils, and about a fifth of the " +
            "pulse stays in the air for many centuries. No single lifetime describes that curve.";
        }
        view.explanation.textContent = text + " The CO₂ curve is a fit to carbon-cycle models for one pulse added " +
          "to today's air; it is not a prediction for any particular emission path.";
      },
    });
  }

  return { CO2_PARTS, defaults, co2Parts, co2Fraction, singleFraction, model, mount };
});

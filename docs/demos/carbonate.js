/* Closed freshwater carbonate teaching model, 25 C. No network or dependencies. */
(function (root, factory) {
  "use strict";
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (typeof document !== "undefined") {
    const start = function () { api.mount(root.EnvChemDemoCore); };
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start, { once: true });
    else start();
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";
  const K1 = Math.pow(10, -6.35);
  const K2 = Math.pow(10, -10.33);
  const KW = 1e-14;
  const PH_MIN = 0;
  const PH_MAX = 14;

  function fractions(pH) {
    if (!Number.isFinite(pH) || pH < PH_MIN || pH > PH_MAX) {
      throw new RangeError("The freshwater model requires a finite pH between 0 and 14.");
    }
    const h = Math.pow(10, -pH);
    const denominator = h * h + K1 * h + K1 * K2;
    return {
      co2: h * h / denominator,
      bicarbonate: K1 * h / denominator,
      carbonate: K1 * K2 / denominator
    };
  }

  // ctMolL is fixed dissolved inorganic carbon; output is eq/L.
  function alkalinity(pH, ctMolL) {
    if (!Number.isFinite(ctMolL) || ctMolL < 0) {
      throw new RangeError("Dissolved inorganic carbon must be finite and nonnegative.");
    }
    const alpha = fractions(pH);
    const h = Math.pow(10, -pH);
    return ctMolL * (alpha.bicarbonate + 2 * alpha.carbonate) + KW / h - h;
  }

  function solvePH(targetEqL, ctMolL) {
    if (!Number.isFinite(targetEqL)) {
      return { ok: false, reason: "The target alkalinity must be finite." };
    }
    let lower = PH_MIN;
    let upper = PH_MAX;
    const minimum = alkalinity(lower, ctMolL);
    const maximum = alkalinity(upper, ctMolL);
    if (targetEqL < minimum || targetEqL > maximum) {
      return { ok: false, reason: "The target lies outside the pH 0–14 calculation bracket. No final pH is reported." };
    }
    // At fixed CT, this carbonate-only alkalinity increases monotonically with pH.
    for (let i = 0; i < 100; i += 1) {
      const middle = (lower + upper) / 2;
      if (alkalinity(middle, ctMolL) < targetEqL) lower = middle;
      else upper = middle;
    }
    return { ok: true, pH: (lower + upper) / 2 };
  }

  function model(values) {
    const ctMmolL = Number(values.ctMmolL);
    const initialPH = Number(values.initialPH);
    const acidMeqL = Number(values.acidMeqL);
    if (!Number.isFinite(ctMmolL) || ctMmolL <= 0 ||
        !Number.isFinite(initialPH) || initialPH < PH_MIN || initialPH > PH_MAX ||
        !Number.isFinite(acidMeqL) || acidMeqL < 0) {
      return { ok: false, reason: "Use a positive finite carbon total, a pH from 0 to 14, and a nonnegative finite acid dose." };
    }
    const ctMolL = ctMmolL / 1000;
    const beforeEqL = alkalinity(initialPH, ctMolL);
    const targetEqL = beforeEqL - acidMeqL / 1000;
    const solution = solvePH(targetEqL, ctMolL);
    if (!solution.ok) return solution;
    return {
      ok: true,
      ctMmolL: ctMmolL,
      initialPH: initialPH,
      acidMeqL: acidMeqL,
      finalPH: solution.pH,
      initialAlkalinityMeqL: beforeEqL * 1000,
      finalAlkalinityMeqL: targetEqL * 1000,
      initialFractions: fractions(initialPH),
      finalFractions: fractions(solution.pH)
    };
  }

  function mount(core) {
    if (!core) return;
    core.mount("carbonate", {
      controls: [
        { key: "ctMmolL", label: "Fixed dissolved inorganic carbon", min: 0.05, max: 2, step: 0.05, value: 1, unit: "mmol/L", format: function (v) { return v.toFixed(2); } },
        { key: "initialPH", label: "Initial pH", min: 5.5, max: 9.5, step: 0.05, value: 7.5, unit: "", format: function (v) { return v.toFixed(2); } },
        { key: "acidMeqL", label: "Strong-acid addition", min: 0, max: 0.2, step: 0.005, value: 0.05, unit: "meq/L", format: function (v) { return v.toFixed(3); } }
      ],
      presets: [
        { label: "Water A: more carbon", values: { ctMmolL: 1, initialPH: 7.5, acidMeqL: 0.05 } },
        { label: "Water B: less carbon", values: { ctMmolL: 0.1, initialPH: 7.5, acidMeqL: 0.05 } },
        { label: "No acid added", values: { ctMmolL: 1, initialPH: 7.5, acidMeqL: 0 } },
        { label: "Check pH 8.35 fractions", values: { ctMmolL: 1, initialPH: 8.35, acidMeqL: 0 } }
      ],
      update: function (values, view) {
        const result = model(values);
        if (!result.ok) {
          view.chart.replaceChildren();
          view.results.replaceChildren();
          view.explanation.textContent = result.reason;
          return;
        }
        const species = [
          { key: "co2", label: "CO₂*", color: "#2468a0" },
          { key: "bicarbonate", label: "HCO₃⁻", color: "#25713e" },
          { key: "carbonate", label: "CO₃²⁻", color: "#ad4825" }
        ];
        const grid = [];
        for (let i = 0; i <= 200; i += 1) {
          const pH = 2 + i / 20;
          grid.push({ pH: pH, alpha: fractions(pH) });
        }
        const plotMin = Math.min(2, result.finalPH);
        const plotMax = Math.max(12, result.initialPH);
        core.lineChart(view.chart, {
          title: "Model carbonate fractions; markers locate the initial and final states",
          xLabel: "Prescribed pH for the distribution curves",
          yLabel: "Fraction of dissolved inorganic carbon",
          xMin: plotMin,
          xMax: plotMax,
          yMin: 0,
          yMax: 1,
          series: species.map(function (entry) {
            return { label: entry.label, color: entry.color,
              points: grid.map(function (point) { return { x: point.pH, y: point.alpha[entry.key] }; }) };
          }),
          markers: [
            { x: result.initialPH, label: "Initial " + result.initialPH.toFixed(2) },
            { x: result.finalPH, label: "Final " + result.finalPH.toFixed(3) }
          ]
        });
        const metrics = document.createElement("div");
        const table = document.createElement("div");
        view.results.replaceChildren(metrics, table);
        core.metrics(metrics, [
          { label: "Final model pH", value: result.finalPH.toFixed(3), unit: "" },
          { label: "Initial alkalinity", value: result.initialAlkalinityMeqL.toFixed(4), unit: "meq/L" },
          { label: "Final alkalinity", value: result.finalAlkalinityMeqL.toFixed(4), unit: "meq/L" },
          { label: "Conserved inorganic carbon", value: result.ctMmolL.toFixed(2), unit: "mmol/L" }
        ]);
        core.table(table, {
          headers: ["Carbon pool", "Initial fraction", "Final fraction", "Final concentration (mmol/L)"],
          rows: species.map(function (entry) {
            const fraction = result.finalFractions[entry.key];
            return [entry.label, result.initialFractions[entry.key].toFixed(4),
              fraction.toFixed(4), (fraction * result.ctMmolL).toPrecision(4)];
          })
        });
        const shift = result.initialPH - result.finalPH;
        const interpretation = result.acidMeqL === 0
          ? "With no acid added, the final state equals the initial state. Compare carbon totals: the fractions at a fixed pH stay the same, but the species concentrations and alkalinity change."
          : "The acid lowers alkalinity by " + result.acidMeqL.toFixed(3) + " meq/L and the model pH falls by " + shift.toFixed(3) + ". Carbon is redistributed toward CO₂*; the dissolved carbon total is conserved. Compare the Water A and Water B presets to see why equal starting pH does not imply equal resistance to this dose.";
        view.explanation.textContent = interpretation + " These are equilibrium model predictions at 25 °C for dilute freshwater, with no gas exchange, mineral reactions, biological change, or dilution. The curves use prescribed pH; the final-state marker additionally satisfies the changed alkalinity balance. CO₂* combines dissolved CO₂ and H₂CO₃.";
      }
    });
  }

  return { fractions: fractions, alkalinity: alkalinity, solvePH: solvePH, model: model, mount: mount };
});

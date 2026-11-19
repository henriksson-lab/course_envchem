/* Open-water CO2 exchange and calcite saturation teaching model, 25 C. No network or dependencies. */
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
  // Constants from carbonate-gases/reference.qmd and make_gases_figures.py.
  const K1 = Math.pow(10, -6.35);
  const K2 = Math.pow(10, -10.33);
  const KW = 1e-14;
  const KH = 0.034;      // mol L-1 atm-1
  const KSP = 3.3e-9;    // calcite, concentrations used for activities
  const P_AIR = 4.0e-4;  // exercise value, atm
  const P_SOIL = 1.0e-2; // soil air, atm

  const defaults = Object.freeze({ pco2Atm: P_SOIL, alkMeqL: 2.8, caMmolL: 1.4 });

  function fractions(pH) {
    const h = Math.pow(10, -pH);
    const d = h * h + K1 * h + K1 * K2;
    return { co2: h * h / d, bicarbonate: K1 * h / d, carbonate: K1 * K2 / d };
  }

  // Alkalinity (eq/L) of a water whose CO2* is fixed by the gas, at a given pH.
  function openAlkalinity(pH, co2MolL) {
    const h = Math.pow(10, -pH);
    const r1 = K1 / h;
    const r2 = K2 / h;
    return co2MolL * (r1 + 2 * r1 * r2) + KW / h - h;
  }

  function model(values = {}) {
    const input = { ...defaults, ...values };
    if (!Number.isFinite(input.pco2Atm) || input.pco2Atm <= 0) {
      throw new RangeError("The CO2 partial pressure must be finite and positive.");
    }
    if (!Number.isFinite(input.alkMeqL) || input.alkMeqL < 0) {
      throw new RangeError("Alkalinity must be finite and nonnegative.");
    }
    if (!Number.isFinite(input.caMmolL) || input.caMmolL < 0) {
      throw new RangeError("Calcium must be finite and nonnegative.");
    }
    const co2MolL = KH * input.pco2Atm;
    const target = input.alkMeqL / 1000;
    // At fixed CO2*, alkalinity rises steadily with pH, so bisection is safe.
    let lo = 0;
    let hi = 14;
    if (target > openAlkalinity(hi, co2MolL)) throw new RangeError("Alkalinity is outside the pH 0–14 range.");
    for (let i = 0; i < 100; i += 1) {
      const mid = (lo + hi) / 2;
      if (openAlkalinity(mid, co2MolL) < target) lo = mid;
      else hi = mid;
    }
    const pH = (lo + hi) / 2;
    const alpha = fractions(pH);
    const ctMolL = co2MolL / alpha.co2;
    const co3MolL = ctMolL * alpha.carbonate;
    const omega = (input.caMmolL / 1000) * co3MolL / KSP;
    return {
      ...input,
      pH,
      co2UmolL: co2MolL * 1e6,
      ctMmolL: ctMolL * 1000,
      hco3MmolL: ctMolL * alpha.bicarbonate * 1000,
      co3UmolL: co3MolL * 1e6,
      gasShare: alpha.co2,
      omega,
    };
  }

  // Slider works on log10(p); round p to two significant figures so presets hit exact values.
  function pressure(logP) {
    return Number(Math.pow(10, logP).toPrecision(2));
  }

  const SUP = { "-": "⁻", "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹" };
  function formatPressure(p) {
    const exponent = Math.floor(Math.log10(p) + 1e-9);
    const mantissa = p / Math.pow(10, exponent);
    const power = String(exponent).split("").map(function (c) { return SUP[c]; }).join("");
    return mantissa.toFixed(1) + " × 10" + power;
  }

  function mount(core) {
    if (!core) return;
    core.mount("gases", {
      controls: [
        { key: "logP", label: "CO₂ in the gas the water meets", min: -4, max: -2, step: 0.05,
          value: Math.log10(defaults.pco2Atm), unit: "atm",
          format: function (v) { return formatPressure(pressure(v)); } },
        { key: "alkMeqL", label: "Alkalinity (held fixed)", min: 0, max: 4, step: 0.01,
          value: defaults.alkMeqL, unit: "meq/L", format: function (v) { return v.toFixed(2); } },
        { key: "caMmolL", label: "Free calcium, Ca²⁺", min: 0.05, max: 3, step: 0.01,
          value: defaults.caMmolL, unit: "mmol/L", format: function (v) { return v.toFixed(2); } }
      ],
      presets: [
        { label: "Groundwater in soil air", values: { logP: -2, alkMeqL: 2.8, caMmolL: 1.4 } },
        { label: "Same water degassed to air", values: { logP: Math.log10(P_AIR), alkMeqL: 2.8, caMmolL: 1.4 } },
        { label: "Exercise 3: pH 8.35 water", values: { logP: Math.log10(P_AIR), alkMeqL: 1.39, caMmolL: 0.5 } },
        { label: "Rain: no alkalinity", values: { logP: Math.log10(P_AIR), alkMeqL: 0, caMmolL: 0.05 } }
      ],
      update: function (values, view) {
        const p = pressure(values.logP);
        const result = model({ pco2Atm: p, alkMeqL: values.alkMeqL, caMmolL: values.caMmolL });
        const points = [];
        for (let i = 0; i <= 80; i += 1) {
          const logP = -4 + i / 40;
          const r = model({ pco2Atm: Math.pow(10, logP), alkMeqL: values.alkMeqL, caMmolL: values.caMmolL });
          points.push({ x: logP, y: Math.log10(r.omega) });
        }
        core.lineChart(view.chart, {
          title: "Calcite saturation as the water equilibrates with more or less CO₂",
          xLabel: "CO₂ in the gas as log₁₀ p (atm): −3.4 is air, −2 is soil air",
          yLabel: "log₁₀ Ω (0 means saturated)",
          xMin: -4, xMax: -2, yMin: -4, yMax: 4,
          series: [
            { label: "This water at fixed alkalinity and calcium", color: "#2468a0", points: points },
            { label: "Saturated, Ω = 1", color: "#a84b20",
              points: [{ x: -4, y: 0 }, { x: -2, y: 0 }] }
          ],
          markers: [
            { x: values.logP, label: "This water" },
            { x: Math.log10(P_AIR), label: "Air" }
          ]
        });
        core.metrics(view.results, [
          { label: "Dissolved CO₂* (Henry's law)", value: result.co2UmolL.toFixed(1), unit: "µmol/L" },
          { label: "Model pH", value: result.pH.toFixed(2), unit: "" },
          { label: "Total inorganic carbon", value: result.ctMmolL.toFixed(3), unit: "mmol/L" },
          { label: "Carbonate CO₃²⁻", value: result.co3UmolL.toFixed(2), unit: "µmol/L" },
          { label: "Calcite saturation Ω", value: result.omega < 0.01 ? result.omega.toExponential(1) : result.omega.toFixed(2), unit: "" }
        ]);
        let state;
        if (result.omega < 0.9) state = "The water is undersaturated (Ω below 1): it could dissolve calcite if calcite is present.";
        else if (result.omega <= 1.1) state = "The water is close to saturation (Ω near 1).";
        else state = "The water is supersaturated (Ω above 1): calcite forming is favoured, but Ω says nothing about how fast or how much.";
        view.explanation.textContent =
          "Henry's law fixes only CO₂* at " + result.co2UmolL.toFixed(1) + " µmol/L; with the alkalinity held fixed, that sets pH " +
          result.pH.toFixed(2) + ". CO₂* is " + (100 * result.gasShare).toFixed(result.gasShare < 0.1 ? 1 : 0) +
          "% of the dissolved inorganic carbon. Moving left on the plot is degassing: total inorganic carbon falls, alkalinity stays, pH and carbonate rise, so Ω rises. " +
          state + " Model at 25 °C in dilute freshwater, at gas equilibrium, with no calcite yet formed or dissolved.";
      }
    });
  }

  return { K1, K2, KW, KH, KSP, defaults, fractions, openAlkalinity, model, pressure, mount };
});

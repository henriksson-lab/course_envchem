/* Annual catchment equivalent budget. Constructed inputs, not a pH model. */
(function (root, factory) {
  const api = factory(root);
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.EnvChemCatchmentDemo = api;
  if (typeof document !== "undefined") {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", () => api.mount());
    } else api.mount();
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function (root) {
  "use strict";

  const defaults = Object.freeze({
    acidKeq: 40,
    capacityKeq: 30,
    referenceKeq: 50,
    waterMillionL: 500,
  });

  function model(values = {}) {
    const input = { ...defaults, ...values };
    for (const key of Object.keys(defaults)) {
      if (!Number.isFinite(input[key]) || input[key] < 0) {
        throw new RangeError(`${key} must be a finite nonnegative number`);
      }
    }
    if (input.waterMillionL === 0) {
      throw new RangeError("Annual water export must be positive");
    }
    const acidEqYear = input.acidKeq * 1000;
    const capacityEqYear = input.capacityKeq * 1000;
    const referenceEqYear = input.referenceKeq * 1000;
    const waterL = input.waterMillionL * 1e6;
    // Capacity that never reacts with this input is not credited to alkalinity.
    const neutralisedEqYear = Math.min(acidEqYear, capacityEqYear);
    const unusedCapacityEqYear = capacityEqYear - neutralisedEqYear;
    const residualEqYear = acidEqYear - neutralisedEqYear;
    const adjustedAlkalinityEqYear = referenceEqYear - residualEqYear;
    return {
      ...input,
      acidEqYear,
      capacityEqYear,
      referenceEqYear,
      waterL,
      neutralisedEqYear,
      unusedCapacityEqYear,
      residualEqYear,
      adjustedAlkalinityEqYear,
      residualMeqL: (residualEqYear / waterL) * 1000,
      referenceMeqL: (referenceEqYear / waterL) * 1000,
      adjustedAlkalinityMeqL: (adjustedAlkalinityEqYear / waterL) * 1000,
    };
  }

  function mount(core = root.EnvChemDemoCore) {
    if (!core) return;
    return core.mount("catchment", {
      controls: [
        { key: "acidKeq", label: "Annual acid input", min: 0, max: 100, step: 1,
          value: defaults.acidKeq, unit: "thousand eq/year" },
        { key: "capacityKeq", label: "Accessible neutralisation capacity", min: 0,
          max: 100, step: 1, value: defaults.capacityKeq, unit: "thousand eq/year" },
        { key: "referenceKeq", label: "Reference alkalinity export", min: 0,
          max: 150, step: 1, value: defaults.referenceKeq, unit: "thousand eq/year" },
        { key: "waterMillionL", label: "Annual water export", min: 100, max: 1500,
          step: 50, value: defaults.waterMillionL, unit: "million L/year" },
      ],
      presets: [
        { label: "Worked catchment", values: { ...defaults } },
        { label: "Less neutralisation", values: { ...defaults, capacityKeq: 20 } },
        { label: "Double water export", values: { ...defaults, waterMillionL: 1000 } },
        { label: "Capacity exceeds input", values: { ...defaults, capacityKeq: 60 } },
        { label: "Exceed reference alkalinity", values: { ...defaults, acidKeq: 100,
          capacityKeq: 20 } },
      ],
      update(values, view) {
        const result = model(values);
        core.barChart(view.chart, {
          title: "Close the annual equivalent budget before calculating concentration",
          unit: "eq/year",
          bars: [
            { label: "Acid input", value: result.acidEqYear, color: "#a84b20" },
            { label: "Acid actually neutralised", value: result.neutralisedEqYear,
              color: "#25713e" },
            { label: "Residual acid", value: result.residualEqYear, color: "#91508c" },
            { label: "Reference alkalinity export", value: result.referenceEqYear,
              color: "#2468a0" },
          ],
        });
        core.metrics(view.results, [
          { label: "Acid actually neutralised", value: result.neutralisedEqYear.toLocaleString(
            "en-GB", { maximumFractionDigits: 0 }), unit: "eq/year" },
          { label: "Unused capacity", value: result.unusedCapacityEqYear.toLocaleString(
            "en-GB", { maximumFractionDigits: 0 }), unit: "eq/year" },
          { label: "Residual acid-equivalent concentration",
            value: result.residualMeqL.toFixed(4), unit: "meq/L" },
          { label: "Reference alkalinity", value: result.referenceMeqL.toFixed(4),
            unit: "meq/L" },
          { label: "Adjusted alkalinity export",
            value: result.adjustedAlkalinityMeqL.toFixed(4), unit: "meq/L" },
        ]);
        let explanation;
        if (result.acidEqYear === 0) {
          explanation = "With no added acid, the reference alkalinity export is unchanged. " +
            "Unused neutralisation capacity is not counted as an extra alkalinity source. ";
        } else if (result.residualEqYear === 0) {
          explanation = "All stipulated acid input is neutralised, so the reference " +
            "alkalinity export is retained. Capacity is an upper limit: only the acid " +
            "actually neutralised enters the budget. ";
        } else if (result.adjustedAlkalinityEqYear < 0) {
          explanation = "Residual acid exceeds the reference alkalinity export. The " +
            "signed result is a negative alkalinity balance, not a negative dissolved " +
            "concentration or a computed pH. ";
        } else {
          explanation = "Subtract acid actually neutralised from acid input, then subtract " +
            "the residual from the reference alkalinity export. Less accessible " +
            "neutralisation leaves more residual acid and less alkalinity export. ";
        }
        view.explanation.textContent = explanation +
          "These are annual flow-weighted quantities with the other supplied terms fixed. " +
          "Changing water export alone changes concentrations, not those annual amounts. " +
          "A pH prediction also needs inorganic carbon, gas exchange, and other acid–base constraints.";
      },
    });
  }

  return { defaults, model, mount };
});

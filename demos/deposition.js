/* Annual deposition teaching model. No dependencies, network requests, or fits. */
(function (root, factory) {
  const api = factory(root);
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.EnvChemDepositionDemo = api;
  if (typeof document !== "undefined") {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", () => api.mount());
    } else api.mount();
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function (root) {
  "use strict";

  const defaults = Object.freeze({
    hno3Mmol: 20,
    h2so4Mmol: 10,
    areaKm2: 1,
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
    const areaM2 = input.areaKm2 * 1e6;
    const waterL = input.waterMillionL * 1e6;
    // Supplied HNO3 and H2SO4 fluxes represent fully accounted acid inputs.
    // Do not interpret measured nitrate/sulfate as free-acid equivalents blindly.
    const nitricFluxEqM2 = input.hno3Mmol / 1000;
    const sulfuricFluxEqM2 = (2 * input.h2so4Mmol) / 1000;
    const nitricEqYear = nitricFluxEqM2 * areaM2;
    const sulfuricEqYear = sulfuricFluxEqM2 * areaM2;
    const totalFluxEqM2 = nitricFluxEqM2 + sulfuricFluxEqM2;
    const acidEqYear = nitricEqYear + sulfuricEqYear;
    const acidMeqL = (acidEqYear / waterL) * 1000;
    return {
      ...input,
      areaM2,
      waterL,
      nitricFluxEqM2,
      sulfuricFluxEqM2,
      totalFluxEqM2,
      nitricEqYear,
      sulfuricEqYear,
      acidEqYear,
      acidMeqL,
    };
  }

  function mount(core = root.EnvChemDemoCore) {
    if (!core) return;
    return core.mount("deposition", {
      controls: [
        { key: "hno3Mmol", label: "HNO₃ deposition flux", min: 0, max: 50, step: 1,
          value: defaults.hno3Mmol, unit: "mmol m⁻² year⁻¹" },
        { key: "h2so4Mmol", label: "H₂SO₄ deposition flux", min: 0, max: 30, step: 1,
          value: defaults.h2so4Mmol, unit: "mmol m⁻² year⁻¹" },
        { key: "areaKm2", label: "Catchment area", min: 0.1, max: 5, step: 0.1,
          value: defaults.areaKm2, unit: "km²" },
        { key: "waterMillionL", label: "Annual water export", min: 100, max: 1500,
          step: 50, value: defaults.waterMillionL, unit: "million L/year" },
      ],
      presets: [
        { label: "Worked example", values: { ...defaults } },
        { label: "Double water export", values: { ...defaults, waterMillionL: 1000 } },
        { label: "Double catchment area", values: { ...defaults, areaKm2: 2 } },
        { label: "Zero acid input", values: { ...defaults, hno3Mmol: 0, h2so4Mmol: 0 } },
      ],
      update(values, view) {
        const result = model(values);
        core.barChart(view.chart, {
          title: "Annual acid input by chemical source",
          unit: "eq/year",
          bars: [
            { label: "From supplied HNO₃", value: result.nitricEqYear, color: "#2468a0" },
            { label: "From supplied H₂SO₄", value: result.sulfuricEqYear, color: "#a84b20" },
            { label: "Total acid input", value: result.acidEqYear, color: "#25713e" },
          ],
        });
        core.metrics(view.results, [
          { label: "Equivalent flux", value: result.totalFluxEqM2.toFixed(4),
            unit: "eq m⁻² year⁻¹" },
          { label: "Annual acid load", value: result.acidEqYear.toLocaleString("en-GB", {
            maximumFractionDigits: 0 }), unit: "eq/year" },
          { label: "Before-neutralisation equivalent concentration",
            value: result.acidMeqL.toFixed(4), unit: "meq/L" },
        ]);
        view.explanation.textContent = result.acidEqYear === 0
          ? "There is no acid input in this model, whatever the water export. " +
            "These are supplied acid fluxes; neither rain pH nor an isolated sulfate result " +
            "would establish the whole deposition budget."
          : "The annual load is flux multiplied by catchment area. The equivalent " +
            "concentration divides that load by annual water export. Increasing area " +
            "at fixed water export increases both load and concentration; increasing " +
            "water export alone dilutes the same annual load. All input is assumed exported, " +
            "without storage or other sinks. This comparison excludes " +
            "catchment neutralisation and does not predict pH or a closed-lake acid pulse.";
      },
    });
  }

  return { defaults, model, mount };
});

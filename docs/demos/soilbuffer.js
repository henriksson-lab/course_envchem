/* Soil acid-neutralising inventories: carbonate, then exchangeable base cations, then aluminium.
   Constructed teaching model; no rates, weathering, uptake, dependencies or network. */
(function (root, factory) {
  const api = factory(root);
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.EnvChemSoilBufferDemo = api;
  if (typeof document !== "undefined") {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", () => api.mount());
    } else api.mount();
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function (root) {
  "use strict";

  // Soil B (clay loam) from the lecture: CEC 20.0, base cations 14.2 cmolc/kg, no carbonate.
  const defaults = Object.freeze({
    cecCmolc: 20,
    basesCmolc: 14.2,
    carbonateCmol: 0,
    acidCmolc: 5,
  });

  function model(values = {}) {
    const input = { ...defaults, ...values };
    for (const key of Object.keys(defaults)) {
      if (!Number.isFinite(input[key]) || input[key] < 0) {
        throw new RangeError(`${key} must be a finite nonnegative number`);
      }
    }
    if (input.cecCmolc === 0) throw new RangeError("CEC must be positive");
    if (input.basesCmolc > input.cecCmolc + 1e-9) {
      throw new RangeError("Exchangeable base cations cannot exceed CEC");
    }
    // CaCO3 + 2H+ -> Ca2+ + CO2* + H2O: two equivalents of acid per mole of calcite.
    const carbonateCmolc = 2 * input.carbonateCmol;
    const reserveCmolc = carbonateCmolc + input.basesCmolc;
    const acid = input.acidCmolc;
    // Order as in the lecture: carbonate first, then exchange (one base equivalent per acid equivalent).
    const byCarbonate = Math.min(acid, carbonateCmolc);
    const byExchange = Math.min(acid - byCarbonate, input.basesCmolc);
    const byAluminium = acid - byCarbonate - byExchange;
    const carbonateLeftCmolc = carbonateCmolc - byCarbonate;
    const basesLeftCmolc = input.basesCmolc - byExchange;
    const stage = byAluminium > 0 ? "aluminium"
      : carbonateLeftCmolc > 0 ? "carbonate" : basesLeftCmolc > 0 ? "exchange" : "aluminium";
    return {
      ...input,
      carbonateCmolc,
      reserveCmolc,
      byCarbonate,
      byExchange,
      byAluminium,
      carbonateLeftCmolc,
      basesLeftCmolc,
      reserveLeftCmolc: carbonateLeftCmolc + basesLeftCmolc,
      baseSaturationPct: 100 * input.basesCmolc / input.cecCmolc,
      baseSaturationAfterPct: 100 * basesLeftCmolc / input.cecCmolc,
      // If the exchanged bases were all Ca2+, moles of Ca are half the moles of charge.
      calciumLostCmol: byExchange / 2,
      stage,
    };
  }

  function fmt(value, digits = 1) {
    return value.toLocaleString("en-GB", { minimumFractionDigits: digits, maximumFractionDigits: digits });
  }

  function mount(core = root.EnvChemDemoCore) {
    if (!core) return;
    const one = v => v.toFixed(1);
    return core.mount("soilbuffer", {
      controls: [
        { key: "cecCmolc", label: "Cation exchange capacity (CEC)", min: 1, max: 30, step: 0.1,
          value: defaults.cecCmolc, unit: "cmolc/kg", format: one },
        { key: "basesCmolc", label: "Exchangeable base cations", min: 0, max: 30, step: 0.1,
          value: defaults.basesCmolc, unit: "cmolc/kg", format: one },
        { key: "carbonateCmol", label: "Accessible CaCO₃", min: 0, max: 10, step: 0.1,
          value: defaults.carbonateCmol, unit: "cmol/kg", format: one },
        { key: "acidCmolc", label: "Cumulative acid added", min: 0, max: 30, step: 0.1,
          value: defaults.acidCmolc, unit: "cmolc/kg", format: one },
      ],
      presets: [
        { label: "Soil B: clay loam", values: { ...defaults } },
        { label: "Soil A: sandy podzol", values: { cecCmolc: 3, basesCmolc: 1.7, carbonateCmol: 0, acidCmolc: 5 } },
        { label: "Exercise 2: 9.0 of 12.0", values: { cecCmolc: 12, basesCmolc: 9, carbonateCmol: 0, acidCmolc: 0 } },
        { label: "Soil A, limed: 2 cmol/kg CaCO₃", values: { cecCmolc: 3, basesCmolc: 1.7, carbonateCmol: 2, acidCmolc: 5 } },
      ],
      update(values, view) {
        let capped = false;
        if (values.basesCmolc > values.cecCmolc) { values.basesCmolc = values.cecCmolc; capped = true; }
        const r = model(values);
        // Axis limits in multiples of 4 or 8 keep the tick labels whole numbers.
        const xMax = Math.max(20, Math.ceil((r.reserveCmolc + 3) / 8) * 8, Math.ceil(r.acidCmolc / 8) * 8);
        const carbonate = [], bases = [], aluminium = [];
        const steps = 300;
        for (let i = 0; i <= steps; i += 1) {
          const q = xMax * i / steps;
          const s = model({ ...values, acidCmolc: q });
          carbonate.push({ x: q, y: s.carbonateLeftCmolc });
          bases.push({ x: q, y: s.basesLeftCmolc });
          aluminium.push({ x: q, y: s.byAluminium });
        }
        const markers = [{ x: r.acidCmolc, label: "Acid added " + fmt(r.acidCmolc) }];
        if (r.reserveCmolc > 0 && Math.abs(r.reserveCmolc - r.acidCmolc) > 0.05 * xMax) {
          markers.push({ x: r.reserveCmolc, label: "Bases used up at " + fmt(r.reserveCmolc) });
        }
        core.lineChart(view.chart, {
          title: "What is left to neutralise acid as acid accumulates",
          xLabel: "Cumulative acid added (cmolc/kg)",
          yLabel: "Amount (cmolc/kg)",
          xMin: 0, xMax, yMin: 0,
          yMax: Math.max(4, Math.ceil(Math.max(r.carbonateCmolc, r.basesCmolc, xMax - r.reserveCmolc) / 4) * 4),
          series: [
            { label: "CaCO₃ left (as charge)", color: "#2468a0", points: carbonate },
            { label: "Exchangeable base cations left", color: "#25713e", points: bases },
            { label: "Acid buffered by aluminium", color: "#a84b20", points: aluminium },
          ],
          markers,
        });
        core.metrics(view.results, [
          { label: "Base saturation before → after", value: fmt(r.baseSaturationPct, 0) + " % → " +
            fmt(r.baseSaturationAfterPct, 0), unit: "%" },
          { label: "Reserve before aluminium takes over", value: fmt(r.reserveCmolc), unit: "cmolc/kg" },
          { label: "Acid now buffered by aluminium", value: fmt(r.byAluminium), unit: "cmolc/kg" },
        ]);
        let text;
        if (r.acidCmolc === 0) {
          text = "No acid added yet. The soil holds " + fmt(r.reserveCmolc) +
            " cmolc/kg of neutralising reserve, but its pH reading alone would not tell you that.";
        } else if (r.stage === "carbonate") {
          text = "Carbonate is still dissolving (2 equivalents of acid per mole of CaCO₃). The exchanger has not been touched yet.";
        } else if (r.byAluminium === 0) {
          text = "Each equivalent of acid has pushed one equivalent of base cations off the exchanger and out with the drainage water. " +
            "If they were all Ca²⁺, that is " + fmt(r.calciumLostCmol, 2) + " cmol Ca per kg, half the charge. " +
            fmt(r.reserveLeftCmolc) + " cmolc/kg is left before aluminium takes over.";
        } else {
          text = "The base cations are used up after " + fmt(r.reserveCmolc) + " cmolc/kg. The last " +
            fmt(r.byAluminium) + " cmolc/kg of acid is buffered by dissolving aluminium, so Al³⁺ fills the sites and reaches the soil water and stream.";
        }
        if (capped) text = "Base cations cannot exceed CEC, so they were set equal to CEC. " + text;
        view.explanation.textContent = text +
          " Compare Soil A and Soil B: similar pH, very different reserves. Slow weathering and uptake by plants are left out.";
      },
    });
  }

  return { defaults, model, mount };
});

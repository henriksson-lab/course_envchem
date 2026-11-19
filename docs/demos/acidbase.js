/* Acid-base accounting for sulfide mine waste. No dependencies, network requests, or fits. */
(function (root, factory) {
  const api = factory(root);
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.EnvChemAcidBaseDemo = api;
  if (typeof document !== "undefined") {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", () => api.mount());
    } else api.mount();
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function (root) {
  "use strict";

  // Supplied molar masses, as in the lecture and notes.
  const MOLAR_MASS_FES2 = 120; // g/mol
  const MOLAR_MASS_CACO3 = 100; // g/mol
  // FeS2 + 15/4 O2 + 7/2 H2O -> Fe(OH)3 + 2 SO4^2- + 4 H+
  const H_PER_FES2 = 4;
  const SO4_PER_FES2 = 2;
  const YEARS_SHOWN = 160;

  const defaults = Object.freeze({
    pyritePct: 1,        // % FeS2 by mass of the waste
    calciteKgT: 7.5,     // kg CaCO3 per tonne of waste
    eqPerCaCO3: 2,       // 2 = CO2* endpoint, 1 = near-neutral (HCO3-) endpoint
    accessiblePct: 100,  // % of the calcite that acid can reach
    ratePerYear: 0.02,   // illustrative first-order pyrite oxidation rate
  });

  function check(name, value, min, max) {
    if (!Number.isFinite(value) || value < min || value > max) {
      throw new RangeError(`${name} must be a finite number from ${min} to ${max}`);
    }
  }

  /* Stoichiometric budget in moles, as in the worked example and exercise 2. */
  function acidBudget({ feS2Mol, caco3Mol, eqPerCaCO3 = 2 }) {
    check("feS2Mol", feS2Mol, 0, Infinity);
    check("caco3Mol", caco3Mol, 0, Infinity);
    if (eqPerCaCO3 !== 1 && eqPerCaCO3 !== 2) {
      throw new RangeError("eqPerCaCO3 must be 1 (near-neutral) or 2 (CO2* endpoint)");
    }
    const acidEq = H_PER_FES2 * feS2Mol;
    const sulfateMol = SO4_PER_FES2 * feS2Mol;
    const capacityEq = eqPerCaCO3 * caco3Mol;
    const neutralisedEq = Math.min(acidEq, capacityEq);
    const caco3NeededMol = acidEq / eqPerCaCO3;
    return {
      acidEq,
      sulfateMol,
      capacityEq,
      neutralisedEq,
      residualAcidEq: acidEq - neutralisedEq,
      caco3NeededMol,
      caco3NeededG: caco3NeededMol * MOLAR_MASS_CACO3,
    };
  }

  function model(values = {}) {
    const input = { ...defaults, ...values };
    check("pyritePct", input.pyritePct, 0, 100);
    check("calciteKgT", input.calciteKgT, 0, 1000);
    check("accessiblePct", input.accessiblePct, 0, 100);
    if (!Number.isFinite(input.ratePerYear) || input.ratePerYear <= 0) {
      throw new RangeError("ratePerYear must be a finite positive number");
    }
    // Per tonne of waste: kg/t x 1000 g/kg / (g/mol) = mol/t.
    const feS2Mol = (input.pyritePct / 100) * 1e6 / MOLAR_MASS_FES2;
    const caco3Mol = input.calciteKgT * 1000 / MOLAR_MASS_CACO3;
    const accessibleMol = caco3Mol * input.accessiblePct / 100;
    const budget = acidBudget({ feS2Mol, caco3Mol: accessibleMol, eqPerCaCO3: input.eqPerCaCO3 });
    const ap = budget.acidEq;
    const np = budget.capacityEq;
    // Cumulative acid generated: AP(1 - exp(-kt)). Calcite runs out when this reaches NP.
    const exhaustionYears = np <= 0 ? 0 : np < ap ? -Math.log(1 - np / ap) / input.ratePerYear : Infinity;
    const halfLifeYears = Math.log(2) / input.ratePerYear;
    return {
      ...input,
      feS2Mol,
      caco3Mol,
      accessibleMol,
      acidPotentialEqT: ap,
      neutralisationEqT: np,
      totalCalciteEqT: input.eqPerCaCO3 * caco3Mol,
      sulfateMolT: budget.sulfateMol,
      caco3NeededKgT: budget.caco3NeededG / 1000,
      residualAcidEqT: budget.residualAcidEq,
      ratio: ap > 0 ? np / ap : Infinity,
      exhaustionYears,
      halfLifeYears,
    };
  }

  /* Cumulative acid generated and acid passed to drainage after t years. */
  function history(result, years) {
    const generated = result.acidPotentialEqT * (1 - Math.exp(-result.ratePerYear * years));
    return {
      generated,
      neutralised: Math.min(generated, result.neutralisationEqT),
      drained: Math.max(0, generated - result.neutralisationEqT),
    };
  }

  /* Axis top with four round tick steps. */
  function niceMax(value) {
    const raw = value / 4;
    const magnitude = Math.pow(10, Math.floor(Math.log10(raw)));
    const step = [1, 2, 2.5, 5, 10].map(m => m * magnitude).find(m => m >= raw);
    return 4 * step;
  }

  function fmt(value, digits) {
    return value.toLocaleString("en-GB", { maximumFractionDigits: digits, minimumFractionDigits: digits });
  }

  function mount(core = root.EnvChemDemoCore) {
    if (!core) return;
    return core.mount("acidbase", {
      controls: [
        { key: "pyritePct", label: "Pyrite in the waste", min: 0, max: 5, step: 0.1,
          value: defaults.pyritePct, unit: "% by mass", format: v => v.toFixed(1) },
        { key: "calciteKgT", label: "Calcite in the waste", min: 0, max: 60, step: 0.5,
          value: defaults.calciteKgT, unit: "kg CaCO₃ per tonne", format: v => v.toFixed(1) },
        { key: "eqPerCaCO3", label: "Neutralisation endpoint", min: 1, max: 2, step: 1,
          value: defaults.eqPerCaCO3, unit: "",
          format: v => v === 2 ? "CO₂*: 2 eq per CaCO₃" : "near-neutral: 1 eq per CaCO₃" },
        { key: "accessiblePct", label: "Calcite reachable by acid", min: 0, max: 100, step: 5,
          value: defaults.accessiblePct, unit: "%", format: v => v.toFixed(0) },
        { key: "ratePerYear", label: "Pyrite oxidation rate", min: 0.005, max: 0.1, step: 0.005,
          value: defaults.ratePerYear, unit: "per year", format: v => v.toFixed(3) },
      ],
      presets: [
        { label: "Worked example", values: { ...defaults } },
        { label: "Near-neutral endpoint", values: { ...defaults, eqPerCaCO3: 1 } },
        { label: "Half the calcite coated", values: { ...defaults, accessiblePct: 50 } },
        { label: "Calcite-rich heap", values: { ...defaults, calciteKgT: 40 } },
      ],
      update(values, view) {
        const result = model(values);
        const series = { generated: [], capacity: [], drained: [] };
        for (let i = 0; i <= 160; i += 1) {
          const t = YEARS_SHOWN * i / 160;
          const h = history(result, t);
          series.generated.push({ x: t, y: h.generated });
          series.capacity.push({ x: t, y: result.neutralisationEqT });
          series.drained.push({ x: t, y: h.drained });
        }
        const top = Math.max(result.acidPotentialEqT, result.neutralisationEqT, 10);
        const markers = Number.isFinite(result.exhaustionYears) && result.acidPotentialEqT > 0
          ? [{ x: result.exhaustionYears, label: "Calcite used up: " + fmt(result.exhaustionYears, 0) + " years" }]
          : [];
        core.lineChart(view.chart, {
          title: "Acid made by pyrite and calcite able to neutralise it, per tonne of waste",
          xLabel: "Years since the waste was exposed",
          yLabel: "H⁺ eq per tonne",
          xMin: 0, xMax: YEARS_SHOWN, yMin: 0, yMax: niceMax(top * 1.1),
          series: [
            { label: "Acid generated so far", color: "#a84b20", points: series.generated },
            { label: "Reachable neutralising capacity", color: "#2468a0", points: series.capacity },
            { label: "Acid passed on to the drainage", color: "#1b2a3a", points: series.drained },
          ],
          markers,
        });

        const metricsBox = document.createElement("div");
        const tableBox = document.createElement("div");
        view.results.replaceChildren(metricsBox, tableBox);
        core.metrics(metricsBox, [
          { label: "Acid potential", value: fmt(result.acidPotentialEqT, 0), unit: "eq/t" },
          { label: "Reachable neutralisation", value: fmt(result.neutralisationEqT, 0), unit: "eq/t" },
          { label: "Drainage stays neutral for",
            value: result.acidPotentialEqT === 0 ? "No acid made"
              : Number.isFinite(result.exhaustionYears) ? "about " + fmt(result.exhaustionYears, 0)
              : "Calcite never runs out",
            unit: result.acidPotentialEqT > 0 && Number.isFinite(result.exhaustionYears) ? "years" : "" },
        ]);
        core.table(tableBox, {
          caption: "Budget per tonne of waste if all pyrite eventually reacts",
          headers: ["Quantity", "Value", "Unit"],
          rows: [
            ["FeS₂ in the waste", fmt(result.feS2Mol, 1), "mol/t"],
            ["Acid potential (4 per FeS₂)", fmt(result.acidPotentialEqT, 0), "eq H⁺/t"],
            ["Sulfate released (2 per FeS₂)", fmt(result.sulfateMolT, 0), "mol/t"],
            ["CaCO₃ needed at this endpoint", fmt(result.caco3NeededKgT, 1), "kg/t"],
            ["CaCO₃ present / reachable", fmt(result.calciteKgT, 1) + " / " +
              fmt(result.calciteKgT * result.accessiblePct / 100, 1), "kg/t"],
            ["Acid left over after all calcite is used", fmt(result.residualAcidEqT, 0), "eq H⁺/t"],
          ],
        });

        let text;
        if (result.acidPotentialEqT === 0) {
          text = "Without pyrite there is no acid source in this model, whatever the calcite content.";
        } else if (!Number.isFinite(result.exhaustionYears)) {
          text = "Reachable calcite (" + fmt(result.neutralisationEqT, 0) + " eq/t) is at least the acid potential (" +
            fmt(result.acidPotentialEqT, 0) + " eq/t), so the drainage stays neutral even after all pyrite has reacted. " +
            "This holds only while the calcite stays reachable and the endpoint is as stated: try the near-neutral " +
            "endpoint or a lower reachable share.";
        } else {
          text = "For about " + fmt(result.exhaustionYears, 0) + " years the calcite neutralises the acid as fast as it forms, " +
            "so the drainage looks harmless. Then the calcite is gone and " + fmt(result.residualAcidEqT, 0) +
            " eq/t of acid still has to come out. The same pH today, different futures.";
          if (result.eqPerCaCO3 === 1 || result.accessiblePct < 100) {
            text += " The calcite inventory is unchanged; a near-neutral endpoint or coated calcite " +
              "simply lets each tonne neutralise less acid.";
          }
        }
        text += " A faster oxidation rate shortens the neutral period but does not change the totals.";
        view.explanation.textContent = text;
      },
    });
  }

  return { defaults, acidBudget, model, history, mount };
});

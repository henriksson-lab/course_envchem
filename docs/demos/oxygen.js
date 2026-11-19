/* Sealed-bottle oxygen demand teaching model (CH2O + O2 -> CO2 + H2O). No network or dependencies. */
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
  const M_C = 12.0;
  const M_O2 = 32.0;
  const RATIO = M_O2 / M_C; // g O2 per g C for CH2O-like substrate

  const defaults = Object.freeze({ carbonMgL: 4.0, oxygenMgL: 9.0, ratePerDay: 0.1, days: 5 });

  function model(values = {}) {
    const input = { ...defaults, ...values };
    for (const key of Object.keys(defaults)) {
      if (!Number.isFinite(input[key]) || input[key] < 0) {
        throw new RangeError(key + " must be a finite nonnegative number");
      }
    }
    // Ultimate (complete-oxidation) demand of the carbon pool.
    const ultimateMgL = input.carbonMgL * RATIO;
    // Aerobic demand exerted so far, first-order in the remaining degradable carbon.
    const exerted = function (t) { return ultimateMgL * (1 - Math.exp(-input.ratePerDay * t)); };
    // Time at which the exerted demand would use up all the oxygen (Infinity if never).
    const anoxicDay = ultimateMgL > input.oxygenMgL && input.ratePerDay > 0
      ? -Math.log(1 - input.oxygenMgL / ultimateMgL) / input.ratePerDay
      : Infinity;
    function at(t) {
      const consumed = Math.min(exerted(t), input.oxygenMgL);
      return { consumedMgL: consumed, oxygenLeftMgL: input.oxygenMgL - consumed };
    }
    const now = at(input.days);
    return {
      ...input,
      ratio: RATIO,
      ultimateMgL,
      leftAfterCompleteMgL: input.oxygenMgL - ultimateMgL,
      consumedMgL: now.consumedMgL,
      oxygenLeftMgL: now.oxygenLeftMgL,
      fractionOxidised: input.carbonMgL > 0 ? now.consumedMgL / ultimateMgL : 0,
      anoxicDay,
      at,
    };
  }

  function mount(core) {
    if (!core) return;
    core.mount("oxygen", {
      controls: [
        { key: "carbonMgL", label: "Degradable organic carbon", min: 0, max: 6, step: 0.1,
          value: defaults.carbonMgL, unit: "mg C/L", format: function (v) { return v.toFixed(2); } },
        { key: "oxygenMgL", label: "Starting oxygen", min: 0, max: 14, step: 0.1,
          value: defaults.oxygenMgL, unit: "mg O₂/L", format: function (v) { return v.toFixed(2); } },
        { key: "ratePerDay", label: "Degradation rate", min: 0.01, max: 0.5, step: 0.01,
          value: defaults.ratePerDay, unit: "per day", format: function (v) { return v.toFixed(2); } },
        { key: "days", label: "Day of the measurement", min: 0, max: 40, step: 1,
          value: defaults.days, unit: "days", format: function (v) { return v.toFixed(0); } }
      ],
      presets: [
        { label: "Exercise 3: 5-day test", values: { carbonMgL: 4, oxygenMgL: 9, ratePerDay: 0.1, days: 5 } },
        { label: "Exercise 2: sealed litre", values: { carbonMgL: 2, oxygenMgL: 9, ratePerDay: 0.1, days: 40 } },
        { label: "Slow humic carbon", values: { carbonMgL: 4, oxygenMgL: 9, ratePerDay: 0.02, days: 5 } },
        { label: "Worked example: 3.00 mg C/L", values: { carbonMgL: 3, oxygenMgL: 9, ratePerDay: 0.1, days: 40 } }
      ],
      update: function (values, view) {
        const r = model(values);
        const left = [], used = [];
        for (let i = 0; i <= 160; i += 1) {
          const t = i / 4;
          const s = r.at(t);
          left.push({ x: t, y: s.oxygenLeftMgL });
          used.push({ x: t, y: s.consumedMgL });
        }
        const markers = [{ x: r.days, label: "Day " + r.days.toFixed(0) }];
        if (Number.isFinite(r.anoxicDay) && r.anoxicDay <= 40) {
          markers.push({ x: r.anoxicDay, label: "O₂ gone, day " + r.anoxicDay.toFixed(1) });
        }
        core.lineChart(view.chart, {
          title: "Oxygen in a sealed bottle while organic carbon is oxidised",
          xLabel: "Time (days)",
          yLabel: "mg O₂ per litre",
          xMin: 0, xMax: 40, yMin: 0, yMax: 16,
          series: [
            { label: "O₂ left in the bottle", color: "#2468a0", points: left },
            { label: "O₂ used so far", color: "#a84b20", points: used },
            { label: "Ultimate demand (all carbon oxidised)", color: "#25713e",
              points: [{ x: 0, y: r.ultimateMgL }, { x: 40, y: r.ultimateMgL }] }
          ],
          markers: markers
        });
        core.metrics(view.results, [
          { label: "Ultimate demand", value: r.ultimateMgL.toFixed(2), unit: "mg O₂/L" },
          { label: "O₂ used by day " + r.days.toFixed(0), value: r.consumedMgL.toFixed(2), unit: "mg O₂/L" },
          { label: "Share of the demand used", value: (100 * r.fractionOxidised).toFixed(0), unit: "%" },
          { label: "O₂ left on day " + r.days.toFixed(0), value: r.oxygenLeftMgL.toFixed(2), unit: "mg/L" }
        ]);
        let text = "Each gram of carbon needs 32/12 = 2.67 g of O₂, so " + r.carbonMgL.toFixed(2) +
          " mg C/L has an ultimate demand of " + r.ultimateMgL.toFixed(2) + " mg O₂/L. ";
        if (r.leftAfterCompleteMgL >= 0) {
          text += "Even complete oxidation would leave " + r.leftAfterCompleteMgL.toFixed(2) + " mg/L of oxygen. ";
        } else if (Number.isFinite(r.anoxicDay)) {
          text += "That is more than the " + r.oxygenMgL.toFixed(2) + " mg/L available: the oxygen runs out on day " +
            r.anoxicDay.toFixed(1) + ", and microbes then turn to nitrate, iron and manganese oxides, and sulfate. ";
        } else {
          text += "That is more than the oxygen available, but with no degradation nothing is used. ";
        }
        const share = (100 * r.fractionOxidised).toFixed(0) + "% of the ultimate demand";
        if (r.carbonMgL === 0) text += "With no degradable carbon, no oxygen is used. ";
        else if (r.fractionOxidised < 0.9) text += "By day " + r.days.toFixed(0) + " only " + share +
          " has been used: a short test sees the early, fast part of the curve, not the total. ";
        else text += "By day " + r.days.toFixed(0) + ", " + share + " has been used. ";
        text += "Sealed bottle: no air, no photosynthesis, no other oxygen users.";
        view.explanation.textContent = text;
      }
    });
  }

  return { RATIO, defaults, model, mount };
});

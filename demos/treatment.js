/* Sequential treatment-stage mass balance (transfer to sludge). No dependencies or network. */
(function (root, factory) {
  const api = factory(root);
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.EnvChemTreatmentDemo = api;
  if (typeof document !== "undefined") {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", () => api.mount());
    } else api.mount();
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function (root) {
  "use strict";

  // Constructed phosphorus plant from the lecture: 30 %, 40 %, 90 % of what enters each stage.
  const defaults = Object.freeze({
    massMg: 100,
    stage1Pct: 30,
    stage2Pct: 40,
    stage3Pct: 90,
  });

  function model(values = {}) {
    const input = { ...defaults, ...values };
    for (const key of Object.keys(defaults)) {
      if (!Number.isFinite(input[key]) || input[key] < 0) {
        throw new RangeError(`${key} must be a finite nonnegative number`);
      }
    }
    for (const key of ["stage1Pct", "stage2Pct", "stage3Pct"]) {
      if (input[key] > 100) throw new RangeError(`${key} cannot exceed 100 %`);
    }
    const fractions = [input.stage1Pct, input.stage2Pct, input.stage3Pct].map(p => p / 100);
    // Each stage transfers its fraction of the mass that ENTERS it, not of the original mass.
    let water = input.massMg;
    const toSludgeMg = fractions.map(f => {
      const moved = water * f;
      water -= moved;
      return moved;
    });
    const effluentMg = water;
    const remainingFraction = fractions.reduce((product, f) => product * (1 - f), 1);
    const sludgeMg = toSludgeMg.reduce((sum, m) => sum + m, 0);
    return {
      ...input,
      toSludgeMg,
      sludgeMg,
      effluentMg,
      remainingFraction,
      overallRemovalPct: 100 * (1 - remainingFraction),
      addedPercentages: input.stage1Pct + input.stage2Pct + input.stage3Pct,
      balanceMg: sludgeMg + effluentMg,
    };
  }

  function pct(value) {
    return value.toLocaleString("en-GB", { maximumFractionDigits: 1 });
  }

  function mount(core = root.EnvChemDemoCore) {
    if (!core) return;
    const stageFormat = v => v.toFixed(0);
    return core.mount("treatment", {
      controls: [
        { key: "massMg", label: "Mass entering the plant", min: 1, max: 200, step: 1,
          value: defaults.massMg, unit: "mg", format: v => v.toFixed(0) },
        { key: "stage1Pct", label: "Stage 1: settling", min: 0, max: 100, step: 1,
          value: defaults.stage1Pct, unit: "% of what enters", format: stageFormat },
        { key: "stage2Pct", label: "Stage 2: biological uptake", min: 0, max: 100, step: 1,
          value: defaults.stage2Pct, unit: "% of what enters", format: stageFormat },
        { key: "stage3Pct", label: "Stage 3: iron precipitation", min: 0, max: 100, step: 1,
          value: defaults.stage3Pct, unit: "% of what enters", format: stageFormat },
      ],
      presets: [
        { label: "Phosphorus plant", values: { ...defaults } },
        { label: "Worked example: 60 % then 50 %",
          values: { massMg: 10, stage1Pct: 60, stage2Pct: 50, stage3Pct: 0 } },
        { label: "Exercise 1: two stages of 30 %",
          values: { massMg: 100, stage1Pct: 30, stage2Pct: 30, stage3Pct: 0 } },
        { label: "Three stages of 50 %",
          values: { massMg: 100, stage1Pct: 50, stage2Pct: 50, stage3Pct: 50 } },
      ],
      update(values, view) {
        const r = model(values);
        core.barChart(view.chart, {
          title: "Where the element ends up (nothing is destroyed)",
          unit: "mg",
          max: r.massMg,
          bars: [
            { label: "Sludge from stage 1", value: r.toSludgeMg[0], color: "#a84b20" },
            { label: "Sludge from stage 2", value: r.toSludgeMg[1], color: "#a84b20" },
            { label: "Sludge from stage 3", value: r.toSludgeMg[2], color: "#a84b20" },
            { label: "Left in the water (effluent)", value: r.effluentMg, color: "#2468a0" },
          ],
        });
        core.metrics(view.results, [
          { label: "Left in the effluent", value: pct(100 * r.remainingFraction), unit: "%" },
          { label: "Overall transferred to sludge", value: pct(r.overallRemovalPct), unit: "%" },
          { label: "Stage percentages added (wrong method)", value: pct(r.addedPercentages), unit: "%" },
        ]);
        const balance = "Check: sludge " + core.number(r.sludgeMg) + " mg + effluent " +
          core.number(r.effluentMg) + " mg = " + core.number(r.balanceMg) + " mg, the amount that entered.";
        let text;
        if (r.remainingFraction === 1) {
          text = "No stage transfers anything, so all of the element stays in the water.";
        } else if (r.remainingFraction === 0) {
          text = "One stage is set to 100 %, so nothing reaches the effluent. Every milligram is now in sludge and still has to be managed.";
        } else {
          text = "Each stage acts only on what reaches it, so the fractions left are multiplied: " +
            [r.stage1Pct, r.stage2Pct, r.stage3Pct].map(p => (1 - p / 100).toFixed(2)).join(" × ") +
            " = " + r.remainingFraction.toFixed(3) + ".";
          if (r.addedPercentages > 100) {
            text += " Adding the stage percentages gives " + pct(r.addedPercentages) +
              " %, which is impossible: you cannot remove more than all of it.";
          } else if (r.addedPercentages > r.overallRemovalPct + 0.05) {
            text += " Adding the percentages would overstate the removal.";
          }
        }
        view.explanation.textContent = text + " " + balance +
          " Removal from the water is a transfer: the element moves into sludge, it is not destroyed.";
      },
    });
  }

  return { defaults, model, mount };
});

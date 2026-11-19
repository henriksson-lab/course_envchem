/* Closed-bottle linear sorption (Kd) teaching model. No dependencies or network. */
(function (root, factory) {
  "use strict";
  const api = factory(root);
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.EnvChemSorptionDemo = api;
  if (typeof document !== "undefined") {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", () => api.mount(), { once: true });
    } else api.mount();
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function (root) {
  "use strict";

  // Worked example from the lecture: 1.00 mg, 1.00 L, 0.0100 kg, Kd = 100 L/kg.
  const defaults = Object.freeze({
    totalMg: 1,
    waterL: 1,
    solidKg: 0.01,
    kdLkg: 100,
  });

  function model(values = {}) {
    const input = { ...defaults, ...values };
    for (const key of Object.keys(defaults)) {
      if (!Number.isFinite(input[key]) || input[key] < 0) {
        throw new RangeError(`${key} must be a finite nonnegative number`);
      }
    }
    if (input.waterL === 0) throw new RangeError("Water volume must be positive");
    // Kd x ms has units of litres: the solid acts like an extra volume.
    const extraVolumeL = input.kdLkg * input.solidKg;
    const cwMgL = input.totalMg / (input.waterL + extraVolumeL);
    const waterMg = cwMgL * input.waterL;
    const solidMg = cwMgL * extraVolumeL;
    const qMgKg = input.kdLkg * cwMgL;
    const sorbedFraction = extraVolumeL / (input.waterL + extraVolumeL);
    return { ...input, extraVolumeL, cwMgL, waterMg, solidMg, qMgKg, sorbedFraction };
  }

  function curve(values, kdLkg, maxSolidKg) {
    const points = [];
    for (let i = 0; i <= 100; i += 1) {
      const solidKg = maxSolidKg * i / 100;
      points.push({ x: solidKg, y: model({ ...values, kdLkg, solidKg }).cwMgL });
    }
    return points;
  }

  function fmt(value, digits) {
    return Number(value).toFixed(digits);
  }

  function mount(core = root.EnvChemDemoCore) {
    if (!core) return;
    return core.mount("sorption", {
      controls: [
        { key: "kdLkg", label: "Distribution coefficient Kd", min: 1, max: 300, step: 1,
          value: defaults.kdLkg, unit: "L/kg" },
        { key: "solidKg", label: "Dry solid in the bottle", min: 0, max: 0.05, step: 0.001,
          value: defaults.solidKg, unit: "kg", format: v => fmt(v, 3) },
        { key: "totalMg", label: "Total solute added", min: 0.1, max: 3, step: 0.05,
          value: defaults.totalMg, unit: "mg", format: v => fmt(v, 2) },
        { key: "waterL", label: "Water volume", min: 0.25, max: 2, step: 0.05,
          value: defaults.waterL, unit: "L", format: v => fmt(v, 2) },
      ],
      presets: [
        { label: "Worked example", values: { ...defaults } },
        { label: "Double the solid", values: { ...defaults, solidKg: 0.02 } },
        { label: "pH change: Kd falls to 10", values: { ...defaults, kdLkg: 10 } },
        { label: "Check yourself 1", values: { totalMg: 2, waterL: 1, solidKg: 0.05, kdLkg: 20 } },
      ],
      update(values, view) {
        const r = model(values);
        const maxSolid = 0.05;
        const lowerKd = Math.max(r.kdLkg / 10, 0.1);
        core.lineChart(view.chart, {
          title: "Water concentration as solid is added to the same bottle",
          xLabel: "Dry solid in the bottle (kg)",
          yLabel: "Cw (mg/L)",
          xMin: 0, xMax: maxSolid, yMin: 0,
          yMax: r.totalMg / r.waterL,
          series: [
            { label: "Kd = " + core.number(r.kdLkg) + " L/kg (current)", color: "#2468a0",
              points: curve(values, r.kdLkg, maxSolid) },
            { label: "Kd ten times smaller (" + core.number(lowerKd) + " L/kg)", color: "#a84b20",
              points: curve(values, lowerKd, maxSolid) },
          ],
          markers: [{ x: r.solidKg, label: "Now: Cw = " + fmt(r.cwMgL, 3) + " mg/L" }],
        });
        const metrics = document.createElement("div");
        const table = document.createElement("div");
        view.results.replaceChildren(metrics, table);
        core.metrics(metrics, [
          { label: "Water concentration Cw", value: fmt(r.cwMgL, 3), unit: "mg/L" },
          { label: "Mass on the solid", value: fmt(r.solidMg, 3), unit: "mg" },
          { label: "Sorbed fraction", value: fmt(100 * r.sorbedFraction, 1), unit: "%" },
        ]);
        core.table(table, {
          caption: "Where the solute is at equilibrium",
          headers: ["Quantity", "Value", "Unit"],
          rows: [
            ["Extra volume Kd × ms", fmt(r.extraVolumeL, 3), "L"],
            ["Denominator Vw + Kd × ms", fmt(r.waterL + r.extraVolumeL, 3), "L"],
            ["Mass in water, Cw × Vw", fmt(r.waterMg, 4), "mg"],
            ["Mass on solid, q × ms", fmt(r.solidMg, 4), "mg"],
            ["Total (unchanged)", fmt(r.waterMg + r.solidMg, 4), "mg"],
            ["Sorbed concentration q", fmt(r.qMgKg, 2), "mg/kg"],
          ],
        });
        let text;
        if (r.solidKg === 0) {
          text = "With no solid, all the solute stays in the water: Cw = total mass ÷ water volume.";
        } else if (Math.abs(r.sorbedFraction - 0.5) < 0.005) {
          text = "Kd × ms equals the water volume, so the solid holds as much as the water: half is sorbed.";
        } else if (r.sorbedFraction > 0.5) {
          text = "Kd × ms is larger than the water volume, so most of the solute sits on the solid.";
        } else {
          text = "Kd × ms is smaller than the water volume, so most of the solute stays in the water.";
        }
        view.explanation.textContent = text + " Lowering Kd, for example after a pH change, " +
          "moves solute back into the water without adding any. Doubling the solid does not halve Cw, " +
          "because the water volume stays in the denominator. The model is linear and has no " +
          "capacity limit: a real solid holds at most qmax × ms.";
      },
    });
  }

  return { defaults, model, mount };
});

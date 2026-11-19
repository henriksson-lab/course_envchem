/* Well-mixed lake box model: inflow, outflow, first-order reaction. No dependencies. */
(function (root, factory) {
  "use strict";
  const api = factory(root);
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.EnvChemBoxModelDemo = api;
  if (typeof document !== "undefined") {
    const start = function () { api.mount(root.EnvChemDemoCore); };
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start, { once: true });
    else start();
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  // Lecture lake: V = 1.0e6 m3, Q = 1.0e4 m3/day, I = 1.0 kg/day, conservative, starts clean.
  const defaults = Object.freeze({
    volumeMillionM3: 1,
    flowThousandM3Day: 10,
    inputKgDay: 1,
    kPerDay: 0,
    startKg: 0,
  });

  function model(values = {}) {
    const input = { ...defaults, ...values };
    for (const key of Object.keys(defaults)) {
      if (!Number.isFinite(input[key]) || input[key] < 0) {
        throw new RangeError(`${key} must be a finite nonnegative number`);
      }
    }
    if (input.volumeMillionM3 === 0) throw new RangeError("Lake volume must be positive");
    if (input.flowThousandM3Day === 0 && input.kPerDay === 0) {
      throw new RangeError("A loss is needed: outflow or reaction must be positive");
    }
    const volumeM3 = input.volumeMillionM3 * 1e6;
    const flowM3Day = input.flowThousandM3Day * 1e3;
    const flushPerDay = flowM3Day / volumeM3;           // 1/tau
    const replacementDays = flowM3Day > 0 ? volumeM3 / flowM3Day : Infinity;
    const lossPerDay = flushPerDay + input.kPerDay;     // the two loss rates add
    const timeConstantDays = 1 / lossPerDay;
    const steadyKg = input.inputKgDay / lossPerDay;
    // 1 kg in 1e6 m3 (1e9 L) is 1e-3 mg/L
    const toMgL = kg => kg * 1e6 / (volumeM3 * 1000);
    const inventoryAt = t => steadyKg + (input.startKg - steadyKg) * Math.exp(-lossPerDay * t);
    const budgetAt = t => {
      const inventoryKg = inventoryAt(t);
      const outflowKgDay = flushPerDay * inventoryKg;   // Q x C
      const reactionKgDay = input.kPerDay * inventoryKg;
      return {
        t, inventoryKg, concentrationMgL: toMgL(inventoryKg),
        inputKgDay: input.inputKgDay, outflowKgDay, reactionKgDay,
        changeKgDay: input.inputKgDay - outflowKgDay - reactionKgDay,
      };
    };
    return {
      ...input,
      volumeM3, flowM3Day, flushPerDay, replacementDays, lossPerDay, timeConstantDays,
      steadyKg, steadyMgL: toMgL(steadyKg),
      inventoryAt, budgetAt,
      start: budgetAt(0),
      oneTimeConstant: budgetAt(timeConstantDays),
      steady: budgetAt(Infinity),
    };
  }

  function mount(core) {
    if (!core) return;
    return core.mount("boxmodel", {
      controls: [
        { key: "volumeMillionM3", label: "Lake volume V", min: 0.2, max: 5, step: 0.1,
          value: defaults.volumeMillionM3, unit: "million m³" },
        { key: "flowThousandM3Day", label: "Water flow Q (in = out)", min: 0, max: 50, step: 1,
          value: defaults.flowThousandM3Day, unit: "thousand m³/day" },
        { key: "inputKgDay", label: "Solute input I", min: 0, max: 5, step: 0.1,
          value: defaults.inputKgDay, unit: "kg/day", format: v => v.toFixed(1) },
        { key: "kPerDay", label: "Reaction rate constant k", min: 0, max: 0.05, step: 0.001,
          value: defaults.kPerDay, unit: "per day", format: v => v.toFixed(3) },
        { key: "startKg", label: "Solute in the lake at day 0", min: 0, max: 300, step: 10,
          value: defaults.startKg, unit: "kg" },
      ],
      presets: [
        { label: "Worked example", values: { ...defaults } },
        { label: "Double the input", values: { ...defaults, inputKgDay: 2 } },
        { label: "Flush with clean water", values: { ...defaults, inputKgDay: 0, startKg: 100 } },
        { label: "Flushing plus reaction", values: { ...defaults, inputKgDay: 0, startKg: 100, kPerDay: 0.01 } },
      ],
      update(values, view) {
        const r = model(values);
        const span = [500, 1000, 2000, 4000, 6000].find(v => v >= 5 * r.timeConstantDays) || 10 * r.timeConstantDays;
        const points = [], level = [];
        for (let i = 0; i <= 200; i += 1) {
          const t = span * i / 200;
          points.push({ x: t, y: r.inventoryAt(t) });
          level.push({ x: t, y: r.steadyKg });
        }
        // Round the axis top so the four grid steps are tidy numbers (e.g. 30 kg, not 27.5 kg).
        const rawStep = Math.max(10, r.steadyKg, r.startKg) * 1.1 / 4;
        const scale = Math.pow(10, Math.floor(Math.log10(rawStep)));
        const step = [1, 2, 2.5, 3, 5, 10].map(m => m * scale).find(v => v >= rawStep);
        const yMax = 4 * step;
        core.lineChart(view.chart, {
          title: "Solute in the lake over time",
          xLabel: "Time (days)",
          yLabel: "Solute in lake, M (kg)",
          xMin: 0, xMax: span, yMin: 0, yMax,
          series: [
            { label: "Solute in the lake", color: "#2468a0", points },
            { label: "Steady-state level (input = losses)", color: "#a84b20", points: level },
          ],
          markers: [{ x: r.timeConstantDays, label: "One time constant: " +
            core.number(Number(r.timeConstantDays.toPrecision(3))) + " days" }],
        });
        const metrics = document.createElement("div");
        const table = document.createElement("div");
        view.results.replaceChildren(metrics, table);
        core.metrics(metrics, [
          { label: "Replacement time V/Q", value: Number.isFinite(r.replacementDays)
            ? Number(r.replacementDays.toPrecision(3)) : "No outflow", unit: Number.isFinite(r.replacementDays) ? "days" : "" },
          { label: "Time constant 1/(Q/V + k)", value: Number(r.timeConstantDays.toPrecision(3)), unit: "days" },
          { label: "Steady-state inventory", value: Number(r.steadyKg.toPrecision(3)), unit: "kg" },
          { label: "Steady-state concentration", value: Number(r.steadyMgL.toPrecision(3)), unit: "mg/L" },
        ]);
        const f = v => Number(v.toPrecision(3));
        const cols = [r.start, r.oneTimeConstant, r.steady];
        core.table(table, {
          caption: "Balance for the lake (kg/day); change = input − outflow − reaction",
          headers: ["Term", "Day 0", "After one time constant", "Steady state"],
          rows: [
            ["Solute in lake (kg)", ...cols.map(c => f(c.inventoryKg))],
            ["Input I", ...cols.map(c => f(c.inputKgDay))],
            ["Outflow Q × C", ...cols.map(c => f(c.outflowKgDay))],
            ["Reaction k × M", ...cols.map(c => f(c.reactionKgDay))],
            ["Change in inventory", ...cols.map(c => f(c.changeKgDay))],
          ],
        });
        let text;
        if (r.inputKgDay === 0 && r.startKg === 0) {
          text = "With no input and a clean lake there is nothing to track: the inventory stays at zero.";
        } else if (r.inputKgDay === 0) {
          text = "No new solute enters, so the inventory only falls. After one time constant about 37% of the " +
            "starting amount is left, not zero, because clean water mixes with the lake water instead of pushing it out. " +
            (r.kPerDay > 0
              ? "Reaction and flushing act together: their loss rates add, so the solute falls faster than by flushing alone."
              : "Here flushing is the only loss, so the time constant equals the replacement time V/Q.");
        } else {
          text = "The inventory moves towards the level where losses equal the input. At steady state the amount " +
            "stops changing, but input and outflow" + (r.kPerDay > 0 ? " and reaction" : "") + " keep running. " +
            "The steady level is proportional to the input: double I and it doubles. " +
            (r.kPerDay > 0
              ? "Reaction is an extra loss, so the steady level is lower and is reached sooner."
              : "With no reaction the steady concentration is I/Q, whatever the volume; a larger volume only makes the approach slower.");
        }
        view.explanation.textContent = text + " The model assumes a well-mixed lake of constant volume, constant flow " +
          "and input, and a first-order reaction.";
      },
    });
  }

  return { defaults, model, mount };
});

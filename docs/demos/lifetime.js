/* OH-controlled lifetime teaching model. No dependencies, network requests, or fits. */
(function (root, factory) {
  "use strict";
  const api = factory(root);
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.EnvChemLifetimeDemo = api;
  if (typeof document !== "undefined") {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", () => api.mount(), { once: true });
    } else api.mount();
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function (root) {
  "use strict";

  const SECONDS_PER_DAY = 86400;
  const DAYS_PER_YEAR = 365.25;

  // Worked example from the lecture and exercise 2.
  const defaults = Object.freeze({
    logK: -12,          // log10 of k in cm3 molecule-1 s-1
    ohMillion: 1,       // OH in units of 1e6 molecules/cm3, held constant
    otherPerDay: 0,     // optional extra first-order loss (e.g. deposition), per day
  });

  // Approximate transport times, as on the "Lifetime decides how far a gas travels" slide.
  function spread(lifetimeDays) {
    if (lifetimeDays < 1) return { key: "local", text: "stays near its source" };
    if (lifetimeDays < 21) return { key: "regional", text: "is a regional pollutant" };
    if (lifetimeDays < DAYS_PER_YEAR) return { key: "hemisphere", text: "spreads around its hemisphere" };
    return { key: "global", text: "mixes over the whole globe" };
  }

  function model(values = {}) {
    const input = { ...defaults, ...values };
    for (const key of Object.keys(defaults)) {
      if (!Number.isFinite(input[key])) throw new RangeError(`${key} must be a finite number`);
    }
    if (input.ohMillion < 0) throw new RangeError("OH concentration cannot be negative");
    if (input.otherPerDay < 0) throw new RangeError("The other loss cannot be negative");
    const k = Math.pow(10, input.logK);
    const oh = input.ohMillion * 1e6;
    const kOH = k * oh;                                   // s-1
    const kOther = input.otherPerDay / SECONDS_PER_DAY;   // s-1
    const kTotal = kOH + kOther;
    if (!(kTotal > 0)) throw new RangeError("With no loss at all, the lifetime is infinite");
    const lifetimeS = 1 / kTotal;
    const lifetimeDays = lifetimeS / SECONDS_PER_DAY;
    const halfLifeDays = Math.LN2 * lifetimeDays;
    return {
      ...input,
      k, oh, kOH, kOther, kTotal,
      lifetimeS, lifetimeDays, halfLifeDays,
      ohShare: kOH / kTotal,
      spread: spread(lifetimeDays),
    };
  }

  function remaining(result, days) {
    return Math.exp(-days / result.lifetimeDays);
  }

  const superscripts = { "-": "⁻", "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
    "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹" };
  function sci(value, digits = 2) {
    const exponent = Math.floor(Math.log10(Math.abs(value)) + 1e-9);
    let mantissa = value / Math.pow(10, exponent);
    let e = exponent;
    if (Number(mantissa.toFixed(digits - 1)) >= 10) { mantissa /= 10; e += 1; }
    const sup = String(e).split("").map(c => superscripts[c]).join("");
    return mantissa.toFixed(digits - 1) + " × 10" + sup;
  }

  function timeUnit(lifetimeDays) {
    if (lifetimeDays < 2) return { name: "hours", perDay: 24 };
    if (lifetimeDays > 2 * DAYS_PER_YEAR) return { name: "years", perDay: 1 / DAYS_PER_YEAR };
    return { name: "days", perDay: 1 };
  }
  // Round the axis end up so that the four axis intervals have tidy tick labels.
  function niceCeil(value) {
    const power = Math.pow(10, Math.floor(Math.log10(value)));
    for (const m of [1, 2, 4, 5, 6, 8, 10]) if (m * power >= value * (1 - 1e-12)) return m * power;
    return 10 * power;
  }
  function fmt(value) {
    return value >= 100 ? value.toFixed(0) : value >= 10 ? value.toFixed(1) : value.toPrecision(2);
  }

  function mount(core = root.EnvChemDemoCore) {
    if (!core) return;
    const reference = model();
    return core.mount("lifetime", {
      controls: [
        { key: "logK", label: "Rate constant k for X + OH", min: -15, max: -10, step: 0.1,
          value: defaults.logK, unit: "cm³ molecule⁻¹ s⁻¹", format: v => sci(Math.pow(10, v)) },
        { key: "ohMillion", label: "OH concentration (held constant)", min: 0.1, max: 5, step: 0.1,
          value: defaults.ohMillion, unit: "× 10⁶ molecules/cm³", format: v => v.toFixed(1) },
        { key: "otherPerDay", label: "Other loss, e.g. deposition", min: 0, max: 0.5, step: 0.01,
          value: defaults.otherPerDay, unit: "per day", format: v => v.toFixed(2) },
      ],
      presets: [
        { label: "Worked example", values: { ...defaults } },
        { label: "Twice as much OH", values: { ...defaults, ohMillion: 2 } },
        { label: "Slow reaction (k 100 times smaller)", values: { ...defaults, logK: -14 } },
        { label: "Add deposition 0.1 per day", values: { ...defaults, otherPerDay: 0.1 } },
      ],
      update(values, view) {
        const result = model(values);
        const unit = timeUnit(result.lifetimeDays);
        const tau = result.lifetimeDays * unit.perDay;
        const half = result.halfLifeDays * unit.perDay;
        const xMax = niceCeil(4 * tau);
        const current = [], ref = [];
        for (let i = 0; i <= 200; i += 1) {
          const t = xMax * i / 200;
          current.push({ x: t, y: remaining(result, t / unit.perDay) });
          ref.push({ x: t, y: remaining(reference, t / unit.perDay) });
        }
        core.lineChart(view.chart, {
          title: `Lifetime ${fmt(tau)} ${unit.name}: X ${result.spread.text}`,
          xLabel: `Time since release (${unit.name})`,
          yLabel: "Fraction of X remaining",
          xMin: 0, xMax, yMin: 0, yMax: 1,
          series: [
            { label: "Current settings", color: "#2468a0", points: current },
            { label: "Worked example (lifetime 11.6 days)", color: "#a84b20", points: ref },
          ],
          markers: [
            { x: half, label: `Half-life ${fmt(half)} ${unit.name}: 0.50 left` },
            { x: tau, label: `Lifetime ${fmt(tau)} ${unit.name}: 0.37 left` },
          ],
        });
        core.metrics(view.results, [
          { label: "Loss rate constant k′", value: sci(result.kTotal), unit: "s⁻¹" },
          { label: "Lifetime τ = 1/k′", value: fmt(tau), unit: unit.name + " (" + sci(result.lifetimeS) + " s)" },
          { label: "Half-life = 0.693 τ", value: fmt(half), unit: unit.name },
        ]);
        const pieces = [
          `k′ = k × [OH] = ${sci(result.k)} × ${sci(result.oh)} = ${sci(result.kOH)} s⁻¹.`,
        ];
        if (result.kOther > 0) {
          pieces.push(`The other loss adds ${sci(result.kOther)} s⁻¹, so OH now removes only ` +
            `${Math.round(100 * result.ohShare)}% of X and the lifetime is shorter than OH alone would give.`);
        }
        pieces.push(`The lifetime 1/k′ is the time for X to fall to 0.37 of its starting amount; ` +
          `half is gone after 0.693 times the lifetime. Doubling OH or k doubles k′ and halves the lifetime.`);
        pieces.push(`Compared with transport times (about 1 day to mix the lowest air layer, ` +
          `a few weeks around a hemisphere, about a year between hemispheres), X ${result.spread.text}.`);
        pieces.push("Model: OH held at a constant average, one air parcel, no new emissions.");
        view.explanation.textContent = pieces.join(" ");
      },
    });
  }

  return { defaults, model, remaining, spread, sci, mount };
});

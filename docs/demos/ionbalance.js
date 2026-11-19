/* Water-analysis charge balance and ionic strength teaching model. No dependencies or network. */
(function (root, factory) {
  "use strict";
  const api = factory(root);
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.EnvChemIonBalanceDemo = api;
  if (typeof document !== "undefined") {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", () => api.mount(), { once: true });
    } else api.mount();
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function (root) {
  "use strict";

  // Worked ion table from the lecture and notes (mmol/L). Ca and SO4 are adjustable
  // table entries; NaCl is extra dissolved salt that adds equal Na+ and Cl-.
  const fixed = Object.freeze({ Mg: 0.25, Na: 0.5, HCO3: 1.2, Cl: 0.4 });
  const defaults = Object.freeze({ caMmolL: 0.5, so4MmolL: 0.2, naclMmolL: 0 });
  const DAVIES_A = 0.509; // 25 degrees C

  function davies(ionicStrengthMolL, z) {
    if (!Number.isFinite(ionicStrengthMolL) || ionicStrengthMolL < 0) {
      throw new RangeError("Ionic strength must be finite and nonnegative");
    }
    const s = Math.sqrt(ionicStrengthMolL);
    return Math.pow(10, -DAVIES_A * z * z * (s / (1 + s) - 0.3 * ionicStrengthMolL));
  }

  function model(values = {}) {
    const input = { ...defaults, ...values };
    for (const key of Object.keys(defaults)) {
      if (!Number.isFinite(input[key]) || input[key] < 0) {
        throw new RangeError(`${key} must be a finite nonnegative number`);
      }
    }
    const ions = [
      { label: "Ca²⁺", z: 2, mmolL: input.caMmolL },
      { label: "Mg²⁺", z: 2, mmolL: fixed.Mg },
      { label: "Na⁺", z: 1, mmolL: fixed.Na + input.naclMmolL },
      { label: "HCO₃⁻", z: -1, mmolL: fixed.HCO3 },
      { label: "Cl⁻", z: -1, mmolL: fixed.Cl + input.naclMmolL },
      { label: "SO₄²⁻", z: -2, mmolL: input.so4MmolL },
    ];
    let cationsMeqL = 0, anionsMeqL = 0, sumCz2 = 0;
    for (const ion of ions) {
      ion.meqL = Math.abs(ion.z) * ion.mmolL;
      if (ion.z > 0) cationsMeqL += ion.meqL; else anionsMeqL += ion.meqL;
      sumCz2 += ion.mmolL * ion.z * ion.z;
    }
    const ionicStrengthMmolL = sumCz2 / 2;
    const ionicStrengthMolL = ionicStrengthMmolL / 1000;
    if (ionicStrengthMolL > 0.5) throw new RangeError("Outside the range of the Davies estimate");
    const gamma1 = davies(ionicStrengthMolL, 1);
    const gamma2 = davies(ionicStrengthMolL, 2);
    for (const ion of ions) {
      ion.gamma = Math.abs(ion.z) === 2 ? gamma2 : gamma1;
      ion.activityMmolL = ion.gamma * ion.mmolL;
    }
    const totalCharge = cationsMeqL + anionsMeqL;
    return {
      ...input,
      ions,
      cationsMeqL,
      anionsMeqL,
      gapMeqL: cationsMeqL - anionsMeqL,
      imbalancePercent: totalCharge > 0 ? 100 * (cationsMeqL - anionsMeqL) / totalCharge : 0,
      ionicStrengthMmolL,
      ionicStrengthMolL,
      gamma1,
      gamma2,
    };
  }

  function signed(value, digits) {
    const text = Math.abs(value).toFixed(digits);
    if (Number(text) === 0) return (0).toFixed(digits);
    return (value > 0 ? "+" : "−") + text;
  }

  function mount(core = root.EnvChemDemoCore) {
    if (!core) return;
    return core.mount("ionbalance", {
      controls: [
        { key: "caMmolL", label: "Ca²⁺ entry in the table", min: 0, max: 1.5, step: 0.01,
          value: defaults.caMmolL, unit: "mmol/L", format: v => v.toFixed(2) },
        { key: "so4MmolL", label: "SO₄²⁻ entry in the table", min: 0, max: 0.6, step: 0.01,
          value: defaults.so4MmolL, unit: "mmol/L", format: v => v.toFixed(2) },
        { key: "naclMmolL", label: "Extra salt NaCl (adds Na⁺ and Cl⁻)", min: 0, max: 200, step: 1,
          value: defaults.naclMmolL, unit: "mmol/L", format: v => v.toFixed(0) },
      ],
      presets: [
        { label: "Worked example", values: { ...defaults } },
        { label: "Sample C: sulfate error", values: { ...defaults, so4MmolL: 0.02 } },
        { label: "Salty river: +20 NaCl", values: { ...defaults, naclMmolL: 20 } },
        { label: "Brackish: +120 NaCl", values: { ...defaults, naclMmolL: 120 } },
      ],
      update(values, view) {
        const r = model(values);
        core.barChart(view.chart, {
          title: "Charge totals from the water table",
          unit: "meq/L",
          bars: [
            { label: "Cation charge", value: Number(r.cationsMeqL.toFixed(3)), color: "#2468a0" },
            { label: "Anion charge", value: Number(r.anionsMeqL.toFixed(3)), color: "#a84b20" },
            { label: "Cations − anions", value: Number(r.gapMeqL.toFixed(3)), color: "#25713e" },
          ],
        });
        const metrics = document.createElement("div");
        const table = document.createElement("div");
        view.results.replaceChildren(metrics, table);
        core.metrics(metrics, [
          { label: "Charge imbalance", value: signed(r.imbalancePercent, 2), unit: "%" },
          { label: "Ionic strength I", value: r.ionicStrengthMmolL.toFixed(r.ionicStrengthMmolL < 10 ? 2 : 1), unit: "mmol/L" },
          { label: "Activity coefficient γ, charge 1 / charge 2",
            value: r.gamma1.toFixed(2) + " / " + r.gamma2.toFixed(2), unit: "" },
        ]);
        core.table(table, {
          caption: "Ion table: amount, charge, and activity (γ × concentration)",
          headers: ["Ion", "mmol/L", "meq/L", "γ", "Activity as mmol/L"],
          rows: r.ions.map(ion => [ion.label, ion.mmolL.toFixed(3), ion.meqL.toFixed(3),
            ion.gamma.toFixed(3), ion.activityMmolL.toFixed(3)]),
        });
        const balance = Math.abs(r.imbalancePercent) < 0.005
          ? "Cation and anion charge are equal, so the table passes the charge-balance check. " +
            "That is a consistency check, not proof that every entry is right."
          : `The table has ${r.cationsMeqL.toFixed(3)} meq/L of cation charge but ` +
            `${r.anionsMeqL.toFixed(3)} meq/L of anion charge (${signed(r.imbalancePercent, 2)}%). ` +
            `The water itself cannot be charged, so ${r.gapMeqL > 0 ? "anion charge is missing or a cation entry is too high"
              : "cation charge is missing or an anion entry is too high"}. ` +
            "Look for an omitted ion or an entry error; do not change numbers until it balances.";
        const activity = r.ionicStrengthMolL < 0.01
          ? ` The ionic strength is ${r.ionicStrengthMmolL.toFixed(2)} mmol/L, typical freshwater: ` +
            `single-charged ions are within about ${Math.round(100 * (1 - r.gamma1))}% of their concentration, ` +
            "so γ ≈ 1 is a fair approximation, but divalent ions are already noticeably lower."
          : ` The ionic strength is ${r.ionicStrengthMmolL.toFixed(1)} mmol/L. A divalent ion now acts as if ` +
            `only ${Math.round(100 * r.gamma2)}% of it were there, so γ ≈ 1 and freshwater constants no longer apply.`;
        view.explanation.textContent = balance + activity +
          " Added NaCl carries equal positive and negative charge, so it changes ionic strength but not the balance." +
          " Activity coefficients are Davies estimates at 25 °C.";
      },
    });
  }

  return { defaults, fixed, davies, model, mount };
});

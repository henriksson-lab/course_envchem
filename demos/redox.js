/* Redox-ladder electron bookkeeping teaching model. No dependencies or network. */
(function (root, factory) {
  "use strict";
  const api = factory(root);
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.EnvChemRedoxDemo = api;
  if (typeof document !== "undefined") {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", () => api.mount(), { once: true });
    } else api.mount();
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function (root) {
  "use strict";

  // Electrons accepted per mole of acceptor (lecture half-reactions).
  // CH2O -> CO2 donates 4 electrons per mol C.
  const ELECTRONS = Object.freeze({ o2: 4, nitrate: 5, iron: 1, sulfate: 8 });
  const DONOR_ELECTRONS = 4;
  // Constructed: phosphate held on the reactive Fe(III) oxide, mol P per mol Fe.
  const P_PER_FE = 0.1;

  // Constructed bottom-water reference case (mmol/L of bottom water).
  const defaults = Object.freeze({
    carbonMmol: 0.5,
    o2Mmol: 0.3,
    nitrateMmol: 0.08,
    ironMmol: 0.2,
    sulfateMmol: 2,
  });

  const ladder = [
    { key: "o2", input: "o2Mmol", label: "O₂", product: "H₂O" },
    { key: "nitrate", input: "nitrateMmol", label: "NO₃⁻", product: "N₂" },
    { key: "iron", input: "ironMmol", label: "Fe(III) oxide", product: "Fe²⁺" },
    { key: "sulfate", input: "sulfateMmol", label: "SO₄²⁻", product: "HS⁻" },
  ];

  function model(values = {}) {
    const input = { ...defaults, ...values };
    for (const key of Object.keys(defaults)) {
      if (!Number.isFinite(input[key]) || input[key] < 0) {
        throw new RangeError(`${key} must be a finite nonnegative number`);
      }
    }
    // Strict sequence: each acceptor is used up before the next one starts.
    let carbonLeft = input.carbonMmol;
    const steps = ladder.map(step => {
      const start = input[step.input];
      const carbonPerAcceptor = ELECTRONS[step.key] / DONOR_ELECTRONS;
      const carbonNeeded = start * carbonPerAcceptor;
      const carbonUsed = Math.min(carbonLeft, carbonNeeded);
      carbonLeft -= carbonUsed;
      const used = carbonPerAcceptor > 0 ? carbonUsed / carbonPerAcceptor : 0;
      return { ...step, start, used, remaining: start - used, carbonUsed,
        electrons: used * ELECTRONS[step.key] };
    });
    // Any organic carbon left after sulfate is fermented: 2 CH2O -> CO2 + CH4.
    const methaneCarbon = carbonLeft;
    const methaneMmol = methaneCarbon / 2;
    const byKey = Object.fromEntries(steps.map(s => [s.key, s]));
    const electronsDonated = DONOR_ELECTRONS * (input.carbonMmol - methaneCarbon) +
      2 * methaneCarbon;
    const electronsAccepted = steps.reduce((sum, s) => sum + s.electrons, 0) + 2 * methaneCarbon;
    let current = "None (no organic matter decomposed)";
    if (input.carbonMmol > 0) {
      const active = steps.filter(s => s.carbonUsed > 0);
      current = methaneCarbon > 0 ? "Methane formation"
        : active.length ? active[active.length - 1].label : "None";
    }
    return {
      ...input,
      steps,
      current,
      n2Mmol: byKey.nitrate.used / 2,
      fe2Mmol: byKey.iron.used,
      phosphateMmol: byKey.iron.used * P_PER_FE,
      sulfideMmol: byKey.sulfate.used,
      methaneMmol,
      methaneCarbon,
      electronsDonated,
      electronsAccepted,
    };
  }

  function mount(core = root.EnvChemDemoCore) {
    if (!core) return;
    const colours = { o2: "#2468a0", nitrate: "#25713e", iron: "#a84b20", sulfate: "#1b2a3a" };
    const f3 = v => v.toFixed(3);
    return core.mount("redox", {
      controls: [
        { key: "carbonMmol", label: "Organic matter decomposed (CH₂O)", min: 0, max: 1, step: 0.005,
          value: defaults.carbonMmol, unit: "mmol C/L", format: f3 },
        { key: "o2Mmol", label: "Starting O₂", min: 0, max: 0.4, step: 0.01,
          value: defaults.o2Mmol, unit: "mmol/L", format: v => v.toFixed(2) },
        { key: "nitrateMmol", label: "Starting nitrate", min: 0, max: 0.2, step: 0.005,
          value: defaults.nitrateMmol, unit: "mmol/L", format: f3 },
        { key: "ironMmol", label: "Reactive Fe(III) oxide", min: 0, max: 0.4, step: 0.01,
          value: defaults.ironMmol, unit: "mmol/L", format: v => v.toFixed(2) },
        { key: "sulfateMmol", label: "Starting sulfate", min: 0, max: 3, step: 0.05,
          value: defaults.sulfateMmol, unit: "mmol/L", format: v => v.toFixed(2) },
      ],
      presets: [
        { label: "Baltic bottom water", values: { ...defaults } },
        { label: "Oxygen still present", values: { ...defaults, carbonMmol: 0.2 } },
        { label: "Denitrification worked example",
          values: { ...defaults, o2Mmol: 0, carbonMmol: 0.1 } },
        { label: "Low-sulfate lake water",
          values: { ...defaults, sulfateMmol: 0.1, carbonMmol: 1 } },
      ],
      update(values, view) {
        const r = model(values);
        const grid = [];
        for (let i = 0; i <= 200; i += 1) grid.push(model({ ...values, carbonMmol: i / 200 }));
        core.lineChart(view.chart, {
          title: "Electron acceptors left as organic matter is decomposed",
          xLabel: "Organic matter decomposed (mmol C/L)",
          yLabel: "Acceptor left (% of start)",
          xMin: 0, xMax: 1, yMin: 0, yMax: 100,
          series: ladder.map((step, index) => ({
            label: step.label, color: colours[step.key],
            points: grid.map(g => ({ x: g.carbonMmol,
              y: g.steps[index].start > 0 ? 100 * g.steps[index].remaining / g.steps[index].start : NaN })),
          })),
          markers: [{ x: r.carbonMmol, label: "Now" }],
        });
        const metrics = document.createElement("div");
        const table = document.createElement("div");
        view.results.replaceChildren(metrics, table);
        core.metrics(metrics, [
          { label: "Acceptor now in use", value: r.current },
          { label: "Fe²⁺ released", value: f3(r.fe2Mmol), unit: "mmol/L" },
          { label: "Phosphate released", value: f3(r.phosphateMmol), unit: "mmol/L" },
        ]);
        core.table(table, {
          caption: "Electron bookkeeping (mmol/L; electrons in mmol e⁻/L)",
          headers: ["Acceptor", "Start", "Used", "Electrons accepted", "Product formed"],
          rows: r.steps.map(s => {
            const product = s.key === "o2" ? "–"
              : s.key === "nitrate" ? f3(r.n2Mmol) + " N₂"
              : s.key === "iron" ? f3(r.fe2Mmol) + " Fe²⁺"
              : f3(r.sulfideMmol) + " HS⁻";
            return [s.label, f3(s.start), f3(s.used), f3(s.electrons), product];
          }).concat([
            ["Methane formation", "–", f3(r.methaneCarbon / 2), f3(2 * r.methaneCarbon),
              f3(r.methaneMmol) + " CH₄"],
            ["Organic carbon (donor)", f3(r.carbonMmol), f3(r.carbonMmol),
              f3(r.electronsDonated) + " given", r.methaneCarbon > 0 ? "CO₂ and CH₄" : "CO₂"],
          ]),
        });
        let text;
        const iron = r.steps[2];
        if (r.carbonMmol === 0) {
          text = "No organic matter has been decomposed yet, so every acceptor is still present.";
        } else if (r.methaneCarbon > 0) {
          text = "All the listed acceptors are used up, so the remaining organic matter is split into CO₂ and methane.";
        } else if (r.steps[3].used > 0) {
          text = "Oxygen, nitrate and the iron oxide are gone. Sulfate is now reduced to sulfide, eight electrons per sulfur, so it lasts a long time.";
        } else if (iron.used > 0) {
          text = "Oxygen and nitrate are gone, so Fe(III) oxide is being reduced. The solid dissolves as Fe²⁺ and the phosphate it held is released. Phosphorus itself stays +V.";
        } else if (r.steps[1].used > 0) {
          text = "Oxygen is gone and nitrate is reduced to N₂: 1.25 mol C per mol nitrate. No phosphate is released yet.";
        } else {
          text = "Oxygen is still being used, so the iron oxide stays solid and keeps its phosphate.";
        }
        view.explanation.textContent = text + " Each acceptor needs a different amount of carbon " +
          "because it takes a different number of electrons: O₂ 4, nitrate 5, Fe(III) 1, sulfate 8, " +
          "against 4 given by each carbon. The model uses the acceptors strictly in order; " +
          "in real sediments the steps overlap.";
      },
    });
  }

  return { defaults, ELECTRONS, P_PER_FE, model, mount };
});

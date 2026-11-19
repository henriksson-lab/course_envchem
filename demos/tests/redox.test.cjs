"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const redox = require("../redox.js");

function close(actual, expected, tolerance = 1e-10) {
  assert.ok(Math.abs(actual - expected) <= tolerance,
    `${actual} differs from expected ${expected}`);
}

test("lecture denitrification: 0.0800 mmol/L nitrate needs 0.100 mmol C/L and gives 0.0400 N2", () => {
  const r = redox.model({ o2Mmol: 0, nitrateMmol: 0.08, carbonMmol: 0.1 });
  const nitrate = r.steps[1];
  close(nitrate.used, 0.08);
  close(nitrate.remaining, 0);
  close(r.n2Mmol, 0.04);
  close(nitrate.carbonUsed * 12.0, 1.2); // 1.20 mg C/L
  close(r.fe2Mmol, 0);
  close(r.phosphateMmol, 0);
});

test("reference case follows the ladder by hand: 0.30 + 0.10 + 0.05 mmol C, then sulfate", () => {
  const r = redox.model();
  // O2: 1 C per O2; nitrate: 5/4 C; Fe(III): 1/4 C; sulfate: 2 C.
  close(r.steps[0].carbonUsed, 0.3);
  close(r.steps[1].carbonUsed, 0.1);
  close(r.steps[2].carbonUsed, 0.05);
  close(r.fe2Mmol, 0.2);
  close(r.phosphateMmol, 0.02);
  close(r.sulfideMmol, 0.025);
  close(r.methaneMmol, 0);
  assert.equal(r.current, "SO₄²⁻");
});

test("strict order: no Fe reduction while O2 or nitrate remain", () => {
  const oxic = redox.model({ carbonMmol: 0.2 });
  close(oxic.steps[0].remaining, 0.1);
  close(oxic.steps[1].used, 0);
  close(oxic.fe2Mmol, 0);
  assert.equal(oxic.current, "O₂");
  const nitrateStep = redox.model({ carbonMmol: 0.35 });
  close(nitrateStep.steps[1].used, 0.04);
  close(nitrateStep.fe2Mmol, 0);
});

test("electrons given equal electrons accepted, and acceptors stay within bounds", () => {
  for (const carbonMmol of [0, 0.05, 0.3, 0.45, 0.7, 1])
    for (const sulfateMmol of [0, 0.1, 2, 3])
      for (const o2Mmol of [0, 0.4]) {
        const r = redox.model({ carbonMmol, sulfateMmol, o2Mmol });
        close(r.electronsDonated, r.electronsAccepted, 1e-12);
        for (const s of r.steps) {
          assert.ok(s.used >= -1e-15 && s.remaining >= -1e-12);
          close(s.used + s.remaining, s.start, 1e-12);
        }
        const carbon = r.steps.reduce((a, s) => a + s.carbonUsed, 0) + r.methaneCarbon;
        close(carbon, carbonMmol, 1e-12);
      }
});

test("methane forms only after sulfate is used up", () => {
  const r = redox.model({ sulfateMmol: 0.1, carbonMmol: 1 });
  close(r.steps[3].remaining, 0);
  close(r.methaneCarbon, 1 - 0.45 - 0.2);
  close(r.methaneMmol, (1 - 0.65) / 2);
  assert.equal(r.current, "Methane formation");
  close(redox.model({ carbonMmol: 1 }).methaneMmol, 0);
});

test("invalid inputs throw", () => {
  assert.throws(() => redox.model({ carbonMmol: -0.1 }), RangeError);
  assert.throws(() => redox.model({ o2Mmol: NaN }), RangeError);
  assert.throws(() => redox.model({ sulfateMmol: Infinity }), RangeError);
});

test("mount configuration updates chart, metrics and explanation for all presets", () => {
  let mounted = false;
  global.document = { createElement: () => ({ replaceChildren() {} }) };
  const core = {
    mount(name, config) {
      assert.equal(name, "redox");
      const view = { chart: {}, results: { replaceChildren() {} }, explanation: { textContent: "" } };
      const base = Object.fromEntries(config.controls.map(c => [c.key, c.value]));
      for (const values of [base, ...config.presets.map(p => ({ ...base, ...p.values }))]) {
        config.update(values, view);
        assert.equal(view.chart.output.series.length, 4);
        assert.match(view.explanation.textContent, /overlap/);
      }
      mounted = true;
    },
    lineChart(target, config) { target.output = config; },
    metrics() {}, table() {},
  };
  try { redox.mount(core); } finally { delete global.document; }
  assert.ok(mounted);
});

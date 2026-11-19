"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const sorption = require("../sorption.js");

function close(actual, expected, tolerance = 1e-10) {
  assert.ok(Math.abs(actual - expected) <= tolerance,
    `${actual} differs from expected ${expected}`);
}

test("worked example: half sorbed, 0.500 mg/L, q = 50 mg/kg", () => {
  const r = sorption.model();
  close(r.extraVolumeL, 1);
  close(r.cwMgL, 0.5);
  close(r.waterMg, 0.5);
  close(r.solidMg, 0.5);
  close(r.qMgKg, 50);
  close(r.sorbedFraction, 0.5);
});

test("exercise 1: doubling the solid gives one third, not one half", () => {
  const r = sorption.model({ solidKg: 0.02 });
  close(r.cwMgL, 1 / 3);
  close(r.solidMg, 2 / 3);
  close(r.qMgKg, 100 / 3);
  assert.notEqual(r.cwMgL.toFixed(4), (0.5 / 2).toFixed(4));
});

test("exercise 3: Kd falling to 10 desorbs without adding solute", () => {
  const r = sorption.model({ kdLkg: 10 });
  close(r.cwMgL, 1 / 1.1);
  close(r.solidMg, 0.1 / 1.1);
  close(r.waterMg + r.solidMg, 1);
});

test("check yourself 1: 2.00 mg, 0.0500 kg, Kd 20 gives 1.00 mg/L and half sorbed", () => {
  const r = sorption.model({ totalMg: 2, waterL: 1, solidKg: 0.05, kdLkg: 20 });
  close(r.cwMgL, 1);
  close(r.sorbedFraction, 0.5);
});

test("mass is conserved and q = Kd Cw across the control ranges", () => {
  for (const kdLkg of [1, 10, 100, 300])
    for (const solidKg of [0, 0.001, 0.025, 0.05])
      for (const totalMg of [0.1, 1, 3])
        for (const waterL of [0.25, 1, 2]) {
          const r = sorption.model({ kdLkg, solidKg, totalMg, waterL });
          close(r.waterMg + r.solidMg, totalMg, 1e-12);
          close(r.qMgKg, kdLkg * r.cwMgL, 1e-9);
          assert.ok(r.sorbedFraction >= 0 && r.sorbedFraction < 1);
        }
  const none = sorption.model({ solidKg: 0 });
  close(none.cwMgL, 1);
  close(none.solidMg, 0);
});

test("invalid inputs throw", () => {
  assert.throws(() => sorption.model({ waterL: 0 }), RangeError);
  assert.throws(() => sorption.model({ kdLkg: -1 }), RangeError);
  assert.throws(() => sorption.model({ solidKg: NaN }), RangeError);
});

test("mount configuration updates chart, metrics and explanation for all presets", () => {
  let mounted = false;
  global.document = { createElement: () => ({ replaceChildren() {} }) };
  const core = {
    number: String,
    mount(name, config) {
      assert.equal(name, "sorption");
      const view = { chart: {}, results: { replaceChildren() {} }, explanation: { textContent: "" } };
      const base = Object.fromEntries(config.controls.map(c => [c.key, c.value]));
      for (const values of [base, ...config.presets.map(p => ({ ...base, ...p.values }))]) {
        config.update(values, view);
        for (const s of view.chart.output.series) assert.ok(s.points.every(p => Number.isFinite(p.y)));
        assert.ok(view.explanation.textContent.length > 50);
      }
      mounted = true;
    },
    lineChart(target, config) { target.output = config; },
    metrics() {}, table() {},
  };
  try { sorption.mount(core); } finally { delete global.document; }
  assert.ok(mounted);
});

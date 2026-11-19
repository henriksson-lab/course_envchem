const test = require('node:test');
const assert = require('node:assert/strict');
const box = require('../boxmodel.js');
const pulse = require('../co2pulse.js');

function close(actual, expected, tolerance = 1e-9) {
  assert.ok(Math.abs(actual - expected) <= tolerance,
    `${actual} differs from expected ${expected}`);
}

test('lecture lake: tau 100 days, steady 100 kg and 0.1 mg/L', () => {
  const r = box.model();
  // V = 1e6 m3, Q = 1e4 m3/day -> tau = 100 days; steady M = I x tau = 100 kg
  close(r.replacementDays, 1e6 / 1e4);
  close(r.timeConstantDays, 100);
  close(r.steadyKg, 1.0 * 100);
  close(r.steadyMgL, 100 * 1e6 / 1e9);          // 100 kg in 1e9 L, in mg/L
  close(r.oneTimeConstant.inventoryKg, 100 * (1 - Math.exp(-1)));
  close(r.steady.outflowKgDay, 1.0);              // output = input at steady state
  close(r.steady.changeKgDay, 0);
});

test('doubling input doubles steady inventory; flow sets steady concentration I/Q', () => {
  close(box.model({ inputKgDay: 2 }).steadyKg, 200);
  const big = box.model({ volumeMillionM3: 4 });
  close(big.steadyMgL, box.model().steadyMgL);   // conservative: C = I/Q, not volume
  close(big.timeConstantDays, 400);
  const fast = box.model({ flowThousandM3Day: 20 });
  close(fast.steadyKg, 50);
  close(fast.replacementDays, 50);
});

test('flushing leaves e^-1 after one tau; reaction adds to flushing', () => {
  const flush = box.model({ inputKgDay: 0, startKg: 100 });
  close(flush.inventoryAt(100), 100 * Math.exp(-1));
  close(flush.steadyKg, 0);
  const both = box.model({ inputKgDay: 0, startKg: 100, kPerDay: 0.01 });
  close(both.lossPerDay, 0.01 + 0.01);
  close(both.inventoryAt(100), 100 * Math.exp(-2));
  close(box.model({ kPerDay: 0.01 }).steadyKg, 50);
});

test('balance closes: change = input - outflow - reaction matches dM/dt', () => {
  for (const values of [{}, { kPerDay: 0.02, startKg: 300 }, { inputKgDay: 0, startKg: 50, flowThousandM3Day: 3 }]) {
    const r = box.model(values);
    for (const t of [1, 13, 100, 777]) {
      const b = r.budgetAt(t);
      const h = 1e-3;
      const numeric = (r.inventoryAt(t + h) - r.inventoryAt(t - h)) / (2 * h);
      close(b.changeKgDay, numeric, 1e-6);
      close(b.inputKgDay - b.outflowKgDay - b.reactionKgDay, b.changeKgDay);
    }
  }
});

test('box model rejects invalid input', () => {
  assert.throws(() => box.model({ volumeMillionM3: 0 }), RangeError);
  assert.throws(() => box.model({ flowThousandM3Day: 0, kPerDay: 0 }), RangeError);
  assert.throws(() => box.model({ inputKgDay: -1 }), RangeError);
  assert.throws(() => box.model({ startKg: NaN }), RangeError);
});

test('exercise 3 numbers: k = 0.0200, lifetime 50.0, half-life 34.7, 0.368 left', () => {
  const r = pulse.model({ lifetimeYears: 50, readYears: 50 });
  close(r.kPerYear, 0.02);
  close(r.halfLifeYears, 50 * Math.log(2));
  assert.equal(r.halfLifeYears.toFixed(1), '34.7');
  assert.equal(r.singleLeft.toFixed(3), '0.368');
});

test('CO2 impulse matches lecture values and the Joos 2013 fit', () => {
  const irf = t => 0.2173 + 0.2240 * Math.exp(-t / 394.4) + 0.2824 * Math.exp(-t / 36.54) + 0.2763 * Math.exp(-t / 4.304);
  for (const t of [0, 20, 100, 500]) close(pulse.co2Fraction(t), irf(t));
  close(pulse.co2Fraction(0), 1, 1e-12);
  assert.equal(pulse.co2Fraction(20).toFixed(2), '0.60');
  assert.equal(pulse.co2Fraction(100).toFixed(2), '0.41');
  assert.equal(pulse.co2Fraction(500).toFixed(2), '0.28');
  assert.ok(pulse.co2Fraction(5000) > 0.2173 && pulse.co2Fraction(5000) < 0.22);
  const r = pulse.model({ lifetimeYears: 12, readYears: 100 });
  assert.ok(r.co2Left > r.singleLeft);
  close(r.co2Parts.reduce((s, p) => s + p.left, 0), r.co2Left);
});

test('pulse model rejects invalid input', () => {
  assert.throws(() => pulse.model({ lifetimeYears: 0 }), RangeError);
  assert.throws(() => pulse.model({ readYears: -5 }), RangeError);
  assert.throws(() => pulse.model({ lifetimeYears: NaN }), RangeError);
});

test('both demos expose mount configurations that update their views', () => {
  for (const [api, expectedName] of [[box, 'boxmodel'], [pulse, 'co2pulse']]) {
    let mounted = false;
    const fakeDocument = { createElement: () => ({}) };
    global.document = fakeDocument;
    const core = {
      number: v => String(v),
      mount(name, config) {
        assert.equal(name, expectedName);
        assert.ok(config.controls.length >= 2 && config.controls.length <= 5);
        assert.ok(config.presets.length >= 3);
        const view = { chart: {}, results: { replaceChildren() {} }, explanation: { textContent: '' } };
        const values = Object.fromEntries(config.controls.map(c => [c.key, c.value]));
        for (const v of [values, ...config.presets.map(p => ({ ...values, ...p.values }))]) {
          for (const c of config.controls) assert.ok(v[c.key] >= c.min && v[c.key] <= c.max, c.key);
          config.update(v, view);
          assert.ok(view.chart.output.series.every(s => s.points.every(p => Number.isFinite(p.y))));
          assert.ok(view.explanation.textContent.length > 50);
        }
        mounted = true;
      },
      lineChart(target, config) { target.output = config; },
      metrics(target, items) { assert.ok(items.length >= 3); },
      table(target, config) { assert.ok(config.rows.length >= 3); },
    };
    api.mount(core);
    delete global.document;
    assert.ok(mounted);
  }
});

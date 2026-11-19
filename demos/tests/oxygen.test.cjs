const test = require('node:test');
const assert = require('node:assert/strict');
const oxygen = require('../oxygen.js');

function close(actual, expected, tolerance) {
  assert.ok(Math.abs(actual - expected) <= tolerance, `${actual} differs from expected ${expected}`);
}

test('worked example: 3.00 mg C/L needs 8.00 mg O2/L', () => {
  close(oxygen.model({ carbonMgL: 3 }).ultimateMgL, 8.0, 1e-9);
  close(oxygen.model({ carbonMgL: 1.5 }).ultimateMgL, 4.0, 1e-9);
});

test('exercise 2: 2.00 mg C/L in 9.00 mg/L leaves 3.67 mg/L after complete oxidation', () => {
  const r = oxygen.model({ carbonMgL: 2, oxygenMgL: 9 });
  close(r.ultimateMgL, 5.333, 0.001);
  close(r.leftAfterCompleteMgL, 3.667, 0.001);
  assert.equal(r.anoxicDay, Infinity);
});

test('exercise 3: 25% of 4.00 mg C/L uses 2.67 mg O2/L; ultimate demand 10.67', () => {
  const t25 = Math.log(4 / 3) / 0.1;
  const r = oxygen.model({ carbonMgL: 4, oxygenMgL: 12, ratePerDay: 0.1, days: t25 });
  close(r.consumedMgL, 1.0 * 32 / 12, 1e-9);
  close(r.ultimateMgL, 4 * 32 / 12, 1e-9);
  close(r.fractionOxidised, 0.25, 1e-12);
});

test('5-day consumption matches the lecture figure (about 4.2 mg/L)', () => {
  const r = oxygen.model();
  close(r.consumedMgL, (32 / 3) * (1 - Math.exp(-0.5)), 1e-9);
  close(r.consumedMgL, 4.2, 0.01);
  close(r.oxygenLeftMgL + r.consumedMgL, r.oxygenMgL, 1e-12);
});

test('oxygen never goes negative and runs out at the computed day', () => {
  const r = oxygen.model({ carbonMgL: 5, oxygenMgL: 9, ratePerDay: 0.1, days: 40 });
  close(r.oxygenLeftMgL, 0, 1e-12);
  const t = r.anoxicDay;
  close((5 * 32 / 12) * (1 - Math.exp(-0.1 * t)), 9, 1e-9);
  close(r.at(t - 1e-6).oxygenLeftMgL, 0, 1e-5);
  assert.ok(r.at(t / 2).oxygenLeftMgL > 0);
  for (let d = 0; d <= 40; d += 0.5) assert.ok(r.at(d).oxygenLeftMgL >= 0);
});

test('limits: no carbon uses no oxygen; long time approaches the ultimate demand', () => {
  const none = oxygen.model({ carbonMgL: 0, days: 40 });
  close(none.consumedMgL, 0, 1e-12);
  const late = oxygen.model({ carbonMgL: 2, oxygenMgL: 9, ratePerDay: 0.5, days: 40 });
  close(late.consumedMgL, late.ultimateMgL, 1e-6);
});

test('invalid inputs throw', () => {
  assert.throws(() => oxygen.model({ carbonMgL: -1 }), RangeError);
  assert.throws(() => oxygen.model({ oxygenMgL: NaN }), RangeError);
  assert.throws(() => oxygen.model({ days: -2 }), RangeError);
});

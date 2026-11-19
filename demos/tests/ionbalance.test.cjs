"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const ion = require("../ionbalance.js");

function close(actual, expected, tolerance = 1e-10) {
  assert.ok(Math.abs(actual - expected) <= tolerance, `${actual} differs from expected ${expected}`);
}
// Independent Davies estimate, A = 0.509.
function davies(I, z) {
  return 10 ** (-0.509 * z * z * (Math.sqrt(I) / (1 + Math.sqrt(I)) - 0.3 * I));
}

test("worked example balances at 2.000 meq/L each", () => {
  const r = ion.model();
  close(r.cationsMeqL, 2 * 0.5 + 2 * 0.25 + 0.5);
  close(r.anionsMeqL, 1.2 + 0.4 + 2 * 0.2);
  close(r.cationsMeqL, 2.0);
  close(r.imbalancePercent, 0);
  // I = 1/2 (0.5*4 + 0.25*4 + 0.5 + 1.2 + 0.4 + 0.2*4) = 2.95 mmol/L
  close(r.ionicStrengthMmolL, 2.95);
  assert.equal(r.gamma1.toFixed(2), "0.94");
  assert.equal(r.gamma2.toFixed(2), "0.79");
});

test("sample C: sulfate 1.9212 mg/L gives +9.89 %", () => {
  const so4 = 1.9212 / 96.06;   // 0.0200 mmol/L
  const r = ion.model({ so4MmolL: so4 });
  close(r.anionsMeqL, 1.64);
  close(r.gapMeqL, 0.36);
  assert.equal(r.imbalancePercent.toFixed(2), "9.89");
  const corrected = ion.model({ so4MmolL: 19.212 / 96.06 });
  close(corrected.imbalancePercent, 0);
});

test("added NaCl raises ionic strength one-for-one but keeps the balance", () => {
  for (const nacl of [20, 120, 200]) {
    const r = ion.model({ naclMmolL: nacl });
    close(r.imbalancePercent, 0);
    close(r.ionicStrengthMmolL, 2.95 + nacl);
    close(r.gamma2, davies((2.95 + nacl) / 1000, 2));
  }
  assert.equal(ion.model({ naclMmolL: 120 }).gamma2.toFixed(2), "0.35");
});

test("exercise 3 ionic strength and activity limits", () => {
  close(0.5 * (0.001 * 4 + 0.002 * 1), 0.003);
  close(ion.davies(0.003, 1), davies(0.003, 1));
  close(ion.davies(0, 2), 1);
  const r = ion.model({ naclMmolL: 50 });
  for (const i of r.ions) close(i.activityMmolL, i.gamma * i.mmolL);
  assert.ok(r.gamma2 < r.gamma1 && r.gamma1 < 1);
});

test("divalent ions count twice in charge, four times in ionic strength", () => {
  const a = ion.model({ caMmolL: 1.0 });
  const b = ion.model();
  close(a.cationsMeqL - b.cationsMeqL, 1.0);
  close(a.ionicStrengthMmolL - b.ionicStrengthMmolL, 0.5 * 0.5 * 4);
});

test("invalid input throws", () => {
  assert.throws(() => ion.model({ caMmolL: -0.1 }), RangeError);
  assert.throws(() => ion.model({ so4MmolL: NaN }), RangeError);
  assert.throws(() => ion.model({ naclMmolL: 1000 }), RangeError);
  assert.throws(() => ion.davies(-1, 1), RangeError);
});

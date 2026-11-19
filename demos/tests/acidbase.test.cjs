const test = require('node:test');
const assert = require('node:assert/strict');
const acidbase = require('../acidbase.js');

function close(actual, expected, tolerance = 1e-9) {
  assert.ok(Math.abs(actual - expected) <= tolerance,
    `${actual} differs from expected ${expected}`);
}

test('notes worked example: 0.0100 mol FeS2 gives 0.0400 eq acid, 0.0200 mol sulfate, 2.00 g CaCO3', () => {
  const r = acidbase.acidBudget({ feS2Mol: 0.01, caco3Mol: 0.02, eqPerCaCO3: 2 });
  close(r.acidEq, 0.04);
  close(r.sulfateMol, 0.02);
  close(r.caco3NeededMol, 0.02);
  close(r.caco3NeededG, 2.0);
  close(r.residualAcidEq, 0);
});

test('exercise 2 shortfall: 0.0150 mol accessible CaCO3 leaves 0.0100 eq', () => {
  const r = acidbase.acidBudget({ feS2Mol: 0.01, caco3Mol: 0.015, eqPerCaCO3: 2 });
  close(r.neutralisedEq, 0.03);
  close(r.residualAcidEq, 0.01);
});

test('Falun estimate: 1 % pyrite per tonne gives about 333 eq, 17 or 33 kg CaCO3', () => {
  const co2 = acidbase.model({ eqPerCaCO3: 2 });
  close(co2.feS2Mol, 10000 / 120);
  close(co2.acidPotentialEqT, 4 * 10000 / 120);
  close(co2.sulfateMolT, 2 * 10000 / 120);
  close(co2.caco3NeededKgT, (4 * 10000 / 120) / 2 * 100 / 1000);
  assert.equal(Math.round(co2.caco3NeededKgT), 17);
  const neutral = acidbase.model({ eqPerCaCO3: 1 });
  assert.equal(Math.round(neutral.caco3NeededKgT), 33);
});

test('lag-time figure: 150 eq capacity, k = 0.02 per year, calcite used up after about 30 years', () => {
  const r = acidbase.model();
  close(r.neutralisationEqT, 150);
  const ap = 4 * 10000 / 120;
  close(r.exhaustionYears, -Math.log(1 - 150 / ap) / 0.02);
  assert.equal(Math.round(r.exhaustionYears), 30);
  const h = acidbase.history(r, r.exhaustionYears);
  close(h.generated, 150, 1e-6);
  close(h.drained, 0, 1e-6);
});

test('endpoint and coating each halve reachable neutralisation; rate changes timing only', () => {
  const base = acidbase.model();
  const nearNeutral = acidbase.model({ eqPerCaCO3: 1 });
  const coated = acidbase.model({ accessiblePct: 50 });
  close(nearNeutral.neutralisationEqT, base.neutralisationEqT / 2);
  close(coated.neutralisationEqT, base.neutralisationEqT / 2);
  assert.ok(nearNeutral.exhaustionYears < base.exhaustionYears);
  const fast = acidbase.model({ ratePerYear: 0.04 });
  close(fast.residualAcidEqT, base.residualAcidEqT);
  close(fast.exhaustionYears, base.exhaustionYears / 2);
});

test('conservation: generated acid = neutralised + drained, and approaches AP', () => {
  const r = acidbase.model({ pyritePct: 2.3, calciteKgT: 12 });
  for (const t of [0, 5, 40, 150, 2000]) {
    const h = acidbase.history(r, t);
    close(h.generated, h.neutralised + h.drained, 1e-9);
    assert.ok(h.neutralised <= r.neutralisationEqT + 1e-9);
  }
  close(acidbase.history(r, 5000).drained, r.residualAcidEqT, 1e-6);
});

test('limits: enough calcite never runs out; no pyrite makes no acid', () => {
  const rich = acidbase.model({ calciteKgT: 40 });
  assert.equal(rich.exhaustionYears, Infinity);
  close(rich.residualAcidEqT, 0);
  const none = acidbase.model({ pyritePct: 0 });
  close(none.acidPotentialEqT, 0);
  close(acidbase.history(none, 100).drained, 0);
  const noCalcite = acidbase.model({ calciteKgT: 0 });
  close(noCalcite.exhaustionYears, 0);
});

test('invalid input throws', () => {
  assert.throws(() => acidbase.model({ pyritePct: -1 }), RangeError);
  assert.throws(() => acidbase.model({ calciteKgT: NaN }), RangeError);
  assert.throws(() => acidbase.model({ accessiblePct: 120 }), RangeError);
  assert.throws(() => acidbase.model({ ratePerYear: 0 }), RangeError);
  assert.throws(() => acidbase.model({ eqPerCaCO3: 1.5 }), RangeError);
});

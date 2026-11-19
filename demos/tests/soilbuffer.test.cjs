const test = require('node:test');
const assert = require('node:assert/strict');
const soil = require('../soilbuffer.js');

function close(actual, expected, tolerance = 1e-9) {
  assert.ok(Math.abs(actual - expected) <= tolerance,
    `${actual} differs from expected ${expected}`);
}

test('soil: lecture soils A and B reserves and base saturation', () => {
  const b = soil.model();
  close(b.reserveCmolc, 14.2);
  close(b.baseSaturationPct, 71);
  close(b.basesLeftCmolc, 9.2);
  close(b.baseSaturationAfterPct, 46);
  close(b.byAluminium, 0);
  close(b.calciumLostCmol, 2.5);
  const a = soil.model({ cecCmolc: 3, basesCmolc: 1.7, acidCmolc: 5 });
  close(a.reserveCmolc, 1.7);
  close(a.basesLeftCmolc, 0);
  close(a.byAluminium, 3.3);
  assert.equal(a.stage, 'aluminium');
  close(b.reserveCmolc / a.reserveCmolc, 14.2 / 1.7);
});

test('soil: exercise 2 base saturation and carbonate counts two equivalents', () => {
  close(soil.model({ cecCmolc: 12, basesCmolc: 9, acidCmolc: 0 }).baseSaturationPct, 75);
  const c = soil.model({ cecCmolc: 3, basesCmolc: 1.7, carbonateCmol: 1, acidCmolc: 1.5 });
  close(c.carbonateCmolc, 2);
  close(c.byCarbonate, 1.5);
  close(c.byExchange, 0);
  assert.equal(c.stage, 'carbonate');
});

test('soil: acid is fully accounted for by the three pathways', () => {
  for (const acid of [0, 0.7, 2, 5, 14.2, 29.9]) {
    const r = soil.model({ carbonateCmol: 1.3, acidCmolc: acid });
    close(r.byCarbonate + r.byExchange + r.byAluminium, acid);
    close(r.reserveLeftCmolc + r.byCarbonate + r.byExchange, r.reserveCmolc);
    assert.ok(r.basesLeftCmolc >= 0 && r.carbonateLeftCmolc >= 0);
  }
});

test('soil: invalid input throws', () => {
  assert.throws(() => soil.model({ basesCmolc: 25 }), RangeError);
  assert.throws(() => soil.model({ cecCmolc: 0, basesCmolc: 0 }), RangeError);
  assert.throws(() => soil.model({ acidCmolc: -1 }), RangeError);
  assert.throws(() => soil.model({ carbonateCmol: Infinity }), RangeError);
});

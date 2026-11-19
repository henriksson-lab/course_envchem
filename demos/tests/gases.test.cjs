const test = require('node:test');
const assert = require('node:assert/strict');
const gases = require('../gases.js');

function close(actual, expected, tolerance) {
  assert.ok(Math.abs(actual - expected) <= tolerance, `${actual} differs from expected ${expected}`);
}

test('Henry law gives 13.6 umol/L CO2* at 4.00e-4 atm, whatever the alkalinity', () => {
  for (const alkMeqL of [0, 1, 2.8]) {
    close(gases.model({ pco2Atm: 4.0e-4, alkMeqL, caMmolL: 1 }).co2UmolL, 13.6, 1e-9);
  }
});

test('pure water with air CO2 gives the clean-rain pH of about 5.6', () => {
  const r = gases.model({ pco2Atm: 4.0e-4, alkMeqL: 0, caMmolL: 0.05 });
  // Independent: [H+]^2 = K1 [CO2*] + Kw
  const h = Math.sqrt(Math.pow(10, -6.35) * 1.36e-5 + 1e-14);
  close(r.pH, -Math.log10(h), 0.002);
  close(r.pH, 5.61, 0.01);
});

test('exercise 3: alkalinity 1.39 meq/L at 4.00e-4 atm reproduces pH 8.35 and C_T 1.388 mmol/L', () => {
  const r = gases.model({ pco2Atm: 4.0e-4, alkMeqL: 1.39, caMmolL: 0.5 });
  close(r.pH, 8.35, 0.005);
  // Lecture: C_T = 13.6 x (1 + 100 + 1.047) umol/L
  close(r.ctMmolL, 13.6 * (1 + 100 + 1.04713) / 1000, 0.01);
});

test('lecture karst water: Omega ~1 in soil air, pH ~7.3; degassed to air pH ~8.6, Omega ~23', () => {
  const soil = gases.model({ pco2Atm: 0.01, alkMeqL: 2.8, caMmolL: 1.4 });
  const air = gases.model({ pco2Atm: 4.0e-4, alkMeqL: 2.8, caMmolL: 1.4 });
  close(soil.omega, 1, 0.05);
  close(soil.pH, 7.3, 0.05);
  close(air.pH, 8.6, 0.06);
  close(air.omega, 23, 1);
  assert.ok(air.ctMmolL < soil.ctMmolL, 'degassing lowers C_T');
});

test('solution satisfies the alkalinity balance and carbon pools add up', () => {
  const r = gases.model({ pco2Atm: 2e-3, alkMeqL: 1.2, caMmolL: 0.8 });
  const h = Math.pow(10, -r.pH);
  const at = r.hco3MmolL / 1000 + 2 * r.co3UmolL / 1e6 + 1e-14 / h - h;
  close(at * 1000, 1.2, 1e-9);
  close(r.co2UmolL / 1000 + r.hco3MmolL + r.co3UmolL / 1000, r.ctMmolL, 1e-12);
  close(r.omega, 0.8e-3 * r.co3UmolL * 1e-6 / 3.3e-9, 1e-9);
});

test('more CO2 at fixed alkalinity lowers pH and Omega; calcium scales Omega linearly', () => {
  let previous = gases.model({ pco2Atm: 1e-4, alkMeqL: 2, caMmolL: 1 });
  for (const p of [3e-4, 1e-3, 3e-3, 1e-2]) {
    const r = gases.model({ pco2Atm: p, alkMeqL: 2, caMmolL: 1 });
    assert.ok(r.pH < previous.pH && r.omega < previous.omega);
    previous = r;
  }
  const a = gases.model({ pco2Atm: 1e-3, alkMeqL: 2, caMmolL: 0.5 });
  const b = gases.model({ pco2Atm: 1e-3, alkMeqL: 2, caMmolL: 1.0 });
  close(b.omega, 2 * a.omega, 1e-9);
  close(b.pH, a.pH, 1e-12);
});

test('slider pressure rounding hits the preset values exactly', () => {
  assert.equal(gases.pressure(-2), 0.01);
  assert.equal(gases.pressure(-3.4), 4.0e-4);
  assert.equal(gases.pressure(Math.log10(4e-4)), 4.0e-4);
});

test('invalid inputs throw', () => {
  assert.throws(() => gases.model({ pco2Atm: 0 }), RangeError);
  assert.throws(() => gases.model({ pco2Atm: NaN }), RangeError);
  assert.throws(() => gases.model({ alkMeqL: -1 }), RangeError);
  assert.throws(() => gases.model({ caMmolL: -0.1 }), RangeError);
});

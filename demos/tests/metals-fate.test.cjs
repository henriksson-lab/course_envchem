'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const metal = require('../metals.js');
const fate = require('../fate.js');
const close = (actual, expected, tolerance = 1e-10) => {
  assert.ok(Number.isFinite(actual));
  assert.ok(Math.abs(actual - expected) <= tolerance, `${actual} differs from ${expected}`);
};

test('metal binding matches the hand calculation and conserves total metal', () => {
  const m = metal.model({ totalUmolL: 2, freeLigandUmolL: 10, pH: 8 });
  close(m.freeUmolL, 2 / 11);
  close(m.complexedUmolL, 20 / 11);
  close(m.freeUmolL + m.complexedUmolL, 2);
  // Independently recover beta from species amounts in mol/L.
  close((m.complexedUmolL * 1e-6) / ((m.freeUmolL * 1e-6) * 1e-5), 1e6, 1e-8);
});

test('saturation uses free metal, not the dissolved total', () => {
  const m = metal.model({ totalUmolL: 10, freeLigandUmolL: 9, pH: 9 });
  close(m.freeUmolL, 1);
  close(m.hydroxideMolL, 1e-5, 1e-18);
  close(m.ionProduct, 1e-16, 1e-28);
  close(m.saturationRatio, 1);
  assert.equal(m.saturationState, 'saturated');
  const noLigand = metal.model({ totalUmolL: 10, freeLigandUmolL: 0, pH: 9 });
  close(noLigand.saturationRatio, 10);
  assert.equal(noLigand.saturationState, 'supersaturated');
});

test('changing pH affects hydroxide saturation rather than the stipulated ligand binding', () => {
  const lo = metal.model({ totalUmolL: 2, freeLigandUmolL: 10, pH: 8 });
  const hi = metal.model({ totalUmolL: 2, freeLigandUmolL: 10, pH: 9 });
  close(lo.freeUmolL, hi.freeUmolL);
  close(hi.saturationRatio / lo.saturationRatio, 100);
});

test('zero metal and zero ligand are valid model limits; invalid inputs are rejected', () => {
  const absent = metal.model({ totalUmolL: 0, freeLigandUmolL: 30, pH: 10 });
  close(absent.freeUmolL + absent.complexedUmolL, 0);
  close(absent.saturationRatio, 0);
  assert.equal(absent.freeFraction, null);
  const unbound = metal.model({ totalUmolL: 7, freeLigandUmolL: 0, pH: 6 });
  close(unbound.freeUmolL, 7);
  close(unbound.complexedUmolL, 0);
  assert.throws(() => metal.model({ totalUmolL: -1, freeLigandUmolL: 1, pH: 7 }), RangeError);
  assert.throws(() => metal.model({ totalUmolL: 1, freeLigandUmolL: NaN, pH: 7 }), RangeError);
});

test('compound U at two and three half-lives matches the course references', () => {
  const day20 = fate.model({ kdLKg: 100, halfLifeDays: 10, timeDays: 20 });
  close(day20.totalParentMg, 0.25);
  close(day20.waterParentMg, 0.125);
  close(day20.solidParentMg, 0.125);
  close(day20.waterMgL, 0.125);
  close(day20.transformedParentMg, 0.75);
  const day30 = fate.model({ kdLKg: 100, halfLifeDays: 10, timeDays: 30 });
  close(day30.totalParentMg, 0.125);
  close(day30.waterMgL, 0.0625);
});

test('compound V after one half-life has the independently specified phase split', () => {
  const v = fate.model({ kdLKg: 10, halfLifeDays: 30, timeDays: 30 });
  close(v.totalParentMg, 0.5);
  close(v.waterMgL, 0.45454545454545453);
  close(v.solidMgKg / v.waterMgL, 10);
});

test('Kd redistributes mass without changing the stipulated total-parent transformation', () => {
  for (const time of [0, 1, 10, 20, 60]) {
    const aqueous = fate.model({ kdLKg: 0, halfLifeDays: 10, timeDays: time });
    const sorbing = fate.model({ kdLKg: 300, halfLifeDays: 10, timeDays: time });
    close(aqueous.totalParentMg, sorbing.totalParentMg);
    close(aqueous.waterParentMg, aqueous.totalParentMg);
    close(aqueous.solidParentMg, 0);
    for (const m of [aqueous, sorbing]) {
      close(m.waterParentMg + m.solidParentMg, m.totalParentMg);
      close(m.totalParentMg + m.transformedParentMg, 1);
      assert.ok(m.remainingFraction >= 0 && m.remainingFraction <= 1);
    }
  }
});

test('half-life and zero-time limits remain valid and nonphysical inputs are rejected', () => {
  for (const halfLife of [1, 10, 60]) {
    close(fate.model({ kdLKg: 100, halfLifeDays: halfLife, timeDays: halfLife }).remainingFraction, 0.5);
    close(fate.model({ kdLKg: 100, halfLifeDays: halfLife, timeDays: 0 }).totalParentMg, 1);
  }
  assert.throws(() => fate.model({ kdLKg: 1, halfLifeDays: 0, timeDays: 1 }), RangeError);
  assert.throws(() => fate.model({ kdLKg: 1, halfLifeDays: 1, timeDays: -1 }), RangeError);
  assert.throws(() => fate.model({ kdLKg: Infinity, halfLifeDays: 1, timeDays: 1 }), RangeError);
});

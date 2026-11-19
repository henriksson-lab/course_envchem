"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const carbonate = require("../carbonate.js");

function close(actual, expected, tolerance = 1e-10) {
  assert.ok(Math.abs(actual - expected) <= tolerance,
    `expected ${actual} to be within ${tolerance} of ${expected}`);
}

// Evaluate mass action independently with species ratios (the implementation
// uses the hydrogen-ion polynomial); test identities across the usable range.
test("fractions obey independent ratio expressions, balance, and limiting cases", () => {
  for (const pH of [0, 2, 4, 6.35, 7.5, 8.35, 10.33, 12, 14]) {
    const a = carbonate.fractions(pH);
    const r1 = 10 ** (pH - 6.35);
    const r2 = 10 ** (pH - 10.33);
    const sum = 1 + r1 + r1 * r2;
    close(a.co2, 1 / sum);
    close(a.bicarbonate, r1 / sum);
    close(a.carbonate, r1 * r2 / sum);
    close(a.co2 + a.bicarbonate + a.carbonate, 1);
    for (const fraction of Object.values(a)) assert.ok(fraction >= 0 && fraction <= 1);
  }
  assert.ok(carbonate.fractions(2).co2 > 0.9999);
  assert.ok(carbonate.fractions(14).carbonate > 0.999);
  close(carbonate.fractions(6.35).co2, carbonate.fractions(6.35).bicarbonate);
  close(carbonate.fractions(10.33).bicarbonate, carbonate.fractions(10.33).carbonate);
});

test("closed acid states reproduce independent course reference calculations", () => {
  const a = carbonate.model({ ctMmolL: 1, initialPH: 7.5, acidMeqL: 0.05 });
  const b = carbonate.model({ ctMmolL: 0.1, initialPH: 7.5, acidMeqL: 0.05 });
  assert.equal(a.ok, true);
  assert.equal(b.ok, true);
  close(a.finalPH, 7.235116, 1e-6);
  close(b.finalPH, 6.251551, 1e-6);
  assert.ok(b.finalPH < a.finalPH);
  close(a.initialAlkalinityMeqL - a.finalAlkalinityMeqL, 0.05);
  close(b.initialAlkalinityMeqL - b.finalAlkalinityMeqL, 0.05);
  for (const state of [a, b]) {
    const h = 10 ** (-state.finalPH);
    const ct = state.ctMmolL / 1000;
    const co2 = ct / (1 + 10 ** (state.finalPH - 6.35) +
      10 ** (2 * state.finalPH - 6.35 - 10.33));
    const bicarbonate = 10 ** (-6.35) * co2 / h;
    const divalent = 10 ** (-10.33) * bicarbonate / h;
    close(co2 + bicarbonate + divalent, ct, 1e-14);
    close((bicarbonate + 2 * divalent + 1e-14 / h - h) * 1000,
      state.finalAlkalinityMeqL, 1e-10);
  }
});

test("no acid preserves the initial pH and all slider endpoints remain physical", () => {
  for (const ctMmolL of [0.05, 0.1, 1, 2]) {
    for (const initialPH of [5.5, 7.5, 9.5]) {
      const unchanged = carbonate.model({ ctMmolL, initialPH, acidMeqL: 0 });
      assert.equal(unchanged.ok, true);
      close(unchanged.finalPH, initialPH);
      for (const acidMeqL of [0.005, 0.05, 0.2]) {
        const state = carbonate.model({ ctMmolL, initialPH, acidMeqL });
        assert.equal(state.ok, true);
        assert.ok(state.finalPH < initialPH);
        close(Object.values(state.finalFractions).reduce((sum, a) => sum + a, 0), 1);
        close(carbonate.alkalinity(state.finalPH, ctMmolL / 1000) * 1000,
          state.finalAlkalinityMeqL, 1e-9);
      }
    }
  }
});

test("invalid inputs and unattainable bracket targets report a controlled failure", () => {
  assert.equal(carbonate.model({ ctMmolL: 0, initialPH: 7.5, acidMeqL: 0 }).ok, false);
  assert.equal(carbonate.model({ ctMmolL: 1, initialPH: NaN, acidMeqL: 0 }).ok, false);
  assert.equal(carbonate.model({ ctMmolL: 1, initialPH: 7.5, acidMeqL: -1 }).ok, false);
  assert.equal(carbonate.model({ ctMmolL: 1, initialPH: 7.5, acidMeqL: 2000 }).ok, false);
  assert.equal(carbonate.solvePH(Infinity, 0.001).ok, false);
});

"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const lifetime = require("../lifetime.js");

function close(actual, expected, tolerance = 1e-9) {
  assert.ok(Math.abs(actual - expected) <= tolerance * Math.max(1, Math.abs(expected)),
    `${actual} differs from expected ${expected}`);
}

test("worked example reproduces exercise 2", () => {
  const r = lifetime.model();
  close(r.kTotal, 1.0e-12 * 1.0e6);
  close(r.lifetimeS, 1.0e6);
  close(r.lifetimeDays, 1.0e6 / 86400);          // 11.574 days
  assert.equal(r.lifetimeDays.toFixed(1), "11.6");
  close(r.halfLifeDays, 0.693147 * 11.574074, 1e-5);
  assert.equal(r.halfLifeDays.toFixed(1), "8.0");
  assert.equal(r.spread.key, "regional");
});

test("decay curve: 0.37 left after one lifetime, 0.50 after one half-life", () => {
  const r = lifetime.model();
  close(lifetime.remaining(r, 0), 1);
  close(lifetime.remaining(r, r.lifetimeDays), Math.exp(-1));
  close(lifetime.remaining(r, r.halfLifeDays), 0.5);
});

test("doubling OH or k halves the lifetime; k and OH enter only as a product", () => {
  const base = lifetime.model();
  close(lifetime.model({ ohMillion: 2 }).lifetimeS, base.lifetimeS / 2);
  close(lifetime.model({ logK: -12 + Math.log10(2) }).lifetimeS, base.lifetimeS / 2);
  close(lifetime.model({ logK: -11, ohMillion: 0.1 }).lifetimeS, base.lifetimeS);
});

test("parallel sinks add rate constants, not lifetimes", () => {
  const r = lifetime.model({ otherPerDay: 0.1 });
  const kTotalPerDay = 86400 / 1.0e6 + 0.1;       // 0.0864 + 0.1 per day
  close(r.lifetimeDays, 1 / kTotalPerDay);
  assert.ok(r.lifetimeDays < lifetime.model().lifetimeDays);
  close(r.ohShare, 0.0864 / 0.1864);
});

test("transport categories follow the lecture time scales", () => {
  assert.equal(lifetime.model({ logK: -10, ohMillion: 5 }).spread.key, "local");
  assert.equal(lifetime.model({ logK: -14 }).spread.key, "global");   // about 3.2 years
  close(lifetime.model({ logK: -14 }).lifetimeDays / 365.25, 1e8 / 86400 / 365.25);
  assert.equal(lifetime.spread(100).key, "hemisphere");
});

test("invalid input throws", () => {
  assert.throws(() => lifetime.model({ ohMillion: -1 }), RangeError);
  assert.throws(() => lifetime.model({ otherPerDay: -0.1 }), RangeError);
  assert.throws(() => lifetime.model({ logK: NaN }), RangeError);
  assert.throws(() => lifetime.model({ ohMillion: 0, otherPerDay: 0 }), RangeError);
  close(lifetime.model({ ohMillion: 0, otherPerDay: 0.5 }).lifetimeDays, 2);
});

test("scientific formatting used in the controls", () => {
  assert.equal(lifetime.sci(1e-12), "1.0 × 10⁻¹²");
  assert.equal(lifetime.sci(1e6), "1.0 × 10⁶");
  assert.equal(lifetime.sci(9.99e-7), "1.0 × 10⁻⁶");
});

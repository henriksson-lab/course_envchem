const test = require('node:test');
const assert = require('node:assert/strict');
const treatment = require('../treatment.js');

function close(actual, expected, tolerance = 1e-9) {
  assert.ok(Math.abs(actual - expected) <= tolerance,
    `${actual} differs from expected ${expected}`);
}

test('treatment: lecture phosphorus plant 30/40/90 leaves 4.2 %', () => {
  const r = treatment.model();
  close(r.toSludgeMg[0], 30);
  close(r.toSludgeMg[1], 28);
  close(r.toSludgeMg[2], 37.8);
  close(r.effluentMg, 4.2);
  close(r.overallRemovalPct, 95.8);
  close(r.addedPercentages, 160);
});

test('treatment: notes worked example and exercise 1', () => {
  const w = treatment.model({ massMg: 10, stage1Pct: 60, stage2Pct: 50, stage3Pct: 0 });
  close(w.toSludgeMg[0], 6); close(w.toSludgeMg[1], 2); close(w.effluentMg, 2);
  close(w.overallRemovalPct, 80);
  const e = treatment.model({ massMg: 100, stage1Pct: 30, stage2Pct: 30, stage3Pct: 0 });
  close(e.effluentMg, 49); close(e.overallRemovalPct, 51);
  const h = treatment.model({ massMg: 100, stage1Pct: 50, stage2Pct: 50, stage3Pct: 50 });
  close(h.remainingFraction, 0.125);
});

test('treatment: mass is conserved and limits behave', () => {
  for (const v of [{}, { stage1Pct: 0, stage2Pct: 0, stage3Pct: 0 }, { stage2Pct: 100 }, { massMg: 37, stage1Pct: 13 }]) {
    const r = treatment.model(v);
    close(r.balanceMg, r.massMg);
  }
  close(treatment.model({ stage1Pct: 0, stage2Pct: 0, stage3Pct: 0 }).effluentMg, 100);
  close(treatment.model({ stage2Pct: 100 }).effluentMg, 0);
  close(treatment.model({ stage2Pct: 100 }).toSludgeMg[2], 0);
});

test('treatment: invalid input throws', () => {
  assert.throws(() => treatment.model({ stage1Pct: 101 }), RangeError);
  assert.throws(() => treatment.model({ massMg: -1 }), RangeError);
  assert.throws(() => treatment.model({ stage3Pct: NaN }), RangeError);
});


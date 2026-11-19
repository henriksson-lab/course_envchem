const test = require('node:test');
const assert = require('node:assert/strict');
const deposition = require('../deposition.js');
const catchment = require('../catchment.js');

function close(actual, expected, tolerance = 1e-10) {
  assert.ok(Math.abs(actual - expected) <= tolerance,
    `${actual} differs from expected ${expected}`);
}

test('deposition worked case preserves flux, load, and concentration units', () => {
  const result = deposition.model();
  close(result.totalFluxEqM2, 0.04);
  close(result.nitricEqYear, 20000);
  close(result.sulfuricEqYear, 20000);
  close(result.acidEqYear, 40000);
  close(result.acidMeqL, 0.08);
});

test('doubling receiving water dilutes without changing annual deposition', () => {
  const base = deposition.model();
  const changed = deposition.model({ waterMillionL: 1000 });
  close(changed.acidEqYear, base.acidEqYear);
  close(changed.acidMeqL, base.acidMeqL / 2);
  close(changed.totalFluxEqM2, base.totalFluxEqM2);
});

test('area changes load but not areal flux; two sulfuric equivalents are counted', () => {
  const base = deposition.model();
  const doubleArea = deposition.model({ areaKm2: 2 });
  close(doubleArea.totalFluxEqM2, base.totalFluxEqM2);
  close(doubleArea.acidEqYear, 2 * base.acidEqYear);
  const nitric = deposition.model({ hno3Mmol: 10, h2so4Mmol: 0 });
  const sulfuric = deposition.model({ hno3Mmol: 0, h2so4Mmol: 10 });
  close(sulfuric.acidEqYear, 2 * nitric.acidEqYear);
});

test('zero source and invalid water boundaries are handled explicitly', () => {
  close(deposition.model({ hno3Mmol: 0, h2so4Mmol: 0 }).acidMeqL, 0);
  assert.throws(() => deposition.model({ waterMillionL: 0 }), RangeError);
  assert.throws(() => deposition.model({ hno3Mmol: -1 }), RangeError);
  assert.throws(() => catchment.model({ waterMillionL: NaN }), RangeError);
});

test('catchment reproduces annual budget and its separate alkalinity reference', () => {
  const result = catchment.model();
  close(result.acidEqYear, 40000);
  close(result.neutralisedEqYear, 30000);
  close(result.residualEqYear, 10000);
  close(result.adjustedAlkalinityEqYear, 40000);
  close(result.residualMeqL, 0.02);
  close(result.referenceMeqL, 0.1);
  close(result.adjustedAlkalinityMeqL, 0.08);
  assert.equal('pH' in result, false);
});

test('less neutralisation matches course sensitivity example', () => {
  const result = catchment.model({ capacityKeq: 20 });
  close(result.residualEqYear, 20000);
  close(result.residualMeqL, 0.04);
  close(result.adjustedAlkalinityMeqL, 0.06);
});

test('surplus accessible capacity does not invent an alkalinity source', () => {
  const result = catchment.model({ capacityKeq: 60 });
  close(result.neutralisedEqYear, 40000);
  close(result.unusedCapacityEqYear, 20000);
  close(result.residualEqYear, 0);
  close(result.adjustedAlkalinityEqYear, result.referenceEqYear);
  const noAcid = catchment.model({ acidKeq: 0 });
  close(noAcid.neutralisedEqYear, 0);
  close(noAcid.adjustedAlkalinityEqYear, noAcid.referenceEqYear);
});

test('flow sensitivity changes concentrations without changing annual inventories', () => {
  const base = catchment.model();
  const wet = catchment.model({ waterMillionL: 1000 });
  close(wet.residualEqYear, base.residualEqYear);
  close(wet.adjustedAlkalinityEqYear, base.adjustedAlkalinityEqYear);
  close(wet.residualMeqL, 0.01);
  close(wet.adjustedAlkalinityMeqL, 0.04);
});

test('negative alkalinity is kept as a signed balance rather than clipped', () => {
  const result = catchment.model({ acidKeq: 100, capacityKeq: 20 });
  close(result.residualEqYear, 80000);
  close(result.adjustedAlkalinityEqYear, -30000);
  close(result.adjustedAlkalinityMeqL, -0.06);
});

test('all accessible UI corner cases conserve acid-equivalent amounts', () => {
  for (const acidKeq of [0, 40, 100]) {
    for (const capacityKeq of [0, 30, 100]) {
      for (const referenceKeq of [0, 50, 150]) {
        const result = catchment.model({ acidKeq, capacityKeq, referenceKeq });
        close(result.neutralisedEqYear + result.residualEqYear, result.acidEqYear);
        close(result.neutralisedEqYear + result.unusedCapacityEqYear,
          result.capacityEqYear);
        close(result.adjustedAlkalinityEqYear + result.residualEqYear,
          result.referenceEqYear);
        assert.ok(result.neutralisedEqYear >= 0 && result.residualEqYear >= 0);
      }
    }
  }
});

test('both demos expose compatible mount configurations and update their views', () => {
  for (const [api, expectedName] of [[deposition, 'deposition'], [catchment, 'catchment']]) {
    let mounted = false;
    const core = {
      mount(name, config) {
        assert.equal(name, expectedName);
        const values = Object.fromEntries(config.controls.map(item => [item.key, item.value]));
        const view = { chart: {}, results: {}, explanation: { textContent: '' } };
        config.update(values, view);
        assert.ok(view.chart.output.bars.every(bar => Number.isFinite(bar.value)));
        assert.ok(view.results.output.length >= 3);
        assert.match(view.explanation.textContent, /pH|deposition budget/);
        for (const preset of config.presets) config.update(preset.values, view);
        mounted = true;
      },
      barChart(target, config) { target.output = config; },
      metrics(target, metrics) { target.output = metrics; },
    };
    api.mount(core);
    assert.ok(mounted);
  }
});

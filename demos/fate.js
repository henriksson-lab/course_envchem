/* Week 4: parent mass in a closed water-solid system with rapid partitioning.
   First-order parent transformation has the same coefficient in both phases. */
(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (typeof document !== 'undefined') {
    const start = function () { api.mount(root.EnvChemDemoCore); };
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, { once: true });
    else start();
  }
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const INITIAL_PARENT_MG = 1;
  const WATER_VOLUME_L = 1;
  const DRY_SOLID_KG = 0.01;

  function model(values) {
    const kd = Number(values.kdLKg);
    const halfLife = Number(values.halfLifeDays);
    const time = Number(values.timeDays);
    if (!Number.isFinite(kd) || kd < 0 || !Number.isFinite(halfLife) || halfLife <= 0 ||
        !Number.isFinite(time) || time < 0) {
      throw new RangeError('Use nonnegative Kd and time, and a positive half-life.');
    }
    const kPerDay = Math.LN2 / halfLife;
    const remainingFraction = Math.exp(-kPerDay * time);
    const totalParentMg = INITIAL_PARENT_MG * remainingFraction;
    const waterMgL = totalParentMg / (WATER_VOLUME_L + kd * DRY_SOLID_KG);
    const waterParentMg = waterMgL * WATER_VOLUME_L;
    const solidParentMg = totalParentMg - waterParentMg;
    const transformedParentMg = INITIAL_PARENT_MG - totalParentMg;
    return { kdLKg: kd, halfLifeDays: halfLife, timeDays: time, kPerDay, remainingFraction,
      totalParentMg, waterMgL, waterParentMg, solidParentMg, transformedParentMg,
      solidMgKg: kd * waterMgL,
      waterFractionOfParent: WATER_VOLUME_L / (WATER_VOLUME_L + kd * DRY_SOLID_KG) };
  }

  function fixed(value) {
    if (value === 0) return '0';
    if (Math.abs(value) < 0.0001) return value.toExponential(3);
    return Number(value.toPrecision(4)).toString();
  }

  function mount(core) {
    if (!core) return;
    core.mount('fate', {
      controls: [
        { key: 'kdLKg', label: 'Water–solid distribution coefficient Kd', min: 0, max: 300, step: 1, value: 100, unit: 'L/kg' },
        { key: 'halfLifeDays', label: 'Parent transformation half-life', min: 1, max: 60, step: 1, value: 10, unit: 'days' },
        { key: 'timeDays', label: 'Inspect time', min: 0, max: 60, step: 1, value: 20, unit: 'days' }
      ],
      presets: [
        { label: 'U at day 20', values: { kdLKg: 100, halfLifeDays: 10, timeDays: 20 } },
        { label: 'U at day 30', values: { kdLKg: 100, halfLifeDays: 10, timeDays: 30 } },
        { label: 'V at day 30', values: { kdLKg: 10, halfLifeDays: 30, timeDays: 30 } },
        { label: 'No sorption at time zero', values: { kdLKg: 0, halfLifeDays: 10, timeDays: 0 } }
      ],
      update: function (values, view) {
        const result = model(values);
        const water = [];
        const solid = [];
        const transformed = [];
        for (let day = 0; day <= 60; day += 1) {
          const state = model({ kdLKg: values.kdLKg, halfLifeDays: values.halfLifeDays, timeDays: day });
          water.push({ x: day, y: state.waterParentMg });
          solid.push({ x: day, y: state.solidParentMg });
          transformed.push({ x: day, y: state.transformedParentMg });
        }
        core.lineChart(view.chart, {
          title: 'Where is the initial 1 mg of parent accounted for?',
          xLabel: 'Time (days)', yLabel: 'Initial-parent accounting (mg)',
          xMin: 0, xMax: 60, yMin: 0, yMax: 1,
          series: [
            { label: 'Parent in water', points: water, color: '#2468a0' },
            { label: 'Parent on solid', points: solid, color: '#28733f' },
            { label: 'Transformed parent equivalent', points: transformed, color: '#a74329' }
          ],
          markers: [{ x: result.timeDays, label: 'Selected time' }]
        });
        core.metrics(view.results, [
          { label: 'Total parent remaining', value: fixed(result.totalParentMg), unit: 'mg' },
          { label: 'Parent in water', value: fixed(result.waterParentMg), unit: 'mg' },
          { label: 'Parent on solid', value: fixed(result.solidParentMg), unit: 'mg' },
          { label: 'Transformed-parent equivalent', value: fixed(result.transformedParentMg), unit: 'mg of initial parent' },
          { label: 'Water parent concentration', value: fixed(result.waterMgL), unit: 'mg/L' },
          { label: 'Accounted initial parent', value: fixed(result.waterParentMg + result.solidParentMg + result.transformedParentMg), unit: 'mg' }
        ]);
        view.explanation.textContent = 'This model starts with 1.00 mg parent distributed between 1.00 L water and 0.0100 kg dry solid. ' +
          'Partitioning is rapid and Kd is fixed. Both phases transform parent at the same k = ln(2) / half-life, so total parent follows one exponential. ' +
          'At the selected time, ' + fixed(100 * result.remainingFraction) + '% of parent remains; ' +
          fixed(100 * result.waterFractionOfParent) + '% of that remaining parent is in water. ' +
          'Changing Kd changes the phase split but not this model’s total-parent half-life. ' +
          'The transformed-parent term closes the initial-parent accounting; it is not a measured product mass, proof of mineralisation, or a toxicity prediction. ' +
          'There is no gas transfer, inflow, outflow, or new input. Slower exchange or transformation confined to water would require another kinetic model.';
      }
    });
  }
  return { model: model, mount: mount,
    constants: { initialParentMg: INITIAL_PARENT_MG, waterVolumeL: WATER_VOLUME_L, drySolidKg: DRY_SOLID_KG } };
});

/* Week 3: a one-complex binding model and a free-ion saturation check.
   Dependency-free; works in a browser or as a CommonJS module for model checks. */
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
  const BETA_L_MOL = 1e6;
  const KSP = 1e-16;
  const KW = 1e-14;

  function model(values) {
    const total = Number(values.totalUmolL);
    const ligand = Number(values.freeLigandUmolL);
    const pH = Number(values.pH);
    if (!Number.isFinite(total) || total < 0 || !Number.isFinite(ligand) || ligand < 0 ||
        !Number.isFinite(pH) || pH < 0 || pH > 14) {
      throw new RangeError('Use nonnegative total metal and free ligand, and pH from 0 to 14.');
    }
    const ligandMolL = ligand * 1e-6;
    const freeUmolL = total / (1 + BETA_L_MOL * ligandMolL);
    const complexedUmolL = total - freeUmolL;
    const hydrogenMolL = Math.pow(10, -pH);
    const hydroxideMolL = KW / hydrogenMolL;
    const ionProduct = freeUmolL * 1e-6 * hydroxideMolL * hydroxideMolL;
    const saturationRatio = ionProduct / KSP;
    const saturatedFreeUmolL = KSP / (hydroxideMolL * hydroxideMolL) * 1e6;
    const saturationState = Math.abs(saturationRatio - 1) <= 1e-10 ? 'saturated' :
      saturationRatio > 1 ? 'supersaturated' : 'undersaturated';
    return { totalUmolL: total, freeLigandUmolL: ligand, pH, freeUmolL, complexedUmolL,
      hydroxideMolL, ionProduct, saturationRatio, saturatedFreeUmolL, saturationState,
      freeFraction: total === 0 ? null : freeUmolL / total };
  }

  function fixed(value) {
    if (value === 0) return '0';
    if (Math.abs(value) < 0.0001 || Math.abs(value) >= 10000) return value.toExponential(3);
    return Number(value.toPrecision(4)).toString();
  }

  function mount(core) {
    if (!core) return;
    core.mount('metals', {
      controls: [
        { key: 'totalUmolL', label: 'Dissolved total metal', min: 0, max: 20, step: 0.1, value: 2, unit: 'µmol/L' },
        { key: 'freeLigandUmolL', label: 'Prescribed free ligand', min: 0, max: 30, step: 0.1, value: 10, unit: 'µmol/L' },
        { key: 'pH', label: 'Prescribed pH', min: 6, max: 10, step: 0.05, value: 8, unit: '' }
      ],
      presets: [
        { label: 'Worked binding case', values: { totalUmolL: 2, freeLigandUmolL: 10, pH: 8 } },
        { label: 'Exactly saturated', values: { totalUmolL: 10, freeLigandUmolL: 9, pH: 9 } },
        { label: 'Same total, no ligand', values: { totalUmolL: 10, freeLigandUmolL: 0, pH: 9 } }
      ],
      update: function (values, view) {
        const result = model(values);
        const free = [];
        const bound = [];
        for (let ligand = 0; ligand <= 30; ligand += 0.25) {
          const state = model({ totalUmolL: values.totalUmolL, freeLigandUmolL: ligand, pH: values.pH });
          free.push({ x: ligand, y: state.freeUmolL });
          bound.push({ x: ligand, y: state.complexedUmolL });
        }
        const maximum = Math.max(1, result.totalUmolL * 1.05);
        const series = [
          { label: 'Free M²⁺', points: free, color: '#2468a0' },
          { label: 'Complex ML', points: bound, color: '#28733f' }
        ];
        if (result.saturatedFreeUmolL <= maximum) {
          series.push({ label: 'Saturated free M²⁺ at this pH', color: '#a74329', points: [
            { x: 0, y: result.saturatedFreeUmolL }, { x: 30, y: result.saturatedFreeUmolL }
          ] });
        }
        core.lineChart(view.chart, {
          title: 'Binding-only distributions before any precipitation',
          xLabel: 'Prescribed free ligand (µmol/L)', yLabel: 'Metal concentration (µmol/L)',
          xMin: 0, xMax: 30, yMin: 0, yMax: maximum, series: series,
          markers: [{ x: result.freeLigandUmolL, label: 'Selected free ligand' }]
        });
        core.metrics(view.results, [
          { label: 'Free M²⁺', value: fixed(result.freeUmolL), unit: 'µmol/L' },
          { label: 'Complexed ML', value: fixed(result.complexedUmolL), unit: 'µmol/L' },
          { label: 'Free + complexed', value: fixed(result.freeUmolL + result.complexedUmolL), unit: 'µmol/L' },
          { label: 'Saturation ratio Ω', value: fixed(result.saturationRatio), unit: result.saturationState },
          { label: 'Saturated free M²⁺', value: fixed(result.saturatedFreeUmolL), unit: 'µmol/L' }
        ]);
        const outcome = result.saturationState === 'supersaturated' ?
          'This hypothetical binding-only state is supersaturated: precipitation is thermodynamically favoured, but its final amount and rate are not calculated.' :
          result.saturationState === 'saturated' ?
            'The free-ion product equals the stipulated solubility product. This identifies saturation, not a precipitation rate.' :
            'The solution is undersaturated with respect to this fictitious hydroxide; an available solid could dissolve. No mineral reaction is simulated.';
        const threshold = result.saturatedFreeUmolL > maximum ?
          ' The free-ion saturation threshold is above the plotted concentration range.' : '';
        view.explanation.textContent = 'At 25 °C in dilute water, free M = total M / (1 + β[L]free), with β = 10⁶ L/mol. ' +
          'The ligand slider fixes FREE ligand, maintained by an external ligand reservoir; it is not total ligand. ' +
          'pH fixes hydroxide for Ω = [M²⁺][OH⁻]² / 10⁻¹⁶. ' + outcome + threshold +
          ' Binding and mineral reactions do not change metal oxidation state here. Other hydrolysis products, competing ligands, and biological effects are omitted.';
      }
    });
  }
  return { model: model, mount: mount, constants: { betaLMol: BETA_L_MOL, ksp: KSP, kw: KW } };
});

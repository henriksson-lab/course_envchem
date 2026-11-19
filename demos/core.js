/* Shared, dependency-free controls and SVG charts for the course demos. */
(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.EnvChemDemoCore = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  let sequence = 0;
  const colours = ['#2468a0', '#24743c', '#af481c', '#7c4296'];
  const NS = 'http://www.w3.org/2000/svg';
  function element(tag, text, cls) {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = String(text);
    if (cls) node.className = cls;
    return node;
  }
  function svgElement(tag, attrs, text) {
    const node = document.createElementNS(NS, tag);
    for (const [key, value] of Object.entries(attrs || {})) node.setAttribute(key, String(value));
    if (text !== undefined) node.textContent = String(text);
    return node;
  }
  function number(value) {
    if (typeof value !== 'number') return String(value);
    if (!Number.isFinite(value)) return 'Outside model range';
    if (value === 0) return '0';
    const absolute = Math.abs(value);
    if (absolute >= 1e6 || absolute < 0.001) return value.toExponential(2);
    return new Intl.NumberFormat('en-GB', { maximumSignificantDigits: 4 }).format(value);
  }
  function constrain(value, control) {
    const numeric = Number(value);
    if (!Number.isFinite(numeric)) throw new Error('A finite control value is required.');
    const bounded = Math.max(control.min, Math.min(control.max, numeric));
    return Number((control.min + Math.round((bounded - control.min) / control.step) * control.step).toPrecision(12));
  }
  function metrics(target, items) {
    const list = element('dl', undefined, 'chem-demo-metrics');
    for (const item of items) {
      const block = element('div');
      block.append(element('dt', item.label));
      const value = element('dd', number(item.value));
      if (item.unit) value.append(element('span', ' ' + item.unit, 'chem-demo-unit'));
      block.append(value); list.append(block);
    }
    target.replaceChildren(list);
  }
  function table(target, config) {
    const wrapper = element('div', undefined, 'chem-demo-table-wrap');
    const result = element('table', undefined, 'chem-demo-table');
    result.append(element('caption', config.caption || 'Calculated model values'));
    const head = element('thead'); const headRow = element('tr');
    for (const text of config.headers) {
      const cell = element('th', text); cell.scope = 'col'; headRow.append(cell);
    }
    head.append(headRow); result.append(head);
    const body = element('tbody');
    for (const row of config.rows) {
      const tr = element('tr');
      row.forEach((text, index) => {
        const td = element(index === 0 ? 'th' : 'td', number(text));
        if (index === 0) td.scope = 'row';
        tr.append(td);
      });
      body.append(tr);
    }
    result.append(body); wrapper.append(result); target.replaceChildren(wrapper);
  }
  function titleLines(text, width) {
    const limit = Math.floor((width-32)/10);
    const lines = [''];
    String(text).split(/\s+/).forEach(word=>{
      const last=lines.length-1;
      if (lines[last] && lines[last].length+word.length+1>limit) lines.push(word);
      else lines[last]+=(lines[last]?' ':'')+word;
    });
    return lines;
  }
  function chartTitle(svg, lines, x) {
    const title=svgElement('text',{x,y:24,class:'chem-chart-title'});
    lines.forEach((line,index)=>title.append(svgElement('tspan',{x,dy:index?24:0},line)));
    svg.append(title);
  }
  function chartRoot(target, title, width, height, description) {
    const id = 'chem-chart-' + (++sequence);
    const svg = svgElement('svg', {viewBox: `0 0 ${width} ${height}`, role: 'img',
      'aria-labelledby': id + '-title ' + id + '-desc', class: 'chem-demo-svg'});
    svg.append(svgElement('title', {id: id + '-title'}, title));
    svg.append(svgElement('desc', {id: id + '-desc'}, description));
    target.replaceChildren(svg);
    return svg;
  }
  function lineChart(target, config) {
    const width = 760;
    const lines=titleLines(config.title,width-70), offset=(lines.length-1)*24;
    const height=370+offset;
    const margin = {left: 83, right: 30, top: 48+offset, bottom: 74};
    const pw = width-margin.left-margin.right, ph = height-margin.top-margin.bottom;
    const all = config.series.flatMap(series => series.points);
    const finite = all.filter(p => Number.isFinite(p.x) && Number.isFinite(p.y));
    if (!finite.length) { target.replaceChildren(element('p', 'No finite model values to plot.')); return; }
    let xmin = config.xMin ?? Math.min(...finite.map(p => p.x));
    let xmax = config.xMax ?? Math.max(...finite.map(p => p.x));
    let ymin = config.yMin ?? Math.min(0,...finite.map(p => p.y));
    let ymax = config.yMax ?? Math.max(...finite.map(p => p.y));
    if (xmax <= xmin) xmax = xmin+1;
    if (ymax <= ymin) ymax = ymin+1;
    const x = value => margin.left+(value-xmin)/(xmax-xmin)*pw;
    const y = value => margin.top+ph-(value-ymin)/(ymax-ymin)*ph;
    const svg = chartRoot(target, config.title, width, height,
      `${config.xLabel}; ${config.yLabel}. Series: ${config.series.map(s=>s.label).join(', ')}. ` +
      'Current calculated values and interpretation accompany the plot.');
    chartTitle(svg,lines,margin.left);
    for (let i=0;i<=4;i++) {
      const vx=xmin+(xmax-xmin)*i/4, vy=ymin+(ymax-ymin)*i/4;
      svg.append(svgElement('line',{x1:margin.left,y1:y(vy),x2:width-margin.right,y2:y(vy),class:'chem-grid'}));
      svg.append(svgElement('text',{x:margin.left-12,y:y(vy)+6,'text-anchor':'end'},number(vy)));
      svg.append(svgElement('text',{x:x(vx),y:height-margin.bottom+27,'text-anchor':'middle'},number(vx)));
    }
    svg.append(svgElement('path',{d:`M${margin.left} ${margin.top}V${height-margin.bottom}H${width-margin.right}`,class:'chem-axis'}));
    config.series.forEach((series,index) => {
      const colour=series.color || colours[index%colours.length];
      let path='', active=false;
      for (const point of series.points) {
        if (!Number.isFinite(point.x)||!Number.isFinite(point.y)) {active=false;continue;}
        path+=(active?'L':'M')+x(Math.max(xmin,Math.min(xmax,point.x))).toFixed(2)+' '+
          y(Math.max(ymin,Math.min(ymax,point.y))).toFixed(2)+' ';
        active=true;
      }
      svg.append(svgElement('path',{d:path,fill:'none',stroke:colour,'stroke-width':3,
        'stroke-dasharray':index%3===1?'9 5':index%3===2?'3 5':'none'}));
    });
    (config.markers||[]).forEach((marker,index)=>{
      if (!Number.isFinite(marker.x)||marker.x<xmin||marker.x>xmax) return;
      svg.append(svgElement('line',{x1:x(marker.x),x2:x(marker.x),y1:margin.top,y2:height-margin.bottom,
        stroke:'#333','stroke-width':1.5,'stroke-dasharray':index%2?'3 4':'7 4'}));
      svg.append(svgElement('text',{x:x(marker.x),y:margin.top+18+index*23,
        'text-anchor':marker.x>(xmin+xmax)/2?'end':'start',class:'chem-marker-label'},marker.label));
    });
    svg.append(svgElement('text',{x:margin.left+pw/2,y:height-17,'text-anchor':'middle'},config.xLabel));
    svg.append(svgElement('text',{transform:`translate(22 ${margin.top+ph/2}) rotate(-90)`,
      'text-anchor':'middle'},config.yLabel));
    const legend=element('ul',undefined,'chem-demo-legend');
    config.series.forEach((series,index)=>{
      const li=element('li'); const swatch=element('span',undefined,'chem-demo-swatch');
      swatch.style.borderColor=series.color||colours[index%colours.length];
      swatch.style.borderTopStyle=index%3===1?'dashed':index%3===2?'dotted':'solid';
      li.append(swatch,element('span',series.label));legend.append(li);
    });
    target.append(legend);
  }
  function barChart(target, config) {
    const width=760, lines=titleLines(config.title,760), offset=(lines.length-1)*24;
    const height=82+offset+config.bars.length*68;
    const min=Math.min(0,...config.bars.map(b=>b.value));
    const max=Math.max(config.max||0,...config.bars.map(b=>b.value),0);
    const span=max-min||1, left=245, right=590, x=v=>left+(v-min)/span*(right-left);
    const svg=chartRoot(target,config.title,width,height,
      config.bars.map(b=>`${b.label}: ${number(b.value)} ${config.unit}`).join('; '));
    chartTitle(svg,lines,16);
    config.bars.forEach((bar,index)=>{
      const cy=65+offset+index*68;
      const labels=titleLines(bar.label,272);
      const label=svgElement('text',{x:16,y:cy+(labels.length>1?7:19)});
      labels.forEach((text,i)=>label.append(svgElement('tspan',{x:16,dy:i?22:0},text)));
      svg.append(label);
      svg.append(svgElement('line',{x1:left,x2:right,y1:cy+14,y2:cy+14,class:'chem-grid'}));
      svg.append(svgElement('rect',{x:Math.min(x(0),x(bar.value)),y:cy,
        width:Math.abs(x(bar.value)-x(0)),height:28,fill:bar.color||colours[index%colours.length],rx:3}));
      svg.append(svgElement('text',{x:right+14,y:cy+20},number(bar.value)+' '+config.unit));
    });
    svg.append(svgElement('line',{x1:x(0),x2:x(0),y1:52+offset,y2:height-24,class:'chem-axis'}));
  }
  function mount(name, config) {
    if (typeof document==='undefined') return;
    document.querySelectorAll('[data-demo="'+name+'"]').forEach(root=>{
      if (root.dataset.demoMounted) return;
      root.dataset.demoMounted='true';
      root.classList.add('chem-demo');
      const instance='chem-demo-'+(++sequence);
      const defaults=Object.fromEntries(config.controls.map(c=>[c.key,constrain(c.value,c)]));
      let values={...defaults}; const inputs={}; const outputs={};
      const layout=element('div',undefined,'chem-demo-layout');
      const fieldset=element('fieldset',undefined,'chem-demo-controls');
      fieldset.append(element('legend','Change the chemical conditions'));
      for (const control of config.controls) {
        const wrapper=element('div',undefined,'chem-demo-control');
        const label=element('label',control.label);label.htmlFor=instance+'-'+control.key;
        const output=element('output');output.htmlFor=label.htmlFor;
        const input=element('input');input.type='range';input.id=label.htmlFor;
        input.min=control.min;input.max=control.max;input.step=control.step;
        input.setAttribute('aria-describedby',instance+'-'+control.key+'-value');
        output.id=instance+'-'+control.key+'-value';
        input.addEventListener('input',()=>{values[control.key]=constrain(input.value,control);refresh();});
        inputs[control.key]=input;outputs[control.key]=output;
        wrapper.append(label,output,input);fieldset.append(wrapper);
      }
      const panel=element('div',undefined,'chem-demo-panel');
      const view={chart:element('div',undefined,'chem-demo-chart'),
        results:element('div',undefined,'chem-demo-results'),
        explanation:element('p',undefined,'chem-demo-explanation')};
      view.explanation.setAttribute('aria-live','polite');view.explanation.setAttribute('aria-atomic','true');
      panel.append(view.chart,view.results,view.explanation);layout.append(fieldset,panel);
      const actions=element('div',undefined,'chem-demo-actions');
      function button(label,action){const b=element('button',label);b.type='button';b.addEventListener('click',action);actions.append(b);}
      button('Reset',()=>{values={...defaults};refresh();});
      for (const preset of config.presets||[]) button(preset.label,()=>{
        values={...defaults};
        for (const control of config.controls) if (preset.values[control.key]!==undefined)
          values[control.key]=constrain(preset.values[control.key],control);
        refresh();
      });
      function refresh(){
        for(const control of config.controls){
          inputs[control.key].value=values[control.key];
          const value=(control.format?control.format(values[control.key]):number(values[control.key]));
          outputs[control.key].textContent=value+(control.unit?' '+control.unit:'');
          inputs[control.key].setAttribute('aria-valuetext',outputs[control.key].textContent);
        }
        try{config.update({...values},view);delete root.dataset.demoError;}
        catch(error){
          root.dataset.demoError='true';
          view.explanation.textContent='This input combination is outside the model range. Reset to the reference case.';
          console.error('Demo '+name+':',error);
        }
      }
      root.replaceChildren(actions,layout);refresh();
    });
  }
  return {mount,metrics,table,lineChart,barChart,number,constrain};
});

"""JavaScript para el dashboard ejecutivo PGMB - Vista comparativa Comp vs WM."""


def get_js():
    return r"""
// ======================================================
// HELPERS
// ======================================================
function filterData(data) {
  const pais = document.getElementById('fil-pais').value;
  const div  = document.getElementById('fil-div').value;
  const cat  = document.getElementById('fil-cat').value;
  return data.filter(r =>
    (!pais || r.PAIS === pais) &&
    (!div  || r.DIVISION === div) &&
    (!cat  || r.CATEGORIA === cat)
  );
}
function resetFilters() {
  ['fil-pais','fil-div','fil-cat'].forEach(id => document.getElementById(id).value = '');
  renderAll();
}
function aggSegmentos(data) {
  const t = {Bajo:0, Subio:0, Mantiene:0, Nuevo:0};
  data.forEach(r => { t.Bajo+=r.Bajo; t.Subio+=r.Subio; t.Mantiene+=r.Mantiene; t.Nuevo+=r.Nuevo; });
  return t;
}
function aggByKey(data, key) {
  const m = {};
  data.forEach(r => {
    const k = r[key];
    if (!m[k]) m[k] = {Bajo:0,Subio:0,Mantiene:0,Nuevo:0};
    m[k].Bajo     += r.Bajo;
    m[k].Subio    += r.Subio;
    m[k].Mantiene += r.Mantiene;
    m[k].Nuevo    += r.Nuevo;
  });
  return m;
}

// ======================================================
// ANIMATED COUNTER
// ======================================================
function animateCounter(el, target) {
  let cur = 0;
  const step = Math.ceil(target / 50);
  const t = setInterval(() => {
    cur = Math.min(cur + step, target);
    el.textContent = cur.toLocaleString();
    if (cur >= target) clearInterval(t);
  }, 18);
}
function initCounters() {
  document.querySelectorAll('[data-count]').forEach(el =>
    animateCounter(el, parseInt(el.dataset.count))
  );
}

// ======================================================
// TAB SWITCHING
// ======================================================
function switchTab(name, btn) {
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-tab').forEach(b => b.classList.remove('active'));
  document.getElementById('panel-' + name).classList.add('active');
  btn.classList.add('active');
  if (name === 'overview')  renderOverview();
  if (name === 'pais')      renderByPais();
  if (name === 'division')  renderByDivision();
  if (name === 'detalle')   renderDetalle();
  if (name === 'gap')       renderGap();
  if (name === 'outliers')  renderOutliers();
}

// ======================================================
// CHART REGISTRY
// ======================================================
const _charts = {};
function mkChart(id, cfg) {
  if (_charts[id]) _charts[id].destroy();
  const c = document.getElementById(id);
  if (!c) return;
  _charts[id] = new Chart(c, cfg);
}

// ======================================================
// COLORS
// ======================================================
const C_BAJO     = '#2a8703';
const C_SUBIO    = '#ea1100';
const C_MANTIENE = '#4a5568';
const C_NUEVO    = '#e6a800';
const C_COMP_ALPHA = (hex, a) => hex + Math.round(a*255).toString(16).padStart(2,'0');

// ======================================================
// 1. DONUT PAIR (Comp + WM)
// ======================================================
function renderDonutPair(compData, wmData) {
  const segs = ['Baj\u00f3', 'Subi\u00f3', 'Mantiene', 'Nuevo'];
  const colors = [C_BAJO, C_SUBIO, C_MANTIENE, C_NUEVO];
  function donut(id, d, title) {
    const t = aggSegmentos(d);
    mkChart(id, {
      type:'doughnut',
      data:{
        labels: segs,
        datasets:[{data:[t.Bajo,t.Subio,t.Mantiene,t.Nuevo],
          backgroundColor:colors, borderWidth:3, borderColor:'#fff'}]
      },
      options:{
        responsive:true, maintainAspectRatio:false, cutout:'62%',
        plugins:{
          legend:{position:'bottom', labels:{padding:14,font:{size:12}}},
          title:{display:true, text:title, font:{size:14,weight:'bold'}, color:'#1d2633', padding:{bottom:8}}
        }
      }
    });
  }
  donut('donut-comp', compData, '\uD83C\uDFAF Competidor \u2014 precio_comp_low');
  donut('donut-wm',   wmData,   '\uD83C\uDFAF Walmart \u2014 precio_wm_low');
}

// ======================================================
// 2. GROUPED COMPARISON BAR (Comp vs WM por segmento)
// ======================================================
function renderGroupedCompBar(compData, wmData, canvasId, groupKey, title) {
  const cByKey = aggByKey(compData, groupKey);
  const wByKey = aggByKey(wmData,   groupKey);
  const labels = [...new Set([...Object.keys(cByKey), ...Object.keys(wByKey)])].sort();
  const segs = [
    {name:'Baj\u00f3',     key:'Bajo',     cColor:'rgba(42,135,3,0.9)',   wColor:'rgba(42,135,3,0.45)'},
    {name:'Subi\u00f3',    key:'Subio',    cColor:'rgba(234,17,0,0.9)',   wColor:'rgba(234,17,0,0.45)'},
    {name:'Mantiene', key:'Mantiene', cColor:'rgba(74,85,104,0.9)', wColor:'rgba(74,85,104,0.45)'},
    {name:'Nuevo',    key:'Nuevo',    cColor:'rgba(230,168,0,0.9)', wColor:'rgba(230,168,0,0.45)'},
  ];
  const datasets = [];
  segs.forEach(s => {
    datasets.push({
      label: s.name + ' (Comp)',
      data: labels.map(l => (cByKey[l] ? cByKey[l][s.key] : 0)),
      backgroundColor: s.cColor,
      borderRadius: 4,
      stack: 'comp',
    });
    datasets.push({
      label: s.name + ' (WM)',
      data: labels.map(l => (wByKey[l] ? wByKey[l][s.key] : 0)),
      backgroundColor: s.wColor,
      borderRadius: 4,
      borderDash: [4,2],
      stack: 'wm',
    });
  });
  mkChart(canvasId, {
    type:'bar',
    data:{labels, datasets},
    options:{
      responsive:true, maintainAspectRatio:false,
      plugins:{
        legend:{display:false},
        title:{display:true, text:title, font:{size:13,weight:'bold'}, color:'#1d2633'}
      },
      scales:{
        x:{grid:{display:false}, ticks:{font:{size:11}}},
        y:{ticks:{callback:v=>v.toLocaleString()}, grid:{color:'#f0f0f0'}}
      }
    }
  });
}

// ======================================================
// 3. SEGMENT COMPARISON: Grouped by segment, Comp vs WM
// ======================================================
function renderSegmentComparison(compData, wmData, canvasId, title) {
  const cTot = aggSegmentos(compData);
  const wTot = aggSegmentos(wmData);
  const labels = ['Baj\u00f3','Subi\u00f3','Mantiene','Nuevo'];
  const cVals  = [cTot.Bajo, cTot.Subio, cTot.Mantiene, cTot.Nuevo];
  const wVals  = [wTot.Bajo, wTot.Subio, wTot.Mantiene, wTot.Nuevo];
  const bgColors = [C_BAJO, C_SUBIO, C_MANTIENE, C_NUEVO];
  mkChart(canvasId, {
    type:'bar',
    data:{
      labels,
      datasets:[
        {label:'Competidor', data:cVals,
          backgroundColor: bgColors.map(c=>c+'dd'), borderRadius:6},
        {label:'Walmart',    data:wVals,
          backgroundColor: bgColors.map(c=>c+'66'), borderRadius:6,
          borderColor: bgColors, borderWidth:2},
      ]
    },
    options:{
      responsive:true, maintainAspectRatio:false,
      plugins:{
        legend:{position:'top', labels:{font:{size:12}}},
        title:{display:true, text:title, font:{size:13,weight:'bold'}, color:'#1d2633'}
      },
      scales:{
        x:{grid:{display:false}},
        y:{ticks:{callback:v=>v.toLocaleString()}, grid:{color:'#f0f0f0'}}
      }
    }
  });
}

// ======================================================
// 4. COUNTRY SCORECARDS (Comp vs WM juntos)
// ======================================================
function renderCountryCards(compData, wmData, containerId) {
  const cByP = aggByKey(compData, 'PAIS');
  const wByP = aggByKey(wmData,   'PAIS');
  const flags = {CR:'\uD83C\uDDE8\uD83C\uDDF7',GT:'\uD83C\uDDEC\uD83C\uDDF9',HN:'\uD83C\uDDED\uD83C\uDDF3',NI:'\uD83C\uDDF3\uD83C\uDDEE',SV:'\uD83C\uDDF8\uD83C\uDDFB'};
  const paises = [...new Set([...Object.keys(cByP),...Object.keys(wByP)])].sort();
  const el = document.getElementById(containerId);
  el.innerHTML = '';
  paises.forEach(p => {
    const c = cByP[p] || {Bajo:0,Subio:0,Mantiene:0,Nuevo:0};
    const w = wByP[p] || {Bajo:0,Subio:0,Mantiene:0,Nuevo:0};
    const cT = c.Bajo+c.Subio+c.Mantiene+c.Nuevo || 1;
    const wT = w.Bajo+w.Subio+w.Mantiene+w.Nuevo || 1;
    el.innerHTML += `
      <div class="country-card">
        <div class="country-name">${flags[p]||''} ${p}</div>
        <div class="cc-row-head"><span></span><span class="cc-head-comp">Comp</span><span class="cc-head-wm">WM</span></div>
        <div class="cc-row">
          <span class="cc-lbl">Baj\u00f3</span>
          <span class="cs-bajo">${c.Bajo.toLocaleString()}<small> ${(c.Bajo/cT*100).toFixed(1)}%</small></span>
          <span class="cs-bajo">${w.Bajo.toLocaleString()}<small> ${(w.Bajo/wT*100).toFixed(1)}%</small></span>
        </div>
        <div class="cc-row">
          <span class="cc-lbl">Subi\u00f3</span>
          <span class="cs-subio">${c.Subio.toLocaleString()}<small> ${(c.Subio/cT*100).toFixed(1)}%</small></span>
          <span class="cs-subio">${w.Subio.toLocaleString()}<small> ${(w.Subio/wT*100).toFixed(1)}%</small></span>
        </div>
        <div class="cc-row">
          <span class="cc-lbl">Mantiene</span>
          <span>${c.Mantiene.toLocaleString()}<small> ${(c.Mantiene/cT*100).toFixed(1)}%</small></span>
          <span>${w.Mantiene.toLocaleString()}<small> ${(w.Mantiene/wT*100).toFixed(1)}%</small></span>
        </div>
        <div class="cc-row">
          <span class="cc-lbl">Nuevo</span>
          <span class="cs-spark">${c.Nuevo.toLocaleString()}</span>
          <span class="cs-spark">${w.Nuevo.toLocaleString()}</span>
        </div>
      </div>`;
  });
}

// ======================================================
// 5. TABLE RENDERER
// ======================================================
let sortStates = {};
function renderSegTable(tbodyId, tblId, data, tipo) {
  const tbody = document.getElementById(tbodyId);
  tbody.innerHTML = '';
  data.forEach(r => {
    const tot = r.Total || 1;
    const pB = (r.Bajo/tot*100).toFixed(1);
    const pS = (r.Subio/tot*100).toFixed(1);
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${r.PAIS}</td><td>${r.DIVISION}</td><td>${r.CATEGORIA}</td>
      <td class="num"><span class="badge badge-bajo">${r.Bajo.toLocaleString()}</span></td>
      <td class="num"><span class="badge badge-subio">${r.Subio.toLocaleString()}</span></td>
      <td class="num"><span class="badge badge-mant">${r.Mantiene.toLocaleString()}</span></td>
      <td class="num"><span class="badge badge-nuevo">${r.Nuevo.toLocaleString()}</span></td>
      <td class="num fw">${r.Total.toLocaleString()}</td>
      <td class="num ${parseFloat(pB)>parseFloat(pS)?'pos':'neg'}">${pB}%</td>
      <td class="num ${parseFloat(pS)>parseFloat(pB)?'neg':'pos'}">${pS}%</td>`;
    tbody.appendChild(tr);
  });
}
function sortTable(tblId, col) {
  const key = tblId+col;
  sortStates[key] = !sortStates[key];
  const tbody = document.querySelector('#'+tblId+' tbody');
  const rows = Array.from(tbody.rows);
  rows.sort((a,b)=>{
    const av=a.cells[col].innerText.replace(/[,%\s]/g,''), bv=b.cells[col].innerText.replace(/[,%\s]/g,'');
    const an=parseFloat(av), bn=parseFloat(bv);
    return !isNaN(an)&&!isNaN(bn) ? (sortStates[key]?an-bn:bn-an) : (sortStates[key]?av.localeCompare(bv):bv.localeCompare(av));
  });
  rows.forEach(r=>tbody.appendChild(r));
}

// ======================================================
// 6. PRICE GAP
// ======================================================
function renderGapChart(data) {
  // Sort by pg ASC (worst first), take top 25
  const sorted = [...data].filter(r => r.pg !== null && r.pg !== undefined)
    .sort((a,b) => a.pg - b.pg).slice(0, 25);
  if (sorted.length === 0) {
    const c = document.getElementById('bar-gap');
    if (c) { const ctx=c.getContext('2d'); ctx.clearRect(0,0,c.width,c.height);
      ctx.font='14px Segoe UI'; ctx.fillStyle='#888';
      ctx.fillText('Sin datos con Peso_calc > 0 para los filtros seleccionados', 20, 50); }
    return;
  }
  const labels = sorted.map(r => `${r.PAIS} | ${r.CATEGORIA.length>28 ? r.CATEGORIA.substr(0,26)+'..' : r.CATEGORIA}`);
  // Convert to percentage
  const pgPct = sorted.map(r => parseFloat((r.pg * 100).toFixed(2)));
  mkChart('bar-gap', {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'PG % = SUM(Factor_calc) / SUM(Peso_calc)',
        data: pgPct,
        backgroundColor: pgPct.map(v => v < 0 ? 'rgba(234,17,0,.85)' : 'rgba(42,135,3,.85)'),
        borderRadius: 4,
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        title: {
          display: true,
          text: 'Top 25 Categor\u00edas \u2014 % PG = SUM(Factor_calc) / SUM(Peso_calc) \u2014 SW8 2026',
          font: { size: 13, weight: 'bold' }
        },
        tooltip: {
          callbacks: {
            label: ctx => ` PG: ${ctx.raw.toFixed(2)}%  |  ${ctx.raw < 0 ? 'WM m\u00e1s caro' : 'WM m\u00e1s barato'}`
          }
        }
      },
      scales: {
        x: {
          ticks: { callback: v => v.toFixed(1) + '%' },
          grid: { color: '#f0f0f0' }
        },
        y: { ticks: { font: { size: 10 } }, grid: { display: false } }
      }
    }
  });
}
function renderGapTable(data) {
  const tbody = document.getElementById('tbody-gap');
  tbody.innerHTML = '';
  if (!data || data.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:20px;color:#888">Sin datos para los filtros seleccionados</td></tr>';
    return;
  }
  data.forEach(r => {
    const pgPct = (r.pg * 100).toFixed(2);
    const cls = r.pg < 0 ? 'neg' : (r.pg > 0 ? 'pos' : '');
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${r.PAIS}</td>
      <td>${r.DIVISION}</td>
      <td>${r.CATEGORIA}</td>
      <td class="num">${r.total_items.toLocaleString()}</td>
      <td class="num">${r.sum_factor_calc.toFixed(6)}</td>
      <td class="num">${r.sum_peso_calc.toFixed(6)}</td>
      <td class="num ${cls} fw">${pgPct}%</td>
      <td class="num">${(r.avg_price_gap * 100).toFixed(2)}%</td>`;
    tbody.appendChild(tr);
  });
}

// ======================================================
// RENDER PANELS
// ======================================================
function renderOverview() {
  const c = filterData(DATA_COMP), w = filterData(DATA_WM);
  renderDonutPair(c, w);
  renderSegmentComparison(c, w, 'bar-seg-compare', 'Comp vs WM \u2014 Total de Cambios por Segmento (SW7 \u2192 SW8)');
  renderGroupedCompBar(c, w, 'bar-pais-compare', 'PAIS', 'Comp vs WM por Pa\u00eds \u2014 Desglose por Segmento');
  renderCountryCards(c, w, 'country-cards');
}
function renderByPais() {
  const c = filterData(DATA_COMP), w = filterData(DATA_WM);
  renderGroupedCompBar(c, w, 'bar-comp-pais2', 'PAIS', 'Competidor \u2014 Variaci\u00f3n de Precios por Pa\u00eds');
  renderGroupedCompBar(c, w, 'bar-wm-pais2',   'PAIS', 'Walmart \u2014 Variaci\u00f3n de Precios por Pa\u00eds');
}
function renderByDivision() {
  const c = filterData(DATA_COMP), w = filterData(DATA_WM);
  renderGroupedCompBar(c, w, 'bar-comp-div', 'DIVISION', 'Competidor \u2014 Variaci\u00f3n por Divisi\u00f3n');
  renderGroupedCompBar(c, w, 'bar-wm-div',   'DIVISION', 'Walmart \u2014 Variaci\u00f3n por Divisi\u00f3n');
}
function renderDetalle() {
  const c = filterData(DATA_COMP), w = filterData(DATA_WM);
  renderSegTable('tbody-comp','tbl-comp', c, 'comp');
  renderSegTable('tbody-wm',  'tbl-wm',  w, 'wm');
}
function renderGap() {
  const d = filterData(DATA_GAP);
  renderGapChart(d);
  renderGapTable(d);
}
function renderAll() {
  const activePanel = document.querySelector('.tab-panel.active');
  if (!activePanel) return;
  const name = activePanel.id.replace('panel-','');
  if (name==='overview')  renderOverview();
  if (name==='pais')      renderByPais();
  if (name==='division')  renderByDivision();
  if (name==='detalle')   renderDetalle();
  if (name==='gap')       renderGap();
  if (name==='outliers')  renderOutliers();
}

// ======================================================
// INIT
// ======================================================
(function init() {
  ['fil-pais','fil-div','fil-cat'].forEach(id => {
    const sel = document.getElementById(id);
    const src = id==='fil-pais'?PAISES:(id==='fil-div'?DIVISIONES:CATEGORIAS);
    src.forEach(v => sel.add(new Option(v,v)));
  });
  initCounters();
  renderOverview();
})();
    """

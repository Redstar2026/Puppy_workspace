"""JavaScript para el tab de Outliers de Price Gap."""


def get_js_outliers():
    return r"""
// ======================================================
// OUTLIERS HELPERS
// ======================================================
function filterOutliers(data) {
  const pais = document.getElementById('fil-pais').value;
  const div  = document.getElementById('fil-div').value;
  const cat  = document.getElementById('fil-cat').value;
  return data.filter(r =>
    (!pais || r.PAIS     === pais) &&
    (!div  || r.DIVISION === div)  &&
    (!cat  || r.CATEGORIA === cat)
  );
}

function outlierKpis(data) {
  const neg  = data.filter(r => r.tipo_outlier === 'Outlier Negativo');
  const pos  = data.filter(r => r.tipo_outlier === 'Outlier Positivo');
  const norm = data.filter(r => r.tipo_outlier === 'Normal');
  const tot  = data.length || 1;
  const lb   = data.length > 0 ? data[data.length-1].lower_bound : 0;
  const ub   = data.length > 0 ? data[data.length-1].upper_bound : 0;
  document.getElementById('out-kpi-neg').textContent  = neg.length.toLocaleString();
  document.getElementById('out-kpi-pos').textContent  = pos.length.toLocaleString();
  document.getElementById('out-kpi-norm').textContent = norm.length.toLocaleString();
  document.getElementById('out-kpi-tot').textContent  = tot.toLocaleString();
  document.getElementById('out-pct-neg').textContent  = (neg.length/tot*100).toFixed(1) + '%';
  document.getElementById('out-pct-pos').textContent  = (pos.length/tot*100).toFixed(1) + '%';
  document.getElementById('out-bound-lb').textContent = (lb*100).toFixed(2) + '%';
  document.getElementById('out-bound-ub').textContent = (ub*100).toFixed(2) + '%';
}

// ======================================================
// OUTLIER CHART: Top 30 neg + Top 30 pos
// ======================================================
function renderOutlierChart(data) {
  const neg = [...data].filter(r=>r.tipo_outlier==='Outlier Negativo')
    .sort((a,b)=>a.pg-b.pg).slice(0,30);
  const pos = [...data].filter(r=>r.tipo_outlier==='Outlier Positivo')
    .sort((a,b)=>b.pg-a.pg).slice(0,30);
  const combined = [...neg, ...pos];
  if (combined.length === 0) return;
  const labels = combined.map(r =>
    `${r.PAIS} | ${(r.item_descrip||r.ITEM).substring(0,30)}`
  );
  const values = combined.map(r => parseFloat((r.pg*100).toFixed(2)));
  const colors = combined.map(r => r.pg < 0 ? 'rgba(234,17,0,.85)' : 'rgba(42,135,3,.85)');
  mkChart('chart-outliers', {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: '% PG',
        data: values,
        backgroundColor: colors,
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
          text: 'Outliers de % PG \u2014 Top 30 Negativos + Top 30 Positivos (SW8 2026)',
          font: { size: 13, weight: 'bold' }
        },
        tooltip: {
          callbacks: {
            label: ctx => {
              const r = combined[ctx.dataIndex];
              return [
                ` % PG: ${ctx.raw.toFixed(2)}%`,
                ` Item: ${r.ITEM}`,
                ` Marca: ${r.brand_name}`,
                ` Categoría: ${r.CATEGORIA}`,
              ];
            }
          }
        }
      },
      scales: {
        x: { ticks: { callback: v => v.toFixed(1)+'%' }, grid: { color: '#f0f0f0' } },
        y: { ticks: { font: { size: 9 } }, grid: { display: false } }
      }
    }
  });
}

// ======================================================
// OUTLIER TABLES
// ======================================================
function renderOutlierTable(tbodyId, rows) {
  const tbody = document.getElementById(tbodyId);
  tbody.innerHTML = '';
  if (!rows || rows.length === 0) {
    tbody.innerHTML = '<tr><td colspan="9" style="text-align:center;padding:16px;color:#888">Sin outliers para los filtros seleccionados</td></tr>';
    return;
  }
  rows.forEach((r, i) => {
    const pgPct = (r.pg * 100).toFixed(2);
    const cls   = r.pg < 0 ? 'neg' : 'pos';
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td class="num fw">#${i+1}</td>
      <td>${r.PAIS}</td>
      <td>${r.DIVISION}</td>
      <td>${r.CATEGORIA}</td>
      <td class="num">${r.ITEM}</td>
      <td>${r.item_descrip}</td>
      <td>${r.brand_name}</td>
      <td class="num">${r.total_rows.toLocaleString()}</td>
      <td class="num ${cls} fw">${pgPct}%</td>`;
    tbody.appendChild(tr);
  });
}

function sortOutlierRows(rows) {
  return [...rows].sort((a, b) => {
    if (a.PAIS     !== b.PAIS)        return a.PAIS.localeCompare(b.PAIS);
    if (a.DIVISION !== b.DIVISION)    return a.DIVISION.localeCompare(b.DIVISION);
    if (a.ITEM     !== b.ITEM)        return a.ITEM.localeCompare(b.ITEM, undefined, {numeric: true});
    return (a.item_descrip||'').localeCompare(b.item_descrip||'');
  });
}

// ======================================================
// EXCEL EXPORT — Outliers Negativos
// ======================================================
function downloadOutliersExcel() {
  const data = filterOutliers(DATA_OUTLIERS);
  const neg  = [...data]
    .filter(r => r.tipo_outlier === 'Outlier Negativo')
    .sort((a, b) => a.pg - b.pg);

  if (neg.length === 0) {
    alert('No hay outliers negativos para los filtros seleccionados.');
    return;
  }

  const rows = neg.map((r, i) => ({
    '#':              i + 1,
    'Pa\u00eds':      r.PAIS,
    'Divisi\u00f3n':  r.DIVISION,
    'Categor\u00eda': r.CATEGORIA,
    'Item':           r.ITEM,
    'Descripci\u00f3n': r.item_descrip,
    'Marca':          r.brand_name,
    'Filas':          r.total_rows,
    '% PG':           parseFloat((r.pg * 100).toFixed(2)),
    'SUM Factor_calc': r.sum_factor_calc,
    'SUM Peso_calc':   r.sum_peso_calc,
    'Avg Price Gap':   parseFloat((r.avg_price_gap * 100).toFixed(2)),
  }));

  const wb = XLSX.utils.book_new();
  const ws = XLSX.utils.json_to_sheet(rows);

  // Ancho de columnas
  ws['!cols'] = [
    {wch:5},{wch:6},{wch:22},{wch:30},{wch:12},{wch:40},{wch:20},
    {wch:8},{wch:10},{wch:16},{wch:14},{wch:14}
  ];

  XLSX.utils.book_append_sheet(wb, ws, 'Outliers Negativos');

  const fecha = new Date().toISOString().slice(0,10);
  XLSX.writeFile(wb, `PGMB_Outliers_Negativos_SW8_${fecha}.xlsx`);
}

// ======================================================
// SORT HELPER (kept for reuse)
// ======================================================
function renderOutliers() {
  const data = filterOutliers(DATA_OUTLIERS);
  outlierKpis(data);
  renderOutlierChart(data);
  // Negativos: de más negativo (peor) a menos negativo
  const neg = [...data].filter(r => r.tipo_outlier === 'Outlier Negativo')
    .sort((a, b) => a.pg - b.pg);
  // Positivos: de más positivo (mejor) a menos positivo
  const pos = [...data].filter(r => r.tipo_outlier === 'Outlier Positivo')
    .sort((a, b) => b.pg - a.pg);
  renderOutlierTable('tbody-out-neg', neg);
  renderOutlierTable('tbody-out-pos', pos);
}
    """

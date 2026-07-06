"""
Reporte Consistencia de Precios - CAM Pricing 2026-07-04
Arquitectura limpia: bloque de datos separado del bloque de logica.
"""
import os, json, webbrowser
from datetime import datetime
import pandas as pd

BASE   = os.path.dirname(os.path.abspath(__file__))
BQ_DIR = os.path.join(BASE, "bq_results")

# ── carga ────────────────────────────────────────────────────────────────────
def load():
    d = pd.read_csv(os.path.join(BQ_DIR, "01_director_pais.csv"))
    f = pd.read_csv(os.path.join(BQ_DIR, "02_resumen_familias.csv"))
    p = pd.read_csv(os.path.join(BQ_DIR, "03_packs_gramajes.csv"))
    t = pd.read_csv(os.path.join(BQ_DIR, "04_detalle_desalineados.csv"))
    return d, f, p, t

# ── json seguro ──────────────────────────────────────────────────────────────
def jsc(df, cols, n=500):
    avail = [c for c in cols if c in df.columns]
    sub   = df[avail].head(n).copy()
    for c in sub.select_dtypes("float").columns:
        sub[c] = sub[c].round(2)
    sub = sub.where(pd.notna(sub), other=None)
    return json.dumps(sub.to_dict("records"), ensure_ascii=False).replace("</", "<\\/")

# ── kpis ─────────────────────────────────────────────────────────────────────
def kpis(d):
    av = int(d["SKUS_VALIDOS"].sum())
    al = int(d["SKUS_ALINEADOS"].sum())
    return {
        "pct":     round(al / av * 100, 2) if av else 0,
        "fam":     int(d["TOTAL_FAMILIAS"].sum()),
        "skus":    int(d["TOTAL_SKUS"].sum()),
        "val":     av,
        "pack":    int(d["SKUS_PACK_GRAMAJE"].sum()),
        "ali":     al,
        "nali":    int(d["SKUS_NO_ALINEADOS"].sum()),
        "fok":     int(d["FAMILIAS_100_ALINEADAS"].sum()),
        "fdif":    int(d["FAMILIAS_CON_DIFERENCIAS"].sum()),
    }

# ── director rows html ────────────────────────────────────────────────────────
PN = {"CR":"Costa Rica","GT":"Guatemala","HN":"Honduras","SV":"El Salvador","NI":"Nicaragua"}
def dir_rows(d):
    rows = []
    for _, r in d.sort_values("PCT_ALINEACION").iterrows():
        pct = float(r["PCT_ALINEACION"])
        col = "#2a8703" if pct >= 94 else ("#e6a817" if pct >= 92 else "#ea1100")
        bar = (f'<div class="bw"><div class="bf" style="width:{pct:.1f}%;background:{col}"></div>'
               f'<span class="bl">{pct:.2f}%</span></div>')
        rows.append(
            f"<tr>"
            f"<td><b>{PN.get(r['PAIS'], r['PAIS'])}</b></td>"
            f"<td class='R'>{int(r['TOTAL_FAMILIAS']):,}</td>"
            f"<td class='R'>{int(r['TOTAL_SKUS']):,}</td>"
            f"<td class='R'>{int(r['SKUS_VALIDOS']):,}</td>"
            f"<td class='R pu'>{int(r['SKUS_PACK_GRAMAJE']):,}</td>"
            f"<td class='R gn'>{int(r['SKUS_ALINEADOS']):,}</td>"
            f"<td class='R rd'>{int(r['SKUS_NO_ALINEADOS']):,}</td>"
            f"<td class='R'>{int(r['FAMILIAS_100_ALINEADAS']):,}</td>"
            f"<td class='R'>{int(r['FAMILIAS_CON_DIFERENCIAS']):,}</td>"
            f"<td>{bar}</td></tr>"
        )
    return "\n".join(rows)

# ── chart.js inline ───────────────────────────────────────────────────────────
def chartjs():
    p = os.path.join(BASE, "chartjs.min.js")
    if os.path.exists(p):
        with open(p, encoding="utf-8", errors="replace") as f:
            return f"<script>{f.read()}</script>"
    return ""

# ── css (string plano, sin f-string) ─────────────────────────────────────────
CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',system-ui,sans-serif;background:#f0f4f8;color:#1e293b;font-size:14px}
.hdr{background:#0053e2;padding:13px 26px;display:flex;align-items:center;gap:12px;
     position:sticky;top:0;z-index:100;box-shadow:0 2px 8px rgba(0,0,80,.2)}
.sp{width:36px;height:36px;background:#ffc220;border-radius:50%;display:flex;align-items:center;
    justify-content:center;font-size:17px;font-weight:800;color:#0053e2;flex-shrink:0}
.hdr h1{color:#fff;font-size:1rem;font-weight:700}
.hdr p{color:#93c5fd;font-size:.68rem;margin-top:2px}
.pg-wrap{max-width:1440px;margin:0 auto;padding:16px}
.gkpi{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:14px 0}
.card{background:#fff;border-radius:10px;padding:14px 16px;
      border:1px solid #e2e8f0;box-shadow:0 1px 4px rgba(0,0,50,.06)}
.kv{font-size:1.75rem;font-weight:800;line-height:1.1}
.kl{font-size:.65rem;text-transform:uppercase;letter-spacing:.05em;color:#64748b;margin-top:3px}
.ks{font-size:.62rem;color:#94a3b8;margin-top:2px}
.g2{display:grid;grid-template-columns:1fr 1fr;gap:14px}
@media(max-width:860px){.g2{grid-template-columns:1fr}}
.tbar{display:flex;gap:3px;flex-wrap:wrap;margin-top:16px;margin-bottom:-1px}
.tbtn{padding:8px 16px;border-radius:8px 8px 0 0;font-weight:600;font-size:.77rem;
      cursor:pointer;border:1px solid #e2e8f0;border-bottom:none;background:#e8edf5;color:#475569}
.tbtn.on{background:#0053e2;color:#fff;border-color:#0053e2}
.tpnl{display:none;background:#fff;border-radius:0 10px 10px 10px;
      padding:16px;border:1px solid #e2e8f0}
.tpnl.on{display:block}
.ctrl{display:flex;gap:8px;align-items:center;margin-bottom:10px;flex-wrap:wrap}
.sb{padding:6px 11px;border:1px solid #cbd5e1;border-radius:6px;font-size:.76rem;
    width:200px;outline:none}
.sb:focus{border-color:#0053e2}
.sl{padding:6px 8px;border:1px solid #cbd5e1;border-radius:6px;
    font-size:.76rem;background:#fff;outline:none;cursor:pointer}
.dl{padding:5px 12px;border-radius:6px;border:1px solid #0053e2;background:#fff;
    color:#0053e2;font-size:.74rem;font-weight:700;cursor:pointer}
.dl:hover{background:#eff6ff}
.rc{font-size:.69rem;color:#64748b}
.tw{overflow-x:auto;max-height:460px;overflow-y:auto;border-radius:7px;border:1px solid #e2e8f0}
table{border-collapse:collapse;width:100%;min-width:500px}
thead th{background:#0053e2;color:#fff;padding:7px 10px;font-size:.69rem;
         text-align:left;position:sticky;top:0;z-index:2;white-space:nowrap}
tbody td{padding:5px 10px;font-size:.69rem;border-bottom:1px solid #f1f5f9;white-space:nowrap}
tr:hover td{background:#f0f6ff}
.R{text-align:right}
.gn{color:#166534;font-weight:700} .rd{color:#991b1b;font-weight:700}
.bl{color:#1e40af;font-weight:700} .pu{color:#6d28d9;font-weight:600}
.b{display:inline-block;padding:2px 7px;border-radius:20px;font-size:.65rem;font-weight:700}
.bg{background:#dcfce7;color:#166534} .by{background:#fef9c3;color:#854d0e}
.br{background:#fee2e2;color:#991b1b} .bz{background:#f1f5f9;color:#64748b}
.bb{background:#dbeafe;color:#1e40af} .bp{background:#ede9fe;color:#5b21b6}
.pager{display:flex;gap:4px;align-items:center;margin-top:9px;flex-wrap:wrap}
.pager button{padding:3px 9px;border-radius:5px;border:1px solid #cbd5e1;
              background:#fff;font-size:.69rem;cursor:pointer}
.pager button.on{background:#0053e2;color:#fff;border-color:#0053e2}
.pi{font-size:.67rem;color:#64748b;margin-left:auto}
.bw{position:relative;background:#f1f5f9;border-radius:5px;height:20px;min-width:120px}
.bf{position:absolute;left:0;top:0;height:100%;border-radius:5px}
.bl2{position:absolute;right:5px;top:2px;font-size:.65rem;font-weight:700}
.banner{border-radius:7px;padding:8px 12px;font-size:.72rem;margin-bottom:10px;border-left:4px solid}
.bann-r{background:#fff7ed;border-color:#ea1100;color:#9a3412}
.bann-b{background:#eff6ff;border-color:#0053e2;color:#1e40af}
.bann-p{background:#faf5ff;border-color:#7c3aed;color:#5b21b6}
"""

# ── logica JS (NO es f-string — usa { } libremente) ─────────────────────────
LOGIC = """
var PG = 50;
var ST = {
  det: { data: W_DET, filtered: [], page: 0 },
  fam: { data: W_FAM, filtered: [], page: 0 },
  pck: { data: W_PCK, filtered: [], page: 0 }
};
ST.det.filtered = ST.det.data.slice();
ST.fam.filtered = ST.fam.data.slice();
ST.pck.filtered = ST.pck.data.slice();

/* helpers */
function X(v) {
  if (v === null || v === undefined || v === '') return '\u2014';
  return String(v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
function N(v, d) {
  if (v === null || v === undefined || v === '') return '\u2014';
  var f = parseFloat(v);
  if (isNaN(f)) return X(v);
  return f.toLocaleString('es', {minimumFractionDigits: d||0, maximumFractionDigits: d||0});
}
function PB(v) {
  if (v === null || v === undefined || v === '') return '<span class="b bz">N/D</span>';
  var f = parseFloat(v);
  var c = f >= 94 ? 'bg' : f >= 85 ? 'by' : 'br';
  return '<span class="b ' + c + '">' + f.toFixed(1) + '%</span>';
}
function AB(v) {
  if (!v) return '<span class="b bz">\u2014</span>';
  return String(v).toUpperCase() === 'PRIMARIO'
    ? '<span class="b bb">PRIMARIO</span>'
    : '<span class="b bz">SECUND.</span>';
}
function EB(v) {
  if (!v) return '<span class="b bz">\u2014</span>';
  var s = String(v);
  if (s.indexOf('REVISAR') >= 0) return '<span class="b br">' + X(s) + '</span>';
  if (s.indexOf('Esperado') >= 0 || s.indexOf('Mayor') >= 0)
    return '<span class="b by">' + X(s) + '</span>';
  if (s.indexOf('Igual') >= 0) return '<span class="b bg">' + X(s) + '</span>';
  return '<span class="b bz">' + X(s) + '</span>';
}
function SB(v) {
  if (!v) return '<span class="b bz">\u2014</span>';
  var s = String(v);
  if (s.indexOf('Diferente') >= 0) return '<span class="b br">Diferente</span>';
  if (s.indexOf('Igual') >= 0)     return '<span class="b bg">Igual</span>';
  if (s.indexOf('pack') >= 0 || s.indexOf('tamano') >= 0)
    return '<span class="b bp">Pack/Tam</span>';
  return '<span class="b bz">' + X(s) + '</span>';
}
function DS(v) {
  if (v === null || v === undefined || v === '') return '';
  var f = parseFloat(v);
  if (isNaN(f) || f === 0) return '';
  return f > 0 ? ' style="color:#166534"' : ' style="color:#991b1b"';
}

/* row renderers */
function rowDet(r) {
  return '<tr>'
    + '<td><b>' + X(r.PAIS) + '</b></td>'
    + '<td>' + X(r.Formato) + '</td>'
    + '<td>' + X(r.ZONA) + '</td>'
    + '<td style="font-family:monospace">' + X(r.CODIGO_FAMILIA) + '</td>'
    + '<td style="font-family:monospace">' + X(r.SKU_PRIMARIO) + '</td>'
    + '<td style="max-width:150px;overflow:hidden;text-overflow:ellipsis" title="' + X(r.DESC_PRIMARIO) + '">' + X(r.DESC_PRIMARIO) + '</td>'
    + '<td class="R">' + N(r.PRECIO_PRIMARIO, 2) + '</td>'
    + '<td style="font-family:monospace">' + X(r.ITEM) + '</td>'
    + '<td>' + AB(r.AGRUPACION) + '</td>'
    + '<td style="max-width:170px;overflow:hidden;text-overflow:ellipsis" title="' + X(r.SIGNING_DESC) + '">' + X(r.SIGNING_DESC) + '</td>'
    + '<td class="R bl">' + N(r.PRECIO_GPI_C_IMP, 2) + '</td>'
    + '<td class="R"' + DS(r.DIFERENCIA_PRECIO) + '>' + N(r.DIFERENCIA_PRECIO, 2) + '</td>'
    + '<td class="R"' + DS(r.DIFERENCIA_PCT) + '>' + N(r.DIFERENCIA_PCT, 1) + '%</td>'
    + '<td>' + SB(r.ESTADO_PRECIO) + '</td>'
    + '<td class="R">' + N(r.CANTIDAD_SKUS_MISMO_PRECIO) + '</td>'
    + '<td class="R">' + N(r.CANTIDAD_PRECIOS_DISTINTOS) + '</td>'
    + '<td class="R">' + N(r.Ventas, 0) + '</td>'
    + '<td class="R">' + N(r.Rotaciones, 0) + '</td>'
    + '<td style="max-width:150px;overflow:hidden;text-overflow:ellipsis;font-size:.64rem" title="' + X(r.OBSERVACIONES) + '">' + X(r.OBSERVACIONES) + '</td>'
    + '</tr>';
}
function rowFam(r) {
  return '<tr>'
    + '<td><b>' + X(r.PAIS) + '</b></td>'
    + '<td>' + X(r.Formato) + '</td>'
    + '<td>' + X(r.ZONA) + '</td>'
    + '<td style="font-family:monospace">' + X(r.CODIGO_FAMILIA) + '</td>'
    + '<td><b>' + X(r.MARCA) + '</b></td>'
    + '<td style="font-size:.65rem">' + X(r.CATEGORIA) + '</td>'
    + '<td style="max-width:170px;overflow:hidden;text-overflow:ellipsis" title="' + X(r.DESC_PRIMARIO) + '">' + X(r.DESC_PRIMARIO) + '</td>'
    + '<td class="R">' + N(r.PRECIO_PRIMARIO, 2) + '</td>'
    + '<td class="R">' + N(r.TOTAL_SKUS) + '</td>'
    + '<td class="R">' + N(r.SKUS_VALIDOS) + '</td>'
    + '<td class="R pu">' + N(r.SKUS_PACK_GRAMAJE) + '</td>'
    + '<td class="R gn">' + N(r.SKUS_ALINEADOS) + '</td>'
    + '<td class="R rd">' + N(r.SKUS_NO_ALINEADOS) + '</td>'
    + '<td>' + PB(r.PCT_ALINEACION) + '</td>'
    + '<td class="R">' + N(r.PRECIOS_DISTINTOS) + '</td>'
    + '<td class="R">' + N(r.VENTAS_FAMILIA, 0) + '</td>'
    + '</tr>';
}
function rowPck(r) {
  return '<tr>'
    + '<td><b>' + X(r.PAIS) + '</b></td>'
    + '<td>' + X(r.Formato) + '</td>'
    + '<td>' + X(r.ZONA) + '</td>'
    + '<td style="font-family:monospace">' + X(r.CODIGO_FAMILIA) + '</td>'
    + '<td style="font-family:monospace">' + X(r.SKU_PRIMARIO) + '</td>'
    + '<td style="max-width:140px;overflow:hidden;text-overflow:ellipsis" title="' + X(r.DESC_PRIMARIO) + '">' + X(r.DESC_PRIMARIO) + '</td>'
    + '<td class="R">' + N(r.PRECIO_PRIMARIO, 2) + '</td>'
    + '<td class="R">' + N(r.TAMANO_PRIMARIO, 0) + ' ' + X(r.MEDIDA_PRIMARIO) + '</td>'
    + '<td style="font-family:monospace">' + X(r.SKU_SECUNDARIO) + '</td>'
    + '<td>' + AB(r.AGRUPACION) + '</td>'
    + '<td style="max-width:160px;overflow:hidden;text-overflow:ellipsis" title="' + X(r.DESC_SECUNDARIO) + '">' + X(r.DESC_SECUNDARIO) + '</td>'
    + '<td class="R bl">' + N(r.PRECIO_SECUNDARIO, 2) + '</td>'
    + '<td class="R">' + N(r.TAMANO_SECUNDARIO, 0) + ' ' + X(r.MEDIDA_SECUNDARIO) + '</td>'
    + '<td class="R pu">' + N(r.FACTOR_DE_CONVERSION, 2) + '</td>'
    + '<td class="R">' + N(r.AHORRO_DIFERENCIAL, 2) + '</td>'
    + '<td class="R"' + DS(r.DIFERENCIA_ABSOLUTA) + '>' + N(r.DIFERENCIA_ABSOLUTA, 2) + '</td>'
    + '<td class="R"' + DS(r.DIFERENCIA_PCT) + '>' + N(r.DIFERENCIA_PCT, 1) + '%</td>'
    + '<td>' + EB(r.EVALUACION) + '</td>'
    + '<td class="R">' + N(r.Ventas, 0) + '</td>'
    + '</tr>';
}

var RFNS = { det: rowDet, fam: rowFam, pck: rowPck };

/* tabla engine */
function render(key) {
  var s     = ST[key];
  var tbody = document.getElementById('bd_' + key);
  if (!tbody) return;
  var start = s.page * PG;
  var rows  = s.filtered.slice(start, start + PG);
  tbody.innerHTML = rows.map(RFNS[key]).join('');
  buildPager(key);
  var rc = document.getElementById('rc_' + key);
  if (rc) rc.textContent = 'Mostrando ' + (start + 1) + '\u2013'
    + Math.min(start + PG, s.filtered.length)
    + ' de ' + s.filtered.length.toLocaleString('es') + ' registros';
}

function buildPager(key) {
  var s     = ST[key];
  var pages = Math.ceil(s.filtered.length / PG);
  var cur   = s.page;
  var el    = document.getElementById('pg_' + key);
  if (!el) return;
  var shown = [], html = '';
  [0, cur - 1, cur, cur + 1, pages - 1].forEach(function(p) {
    if (p >= 0 && p < pages && shown.indexOf(p) < 0) shown.push(p);
  });
  shown.sort(function(a, b) { return a - b; });
  var last = -1;
  shown.forEach(function(p) {
    if (last >= 0 && p - last > 1) html += '<span style="color:#94a3b8">&hellip;</span>';
    html += '<button class="' + (cur === p ? 'on' : '')
          + '" onclick="go(\'' + key + '\',' + p + ')">' + (p + 1) + '</button>';
    last = p;
  });
  html += '<span class="pi">Pag ' + (cur + 1) + '/' + pages + '</span>';
  el.innerHTML = html;
}

function go(key, p) { ST[key].page = p; render(key); }

/* filtros */
function filt(key) {
  var term  = (document.getElementById('sr_' + key) || {value:''}).value.toLowerCase();
  var pais  = (document.getElementById('pa_' + key) || {value:''}).value;
  var evalV = (document.getElementById('ev_' + key) || {value:''}).value;
  ST[key].filtered = ST[key].data.filter(function(r) {
    if (pais  && r.PAIS !== pais)              return false;
    if (evalV && (r.EVALUACION||'') !== evalV) return false;
    if (term  && JSON.stringify(r).toLowerCase().indexOf(term) < 0) return false;
    return true;
  });
  ST[key].page = 0;
  render(key);
}

/* descarga csv */
function dlcsv(key) {
  var names = { det:'detalle_desalineados', fam:'resumen_familias',
                pck:'packs_gramajes', dir:'director_pais' };
  var rows  = (key === 'dir') ? W_DIR : ST[key].filtered;
  if (!rows || !rows.length) return;
  var ks = Object.keys(rows[0]);
  function esc(v) {
    var s = (v === null || v === undefined) ? '' : String(v);
    return (s.indexOf(',') >= 0 || s.indexOf('"') >= 0 || s.indexOf('\n') >= 0)
      ? '"' + s.replace(/"/g, '""') + '"' : s;
  }
  var lines = [ks.join(',')];
  rows.forEach(function(r) { lines.push(ks.map(function(k) { return esc(r[k]); }).join(',')); });
  var blob = new Blob(['\ufeff' + lines.join('\n')], { type: 'text/csv;charset=utf-8;' });
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = names[key] + '.csv';
  a.click();
}

/* tabs */
function tab(id, btn) {
  document.querySelectorAll('.tpnl').forEach(function(p) { p.classList.remove('on'); });
  document.querySelectorAll('.tbtn').forEach(function(b) { b.classList.remove('on'); });
  document.getElementById(id).classList.add('on');
  btn.classList.add('on');
}

/* charts - despues de que el DOM este listo */
window.addEventListener('load', function() {
  var c1 = document.getElementById('ch1');
  var c2 = document.getElementById('ch2');
  if (typeof Chart === 'undefined') return;
  if (c1) {
    new Chart(c1.getContext('2d'), {
      type: 'bar',
      data: {
        labels: W_CHL,
        datasets: [
          { label: 'Alineados',    data: W_ALI,  backgroundColor: '#2a8703', borderRadius: 4 },
          { label: 'No Alineados', data: W_NALI, backgroundColor: '#ea1100', borderRadius: 4 }
        ]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top' },
          tooltip: { callbacks: {
            afterBody: function(items) {
              return 'Alineacion: ' + W_PCTS[items[0].dataIndex] + '%';
            }
          }}
        },
        scales: {
          x: { stacked: true },
          y: { stacked: true, ticks: { callback: function(v) { return v.toLocaleString('es'); } } }
        }
      }
    });
  }
  if (c2) {
    new Chart(c2.getContext('2d'), {
      type: 'doughnut',
      data: {
        labels: ['Alineados', 'No Alineados', 'Pack/Gramaje'],
        datasets: [{
          data: W_DONA,
          backgroundColor: ['#2a8703', '#ea1100', '#7c3aed'],
          borderWidth: 2, borderColor: '#fff'
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { position: 'bottom' } }
      }
    });
  }
});

/* init tablas */
render('det');
render('fam');
render('pck');
"""

# ── genera html ───────────────────────────────────────────────────────────────
def build(director, familias, packs, detalle):
    g   = kpis(director)
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    gc  = "#2a8703" if g["pct"] >= 94 else ("#e6a817" if g["pct"] >= 92 else "#ea1100")

    # columnas por tabla
    det_c = ["PAIS","Formato","ZONA","CODIGO_FAMILIA","SKU_PRIMARIO","DESC_PRIMARIO",
             "PRECIO_PRIMARIO","ITEM","AGRUPACION","SIGNING_DESC",
             "PRECIO_GPI_C_IMP","DIFERENCIA_PRECIO","DIFERENCIA_PCT",
             "ESTADO_PRECIO","CANTIDAD_SKUS_MISMO_PRECIO","CANTIDAD_PRECIOS_DISTINTOS",
             "Ventas","Rotaciones","OBSERVACIONES"]
    fam_c = ["PAIS","Formato","ZONA","CODIGO_FAMILIA","MARCA","CATEGORIA",
             "DESC_PRIMARIO","SKU_PRIMARIO","PRECIO_PRIMARIO","VENTAS_PRIMARIO",
             "TOTAL_SKUS","SKUS_VALIDOS","SKUS_PACK_GRAMAJE",
             "SKUS_ALINEADOS","SKUS_NO_ALINEADOS","PCT_ALINEACION",
             "PRECIOS_DISTINTOS","VENTAS_FAMILIA"]
    pck_c = ["PAIS","Formato","ZONA","CODIGO_FAMILIA","DESC_PRIMARIO","SKU_PRIMARIO",
             "PRECIO_PRIMARIO","TAMANO_PRIMARIO","MEDIDA_PRIMARIO",
             "SKU_SECUNDARIO","AGRUPACION","DESC_SECUNDARIO","PRECIO_SECUNDARIO",
             "TAMANO_SECUNDARIO","MEDIDA_SECUNDARIO",
             "FACTOR_DE_CONVERSION","AHORRO_DIFERENCIAL",
             "DIFERENCIA_ABSOLUTA","DIFERENCIA_PCT","EVALUACION",
             "Ventas","Rotaciones","MARCA","CATEGORIA"]

    j_det = jsc(detalle,  det_c, 500)
    j_fam = jsc(familias, fam_c, 500)
    j_pck = jsc(packs,    pck_c, 500)
    j_dir = jsc(director, list(director.columns), 10)

    ds = director.sort_values("PCT_ALINEACION")
    c_labels = json.dumps(ds["PAIS"].tolist())
    c_ali    = json.dumps(ds["SKUS_ALINEADOS"].tolist())
    c_nali   = json.dumps(ds["SKUS_NO_ALINEADOS"].tolist())
    c_pcts   = json.dumps(ds["PCT_ALINEACION"].round(2).tolist())
    c_dona   = json.dumps([g["ali"], g["nali"], g["pack"]])

    # Bloque de datos: f-string SOLO con variables JSON — sin llaves JS
    data_block = (
        "<script>\n"
        f"var W_DET  = {j_det};\n"
        f"var W_FAM  = {j_fam};\n"
        f"var W_PCK  = {j_pck};\n"
        f"var W_DIR  = {j_dir};\n"
        f"var W_CHL  = {c_labels};\n"
        f"var W_ALI  = {c_ali};\n"
        f"var W_NALI = {c_nali};\n"
        f"var W_PCTS = {c_pcts};\n"
        f"var W_DONA = {c_dona};\n"
        "</script>"
    )

    dir_h = dir_rows(director)

    # HTML estructura (f-string solo para valores Python: KPIs, fechas, dir_h)
    return (
        "<!DOCTYPE html>\n<html lang='es'>\n<head>\n"
        "<meta charset='UTF-8'/>\n"
        "<meta name='viewport' content='width=device-width,initial-scale=1'/>\n"
        "<title>Consistencia de Precios CAM 2026-07-04</title>\n"
        + chartjs()
        + f"<style>{CSS}</style>\n"
        "</head>\n<body>\n"

        "<div class='hdr'>"
        "<div class='sp'>W</div>"
        "<div>"
        "<h1>Consistencia de Precios por Familias &mdash; CAM Pricing</h1>"
        f"<p>Datos: 2026-07-04 &nbsp;|&nbsp; Generado: {now}</p>"
        "</div></div>\n"

        "<div class='pg-wrap'>\n"

        # KPIs
        "<div class='gkpi'>\n"
        f"<div class='card'><div class='kv' style='color:{gc}'>{g['pct']:.2f}%</div>"
        "<div class='kl'>Alineacion Global</div><div class='ks'>Excluye packs/gramajes</div></div>\n"
        f"<div class='card'><div class='kv' style='color:#0053e2'>{g['fam']:,}</div>"
        "<div class='kl'>Total Familias</div></div>\n"
        f"<div class='card'><div class='kv'>{g['skus']:,}</div>"
        "<div class='kl'>Total SKUs</div></div>\n"
        f"<div class='card'><div class='kv' style='color:#2a8703'>{g['ali']:,}</div>"
        "<div class='kl'>SKUs Alineados</div></div>\n"
        f"<div class='card'><div class='kv' style='color:#ea1100'>{g['nali']:,}</div>"
        "<div class='kl'>SKUs No Alineados</div></div>\n"
        f"<div class='card'><div class='kv' style='color:#166534'>{g['fok']:,}</div>"
        "<div class='kl'>Familias 100% OK</div></div>\n"
        f"<div class='card'><div class='kv' style='color:#995213'>{g['fdif']:,}</div>"
        "<div class='kl'>Familias con Diferencias</div></div>\n"
        f"<div class='card'><div class='kv' style='color:#6d28d9'>{g['pack']:,}</div>"
        "<div class='kl'>SKUs Pack/Gramaje</div><div class='ks'>Excluidos del indicador</div></div>\n"
        "</div>\n"

        # TABS
        "<div class='tbar'>\n"
        "<button class='tbtn on'  onclick='tab(\"t1\",this)'>Indicadores por Pais</button>\n"
        f"<button class='tbtn' onclick='tab(\"t2\",this)'>Detalle Desalineados ({g['nali']:,})</button>\n"
        f"<button class='tbtn' onclick='tab(\"t3\",this)'>Resumen por Familia ({g['fdif']:,})</button>\n"
        f"<button class='tbtn' onclick='tab(\"t4\",this)'>Packs / Gramajes ({g['pack']:,})</button>\n"
        "</div>\n"

        # TAB 1: Directores
        "<div id='t1' class='tpnl on'>\n"
        "<div class='g2' style='margin-bottom:14px'>\n"
        "<div class='card'><div style='font-weight:700;font-size:.82rem;color:#0053e2;margin-bottom:9px'>"
        "Alineacion por Pais</div>"
        "<div style='height:240px;position:relative'><canvas id='ch1'></canvas></div></div>\n"
        "<div class='card'><div style='font-weight:700;font-size:.82rem;color:#0053e2;margin-bottom:9px'>"
        "Distribucion Global de SKUs</div>"
        "<div style='height:240px;position:relative'><canvas id='ch2'></canvas></div></div>\n"
        "</div>\n"
        "<div class='card'>\n"
        "<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:10px'>"
        "<span style='font-weight:700;font-size:.82rem;color:#0053e2'>Detalle por Pais</span>"
        "<button class='dl' onclick='dlcsv(\"dir\")'>Descargar CSV</button></div>\n"
        "<div class='tw'><table><thead><tr>"
        "<th>Pais</th><th>Familias</th><th>Total SKUs</th><th>SKUs Validos</th>"
        "<th>Pack/Gramaje</th><th>Alineados</th><th>No Alineados</th>"
        "<th>Fam 100% OK</th><th>Fam c/Dif</th><th style='min-width:130px'>% Alineacion</th>"
        f"</tr></thead><tbody>{dir_h}</tbody></table></div>\n"
        "</div>\n"
        "</div>\n"

        # TAB 2: Detalle
        "<div id='t2' class='tpnl'>\n"
        f"<div class='banner bann-r'><b>SKUs desalineados (mismo tamano)</b> — Muestra: top 500 por ventas de {g['nali']:,} totales</div>\n"
        "<div class='ctrl'>\n"
        "<input class='sb' id='sr_det' placeholder='Buscar item, descripcion, marca...' oninput='filt(\"det\")'>\n"
        "<select class='sl' id='pa_det' onchange='filt(\"det\")'>"
        "<option value=''>Todos los paises</option>"
        "<option>CR</option><option>GT</option><option>HN</option><option>SV</option><option>NI</option>"
        "</select>\n"
        "<button class='dl' onclick='dlcsv(\"det\")'>Descargar CSV</button>\n"
        "<span class='rc' id='rc_det'></span>\n"
        "</div>\n"
        "<div class='tw'><table><thead><tr>"
        "<th>Pais</th><th>Formato</th><th>Zona</th><th>Cod.Familia</th>"
        "<th>SKU Primario</th><th>Desc. Primario</th><th>Precio Primario</th>"
        "<th>Item</th><th>Agrupacion</th><th>Descripcion SKU</th>"
        "<th>Precio SKU</th><th>Dif.$</th><th>Dif.%</th>"
        "<th>Estado</th><th>SKUs mismo precio</th><th>Precios dist.</th>"
        "<th>Ventas</th><th>Rotaciones</th><th>Observaciones</th>"
        "</tr></thead><tbody id='bd_det'></tbody></table></div>\n"
        "<div class='pager' id='pg_det'></div>\n"
        "</div>\n"

        # TAB 3: Resumen familia
        "<div id='t3' class='tpnl'>\n"
        f"<div class='banner bann-b'><b>Resumen por familia</b> — Top 500 con mas SKUs desalineados de {g['fdif']:,} familias con diferencias</div>\n"
        "<div class='ctrl'>\n"
        "<input class='sb' id='sr_fam' placeholder='Buscar marca, familia, descripcion...' oninput='filt(\"fam\")'>\n"
        "<select class='sl' id='pa_fam' onchange='filt(\"fam\")'>"
        "<option value=''>Todos los paises</option>"
        "<option>CR</option><option>GT</option><option>HN</option><option>SV</option><option>NI</option>"
        "</select>\n"
        "<button class='dl' onclick='dlcsv(\"fam\")'>Descargar CSV</button>\n"
        "<span class='rc' id='rc_fam'></span>\n"
        "</div>\n"
        "<div class='tw'><table><thead><tr>"
        "<th>Pais</th><th>Formato</th><th>Zona</th><th>Cod.Familia</th>"
        "<th>Marca</th><th>Categoria</th><th>Desc. Primario</th>"
        "<th>Precio Primario</th><th>Total SKUs</th><th>SKUs Validos</th>"
        "<th>SKUs Pack</th><th>Alineados</th><th>No Alineados</th>"
        "<th>% Alineacion</th><th>Precios Dist.</th><th>Ventas Familia</th>"
        "</tr></thead><tbody id='bd_fam'></tbody></table></div>\n"
        "<div class='pager' id='pg_fam'></div>\n"
        "</div>\n"

        # TAB 4: Packs
        "<div id='t4' class='tpnl'>\n"
        f"<div class='banner bann-p'><b>Packs / Gramajes</b> — Factor o Ahorro != 1. Precio mayor al primario es CORRECTO. Solo 'REVISAR' requiere atencion. Top 500 de {g['pack']:,} totales.</div>\n"
        "<div class='ctrl'>\n"
        "<input class='sb' id='sr_pck' placeholder='Buscar item, descripcion, marca...' oninput='filt(\"pck\")'>\n"
        "<select class='sl' id='pa_pck' onchange='filt(\"pck\")'>"
        "<option value=''>Todos los paises</option>"
        "<option>CR</option><option>GT</option><option>HN</option><option>SV</option><option>NI</option>"
        "</select>\n"
        "<select class='sl' id='ev_pck' onchange='filt(\"pck\")'>"
        "<option value=''>Todas las evaluaciones</option>"
        "<option>Mayor al primario - Esperado para pack</option>"
        "<option>Igual al primario - Verificar factor</option>"
        "<option>REVISAR: Precio menor al primario</option>"
        "</select>\n"
        "<button class='dl' onclick='dlcsv(\"pck\")'>Descargar CSV</button>\n"
        "<span class='rc' id='rc_pck'></span>\n"
        "</div>\n"
        "<div class='tw'><table><thead><tr>"
        "<th>Pais</th><th>Formato</th><th>Zona</th><th>Cod.Familia</th>"
        "<th>SKU Primario</th><th>Desc. Primario</th><th>Precio Primario</th><th>Tamano Prim.</th>"
        "<th>SKU Sec.</th><th>Agrupacion</th><th>Desc. Secundario</th>"
        "<th>Precio Sec.</th><th>Tamano Sec.</th>"
        "<th>Factor</th><th>% Ahorro</th><th>Dif.$</th><th>Dif.%</th>"
        "<th>Evaluacion</th><th>Ventas</th>"
        "</tr></thead><tbody id='bd_pck'></tbody></table></div>\n"
        "<div class='pager' id='pg_pck'></div>\n"
        "</div>\n"

        "</div>\n"  # /pg-wrap

        # Scripts: datos primero, luego logica
        + data_block + "\n"
        + "<script>" + LOGIC + "</script>\n"
        "</body></html>"
    )


def main():
    print("Cargando datos...")
    director, familias, packs, detalle = load()
    g = kpis(director)
    print(f"  Director : {len(director)} paises")
    print(f"  Familias : {len(familias):,} | Packs: {len(packs):,} | Detalle: {len(detalle):,}")
    print(f"  Alineacion global: {g['pct']:.2f}%")

    out = os.path.join(BASE, "reporte_familias_precios.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(build(director, familias, packs, detalle))

    kb = os.path.getsize(out) / 1024
    print(f"\nReporte: {out}")
    print(f"  Tamano: {kb:.0f} KB")
    webbrowser.open(f"file:///{out.replace(os.sep, '/')}")
    print("  Abierto en navegador.")

if __name__ == "__main__":
    main()

"""
Reporte Consistencia de Precios - CAM Pricing 2026-07-04
Solo tablas + filtros + KPIs. Sin texto explicativo.
"""
import os, json, webbrowser
from datetime import datetime
import pandas as pd

BASE   = os.path.dirname(os.path.abspath(__file__))
BQ_DIR = os.path.join(BASE, "bq_results")

# ── CARGA ────────────────────────────────────────────────────────────────────
def load():
    d = pd.read_csv(os.path.join(BQ_DIR, "01_director_pais.csv"))
    f = pd.read_csv(os.path.join(BQ_DIR, "02_resumen_familias.csv"))
    p = pd.read_csv(os.path.join(BQ_DIR, "03_packs_gramajes.csv"))
    t = pd.read_csv(os.path.join(BQ_DIR, "04_detalle_desalineados.csv"))
    return d, f, p, t

# ── JSON seguro (escapa </script> y NaN) ─────────────────────────────────────
def to_j(df, cols, n=1500):
    avail = [c for c in cols if c in df.columns]
    sub   = df[avail].head(n).copy()
    for c in sub.select_dtypes("float").columns:
        sub[c] = sub[c].round(2)
    sub = sub.where(pd.notna(sub), other=None)
    return json.dumps(sub.to_dict("records"), ensure_ascii=False).replace("</", "<\\/")

# ── DIRECTOR ROWS HTML ────────────────────────────────────────────────────────
PNAMES = {"CR":"Costa Rica","GT":"Guatemala","HN":"Honduras","SV":"El Salvador","NI":"Nicaragua"}

def dir_rows(director):
    rows = []
    for _, r in director.sort_values("PCT_ALINEACION").iterrows():
        pct   = float(r["PCT_ALINEACION"])
        color = "#2a8703" if pct >= 94 else ("#e6a817" if pct >= 92 else "#ea1100")
        bar   = (f'<div class="barw"><div class="barf" style="width:{pct:.1f}%;'
                 f'background:{color}"></div>'
                 f'<span class="barl">{pct:.2f}%</span></div>')
        rows.append(
            f"<tr><td><b>{PNAMES.get(r['PAIS'], r['PAIS'])}</b></td>"
            f"<td class='tr'>{int(r['TOTAL_FAMILIAS']):,}</td>"
            f"<td class='tr'>{int(r['TOTAL_SKUS']):,}</td>"
            f"<td class='tr'>{int(r['SKUS_VALIDOS']):,}</td>"
            f"<td class='tr pu'>{int(r['SKUS_PACK_GRAMAJE']):,}</td>"
            f"<td class='tr gn'>{int(r['SKUS_ALINEADOS']):,}</td>"
            f"<td class='tr rd'>{int(r['SKUS_NO_ALINEADOS']):,}</td>"
            f"<td class='tr'>{int(r['FAMILIAS_100_ALINEADAS']):,}</td>"
            f"<td class='tr'>{int(r['FAMILIAS_CON_DIFERENCIAS']):,}</td>"
            f"<td>{bar}</td></tr>"
        )
    return "\n".join(rows)

# ── GLOBAL KPIs ───────────────────────────────────────────────────────────────
def kpis(director):
    return {
        "total_familias":          int(director["TOTAL_FAMILIAS"].sum()),
        "total_skus":              int(director["TOTAL_SKUS"].sum()),
        "skus_validos":            int(director["SKUS_VALIDOS"].sum()),
        "skus_pack":               int(director["SKUS_PACK_GRAMAJE"].sum()),
        "alineados":               int(director["SKUS_ALINEADOS"].sum()),
        "no_alineados":            int(director["SKUS_NO_ALINEADOS"].sum()),
        "fam_ok":                  int(director["FAMILIAS_100_ALINEADAS"].sum()),
        "fam_dif":                 int(director["FAMILIAS_CON_DIFERENCIAS"].sum()),
        "pct":                     round(director["SKUS_ALINEADOS"].sum()
                                         / director["SKUS_VALIDOS"].sum() * 100, 2),
    }

# ── Chart.js inline ───────────────────────────────────────────────────────────
def chartjs_tag():
    p = os.path.join(BASE, "chartjs.min.js")
    if os.path.exists(p):
        with open(p, encoding="utf-8", errors="replace") as f:
            return f"<script>{f.read()}</script>"
    return ""

# ── HTML ──────────────────────────────────────────────────────────────────────
def build(director, familias, packs, detalle):
    g   = kpis(director)
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    gc  = "#2a8703" if g["pct"] >= 94 else ("#e6a817" if g["pct"] >= 92 else "#ea1100")

    # Datos JSON por tabla
    det_cols = ["PAIS","Formato","ZONA","CODIGO_FAMILIA","SKU_PRIMARIO","DESC_PRIMARIO",
                "PRECIO_PRIMARIO","ITEM","AGRUPACION","SIGNING_DESC",
                "PRECIO_GPI_C_IMP","DIFERENCIA_PRECIO","DIFERENCIA_PCT",
                "ESTADO_PRECIO","CANTIDAD_SKUS_MISMO_PRECIO","CANTIDAD_PRECIOS_DISTINTOS",
                "Ventas","Rotaciones","OBSERVACIONES"]
    fam_cols = ["PAIS","Formato","ZONA","CODIGO_FAMILIA","MARCA","CATEGORIA",
                "DESC_PRIMARIO","SKU_PRIMARIO","PRECIO_PRIMARIO","VENTAS_PRIMARIO",
                "ROTACIONES_PRIMARIO","TOTAL_SKUS","SKUS_VALIDOS","SKUS_PACK_GRAMAJE",
                "SKUS_ALINEADOS","SKUS_NO_ALINEADOS","PCT_ALINEACION",
                "PRECIOS_DISTINTOS","VENTAS_FAMILIA"]
    pck_cols = ["PAIS","Formato","ZONA","CODIGO_FAMILIA","DESC_PRIMARIO","SKU_PRIMARIO",
                "PRECIO_PRIMARIO","TAMANO_PRIMARIO","MEDIDA_PRIMARIO",
                "SKU_SECUNDARIO","AGRUPACION","DESC_SECUNDARIO","PRECIO_SECUNDARIO",
                "TAMANO_SECUNDARIO","MEDIDA_SECUNDARIO",
                "FACTOR_DE_CONVERSION","AHORRO_DIFERENCIAL",
                "DIFERENCIA_ABSOLUTA","DIFERENCIA_PCT","EVALUACION",
                "Ventas","Rotaciones","MARCA","CATEGORIA"]
    dir_cols = list(director.columns)

    j_det = to_j(detalle,  det_cols, 1500)
    j_fam = to_j(familias, fam_cols, 1500)
    j_pck = to_j(packs,    pck_cols, 1500)
    j_dir = to_j(director, dir_cols,    10)

    # Chart data
    ds = director.sort_values("PCT_ALINEACION")
    c_labels = json.dumps(ds["PAIS"].tolist())
    c_ali    = json.dumps(ds["SKUS_ALINEADOS"].tolist())
    c_nali   = json.dumps(ds["SKUS_NO_ALINEADOS"].tolist())
    c_pcts   = json.dumps(ds["PCT_ALINEACION"].round(2).tolist())
    c_dona   = json.dumps([g["alineados"], g["no_alineados"], g["skus_pack"]])

    dir_html = dir_rows(director)

    # ── CSS ──────────────────────────────────────────────────────────────────
    CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',system-ui,sans-serif;background:#f0f4f8;color:#1e293b;font-size:14px}
.hdr{background:#0053e2;padding:14px 26px;display:flex;align-items:center;gap:14px;
     position:sticky;top:0;z-index:100;box-shadow:0 2px 8px rgba(0,0,80,.2)}
.spark{width:38px;height:38px;background:#ffc220;border-radius:50%;display:flex;
       align-items:center;justify-content:center;font-size:18px;font-weight:800;
       color:#0053e2;flex-shrink:0}
.hdr h1{color:#fff;font-size:1.05rem;font-weight:700}
.hdr small{color:#93c5fd;font-size:.7rem}
.page{max-width:1440px;margin:0 auto;padding:18px 16px}
.g2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.gkpi{display:grid;grid-template-columns:repeat(auto-fit,minmax(155px,1fr));gap:11px;margin-bottom:18px}
@media(max-width:860px){.g2{grid-template-columns:1fr}}
.card{background:#fff;border-radius:11px;padding:16px 18px;
      border:1px solid #e2e8f0;box-shadow:0 1px 5px rgba(0,0,50,.06)}
.kv{font-size:1.8rem;font-weight:800;line-height:1.1}
.kl{font-size:.67rem;text-transform:uppercase;letter-spacing:.05em;color:#64748b;margin-top:4px}
.ks{font-size:.63rem;color:#94a3b8;margin-top:2px}
.tabs{display:flex;gap:3px;flex-wrap:wrap;margin-top:18px;margin-bottom:-1px}
.tbtn{padding:8px 18px;border-radius:8px 8px 0 0;font-weight:600;font-size:.78rem;
      cursor:pointer;border:1px solid #e2e8f0;border-bottom:none;
      background:#e8edf5;color:#475569;transition:background .15s}
.tbtn.active{background:#0053e2;color:#fff;border-color:#0053e2}
.tpnl{display:none;background:#fff;border-radius:0 12px 12px 12px;
      padding:18px;border:1px solid #e2e8f0}
.tpnl.active{display:block}
.ctrl{display:flex;gap:8px;align-items:center;margin-bottom:11px;flex-wrap:wrap}
.sbox{padding:6px 11px;border:1px solid #cbd5e1;border-radius:7px;
      font-size:.77rem;width:220px;outline:none}
.sbox:focus{border-color:#0053e2;box-shadow:0 0 0 2px rgba(0,83,226,.15)}
.sel{padding:6px 9px;border:1px solid #cbd5e1;border-radius:7px;
     font-size:.77rem;background:#fff;outline:none;cursor:pointer}
.bdl{padding:5px 13px;border-radius:7px;border:1px solid #0053e2;
     background:#fff;color:#0053e2;font-size:.75rem;font-weight:700;cursor:pointer}
.bdl:hover{background:#eff6ff}
.rc{font-size:.7rem;color:#64748b}
.tw{overflow-x:auto;max-height:480px;overflow-y:auto;
    border-radius:8px;border:1px solid #e2e8f0}
table{border-collapse:collapse;width:100%;min-width:600px}
thead th{background:#0053e2;color:#fff;padding:8px 11px;font-size:.71rem;
         text-align:left;position:sticky;top:0;z-index:2;white-space:nowrap}
tbody td{padding:6px 11px;font-size:.71rem;border-bottom:1px solid #f1f5f9;white-space:nowrap}
tr:hover td{background:#f0f6ff}
.tr{text-align:right} .gn{color:#166534;font-weight:700} .rd{color:#991b1b;font-weight:700}
.bl{color:#1e40af;font-weight:700} .pu{color:#6d28d9;font-weight:600}
.b{display:inline-block;padding:2px 7px;border-radius:20px;font-size:.66rem;font-weight:700}
.bg{background:#dcfce7;color:#166534} .by{background:#fef9c3;color:#854d0e}
.br{background:#fee2e2;color:#991b1b} .bz{background:#f1f5f9;color:#64748b}
.bb{background:#dbeafe;color:#1e40af} .bp{background:#ede9fe;color:#5b21b6}
.pg{display:flex;gap:4px;align-items:center;margin-top:10px;flex-wrap:wrap}
.pg button{padding:3px 10px;border-radius:5px;border:1px solid #cbd5e1;
           background:#fff;font-size:.71rem;cursor:pointer}
.pg button.on{background:#0053e2;color:#fff;border-color:#0053e2}
.pgi{font-size:.68rem;color:#64748b;margin-left:auto}
.barw{position:relative;background:#f1f5f9;border-radius:5px;height:20px;min-width:130px}
.barf{position:absolute;left:0;top:0;height:100%;border-radius:5px}
.barl{position:absolute;right:5px;top:2px;font-size:.67rem;font-weight:700}
"""

    # ── JS (sin f-string para evitar problemas con llaves) ───────────────────
    JS = """
var PAGE = 50;
var ST = {
  det: { data: DATA_DET, filtered: DATA_DET.slice(), page: 0 },
  fam: { data: DATA_FAM, filtered: DATA_FAM.slice(), page: 0 },
  pck: { data: DATA_PCK, filtered: DATA_PCK.slice(), page: 0 }
};

function xss(v) {
  if (v === null || v === undefined || v === '') return '\u2014';
  return String(v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
function num(v, d) {
  if (v === null || v === undefined || v === '') return '\u2014';
  var x = parseFloat(v);
  if (isNaN(x)) return xss(v);
  return x.toLocaleString('es', {minimumFractionDigits: d||0, maximumFractionDigits: d||0});
}
function pctBadge(v) {
  if (v === null || v === undefined || v === '') return '<span class="b bz">N/D</span>';
  var x = parseFloat(v);
  var cls = x >= 94 ? 'bg' : x >= 85 ? 'by' : 'br';
  return '<span class="b ' + cls + '">' + x.toFixed(1) + '%</span>';
}
function agBadge(v) {
  if (!v) return '<span class="b bz">\u2014</span>';
  return String(v).toUpperCase() === 'PRIMARIO'
    ? '<span class="b bb">PRIMARIO</span>'
    : '<span class="b bz">SECUNDARIO</span>';
}
function evBadge(v) {
  if (!v) return '<span class="b bz">\u2014</span>';
  var s = String(v);
  if (s.indexOf('REVISAR') >= 0)  return '<span class="b br">' + xss(s) + '</span>';
  if (s.indexOf('Esperado') >= 0 || s.indexOf('Mayor') >= 0) return '<span class="b by">' + xss(s) + '</span>';
  if (s.indexOf('Igual') >= 0)    return '<span class="b bg">' + xss(s) + '</span>';
  return '<span class="b bz">' + xss(s) + '</span>';
}
function estBadge(v) {
  if (!v) return '<span class="b bz">\u2014</span>';
  var s = String(v);
  if (s.indexOf('Diferente') >= 0)  return '<span class="b br">Diferente</span>';
  if (s.indexOf('Igual') >= 0)      return '<span class="b bg">Igual</span>';
  if (s.indexOf('pack') >= 0 || s.indexOf('tamano') >= 0) return '<span class="b bp">Pack/Gramaje</span>';
  return '<span class="b bz">' + xss(s) + '</span>';
}
function difStyle(v) {
  if (v === null || v === undefined || v === '') return '';
  var x = parseFloat(v);
  return isNaN(x) ? '' : (x > 0 ? ' style="color:#166534"' : x < 0 ? ' style="color:#991b1b"' : '');
}

function rowDet(r) {
  return '<tr>'
    + '<td><b>' + xss(r.PAIS) + '</b></td>'
    + '<td>' + xss(r.Formato) + '</td>'
    + '<td>' + xss(r.ZONA) + '</td>'
    + '<td style="font-family:monospace">' + xss(r.CODIGO_FAMILIA) + '</td>'
    + '<td style="font-family:monospace">' + xss(r.SKU_PRIMARIO) + '</td>'
    + '<td style="max-width:160px;overflow:hidden;text-overflow:ellipsis" title="' + xss(r.DESC_PRIMARIO) + '">' + xss(r.DESC_PRIMARIO) + '</td>'
    + '<td class="tr">' + num(r.PRECIO_PRIMARIO, 2) + '</td>'
    + '<td style="font-family:monospace">' + xss(r.ITEM) + '</td>'
    + '<td>' + agBadge(r.AGRUPACION) + '</td>'
    + '<td style="max-width:180px;overflow:hidden;text-overflow:ellipsis" title="' + xss(r.SIGNING_DESC) + '">' + xss(r.SIGNING_DESC) + '</td>'
    + '<td class="tr bl">' + num(r.PRECIO_GPI_C_IMP, 2) + '</td>'
    + '<td class="tr"' + difStyle(r.DIFERENCIA_PRECIO) + '>' + num(r.DIFERENCIA_PRECIO, 2) + '</td>'
    + '<td class="tr"' + difStyle(r.DIFERENCIA_PCT) + '>' + num(r.DIFERENCIA_PCT, 1) + '%</td>'
    + '<td>' + estBadge(r.ESTADO_PRECIO) + '</td>'
    + '<td class="tr">' + num(r.CANTIDAD_SKUS_MISMO_PRECIO) + '</td>'
    + '<td class="tr">' + num(r.CANTIDAD_PRECIOS_DISTINTOS) + '</td>'
    + '<td class="tr">' + num(r.Ventas, 0) + '</td>'
    + '<td class="tr">' + num(r.Rotaciones, 0) + '</td>'
    + '<td style="max-width:160px;overflow:hidden;text-overflow:ellipsis;font-size:.66rem" title="' + xss(r.OBSERVACIONES) + '">' + xss(r.OBSERVACIONES) + '</td>'
    + '</tr>';
}

function rowFam(r) {
  return '<tr>'
    + '<td><b>' + xss(r.PAIS) + '</b></td>'
    + '<td>' + xss(r.Formato) + '</td>'
    + '<td>' + xss(r.ZONA) + '</td>'
    + '<td style="font-family:monospace">' + xss(r.CODIGO_FAMILIA) + '</td>'
    + '<td><b>' + xss(r.MARCA) + '</b></td>'
    + '<td style="font-size:.66rem">' + xss(r.CATEGORIA) + '</td>'
    + '<td style="max-width:180px;overflow:hidden;text-overflow:ellipsis" title="' + xss(r.DESC_PRIMARIO) + '">' + xss(r.DESC_PRIMARIO) + '</td>'
    + '<td class="tr">' + num(r.PRECIO_PRIMARIO, 2) + '</td>'
    + '<td class="tr">' + num(r.TOTAL_SKUS) + '</td>'
    + '<td class="tr">' + num(r.SKUS_VALIDOS) + '</td>'
    + '<td class="tr pu">' + num(r.SKUS_PACK_GRAMAJE) + '</td>'
    + '<td class="tr gn">' + num(r.SKUS_ALINEADOS) + '</td>'
    + '<td class="tr rd">' + num(r.SKUS_NO_ALINEADOS) + '</td>'
    + '<td>' + pctBadge(r.PCT_ALINEACION) + '</td>'
    + '<td class="tr">' + num(r.PRECIOS_DISTINTOS) + '</td>'
    + '<td class="tr">' + num(r.VENTAS_FAMILIA, 0) + '</td>'
    + '</tr>';
}

function rowPck(r) {
  return '<tr>'
    + '<td><b>' + xss(r.PAIS) + '</b></td>'
    + '<td>' + xss(r.Formato) + '</td>'
    + '<td>' + xss(r.ZONA) + '</td>'
    + '<td style="font-family:monospace">' + xss(r.CODIGO_FAMILIA) + '</td>'
    + '<td style="font-family:monospace">' + xss(r.SKU_PRIMARIO) + '</td>'
    + '<td style="max-width:150px;overflow:hidden;text-overflow:ellipsis" title="' + xss(r.DESC_PRIMARIO) + '">' + xss(r.DESC_PRIMARIO) + '</td>'
    + '<td class="tr">' + num(r.PRECIO_PRIMARIO, 2) + '</td>'
    + '<td class="tr">' + num(r.TAMANO_PRIMARIO, 0) + ' ' + xss(r.MEDIDA_PRIMARIO) + '</td>'
    + '<td style="font-family:monospace">' + xss(r.SKU_SECUNDARIO) + '</td>'
    + '<td>' + agBadge(r.AGRUPACION) + '</td>'
    + '<td style="max-width:170px;overflow:hidden;text-overflow:ellipsis" title="' + xss(r.DESC_SECUNDARIO) + '">' + xss(r.DESC_SECUNDARIO) + '</td>'
    + '<td class="tr bl">' + num(r.PRECIO_SECUNDARIO, 2) + '</td>'
    + '<td class="tr">' + num(r.TAMANO_SECUNDARIO, 0) + ' ' + xss(r.MEDIDA_SECUNDARIO) + '</td>'
    + '<td class="tr pu">' + num(r.FACTOR_DE_CONVERSION, 2) + '</td>'
    + '<td class="tr">' + num(r.AHORRO_DIFERENCIAL, 2) + '</td>'
    + '<td class="tr"' + difStyle(r.DIFERENCIA_ABSOLUTA) + '>' + num(r.DIFERENCIA_ABSOLUTA, 2) + '</td>'
    + '<td class="tr"' + difStyle(r.DIFERENCIA_PCT) + '>' + num(r.DIFERENCIA_PCT, 1) + '%</td>'
    + '<td>' + evBadge(r.EVALUACION) + '</td>'
    + '<td class="tr">' + num(r.Ventas, 0) + '</td>'
    + '</tr>';
}

var ROW_FNS = { det: rowDet, fam: rowFam, pck: rowPck };

function renderTbl(key) {
  var s = ST[key];
  var el = document.getElementById('body_' + key);
  if (!el) return;
  var start = s.page * PAGE;
  var slice = s.filtered.slice(start, start + PAGE);
  el.innerHTML = slice.map(ROW_FNS[key]).join('');
  buildPager(key);
  var rc = document.getElementById('rc_' + key);
  if (rc) rc.textContent = 'Mostrando ' + (start + 1) + '\u2013'
    + Math.min(start + PAGE, s.filtered.length) + ' de '
    + s.filtered.length.toLocaleString('es') + ' registros';
}

function buildPager(key) {
  var s = ST[key];
  var pages = Math.ceil(s.filtered.length / PAGE);
  var cur = s.page;
  var el = document.getElementById('pg_' + key);
  if (!el) return;
  var shown = [], html = '';
  [0, cur - 1, cur, cur + 1, pages - 1].forEach(function(p) {
    if (p >= 0 && p < pages && shown.indexOf(p) < 0) shown.push(p);
  });
  shown.sort(function(a, b) { return a - b; });
  var last = -1;
  shown.forEach(function(p) {
    if (last >= 0 && p - last > 1) html += '<span style="color:#94a3b8">&hellip;</span>';
    html += '<button class="' + (cur === p ? 'on' : '') + '" onclick="go(\'' + key + '\',' + p + ')">' + (p + 1) + '</button>';
    last = p;
  });
  html += '<span class="pgi">Pag ' + (cur + 1) + ' / ' + pages + '</span>';
  el.innerHTML = html;
}

function go(key, p) {
  ST[key].page = p;
  renderTbl(key);
}

function applyFilter(key) {
  var term  = (document.getElementById('sr_' + key) || {}).value || '';
  var pais  = (document.getElementById('pa_' + key) || {}).value || '';
  var evalF = (document.getElementById('ev_' + key) || {}).value || '';
  term = term.toLowerCase();
  ST[key].filtered = ST[key].data.filter(function(r) {
    var str = JSON.stringify(r).toLowerCase();
    var match = (!term || str.indexOf(term) >= 0)
             && (!pais  || r.PAIS === pais)
             && (!evalF || (r.EVALUACION || '') === evalF);
    return match;
  });
  ST[key].page = 0;
  renderTbl(key);
}

function dlCSV(key) {
  var names = { det: 'detalle_desalineados', fam: 'resumen_familias',
                pck: 'packs_gramajes', dir: 'director_pais' };
  var rows = key === 'dir' ? DATA_DIR : ST[key].filtered;
  if (!rows || !rows.length) return;
  var keys = Object.keys(rows[0]);
  function esc2(v) {
    var s = (v === null || v === undefined) ? '' : String(v);
    if (s.indexOf(',') >= 0 || s.indexOf('"') >= 0 || s.indexOf('\\n') >= 0)
      return '"' + s.replace(/"/g, '""') + '"';
    return s;
  }
  var lines = [keys.join(',')];
  rows.forEach(function(r) {
    lines.push(keys.map(function(k) { return esc2(r[k]); }).join(','));
  });
  var blob = new Blob(['\ufeff' + lines.join('\\n')], {type: 'text/csv;charset=utf-8;'});
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = names[key] + '.csv';
  a.click();
}

function switchTab(id, btn) {
  document.querySelectorAll('.tpnl').forEach(function(p) { p.classList.remove('active'); });
  document.querySelectorAll('.tbtn').forEach(function(b) { b.classList.remove('active'); });
  document.getElementById(id).classList.add('active');
  btn.classList.add('active');
}

// CHARTS
(function() {
  var c1 = document.getElementById('ch1');
  var c2 = document.getElementById('ch2');
  if (c1 && typeof Chart !== 'undefined') {
    new Chart(c1.getContext('2d'), {
      type: 'bar',
      data: {
        labels: LABELS,
        datasets: [
          { label: 'Alineados', data: ALI, backgroundColor: '#2a8703', borderRadius: 4 },
          { label: 'No Alineados', data: NALI, backgroundColor: '#ea1100', borderRadius: 4 }
        ]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top' },
          tooltip: { callbacks: { afterBody: function(i) { return 'Alineacion: ' + PCTS[i[0].dataIndex] + '%'; } } }
        },
        scales: { x: { stacked: true }, y: { stacked: true } }
      }
    });
  }
  if (c2 && typeof Chart !== 'undefined') {
    new Chart(c2.getContext('2d'), {
      type: 'doughnut',
      data: {
        labels: ['Alineados', 'No Alineados', 'Pack/Gramaje'],
        datasets: [{ data: DONA, backgroundColor: ['#2a8703','#ea1100','#7c3aed'],
                     borderWidth: 2, borderColor: '#fff' }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { position: 'bottom' } }
      }
    });
  }
})();

renderTbl('det');
renderTbl('fam');
renderTbl('pck');
"""

    # Inyectar datos en el JS (sin f-string, sin riesgo de llaves)
    JS = JS \
        .replace("DATA_DET", j_det) \
        .replace("DATA_FAM", j_fam) \
        .replace("DATA_PCK", j_pck) \
        .replace("DATA_DIR", j_dir) \
        .replace("LABELS",   c_labels) \
        .replace("PCTS",     c_pcts) \
        .replace("NALI",     c_nali) \
        .replace("ALI",      c_ali) \
        .replace("DONA",     c_dona)

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Consistencia de Precios CAM - 2026-07-04</title>
{chartjs_tag()}
<style>{CSS}</style>
</head>
<body>

<div class="hdr">
  <div class="spark">W</div>
  <div>
    <h1>Consistencia de Precios por Familias &mdash; CAM Pricing</h1>
    <small>Datos: 2026-07-04 &nbsp;|&nbsp; Generado: {now} &nbsp;|&nbsp; 5 paises</small>
  </div>
</div>

<div class="page">

<!-- KPIs -->
<div class="gkpi" style="margin-top:16px">
  <div class="card"><div class="kv" style="color:{gc}">{g['pct']:.2f}%</div><div class="kl">Alineacion Global</div><div class="ks">Excluye packs/gramajes</div></div>
  <div class="card"><div class="kv" style="color:#0053e2">{g['total_familias']:,}</div><div class="kl">Total Familias</div><div class="ks">Pais x Formato x Zona</div></div>
  <div class="card"><div class="kv" style="color:#1e293b">{g['total_skus']:,}</div><div class="kl">Total SKUs</div><div class="ks">Todos los paises</div></div>
  <div class="card"><div class="kv" style="color:#2a8703">{g['alineados']:,}</div><div class="kl">SKUs Alineados</div><div class="ks">Precio igual al primario</div></div>
  <div class="card"><div class="kv" style="color:#ea1100">{g['no_alineados']:,}</div><div class="kl">SKUs No Alineados</div><div class="ks">Oportunidad de homologacion</div></div>
  <div class="card"><div class="kv" style="color:#166534">{g['fam_ok']:,}</div><div class="kl">Familias 100% OK</div><div class="ks">Sin desviaciones</div></div>
  <div class="card"><div class="kv" style="color:#995213">{g['fam_dif']:,}</div><div class="kl">Familias con Diferencias</div><div class="ks">Al menos 1 SKU desalineado</div></div>
  <div class="card"><div class="kv" style="color:#6d28d9">{g['skus_pack']:,}</div><div class="kl">SKUs Pack / Gramaje</div><div class="ks">Excluidos del indicador</div></div>
</div>

<!-- TABS -->
<div class="tabs">
  <button class="tbtn active" onclick="switchTab('t1',this)">Indicadores por Pais</button>
  <button class="tbtn" onclick="switchTab('t2',this)">Detalle Desalineados ({g['no_alineados']:,} total)</button>
  <button class="tbtn" onclick="switchTab('t3',this)">Resumen por Familia ({g['fam_dif']:,} con diferencias)</button>
  <button class="tbtn" onclick="switchTab('t4',this)">Packs / Gramajes ({g['skus_pack']:,} total)</button>
</div>

<!-- TAB 1: DIRECTORES -->
<div id="t1" class="tpnl active">
  <div class="g2" style="margin-bottom:16px">
    <div class="card"><div style="font-weight:700;font-size:.85rem;color:#0053e2;margin-bottom:10px">Alineacion por Pais (SKUs mismo tamano)</div>
      <div style="height:250px;position:relative"><canvas id="ch1"></canvas></div>
    </div>
    <div class="card"><div style="font-weight:700;font-size:.85rem;color:#0053e2;margin-bottom:10px">Distribucion Global SKUs</div>
      <div style="height:250px;position:relative"><canvas id="ch2"></canvas></div>
    </div>
  </div>
  <div class="card">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:11px">
      <span style="font-weight:700;font-size:.85rem;color:#0053e2">Detalle por Pais</span>
      <button class="bdl" onclick="dlCSV('dir')">Descargar CSV</button>
    </div>
    <div class="tw">
      <table><thead><tr>
        <th>Pais</th><th>Familias</th><th>Total SKUs</th><th>SKUs Validos</th>
        <th>Pack/Gramaje</th><th>Alineados</th><th>No Alineados</th>
        <th>Fam 100% OK</th><th>Fam c/Dif</th><th style="min-width:150px">% Alineacion</th>
      </tr></thead>
      <tbody>{dir_html}</tbody>
      </table>
    </div>
  </div>
</div>

<!-- TAB 2: DETALLE -->
<div id="t2" class="tpnl">
  <div style="background:#fff7ed;border-left:4px solid #ea1100;border-radius:7px;padding:9px 13px;font-size:.74rem;color:#9a3412;margin-bottom:11px">
    <b>SKUs desalineados de mismo tamano</b> (Factor=1, Ahorro=1) — Muestra: top 1,500 por ventas de {g['no_alineados']:,} totales
  </div>
  <div class="ctrl">
    <input class="sbox" id="sr_det" placeholder="Buscar item, descripcion, marca..." oninput="applyFilter('det')">
    <select class="sel" id="pa_det" onchange="applyFilter('det')">
      <option value="">Todos los paises</option>
      <option>CR</option><option>GT</option><option>HN</option><option>SV</option><option>NI</option>
    </select>
    <button class="bdl" onclick="dlCSV('det')">Descargar CSV</button>
    <span class="rc" id="rc_det"></span>
  </div>
  <div class="tw">
    <table><thead><tr>
      <th>Pais</th><th>Formato</th><th>Zona</th><th>Cod.Familia</th>
      <th>SKU Primario</th><th>Desc. Primario</th><th>Precio Primario</th>
      <th>Item</th><th>Agrupacion</th><th>Descripcion SKU</th>
      <th>Precio SKU</th><th>Dif.$</th><th>Dif.%</th>
      <th>Estado</th><th>SKUs mismo precio</th><th>Precios distintos</th>
      <th>Ventas</th><th>Rotaciones</th><th>Observaciones</th>
    </tr></thead>
    <tbody id="body_det"></tbody></table>
  </div>
  <div class="pg" id="pg_det"></div>
</div>

<!-- TAB 3: RESUMEN FAMILIA -->
<div id="t3" class="tpnl">
  <div style="background:#eff6ff;border-left:4px solid #0053e2;border-radius:7px;padding:9px 13px;font-size:.74rem;color:#1e40af;margin-bottom:11px">
    <b>Resumen por familia</b> — Top 1,500 con mas SKUs no alineados de {g['fam_dif']:,} familias con diferencias
  </div>
  <div class="ctrl">
    <input class="sbox" id="sr_fam" placeholder="Buscar marca, familia, descripcion..." oninput="applyFilter('fam')">
    <select class="sel" id="pa_fam" onchange="applyFilter('fam')">
      <option value="">Todos los paises</option>
      <option>CR</option><option>GT</option><option>HN</option><option>SV</option><option>NI</option>
    </select>
    <button class="bdl" onclick="dlCSV('fam')">Descargar CSV</button>
    <span class="rc" id="rc_fam"></span>
  </div>
  <div class="tw">
    <table><thead><tr>
      <th>Pais</th><th>Formato</th><th>Zona</th><th>Cod.Familia</th>
      <th>Marca</th><th>Categoria</th><th>Desc. Primario</th>
      <th>Precio Primario</th><th>Total SKUs</th><th>SKUs Validos</th>
      <th>SKUs Pack</th><th>Alineados</th><th>No Alineados</th>
      <th>% Alineacion</th><th>Precios Dist.</th><th>Ventas Familia</th>
    </tr></thead>
    <tbody id="body_fam"></tbody></table>
  </div>
  <div class="pg" id="pg_fam"></div>
</div>

<!-- TAB 4: PACKS -->
<div id="t4" class="tpnl">
  <div style="background:#faf5ff;border-left:4px solid #7c3aed;border-radius:7px;padding:9px 13px;font-size:.74rem;color:#5b21b6;margin-bottom:11px">
    <b>Items con Factor_Conversion != 1 o Ahorro_Diferencial != 1</b> — Precio mayor al primario es CORRECTO para packs.
    Solo los marcados <b>REVISAR</b> requieren atencion (precio menor al primario). <b>No afectan el % de alineacion.</b>
  </div>
  <div class="ctrl">
    <input class="sbox" id="sr_pck" placeholder="Buscar item, descripcion, marca..." oninput="applyFilter('pck')">
    <select class="sel" id="pa_pck" onchange="applyFilter('pck')">
      <option value="">Todos los paises</option>
      <option>CR</option><option>GT</option><option>HN</option><option>SV</option><option>NI</option>
    </select>
    <select class="sel" id="ev_pck" onchange="applyFilter('pck')">
      <option value="">Todas las evaluaciones</option>
      <option>Mayor al primario - Esperado para pack</option>
      <option>Igual al primario - Verificar factor</option>
      <option>REVISAR: Precio menor al primario</option>
    </select>
    <button class="bdl" onclick="dlCSV('pck')">Descargar CSV</button>
    <span class="rc" id="rc_pck"></span>
  </div>
  <div class="tw">
    <table><thead><tr>
      <th>Pais</th><th>Formato</th><th>Zona</th><th>Cod.Familia</th>
      <th>SKU Primario</th><th>Desc. Primario</th><th>Precio Primario</th><th>Tamano Prim.</th>
      <th>SKU Secundario</th><th>Agrupacion</th><th>Desc. Secundario</th>
      <th>Precio Sec.</th><th>Tamano Sec.</th>
      <th>Factor Conv.</th><th>% Ahorro</th>
      <th>Dif.$</th><th>Dif.%</th><th>Evaluacion</th><th>Ventas</th>
    </tr></thead>
    <tbody id="body_pck"></tbody></table>
  </div>
  <div class="pg" id="pg_pck"></div>
</div>

</div>
<script>{JS}</script>
</body></html>"""


def main():
    print("Cargando datos...")
    director, familias, packs, detalle = load()
    print(f"  Director : {len(director)} paises")
    print(f"  Familias : {len(familias):,} filas")
    print(f"  Packs    : {len(packs):,} filas")
    print(f"  Detalle  : {len(detalle):,} filas")

    out = os.path.join(BASE, "reporte_familias_precios.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(build(director, familias, packs, detalle))

    kb = os.path.getsize(out) / 1024
    print(f"\nReporte: {out}")
    print(f"  Tamano : {kb:.0f} KB")
    webbrowser.open(f"file:///{out.replace(os.sep, '/')}")
    print("  Abierto en navegador.")

if __name__ == "__main__":
    main()

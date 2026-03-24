"""HTML template builder para el dashboard ejecutivo PGMB - v3 comparativo."""
import json
from dashboard_css import get_css
from dashboard_js import get_js
from dashboard_js_outliers import get_js_outliers


def _pct(v, t):
    return f"{round(v/t*100,1)}%" if t > 0 else "0%"


def _kpi_hero(kpi_comp, kpi_wm):
    tc = kpi_comp["bajo"] + kpi_comp["subio"] + kpi_comp["mantiene"] + kpi_comp["nuevo"]
    tw = kpi_wm["bajo"]   + kpi_wm["subio"]   + kpi_wm["mantiene"]   + kpi_wm["nuevo"]
    rows = [
        ("Baj&oacute;",  "&#128200;", kpi_comp["bajo"],     tc, kpi_wm["bajo"],     tw, "green"),
        ("Subi&oacute;", "&#128201;", kpi_comp["subio"],    tc, kpi_wm["subio"],    tw, "red"),
        ("Mantiene",     "&#9866;",   kpi_comp["mantiene"], tc, kpi_wm["mantiene"], tw, ""),
        ("Nuevo (SW8)",  "&#10024;",  kpi_comp["nuevo"],    tc, kpi_wm["nuevo"],    tw, "spark"),
    ]
    cards = ""
    for lbl, icon, cv, ct, wv, wt, cls in rows:
        cards += f"""
        <div class="hero-kpi {cls}">
          <div class="hero-kpi-icon">{icon}</div>
          <div class="hero-kpi-label">{lbl}</div>
          <div style="display:flex;gap:16px;align-items:flex-end;margin-top:4px">
            <div>
              <div style="font-size:.68rem;opacity:.7;text-transform:uppercase">Comp</div>
              <div class="hero-kpi-val" data-count="{cv}">0</div>
              <div class="hero-kpi-pct">{_pct(cv,ct)}</div>
            </div>
            <div style="width:1px;background:rgba(255,255,255,.3);height:40px"></div>
            <div>
              <div style="font-size:.68rem;opacity:.7;text-transform:uppercase">WM</div>
              <div class="hero-kpi-val" data-count="{wv}">0</div>
              <div class="hero-kpi-pct">{_pct(wv,wt)}</div>
            </div>
          </div>
        </div>"""
    return cards


def _seg_table_html(tbl_id, tbody_id):
    return f"""
      <div class="tbl-scroll">
        <table id="{tbl_id}">
          <thead><tr>
            <th onclick="sortTable('{tbl_id}',0)">Pa&iacute;s &#8597;</th>
            <th onclick="sortTable('{tbl_id}',1)">Divisi&oacute;n &#8597;</th>
            <th onclick="sortTable('{tbl_id}',2)">Categor&iacute;a &#8597;</th>
            <th onclick="sortTable('{tbl_id}',3)" class="num">Baj&oacute; &#8597;</th>
            <th onclick="sortTable('{tbl_id}',4)" class="num">Subi&oacute; &#8597;</th>
            <th onclick="sortTable('{tbl_id}',5)" class="num">Mantiene &#8597;</th>
            <th onclick="sortTable('{tbl_id}',6)" class="num">Nuevo &#8597;</th>
            <th onclick="sortTable('{tbl_id}',7)" class="num">Total &#8597;</th>
            <th onclick="sortTable('{tbl_id}',8)" class="num">% Baj&oacute; &#8597;</th>
            <th onclick="sortTable('{tbl_id}',9)" class="num">% Subi&oacute; &#8597;</th>
          </tr></thead>
          <tbody id="{tbody_id}"></tbody>
        </table>
      </div>"""


def render_html(q1, q2, q3, q4, paises, divisiones, categorias, kpi_comp, kpi_wm):
    css = get_css()
    js  = get_js()
    js_out = get_js_outliers()
    q1_j = json.dumps(q1,        ensure_ascii=False)
    q2_j = json.dumps(q2,        ensure_ascii=False)
    q3_j = json.dumps(q3,        ensure_ascii=False)
    q4_j = json.dumps(q4,        ensure_ascii=False)
    p_j  = json.dumps(paises,    ensure_ascii=False)
    d_j  = json.dumps(divisiones,ensure_ascii=False)
    c_j  = json.dumps(categorias,ensure_ascii=False)

    hero_cards = _kpi_hero(kpi_comp, kpi_wm)

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>PGMB &mdash; Dashboard Comparativo SW7 vs SW8 &middot; 2026</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
  <style>{css}</style>
</head>
<body>

<!-- TOPBAR -->
<header class="topbar">
  <div class="topbar-brand">
    <div class="spark-icon">&#9889;</div>
    <div>
      <div class="topbar-title">PGMB Price Intelligence &mdash; Competidor vs Walmart</div>
      <div class="topbar-sub">k1_adhoc_tables.PGMB_PREMED_A0M1J1N &middot; ANIO=2026 &middot; SW IN(7,8)</div>
    </div>
  </div>
  <div class="topbar-badge">SW7 &#8594; SW8 &middot; 2026</div>
</header>

<!-- HERO -->
<section class="hero">
  <div class="hero-title">&#9878; Variaci&oacute;n de Precios &mdash; Semana 7 vs Semana 8 &middot; 2026</div>
  <div class="hero-sub">
    <strong style="color:#ffc220">Competidor</strong> (precio_comp_low) &nbsp;vs&nbsp;
    <strong style="color:#a0c4ff">Walmart</strong> (precio_wm_low)
    &mdash; JOIN corregido: ITEM + PAIS + COMPETIDOR + FORMATO + ZONA
  </div>
  <div class="hero-kpis" style="grid-template-columns:repeat(4,1fr)">
    {hero_cards}
  </div>
</section>

<!-- FILTER BAR -->
<div class="filter-bar">
  <span class="filter-label">&#127919; Filtros</span>
  <select id="fil-pais" onchange="renderAll()">
    <option value="">&#127757; Pa&iacute;s: Todos</option>
  </select>
  <select id="fil-div" onchange="renderAll()">
    <option value="">&#127968; Divisi&oacute;n: Todas</option>
  </select>
  <select id="fil-cat" onchange="renderAll()">
    <option value="">&#127991; Categor&iacute;a: Todas</option>
  </select>
  <button class="btn-reset" onclick="resetFilters()">&#x21ba; Limpiar</button>
</div>

<!-- MAIN -->
<div class="main">
  <div class="nav-tabs">
    <button class="nav-tab active" onclick="switchTab('overview',this)">&#128202; Vista General</button>
    <button class="nav-tab" onclick="switchTab('pais',this)">&#127757; Por Pa&iacute;s</button>
    <button class="nav-tab" onclick="switchTab('division',this)">&#127968; Por Divisi&oacute;n</button>
    <button class="nav-tab" onclick="switchTab('detalle',this)">&#128203; Detalle Tabla</button>
    <button class="nav-tab" onclick="switchTab('gap',this)">&#128269; Price Gap</button>
    <button class="nav-tab" onclick="switchTab('outliers',this)">&#9889; Outliers PG</button>
  </div>

  <!-- ======= OVERVIEW ======= -->
  <div id="panel-overview" class="tab-panel active">

    <div class="insight-bar">
      <div class="insight-pill">
        <strong>&#9432; C&oacute;mo leer el dashboard</strong>
        <strong style="color:var(--blue)">Colores s&oacute;lidos</strong> = Competidor &nbsp;|
        <strong style="color:#aaa">Colores transparentes</strong> = Walmart.
        Los donuts y barras muestran ambos simult&aacute;neamente para comparar.
      </div>
      <div class="insight-pill good">
        <strong>&#9989; JOIN corregido en esta versi&oacute;n</strong>
        Se join&oacute; por ITEM + PAIS + COMPETIDOR + FORMATO + CODIGO_ZONA.
        El JOIN anterior inflaba los conteos hasta 29&times; por efecto cartesiano.
      </div>
    </div>

    <!-- Donuts lado a lado -->
    <div class="grid-2">
      <div class="card">
        <div class="donut-wrap"><canvas id="donut-comp"></canvas></div>
      </div>
      <div class="card">
        <div class="donut-wrap"><canvas id="donut-wm"></canvas></div>
      </div>
    </div>

    <!-- Comp vs WM por segmento total -->
    <div class="card">
      <div class="chart-wrap"><canvas id="bar-seg-compare"></canvas></div>
    </div>

    <!-- Comp vs WM por país stacked -->
    <div class="card">
      <div class="chart-wrap"><canvas id="bar-pais-compare"></canvas></div>
    </div>

    <!-- Scorecards por país -->
    <div class="section-title">&#127760; Scorecards por Pa&iacute;s &mdash; Comp vs WM</div>
    <div class="country-grid" id="country-cards"></div>

  </div>

  <!-- ======= POR PAIS ======= -->
  <div id="panel-pais" class="tab-panel">
    <div class="insight-bar">
      <div class="insight-pill neutral">
        <strong>&#127757; An&aacute;lisis por Pa&iacute;s</strong>
        Cada barra agrupada muestra Comp (s&oacute;lido) vs WM (transparente) por segmento y pa&iacute;s.
      </div>
    </div>
    <div class="card">
      <div class="chart-wrap-lg"><canvas id="bar-comp-pais2"></canvas></div>
    </div>
    <div class="card">
      <div class="chart-wrap-lg"><canvas id="bar-wm-pais2"></canvas></div>
    </div>
  </div>

  <!-- ======= POR DIVISION ======= -->
  <div id="panel-division" class="tab-panel">
    <div class="insight-bar">
      <div class="insight-pill neutral">
        <strong>&#127968; An&aacute;lisis por Divisi&oacute;n</strong>
        Comparativa de variaci&oacute;n de precios por divisi&oacute;n comercial.
      </div>
    </div>
    <div class="card">
      <div class="chart-wrap-lg"><canvas id="bar-comp-div"></canvas></div>
    </div>
    <div class="card">
      <div class="chart-wrap-lg"><canvas id="bar-wm-div"></canvas></div>
    </div>
  </div>

  <!-- ======= DETALLE ======= -->
  <div id="panel-detalle" class="tab-panel">
    <div class="card">
      <div class="section-title">&#128202; Competidor &mdash; precio_comp_low (click columna para ordenar)</div>
      {_seg_table_html('tbl-comp','tbody-comp')}
    </div>
    <div class="card" style="margin-top:22px">
      <div class="section-title">&#127873; Walmart &mdash; precio_wm_low (click columna para ordenar)</div>
      {_seg_table_html('tbl-wm','tbody-wm')}
    </div>
  </div>

  <!-- ======= PRICE GAP ======= -->
  <div id="panel-gap" class="tab-panel">
    <div class="insight-bar">
      <div class="insight-pill warn">
        <strong>&#128269; Price Gap &mdash; PG = SUM(Factor_calc) / SUM(Peso_calc)</strong>
        Solo filas con Factor_calc y Peso_calc disponibles (Peso_calc &gt; 0). Base SW8 2026.
        Rojo = WM m&aacute;s caro (PG &lt; 0). Verde = WM m&aacute;s barato (PG &gt; 0).
      </div>
      <div class="insight-pill neutral">
        <strong>&#9878; F&oacute;rmula</strong>
        % PG = (SUM(Factor_calc) / SUM(Peso_calc)) &times; 100. Por Pa&iacute;s, Divisi&oacute;n, Categor&iacute;a. Base: SW8 2026.
      </div>
    </div>
    <div class="card">
      <div class="chart-wrap-lg"><canvas id="bar-gap"></canvas></div>
    </div>
    <div class="card">
      <div class="section-title">&#128203; Detalle Price Gap &mdash; Pa&iacute;s / Divisi&oacute;n / Categor&iacute;a</div>
      <div class="tbl-scroll">
        <table id="tbl-gap">
          <thead><tr>
            <th onclick="sortTable('tbl-gap',0)">Pa&iacute;s &#8597;</th>
            <th onclick="sortTable('tbl-gap',1)">Divisi&oacute;n &#8597;</th>
            <th onclick="sortTable('tbl-gap',2)">Categor&iacute;a &#8597;</th>
            <th onclick="sortTable('tbl-gap',3)" class="num">Items &#8597;</th>
            <th onclick="sortTable('tbl-gap',4)" class="num">SUM(Factor_calc) &#8597;</th>
            <th onclick="sortTable('tbl-gap',5)" class="num">SUM(Peso_calc) &#8597;</th>
            <th onclick="sortTable('tbl-gap',6)" class="num">% PG = F/P &#8597;</th>
            <th onclick="sortTable('tbl-gap',7)" class="num">% Avg Price Gap &#8597;</th>
          </tr></thead>
          <tbody id="tbody-gap"></tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- ======= OUTLIERS PRICE GAP ======= -->
  <div id="panel-outliers" class="tab-panel">

    <div class="insight-bar">
      <div class="insight-pill warn">
        <strong>&#9889; Outliers Negativos &mdash; Acci&oacute;n urgente</strong>
        Items donde WM est&aacute; significativamente m&aacute;s caro que la competencia.
        Rango: PG &lt; <span id="out-bound-lb" style="color:var(--red);font-weight:800">...</span> (Q1 &minus; 1.5&times;IQR).
      </div>
      <div class="insight-pill good">
        <strong>&#127881; Outliers Positivos &mdash; Ventaja competitiva</strong>
        Items donde WM est&aacute; significativamente m&aacute;s barato.
        Rango: PG &gt; <span id="out-bound-ub" style="color:var(--green);font-weight:800">...</span> (Q3 + 1.5&times;IQR).
      </div>
    </div>

    <!-- KPI mini cards -->
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:20px">
      <div class="card" style="text-align:center;border-top:4px solid var(--red)">
        <div style="font-size:.75rem;color:#888;text-transform:uppercase;letter-spacing:.4px">Outliers Negativos</div>
        <div id="out-kpi-neg" style="font-size:2rem;font-weight:900;color:var(--red)">...</div>
        <div id="out-pct-neg" style="font-size:.82rem;color:#888">del total</div>
      </div>
      <div class="card" style="text-align:center;border-top:4px solid var(--green)">
        <div style="font-size:.75rem;color:#888;text-transform:uppercase;letter-spacing:.4px">Outliers Positivos</div>
        <div id="out-kpi-pos" style="font-size:2rem;font-weight:900;color:var(--green)">...</div>
        <div id="out-pct-pos" style="font-size:.82rem;color:#888">del total</div>
      </div>
      <div class="card" style="text-align:center;border-top:4px solid #4a5568">
        <div style="font-size:.75rem;color:#888;text-transform:uppercase;letter-spacing:.4px">Rango Normal</div>
        <div id="out-kpi-norm" style="font-size:2rem;font-weight:900;color:#4a5568">...</div>
        <div style="font-size:.82rem;color:#888">items</div>
      </div>
      <div class="card" style="text-align:center;border-top:4px solid var(--blue)">
        <div style="font-size:.75rem;color:#888;text-transform:uppercase;letter-spacing:.4px">Total Items</div>
        <div id="out-kpi-tot" style="font-size:2rem;font-weight:900;color:var(--blue)">...</div>
        <div style="font-size:.82rem;color:#888">analizados</div>
      </div>
    </div>

    <!-- Chart outliers -->
    <div class="card">
      <div style="height:700px"><canvas id="chart-outliers"></canvas></div>
    </div>

    <!-- Tabla Outliers Negativos -->
    <div class="card">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">
        <div class="section-title" style="color:var(--red);margin-bottom:0">&#128308; Outliers Negativos &mdash; WM m&aacute;s caro (mayor urgencia)</div>
        <button class="btn-excel" onclick="downloadOutliersExcel()">
          &#11015; Descargar Excel
        </button>
      </div>
      <div class="tbl-scroll">
        <table id="tbl-out-neg">
          <thead><tr>
            <th class="num"># &#8597;</th>
            <th>Pa&iacute;s</th><th>Divisi&oacute;n</th><th>Categor&iacute;a</th>
            <th class="num">Item</th><th>Descripci&oacute;n</th><th>Marca</th>
            <th class="num">Filas</th><th class="num">% PG &#8597;</th>
          </tr></thead>
          <tbody id="tbody-out-neg"></tbody>
        </table>
      </div>
    </div>

    <!-- Tabla Outliers Positivos -->
    <div class="card" style="margin-top:22px">
      <div class="section-title" style="color:var(--green)">&#128994; Outliers Positivos &mdash; WM m&aacute;s barato (ventaja competitiva)</div>
      <div class="tbl-scroll">
        <table id="tbl-out-pos">
          <thead><tr>
            <th class="num"># &#8597;</th>
            <th>Pa&iacute;s</th><th>Divisi&oacute;n</th><th>Categor&iacute;a</th>
            <th class="num">Item</th><th>Descripci&oacute;n</th><th>Marca</th>
            <th class="num">Filas</th><th class="num">% PG &#8597;</th>
          </tr></thead>
          <tbody id="tbody-out-pos"></tbody>
        </table>
      </div>
    </div>

  </div>

  <footer class="footer">
    PGMB PREMED &mdash; wmt-k1-cons-data-users.k1_adhoc_tables.PGMB_PREMED_A0M1J1N
    &mdash; ANIO=2026 &middot; SW IN(7,8) &middot; JOIN: ITEM+PAIS+COMPETIDOR+FORMATO+CODIGO_ZONA
  </footer>
</div>

<script>
  const DATA_COMP     = {q1_j};
  const DATA_WM       = {q2_j};
  const DATA_GAP      = {q3_j};
  const DATA_OUTLIERS = {q4_j};
  const PAISES        = {p_j};
  const DIVISIONES    = {d_j};
  const CATEGORIAS    = {c_j};
  {js}
  {js_out}
</script>
</body>
</html>"""

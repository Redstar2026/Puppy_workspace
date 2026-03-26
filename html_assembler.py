"""Ensambla el HTML final del reporte CAM v6 (+ Etapa 2 Index)."""
from report_template import CSS, JS_LIB
from report_app import JS_APP
from report_index import JS_INDEX


def build_html(q1_json, q3_json, q_idx_json):
    """Genera el HTML completo con datos embebidos y mini-libreria canvas."""

    TABS_HTML = """
<div class="tabs">
  <button class="tab-btn active" onclick="showTab('t1',this)">1&#65039;&#8419; Conteos Semanal</button>
  <button class="tab-btn" onclick="showTab('t2',this)">2&#65039;&#8419; Tendencia Diaria</button>
  <button class="tab-btn" onclick="showTab('t3',this)">3&#65039;&#8419; Mes / Pais / Comp</button>
  <button class="tab-btn" onclick="showTab('t4',this)">4&#65039;&#8419; Caida FdS</button>
  <button class="tab-btn" onclick="showTab('t5',this)">5&#65039;&#8419; Deltas MoM</button>
  <button class="tab-btn" onclick="showTab('t6',this)">6&#65039;&#8419; Tendencias Competidor</button>
  <button class="tab-btn" onclick="showTab('tidx',this)" style="background:#fff3cd;border-color:#ffc220;color:#92400e">&#128200; INDEX FdS vs ES</button>

</div>"""

    FILTER_BAR = """
<div class="filters">
  <div class="flt-group">
    <span class="flt-label">&#127758; Pais</span>
    <select id="flt-pais" onchange="applyFilters()">
      <option value="">Todos los paises</option>
    </select>
  </div>
  <div class="flt-group">
    <span class="flt-label">&#127978; Competidor</span>
    <select id="flt-comp" onchange="applyFilters()">
      <option value="">Todos los competidores</option>
    </select>
  </div>
  <div class="flt-group">
    <span class="flt-label">&#128197; Mes</span>
    <select id="flt-mes" onchange="applyFilters()">
      <option value="">Todos los meses</option>
      <option value="2025-8">Agosto 2025</option>
      <option value="2025-9">Septiembre 2025</option>
      <option value="2025-10">Octubre 2025</option>
      <option value="2025-11">Noviembre 2025</option>
      <option value="2025-12">Diciembre 2025</option>
      <option value="2026-1">Enero 2026</option>
      <option value="2026-2">Febrero 2026</option>
      <option value="2026-3">Marzo 2026</option>
    </select>
  </div>
  <button class="btn-reset" onclick="resetFilters()">&#128260; Reset</button>
  <span id="total-info"></span>
</div>"""

    TAB1 = """
<div id="t1" class="tab-pane active">
  <div class="card">
    <h2>&#128198; Precio Normal por Semana &mdash; Entre Semana vs Fin de Semana</h2>
    <canvas id="c_sw_n" class="cc-lg"></canvas>
  </div>
  <div class="g2">
    <div class="card"><h2>&#127991;&#65039; Precio Oferta por Semana</h2>
      <canvas id="c_sw_o" class="cc"></canvas></div>
    <div class="card"><h2>&#128218; Precio Mayoreo por Semana</h2>
      <canvas id="c_sw_m" class="cc"></canvas></div>
  </div>
  <div class="card">
    <div class="sec-hdr">
      <h2>&#128203; Tabla Resumen Semanal</h2>
      <button class="btn-export" onclick="exportCSV('tb_sw','resumen_semanal.csv')">&#8595; CSV</button>
    </div>
    <div class="tbl-wrap">
      <table id="tb_sw">
        <thead><tr><th>Mes</th><th>Semana</th><th>Pais</th><th>Competidor</th>
          <th>Seg</th><th>Dia</th><th>Normal</th><th>Oferta</th><th>Mayoreo</th></tr></thead>
        <tbody id="tb_sw_body"></tbody>
      </table>
    </div>
  </div>
</div>"""

    TAB2 = """
<div id="t2" class="tab-pane">
  <div class="card">
    <div class="sec-hdr">
      <h2>&#128200; Conteo por Dia de la Semana</h2>
      <div class="filter-pills">
        <span class="fpill on" onclick="setDailyType('normal',this)">Normal</span>
        <span class="fpill" onclick="setDailyType('oferta',this)">Oferta</span>
        <span class="fpill" onclick="setDailyType('mayoreo',this)">Mayoreo</span>
      </div>
    </div>
    <p class="info-bar">Azul = Entre Semana (Lun&ndash;Jue) &nbsp;|&nbsp; Amarillo = Fin de Semana (Vie&ndash;Dom)</p>
    <canvas id="c_day" class="cc-lg"></canvas>
  </div>
  <div class="card" style="max-width:420px;margin:0 auto">
    <h2>&#129374; Distribucion ES vs FdS</h2>
    <canvas id="c_day_pie" class="cc"></canvas>
  </div>
</div>"""

    TAB3 = """
<div id="t3" class="tab-pane">
  <div class="card">
    <h2>&#128197; Precio Normal por Mes &mdash; Top 10 Competidores</h2>
    <p class="info-bar">Linea solida = Entre Semana &nbsp;|&nbsp; Linea discontinua = Fin de Semana</p>
    <canvas id="c_mes_n" class="cc-lg"></canvas>
  </div>
  <div class="g2">
    <div class="card"><h2>&#127991;&#65039; Precio Oferta por Mes</h2>
      <canvas id="c_mes_o" class="cc"></canvas></div>
    <div class="card"><h2>&#128218; Precio Mayoreo por Mes</h2>
      <canvas id="c_mes_m" class="cc"></canvas></div>
  </div>
</div>"""

    TAB4 = """
<div id="t4" class="tab-pane">
  <div class="card">
    <div class="sec-hdr">
      <h2>&#9888;&#65039; Conteo de Precios FdS por Mes y Competidor</h2>
      <div class="filter-pills">
        <span class="fpill on" onclick="setCaidaType('normal',this)">Normal</span>
        <span class="fpill" onclick="setCaidaType('oferta',this)">Oferta</span>
        <span class="fpill" onclick="setCaidaType('mayoreo',this)">Mayoreo</span>
      </div>
    </div>
    <p class="info-bar">Una linea que baja o toca cero indica caida de cobertura en fines de semana para ese competidor.</p>
    <canvas id="c_caida" class="cc-lg"></canvas>
  </div>
  <div class="card">
    <h2>&#128203; Semanas con Cero Chequeos FdS por Competidor</h2>
    <div class="tbl-wrap">
      <table>
        <thead><tr><th>Pais</th><th>Competidor</th><th>0 FdS Normal</th>
          <th>0 FdS Oferta</th><th>0 FdS Mayoreo</th><th>Total Sem.</th><th>% sin FdS</th></tr></thead>
        <tbody id="tb_caida_body"></tbody>
      </table>
    </div>
  </div>
</div>"""

    TAB5 = """
<div id="t5" class="tab-pane">
  <div class="card">
    <h2>&#128202; Evolucion Mensual &mdash; Precio Normal (Top 8 Competidores)</h2>
    <canvas id="c_mom" class="cc-lg"></canvas>
  </div>
  <div class="card">
    <div class="sec-hdr">
      <h2>&#128203; Tabla Deltas Mes a Mes</h2>
      <button class="btn-export" onclick="exportCSV('tb_mom','deltas_mom.csv')">&#8595; CSV</button>
    </div>
    <div class="tbl-wrap">
      <table id="tb_mom">
        <thead><tr><th>Pais</th><th>Competidor</th><th>Mes</th><th>Seg</th>
          <th>Cnt Normal</th><th>&#916; Normal</th>
          <th>Cnt Oferta</th><th>&#916; Oferta</th>
          <th>Cnt Mayoreo</th><th>&#916; Mayoreo</th></tr></thead>
        <tbody id="tb_mom_body"></tbody>
      </table>
    </div>
  </div>
</div>"""

    TAB6 = """
<div id="t6" class="tab-pane">
  <div class="card">
    <div class="sec-hdr">
      <h2>&#128200; Tendencia Mensual por Competidor</h2>
      <div style="display:flex;gap:16px;flex-wrap:wrap">
        <div class="filter-pills">
          <span class="fpill on" onclick="setTrendSeg('ambos',this)">ES + FdS</span>
          <span class="fpill" onclick="setTrendSeg('es',this)">Solo ES</span>
          <span class="fpill" onclick="setTrendSeg('fds',this)">Solo FdS</span>
        </div>
        <div class="filter-pills">
          <span class="fpill on" onclick="setTrendType('normal',this)">Normal</span>
          <span class="fpill" onclick="setTrendType('oferta',this)">Oferta</span>
          <span class="fpill" onclick="setTrendType('mayoreo',this)">Mayoreo</span>
        </div>
      </div>
    </div>
    <canvas id="c_trend" class="cc-lg"></canvas>
  </div>
  <div class="card">
    <h2>&#128202; ES vs FdS en el Ultimo Mes disponible</h2>
    <canvas id="c_trend_esfd" class="cc"></canvas>
  </div>
</div>"""

    TAB_INDEX = """
<div id="tidx" class="tab-pane">

  <!-- KPIs -->
  <div style="display:grid;grid-template-columns:repeat(6,1fr);gap:10px;margin-bottom:14px">
    <div class="card" style="text-align:center;padding:12px 8px">
      <div style="font-size:9px;color:#6b7280;font-weight:700;text-transform:uppercase;margin-bottom:4px">Index Normal</div>
      <div id="kpi_idx_n" class="kpi-val" style="font-size:20px;font-weight:800">-</div>
      <div style="font-size:9px;color:#6b7280;margin-top:2px">- = FdS mas barato</div>
    </div>
    <div class="card" style="text-align:center;padding:12px 8px">
      <div style="font-size:9px;color:#6b7280;font-weight:700;text-transform:uppercase;margin-bottom:4px">Index Oferta</div>
      <div id="kpi_idx_o" class="kpi-val" style="font-size:20px;font-weight:800">-</div>
      <div style="font-size:9px;color:#6b7280;margin-top:2px">- = FdS mas barato</div>
    </div>
    <div class="card" style="text-align:center;padding:12px 8px">
      <div style="font-size:9px;color:#6b7280;font-weight:700;text-transform:uppercase;margin-bottom:4px">Index Mayoreo</div>
      <div id="kpi_idx_m" class="kpi-val" style="font-size:20px;font-weight:800">-</div>
      <div style="font-size:9px;color:#6b7280;margin-top:2px">- = FdS mas barato</div>
    </div>
    <div class="card" style="text-align:center;padding:12px 8px">
      <div style="font-size:9px;color:#6b7280;font-weight:700;text-transform:uppercase;margin-bottom:4px">UPCs Comparables</div>
      <div id="kpi_upcs" style="font-size:20px;font-weight:800;color:#0053e2">-</div>
      <div style="font-size:9px;color:#6b7280;margin-top:2px">Con precio ES y FdS</div>
    </div>
    <div class="card" style="text-align:center;padding:12px 8px">
      <div style="font-size:9px;color:#6b7280;font-weight:700;text-transform:uppercase;margin-bottom:4px">Rotaciones (M)</div>
      <div id="kpi_rot" style="font-size:20px;font-weight:800;color:#2a8703">-</div>
      <div style="font-size:9px;color:#6b7280;margin-top:2px">Millones rotaciones</div>
    </div>
    <div class="card" style="text-align:center;padding:12px 8px">
      <div style="font-size:9px;color:#6b7280;font-weight:700;text-transform:uppercase;margin-bottom:4px">Comps FdS &lt; ES</div>
      <div id="kpi_comps_baja" style="font-size:20px;font-weight:800;color:#ea1100">-</div>
      <div id="kpi_comps_baja_list" style="font-size:8px;color:#6b7280;margin-top:2px">-</div>
    </div>
  </div>

  <div class="info-bar">
    <b>Metodologia del Volumen:</b>
    Vol<sub>ES</sub> = &Sigma;<sub>UPC</sub> [SUM(precio_dia<sub>ES</sub>) &times; rotaciones<sub>UPC</sub>] &nbsp;&nbsp;
    Vol<sub>FdS</sub> = &Sigma;<sub>UPC</sub> [SUM(precio_dia<sub>FdS</sub>) &times; rotaciones<sub>UPC</sub>]
    &nbsp;|&nbsp; <b>Index = (Vol<sub>FdS</sub> &minus; Vol<sub>ES</sub>) / Vol<sub>ES</sub></b>
    &nbsp;|&nbsp; SUM de precios diarios por segmento refleja cobertura real de checkeos.
    <br>Solo UPCs con precio Normal en <b>ambos</b> segmentos son comparables.
    &#9660; Negativo = FdS mas barato &nbsp;|&nbsp; &#9650; Positivo = FdS mas caro.
  </div>

  <!-- Cobertura: grafica mas importante para detectar ausencia de precios FdS -->
  <div class="card" style="border-left:4px solid #ea1100">
    <h2>&#128269; Cobertura de Checkeos: Dias con Precio ES vs FdS por Competidor</h2>
    <p style="font-size:11px;color:#6b7280;margin-bottom:6px">
      Si la barra FdS (azul claro / amarillo) es mucho menor que la barra ES,
      significa que <b>no se estan capturando precios de fin de semana</b> para ese competidor.
      Dias maximos: ES=4 (L-J), FdS=3 (V-D).
    </p>
    <div style="height:340px"><canvas id="c_idx_cobertura" style="width:100%;height:100%"></canvas></div>
  </div>

  <div class="card">
    <h2>&#128200; Index Normal FdS vs ES por Semana por Competidor</h2>
    <div style="height:340px"><canvas id="c_idx_normal" style="width:100%;height:100%"></canvas></div>
  </div>

  <div class="g2">
    <div class="card">
      <h2>&#127991;&#65039; Index Oferta por Semana</h2>
      <div style="height:300px"><canvas id="c_idx_oferta" style="width:100%;height:100%"></canvas></div>
    </div>
    <div class="card">
      <h2>&#127978; Index Mayoreo por Semana</h2>
      <div style="height:300px"><canvas id="c_idx_mayoreo" style="width:100%;height:100%"></canvas></div>
    </div>
  </div>

  <div class="g2">
    <div class="card">
      <h2>&#127758; Index Promedio por Pais</h2>
      <div style="height:280px"><canvas id="c_idx_pais" style="width:100%;height:100%"></canvas></div>
    </div>
    <div class="card">
      <h2>&#128210; Precio Normal Promedio ES vs FdS</h2>
      <div style="height:280px"><canvas id="c_idx_precio" style="width:100%;height:100%"></canvas></div>
    </div>
  </div>

  <div class="card">
    <h2>&#128101; UPCs: FdS mas Barato / Igual / Mas Caro en Precio Normal</h2>
    <div style="height:320px"><canvas id="c_idx_upcs" style="width:100%;height:100%"></canvas></div>
  </div>

  <div class="card">
    <div class="sec-hdr">
      <h2>&#128203; Tabla Detalle por Competidor / Semana</h2>
      <button class="btn-export" onclick="exportCSV('tb_idx','index_fds_es.csv')">&#8595; CSV</button>
    </div>
    <div class="tbl-wrap">
      <table id="tb_idx">
        <thead><tr>
          <th>Pais</th><th>Competidor</th><th>Semana</th>
          <th>UPCs</th><th>Rotaciones</th>
          <th>Dias ES</th><th>Dias FdS</th>
          <th>P.Normal ES</th><th>P.Normal FdS</th><th>Idx Normal</th>
          <th>P.Oferta ES</th><th>P.Oferta FdS</th><th>Idx Oferta</th>
          <th>P.Mayoreo ES</th><th>P.Mayoreo FdS</th><th>Idx Mayoreo</th>
          <th>UPCs FdS Barato</th><th>UPCs FdS Caro</th>
        </tr></thead>
        <tbody id="tb_idx_body"></tbody>
      </table>
    </div>
  </div>

</div>"""


    script = f"""
<script>
const RAW_Q1 = {q1_json};
const RAW_Q3 = {q3_json};
const RAW_IDX = {q_idx_json};
{JS_LIB}
{JS_APP}
{JS_INDEX}
// Inicializar Index una vez que IDX ya esta definido
IDX.render();
</script>"""

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>Analisis de Precios CAM - Entre Semana vs Fines de Semana</title>
  <style>{CSS}</style>
</head>
<body>
<div class="hdr">
  <span style="font-size:26px">&#128202;</span>
  <div>
    <h1>Analisis de Precios CAM</h1>
    <p class="hdr-sub">Entre Semana (Lun&ndash;Jue) vs Fines de Semana (Vie&ndash;Dom) &middot; Ago 2025 &ndash; Mar 2026</p>
  </div>
  <div style="margin-left:auto;display:flex;gap:8px">
    <span class="badge badge-es">Entre Semana</span>
    <span class="badge badge-fds">Fin de Semana</span>
  </div>
</div>
{FILTER_BAR}
{TABS_HTML}
{TAB1}{TAB2}{TAB3}{TAB4}{TAB5}{TAB6}{TAB_INDEX}
{script}
</body>
</html>"""

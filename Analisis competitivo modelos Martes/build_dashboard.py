"""
Dashboard Builder — Análisis Semanal de Impactos Modelo
Genera un reporte HTML interactivo (5 segmentos) a partir de los CSVs de BigQuery.
"""
import csv, json, os, glob
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))

# ── Carga de datos ────────────────────────────────────────────────
def find_csv(pattern):
    m = glob.glob(os.path.join(BASE, pattern))
    return m[0] if m else None

def load_csv(pattern):
    path = find_csv(pattern)
    if not path:
        return []
    with open(path, encoding="utf-8") as f:
        rows = []
        for r in csv.DictReader(f):
            row = {}
            for k, v in r.items():
                if v in ("", "NULL", "None", None):
                    row[k] = None
                else:
                    try: row[k] = int(v)
                    except ValueError:
                        try: row[k] = float(v)
                        except ValueError: row[k] = v
            rows.append(row)
        return rows

def jdump(obj):
    return json.dumps(obj, ensure_ascii=False, default=str)

# ── Formateadores ─────────────────────────────────────────────────
def fmt_m(v):
    if v is None: return "N/A"
    av, sign = abs(float(v)), ("-" if float(v) < 0 else "")
    if av >= 1_000_000: return f"{sign}${av/1_000_000:.2f}M"
    if av >= 1_000:     return f"{sign}${av/1_000:.1f}K"
    return f"{sign}${av:.0f}"

def fmt_pct(v, d=2):
    return "N/A" if v is None else f"{float(v):.{d}f}%"

def html_currency(v):
    if v is None: return "-"
    fv = float(v)
    c = "#ea1100" if fv < 0 else ("#2a8703" if fv > 0 else "#6b7280")
    return f'<span style="color:{c};font-weight:600">{fmt_m(fv)}</span>'

def html_pct(v):
    if v is None: return "-"
    fv = float(v)
    c = "#ea1100" if fv < 0 else ("#2a8703" if fv > 0 else "#6b7280")
    return f'<span style="color:{c}">{fv:.2f}%</span>'

# ── Componentes HTML ──────────────────────────────────────────────
def kpi_card(label, value, kind="neutral"):
    border = {"pos":"border-green-500","neg":"border-red-500","warn":"border-yellow-400"}.get(kind,"border-blue-600")
    return f"""<div class="bg-white rounded-lg p-3 shadow-sm border-l-4 {border}">
      <div class="text-xs text-gray-500 uppercase tracking-wide font-medium">{label}</div>
      <div class="text-xl font-bold mt-1 text-blue-700">{value}</div></div>"""

def nav_btn(n, label, active=False):
    cls = "active " if active else ""
    return f'<button id="nav{n}" data-seg="{n}" class="nav-btn {cls}px-4 py-2 rounded-full border text-sm font-semibold" style="border-color:#0053e2;color:#0053e2">{label}</button>'

def subtabs(seg, labels):
    out = ""
    for i, lbl in enumerate(labels):
        cls = "active" if i == 0 else ""
        out += f'<span class="tab-sub {cls}" data-grp="s{seg}" data-target="s{seg}p{i}">{lbl}</span>'
    return out

def chart_bar(cid, labels, datasets, title="", height=280):
    title_html = f"<h3 class='font-semibold mb-2 text-sm text-gray-700'>{title}</h3>" if title else ""
    return f"""<div class="bg-white rounded-lg shadow-sm p-4 mb-4">
      {title_html}
      <div style="position:relative;height:{height}px"><canvas id="{cid}"></canvas></div></div>
    <script>(function(){{var c=document.getElementById('{cid}');if(!c)return;
      new Chart(c.getContext('2d'),{{type:'bar',data:{{labels:{jdump(labels)},datasets:{jdump(datasets)}}},
      options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{position:'top'}}}},
      scales:{{y:{{beginAtZero:false}},x:{{ticks:{{maxRotation:45}}}}}}}}}});}})();</script>"""

def chart_doughnut(cid, labels, data_vals, title="", height=260):
    colors = ["#0053e2","#ffc220","#2a8703","#ea1100","#7c3aed","#0891b2","#db2777","#d97706","#65a30d","#9333ea"]
    title_html = f"<h3 class='font-semibold mb-2 text-sm text-gray-700'>{title}</h3>" if title else ""
    return f"""<div class="bg-white rounded-lg shadow-sm p-4 mb-4">
      {title_html}
      <div style="position:relative;height:{height}px"><canvas id="{cid}"></canvas></div></div>
    <script>(function(){{var c=document.getElementById('{cid}');if(!c)return;
      new Chart(c.getContext('2d'),{{type:'doughnut',data:{{labels:{jdump(labels)},
      datasets:[{{data:{jdump(data_vals)},backgroundColor:{jdump(colors[:len(data_vals)])}}}]}},
      options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{position:'right'}}}}}}}});}})();</script>"""

def insight(text):
    return f'<div class="insight-box text-sm mb-2">💡 {text}</div>'

def data_table(headers, rows, tid, row_fn, scrollable=True):
    ths = "".join(f'<th class="px-2 py-2 text-left text-xs font-semibold text-gray-600 border-b bg-gray-50">{h}</th>' for h in headers)
    tbody = "".join(row_fn(r) for r in rows)
    wrap_class = 'style="max-height:480px;overflow-y:auto"' if scrollable else ""
    return f"""<div class="overflow-x-auto bg-white rounded-lg shadow-sm" {wrap_class}>
      <table id="{tid}" class="w-full text-xs"><thead><tr>{ths}</tr></thead><tbody>{tbody}</tbody></table></div>"""

# ── Segmento 1 — General ─────────────────────────────────────────
def seg1_metrics_row_fn(dim_key):
    def fn(r):
        tw = r.get("costo_comp_ho_tw") or 0
        lw = r.get("costo_comp_inicial_lw") or 0
        delta = tw - lw
        return f"""<tr>
          <td class="px-2 py-1.5 border-b font-semibold">{r.get(dim_key) or "-"}</td>
          <td class="px-2 py-1.5 border-b">{html_currency(tw)}</td>
          <td class="px-2 py-1.5 border-b">{html_currency(lw)}</td>
          <td class="px-2 py-1.5 border-b">{html_currency(delta)}</td>
          <td class="px-2 py-1.5 border-b text-right">{int(r.get('cambios_precios_tw') or 0):,}</td>
          <td class="px-2 py-1.5 border-b text-right">{int(r.get('cambios_precios_lw') or 0):,}</td>
          <td class="px-2 py-1.5 border-b">{html_pct(r.get('pct_pg_actual_tw'))}</td>
          <td class="px-2 py-1.5 border-b">{html_pct(r.get('pct_mb_actual_tw'))}</td>
          <td class="px-2 py-1.5 border-b">{html_pct(r.get('pct_pg_ho_inicial'))}</td>
          <td class="px-2 py-1.5 border-b">{html_pct(r.get('pct_mb_ho_inicial'))}</td>
          <td class="px-2 py-1.5 border-b">{html_pct(r.get('bps_mb_ho'))}</td>
          <td class="px-2 py-1.5 border-b">{html_pct(r.get('pct_pg_medicion_tw'))}</td>
          <td class="px-2 py-1.5 border-b">{html_pct(r.get('pct_mb_tw_medicion'))}</td>
          <td class="px-2 py-1.5 border-b text-gray-400">{int(r.get('total_items') or 0):,}</td>
        </tr>"""
    return fn

S1_HDRS = ["Dimensión","CC TW","CC LW","Δ CC","Cambios TW","Cambios LW","% PG Actual","% MB Actual","% PG HO Ini","% MB HO Ini","BPS MB","% PG Med TW","% MB Med TW","Ítems"]

def build_seg1_pais(q1):
    paises = [r["pais"] for r in q1]
    cc_tw  = [round(r.get("costo_comp_ho_tw") or 0) for r in q1]
    cc_lw  = [round(r.get("costo_comp_inicial_lw") or 0) for r in q1]
    chg_tw = [r.get("cambios_precios_tw") or 0 for r in q1]
    pg_act = [r.get("pct_pg_actual_tw") or 0 for r in q1]
    mb_act = [r.get("pct_mb_actual_tw") or 0 for r in q1]

    max_inv = min(q1, key=lambda r: (r.get("costo_comp_ho_tw") or 0) - (r.get("costo_comp_inicial_lw") or 0))
    max_oxy = max(q1, key=lambda r: (r.get("costo_comp_ho_tw") or 0) - (r.get("costo_comp_inicial_lw") or 0))
    max_pg  = max(q1, key=lambda r: r.get("pct_pg_actual_tw") or 0)

    c1 = chart_bar("ch_pais_cc", paises, [
        {"label":"CC TW","data":cc_tw,"backgroundColor":"#0053e2","borderRadius":4},
        {"label":"CC LW","data":cc_lw,"backgroundColor":"#93c5fd","borderRadius":4},
    ], "Costo Competitivo Inicial — TW vs LW")
    c2 = chart_bar("ch_pais_chg", paises, [
        {"label":"Cambios Precio TW","data":chg_tw,"backgroundColor":"#ffc220","borderRadius":4},
    ], "Cambios de Precio — Por País")
    c3 = chart_bar("ch_pais_pgmb", paises, [
        {"label":"% PG Actual","data":pg_act,"backgroundColor":"#2a8703","borderRadius":4},
        {"label":"% MB Actual","data":mb_act,"backgroundColor":"#0891b2","borderRadius":4},
    ], "% PG y % MB Actual — Por País")

    ins = (insight(f"Mayor inversión: <b>{max_inv['pais']}</b> con Δ CC {fmt_m((max_inv.get('costo_comp_ho_tw') or 0)-(max_inv.get('costo_comp_inicial_lw') or 0))} — mayor presión competitiva regional") +
           insight(f"Mayor oxigenación: <b>{max_oxy['pais']}</b> con Δ CC {fmt_m((max_oxy.get('costo_comp_ho_tw') or 0)-(max_oxy.get('costo_comp_inicial_lw') or 0))} — recuperación de competitividad vs semana anterior") +
           insight(f"Mejor PG Actual: <b>{max_pg['pais']}</b> con {fmt_pct(max_pg.get('pct_pg_actual_tw'))} — ejecución del modelo más alineada") +
           insight("BPS MB negativo generalizado (≈ -200 a -300 bps) — presión de margen sistémica en toda la región; priorizar recuperación en TIER_1"))

    tbl = data_table(S1_HDRS, q1, "tbl_pais", seg1_metrics_row_fn("pais"), scrollable=False)
    return f'<div class="grid grid-cols-1 lg:grid-cols-3 gap-4">{c1}{c2}{c3}</div>{ins}{tbl}'

def build_seg1_div(q2):
    dims   = [r["division"] for r in q2]
    cc_tw  = [round(r.get("costo_comp_ho_tw") or 0) for r in q2]
    cc_lw  = [round(r.get("costo_comp_inicial_lw") or 0) for r in q2]
    pg_act = [r.get("pct_pg_actual_tw") or 0 for r in q2]

    c1 = chart_bar("ch_div_cc", dims, [
        {"label":"CC TW","data":cc_tw,"backgroundColor":"#0053e2","borderRadius":4},
        {"label":"CC LW","data":cc_lw,"backgroundColor":"#93c5fd","borderRadius":4},
    ], "Costo Competitivo — Por División (TW vs LW)")
    c2 = chart_bar("ch_div_pg", dims, [
        {"label":"% PG Actual","data":pg_act,"backgroundColor":"#2a8703","borderRadius":4},
    ], "% PG Actual — Por División")

    ins = (insight("ABARROTES: mayor inversión CC acumulada (-$2.26M TW) — categoría de referencia para el consumidor, alta sensibilidad") +
           insight("FARMACIA muestra oxigenación CC (+$58K) — menor presión competitiva directa, evaluar oportunidad de margen") +
           insight("MI (Mercadería Intensiva): recupera $187K en CC vs LW — señal de mejora competitiva en perecederos") +
           insight("FRUTAS Y VEGETALES: delta CC negativo urgente (-$71K) — altamente influenciado por estacionalidad y precios spot"))

    tbl = data_table(S1_HDRS, q2, "tbl_div", seg1_metrics_row_fn("division"), scrollable=False)
    return f'<div class="grid grid-cols-1 lg:grid-cols-2 gap-4">{c1}{c2}</div>{ins}{tbl}'

def build_seg1_tier(q3):
    tiers = [r["tier"] for r in q3]
    cc_tw = [round(r.get("costo_comp_ho_tw") or 0) for r in q3]
    cc_lw = [round(r.get("costo_comp_inicial_lw") or 0) for r in q3]
    items = [r.get("total_items") or 0 for r in q3]

    c1 = chart_bar("ch_tier_cc", tiers, [
        {"label":"CC TW","data":cc_tw,"backgroundColor":"#0053e2","borderRadius":4},
        {"label":"CC LW","data":cc_lw,"backgroundColor":"#93c5fd","borderRadius":4},
    ], "Costo Competitivo — Por Tier")
    c2 = chart_doughnut("ch_tier_items", tiers, items, "Distribución de Ítems por Tier")

    ins = (insight("TIER_3: mayor inversión CC TW (-$2.17M) con mayor volumen (369K ítems) — ítems de alta rotación bajo ataque competitivo") +
           insight("TIER_1 y TIER_2 oxigenan vs LW — recuperación de competitividad en ítems de referencia de mercado") +
           insight("PG TIER_2 (9.13%) supera a TIER_1 (6.48%) — revisar alineación de metas por segmento"))

    tbl = data_table(S1_HDRS, q3, "tbl_tier", seg1_metrics_row_fn("tier"), scrollable=False)
    return f'<div class="grid grid-cols-1 lg:grid-cols-2 gap-4">{c1}{c2}</div>{ins}{tbl}'

def build_seg1_flag(data, flag_key, title, cid_suffix):
    labels = [str(r.get(flag_key) or "NULL") for r in data]
    items  = [r.get("total_items") or 0 for r in data]
    cc_tw  = [round(r.get("costo_comp_ho_tw") or 0) for r in data]

    c1 = chart_doughnut(f"ch_fd_{cid_suffix}", labels, items, f"Distribución — {title}")
    c2 = chart_bar(f"ch_fb_{cid_suffix}", labels, [
        {"label":"CC TW","data":cc_tw,"backgroundColor":"#0053e2","borderRadius":4},
    ], f"CC TW — {title}")

    hdrs = [title,"Ítems","CC TW","CC LW","% PG Actual","% MB Actual","% PG HO Ini","% MB HO Ini"]
    def row_fn(r):
        return f"""<tr>
          <td class="px-2 py-1.5 border-b font-semibold">{r.get(flag_key) or "NULL"}</td>
          <td class="px-2 py-1.5 border-b text-right">{int(r.get('total_items') or 0):,}</td>
          <td class="px-2 py-1.5 border-b">{html_currency(r.get('costo_comp_ho_tw'))}</td>
          <td class="px-2 py-1.5 border-b">{html_currency(r.get('costo_comp_inicial_lw'))}</td>
          <td class="px-2 py-1.5 border-b">{html_pct(r.get('pct_pg_actual_tw'))}</td>
          <td class="px-2 py-1.5 border-b">{html_pct(r.get('pct_mb_actual_tw'))}</td>
          <td class="px-2 py-1.5 border-b">{html_pct(r.get('pct_pg_ho_inicial'))}</td>
          <td class="px-2 py-1.5 border-b">{html_pct(r.get('pct_mb_ho_inicial'))}</td>
        </tr>"""
    tbl = data_table(hdrs, data, f"tbl_{cid_suffix}", row_fn, scrollable=False)
    return f'<div class="grid grid-cols-1 lg:grid-cols-2 gap-4">{c1}{c2}</div>{tbl}'

# ── Segmento 2 — Calidad ─────────────────────────────────────────
def build_seg2_performance(q7):
    top12 = q7[:12]
    labels = [r.get("PERFORMANCE_PRIMARIO") or "NULL" for r in top12]
    items  = [r.get("total_items") or 0 for r in top12]
    cc_tw  = [round(r.get("costo_comp_ho_tw") or 0) for r in top12]

    c1 = chart_doughnut("ch_perf_d", labels[:8], items[:8], "Distribución Items — Performance (Top 8)")
    c2 = chart_bar("ch_perf_b", labels, [
        {"label":"CC TW","data":cc_tw,"backgroundColor":"#0053e2","borderRadius":4},
    ], "CC TW por Performance")

    ins = (insight("NEG 4 WKS: -$2.07M CC — ítems con PG negativo sostenido, requieren revisión estratégica urgente de precios") +
           insight("EXCEDIDO 4 WKS: +$1.27M CC — buen performance pero bajo ataque competitivo creciente") +
           insight("BAJO META 4 WKS: -$393K CC — riesgo de erosión de margen sin cumplir objetivo de PG") +
           insight("MP (Marca Propia): CC equilibrado — evaluar espacio de margen sin perder posición vs competencia"))

    hdrs = ["Performance","Ítems","CC TW","CC LW","% PG Actual","% PG HO Ini","% MB Actual","% MB HO Ini"]
    def row_fn(r):
        return f"""<tr>
          <td class="px-2 py-1.5 border-b font-semibold">{r.get('PERFORMANCE_PRIMARIO') or "NULL"}</td>
          <td class="px-2 py-1.5 border-b text-right">{int(r.get('total_items') or 0):,}</td>
          <td class="px-2 py-1.5 border-b">{html_currency(r.get('costo_comp_ho_tw'))}</td>
          <td class="px-2 py-1.5 border-b">{html_currency(r.get('costo_comp_inicial_lw'))}</td>
          <td class="px-2 py-1.5 border-b">{html_pct(r.get('pct_pg_actual_tw'))}</td>
          <td class="px-2 py-1.5 border-b">{html_pct(r.get('pct_pg_ho_inicial'))}</td>
          <td class="px-2 py-1.5 border-b">{html_pct(r.get('pct_mb_actual_tw'))}</td>
          <td class="px-2 py-1.5 border-b">{html_pct(r.get('pct_mb_ho_inicial'))}</td>
        </tr>"""
    tbl = data_table(hdrs, q7, "tbl_perf", row_fn)
    return f'<div class="grid grid-cols-1 lg:grid-cols-2 gap-4">{c1}{c2}</div>{ins}{tbl}'

def build_seg2_rangos_cc(q8):
    labels = [r.get("RANGOS_COSTO_COMPETITIVO_INICIAL") or "NULL" for r in q8]
    items  = [r.get("total_items") or 0 for r in q8]
    pg     = [r.get("pct_pg_actual_tw") or 0 for r in q8]

    c1 = chart_doughnut("ch_rcc_d", labels[:10], items[:10], "Distribución Ítems por Rango CC (Top 10)")
    c2 = chart_bar("ch_rcc_pg", labels, [
        {"label":"% PG Actual","data":pg,"backgroundColor":"#2a8703","borderRadius":4},
    ], "% PG Actual por Rango CC")

    ins = (insight("78% de ítems con CC = 0$ — sin referencia competitiva directa; evaluar pricing autónomo basado en elasticidad") +
           insight("Rango -250$~0$ con PG -5.4%: zona crítica de inversión que erosiona margen — acción correctiva necesaria") +
           insight("Rangos extremos (<-4000$): pocas SKUs pero con impacto financiero significativo — identificar y escalar"))

    hdrs = ["Rango CC","Ítems","CC TW","% PG Actual","% MB Actual"]
    def row_fn(r):
        return f"""<tr>
          <td class="px-2 py-1.5 border-b font-semibold">{r.get('RANGOS_COSTO_COMPETITIVO_INICIAL') or "NULL"}</td>
          <td class="px-2 py-1.5 border-b text-right">{int(r.get('total_items') or 0):,}</td>
          <td class="px-2 py-1.5 border-b">{html_currency(r.get('costo_comp_ho_tw'))}</td>
          <td class="px-2 py-1.5 border-b">{html_pct(r.get('pct_pg_actual_tw'))}</td>
          <td class="px-2 py-1.5 border-b">{html_pct(r.get('pct_mb_actual_tw'))}</td>
        </tr>"""
    return f'<div class="grid grid-cols-1 lg:grid-cols-2 gap-4">{c1}{c2}</div>{ins}{data_table(hdrs, q8, "tbl_rcc", row_fn, scrollable=False)}'

def build_seg2_rango_pg(q9):
    rang_pg = sorted(set(r.get("RANGO_PG_ACTUAL") for r in q9 if r.get("RANGO_PG_ACTUAL")))
    by_rp = {rp: sum(r.get("total_items") or 0 for r in q9 if r.get("RANGO_PG_ACTUAL")==rp) for rp in rang_pg}
    c1 = chart_doughnut("ch_rpg_d", list(by_rp.keys()), list(by_rp.values()), "Distribución Ítems por Rango PG Actual")

    ins = (insight("0%~5% PG: zona de mayor concentración — margen ajustado con alta sensibilidad a movimientos competitivos") +
           insight(">15% PG: 61K ítems — oportunidad de inversión controlada para ganar share sin sacrificar margen total") +
           insight("PG negativo en ~57K ítems — zona de alerta prioritaria; correlacionar con TIER y competidor para acción"))

    hdrs = ["Rango PG","Meta","Ítems","% PG Actual","% MB Actual"]
    def row_fn(r):
        return f"""<tr>
          <td class="px-2 py-1.5 border-b">{r.get('RANGO_PG_ACTUAL') or "NULL"}</td>
          <td class="px-2 py-1.5 border-b">{r.get('RANGO_META') or "NULL"}</td>
          <td class="px-2 py-1.5 border-b text-right">{int(r.get('total_items') or 0):,}</td>
          <td class="px-2 py-1.5 border-b">{html_pct(r.get('pct_pg_actual_tw'))}</td>
          <td class="px-2 py-1.5 border-b">{html_pct(r.get('pct_mb_actual_tw'))}</td>
        </tr>"""
    return f'{c1}{ins}{data_table(hdrs, q9, "tbl_rpg", row_fn)}'

def build_seg2_rango_meta(q9):
    metas = sorted(set(r.get("RANGO_META") for r in q9 if r.get("RANGO_META")))
    by_m  = {m: sum(r.get("total_items") or 0 for r in q9 if r.get("RANGO_META")==m) for m in metas}
    c1 = chart_doughnut("ch_rmeta_d", list(by_m.keys()), list(by_m.values()), "Distribución Ítems por Rango Meta")

    ins = (insight("SOBRE META: 164K ítems — 25%+ del portafolio con indicador supera la meta de PG definida") +
           insight("EN META: 154K ítems — ejecución alineada al modelo; mantener disciplina de reacción") +
           insight("BAJO META - NEGATIVO: 28K ítems con PG negativo — requieren acción correctiva prioritaria esta semana") +
           insight("BAJO META: 67K ítems — zona de mejora; revisar si el gap es por presión competitiva o gestión de precios interna"))
    return f'{c1}{ins}'

# ── Segmento 3 — Categoría / Competidor ─────────────────────────
def build_seg3(q10):
    paises = sorted(set(r.get("pais") for r in q10 if r.get("pais")))
    divs   = sorted(set(r.get("division") for r in q10 if r.get("division")))
    tiers  = sorted(set(r.get("tier") for r in q10 if r.get("tier")))

    filters = f"""<div class="flex flex-wrap gap-3 mb-4 items-center bg-white p-4 rounded-lg shadow-sm">
      <select id="f3pais"><option value="">🌎 Todos los Países</option>{"".join(f'<option>{p}</option>' for p in paises)}</select>
      <select id="f3div"><option value="">🏢 Todas las Divisiones</option>{"".join(f'<option>{d}</option>' for d in divs)}</select>
      <input type="text" id="f3cat" placeholder="🔍 Categoría..." style="width:180px"/>
      <select id="f3tier"><option value="">🎯 Todos los Tiers</option>{"".join(f'<option>{t}</option>' for t in tiers)}</select>
      <select id="f3top">
        <option value="">Todos los registros</option>
        <option value="inv">📉 Top 10 Mayor Inversión (Δ CC -)</option>
        <option value="oxy">📈 Top 10 Mayor Oxigenación (Δ CC +)</option>
      </select>
      <span id="f3count" class="text-sm text-gray-500 ml-auto font-medium">{len(q10):,} registros</span>
      <button onclick="exportCSV('tbl3','seg3_categorias.csv')" class="px-3 py-1.5 rounded text-white text-xs font-semibold" style="background:#0053e2">⬇ Exportar CSV</button>
    </div>"""

    hdrs = ["País","División","Categoría","Tier","Competidor","Ítems","CC TW","CC LW","Δ CC","Cambios TW","% PG Act","% MB Act","% PG HO Ini","% MB HO Ini","BPS MB","% PG Med","% MB Med"]
    def row_fn(r):
        tw = r.get("costo_comp_ho_tw") or 0
        lw = r.get("costo_comp_inicial_lw") or 0
        delta = tw - lw
        return f"""<tr data-delta="{delta:.2f}">
          <td class="px-2 py-1 border-b">{r.get('pais','')}</td>
          <td class="px-2 py-1 border-b">{r.get('division','')}</td>
          <td class="px-2 py-1 border-b">{r.get('categoria','')}</td>
          <td class="px-2 py-1 border-b">{r.get('tier','')}</td>
          <td class="px-2 py-1 border-b text-gray-500">{r.get('competidor') or '-'}</td>
          <td class="px-2 py-1 border-b text-right">{int(r.get('total_items') or 0):,}</td>
          <td class="px-2 py-1 border-b">{html_currency(tw)}</td>
          <td class="px-2 py-1 border-b">{html_currency(lw)}</td>
          <td class="px-2 py-1 border-b">{html_currency(delta)}</td>
          <td class="px-2 py-1 border-b text-right">{int(r.get('cambios_precios_tw') or 0):,}</td>
          <td class="px-2 py-1 border-b">{html_pct(r.get('pct_pg_actual_tw'))}</td>
          <td class="px-2 py-1 border-b">{html_pct(r.get('pct_mb_actual_tw'))}</td>
          <td class="px-2 py-1 border-b">{html_pct(r.get('pct_pg_ho_inicial'))}</td>
          <td class="px-2 py-1 border-b">{html_pct(r.get('pct_mb_ho_inicial'))}</td>
          <td class="px-2 py-1 border-b">{html_pct(r.get('bps_mb_ho'))}</td>
          <td class="px-2 py-1 border-b">{html_pct(r.get('pct_pg_medicion_tw'))}</td>
          <td class="px-2 py-1 border-b">{html_pct(r.get('pct_mb_tw_medicion'))}</td>
        </tr>"""
    tbl = data_table(hdrs, q10, "tbl3", row_fn)
    return filters + tbl

# ── Segmento 4 — Micro Ítem ──────────────────────────────────────
def build_seg4_items(data, tipo, sfx):
    paises = sorted(set(r.get("pais") for r in data if r.get("pais")))
    divs   = sorted(set(r.get("division") for r in data if r.get("division")))

    filters = f"""<div class="flex flex-wrap gap-3 mb-4 items-center bg-white p-4 rounded-lg shadow-sm">
      <select id="f{sfx}pais"><option value="">🌎 Todos</option>{"".join(f'<option>{p}</option>' for p in paises)}</select>
      <select id="f{sfx}div"><option value="">🏢 Todas las Divisiones</option>{"".join(f'<option>{d}</option>' for d in divs)}</select>
      <input type="text" id="f{sfx}cat" placeholder="Categoría..."/>
      <input type="text" id="f{sfx}tier" placeholder="Tier..."/>
      <button onclick="exportCSV('tbl4{sfx}','top50_{sfx}.csv')" class="px-3 py-1.5 rounded text-white text-xs font-semibold ml-auto" style="background:#0053e2">⬇ CSV</button>
    </div>"""

    top = data[0] if data else {}
    ins = (insight(f"#1 en {tipo}: <b>{top.get('item','?')}</b> ({top.get('pais','')}/{top.get('categoria','')}) — Δ CC {fmt_m(top.get('delta_costo_comp'))}") +
           insight("Frutas/Vegetales y Bebidas concentran mayor volatilidad — estacionalidad y promociones de competencia como drivers principales") +
           insight("Ítems con Δ CC negativo Y % PG negativo son prioridad de escalamiento para decisión comercial esta semana"))

    hdrs = ["País","Formato","División","Categoría","Tier","Ítem","CC TW","CC LW","Δ CC","% PG Act","% MB Act","% PG HO Ini","Δ MB"]
    def row_fn(r):
        d = r.get("delta_costo_comp") or 0
        dpg = r.get("delta_pg") or 0
        pg_a = r.get("pct_pg_actual")
        mb_a = r.get("pct_mb_actual")
        pg_h = r.get("pct_pg_ho_inicial")
        return f"""<tr>
          <td class="px-2 py-1 border-b">{r.get('pais','')}</td>
          <td class="px-2 py-1 border-b">{r.get('formato','')}</td>
          <td class="px-2 py-1 border-b">{r.get('division','')}</td>
          <td class="px-2 py-1 border-b">{r.get('categoria','')}</td>
          <td class="px-2 py-1 border-b">{r.get('tier','')}</td>
          <td class="px-2 py-1 border-b font-semibold">{r.get('item','')}</td>
          <td class="px-2 py-1 border-b">{html_currency(r.get('costo_comp_tw'))}</td>
          <td class="px-2 py-1 border-b">{html_currency(r.get('costo_comp_lw'))}</td>
          <td class="px-2 py-1 border-b">{html_currency(d)}</td>
          <td class="px-2 py-1 border-b">{html_pct(float(pg_a)*100 if pg_a is not None else None)}</td>
          <td class="px-2 py-1 border-b">{html_pct(float(mb_a)*100 if mb_a is not None else None)}</td>
          <td class="px-2 py-1 border-b">{html_pct(float(pg_h)*100 if pg_h is not None else None)}</td>
          <td class="px-2 py-1 border-b">{html_pct(float(dpg)*100 if dpg is not None else None)}</td>
        </tr>"""
    tbl = data_table(hdrs, data, f"tbl4{sfx}", row_fn)
    return filters + ins + tbl

# ── Segmento 5 — Competitivo ─────────────────────────────────────
def build_seg5_reaccion(q13):
    paises = sorted(set(r.get("pais") for r in q13 if r.get("pais")))
    colors = ["#0053e2","#ffc220","#2a8703","#ea1100","#7c3aed","#0891b2"]
    charts = []
    for i, pais in enumerate(paises):
        rows_p = sorted([r for r in q13 if r.get("pais")==pais], key=lambda r: -(r.get("items_tw") or 0))
        labels = [r.get("competidor_reaccion","?") for r in rows_p]
        vals   = [r.get("items_tw") or 0 for r in rows_p]
        charts.append(chart_bar(f"ch_reac_{pais}", labels, [
            {"label":f"Ítems {pais}","data":vals,"backgroundColor":colors[i%len(colors)],"borderRadius":4},
        ], f"Competidores — {pais}", height=240))

    ins = (insight("NIELSEN 90 es el competidor de referencia universal — presente en los 5 países como benchmark de mercado") +
           insight("COLMENA INTERNA activo en CR/GT/HN/NI/SV — canal interno de vigilancia de precios propios") +
           insight("PRICESMART en todos los países — referencia para formato club; monitoreo crítico en categorías TIER_1") +
           insight("Super Selectos (SV) y La Colonia (HN/NI) dominan en sus mercados locales — estrategia diferenciada requerida"))

    hdrs = ["País","Competidor","Ítems TW"]
    def row_fn(r):
        return f"""<tr>
          <td class="px-2 py-1.5 border-b font-semibold">{r.get('pais','')}</td>
          <td class="px-2 py-1.5 border-b">{r.get('competidor_reaccion','')}</td>
          <td class="px-2 py-1.5 border-b text-right font-medium">{int(r.get('items_tw') or 0):,}</td>
        </tr>"""
    tbl = data_table(hdrs, q13, "tbl5reac", row_fn, scrollable=False)
    grid = f'<div class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">{"".join(charts)}</div>'
    return grid + ins + tbl

def build_seg5_movimiento(q14):
    clases = sorted(set(r.get("clasificacion_movimiento","SIN DATOS") for r in q14))
    by_cls = {c: sum(r.get("total_items") or 0 for r in q14 if r.get("clasificacion_movimiento")==c) for c in clases}
    c1 = chart_doughnut("ch_mov5", list(by_cls.keys()), list(by_cls.values()), "Clasificación Movimiento Precios Competencia")

    paises = sorted(set(r.get("pais") for r in q14 if r.get("pais")))
    filters = f"""<div class="flex flex-wrap gap-3 mb-4 items-center bg-white p-4 rounded-lg shadow-sm">
      <select id="f5pais"><option value="">🌎 Todos los Países</option>{"".join(f'<option>{p}</option>' for p in paises)}</select>
      <input type="text" id="f5comp" placeholder="Competidor..."/>
      <select id="f5cls"><option value="">Todas las Clasificaciones</option>{"".join(f'<option>{c}</option>' for c in clases)}</select>
    </div>"""

    ins = (insight("SIN DATOS: ítems sin precio de competencia — evaluar cobertura del modelo de vigilancia competitiva") +
           insight("BAJO: precios de competencia bajando — señal de guerra de precios activa; revisar plan de reacción") +
           insight("SUBIO: competencia subió precios — oportunidad de oxigenación controlada de márgenes") +
           insight("NUEVO REGISTRO: primera aparición en el modelo — monitoreo inicial; validar con el equipo de pricing local"))

    hdrs = ["País","Competidor","División","Categoría","Clasificación","Ítems"]
    badge_map = {"BAJO":"badge-neg","SUBIO":"badge-pos","MANTIENE":"badge-neu","NUEVO REGISTRO":"badge-pos","SOLO LW":"badge-neu"}
    def row_fn(r):
        cls = r.get("clasificacion_movimiento","")
        bc = badge_map.get(cls,"")
        return f"""<tr>
          <td class="px-2 py-1 border-b">{r.get('pais','')}</td>
          <td class="px-2 py-1 border-b">{r.get('competidor') or '-'}</td>
          <td class="px-2 py-1 border-b">{r.get('division','')}</td>
          <td class="px-2 py-1 border-b">{r.get('categoria','')}</td>
          <td class="px-2 py-1 border-b"><span class="badge {bc}">{cls}</span></td>
          <td class="px-2 py-1 border-b text-right">{int(r.get('total_items') or 0):,}</td>
        </tr>"""
    tbl = data_table(hdrs, q14, "tbl5mov", row_fn)
    return f'<div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">{c1}<div>{ins}</div></div>{filters}{tbl}'

# ── Build final HTML ──────────────────────────────────────────────
def build():
    # Cargar todos los datasets
    q1  = load_csv("q1-por-pais-*.csv")
    q2  = load_csv("q2-por-division-*.csv")
    q3  = load_csv("q3-por-tier-*.csv")
    q4  = load_csv("q4-por-mov-precio-comp-*.csv")
    q5  = load_csv("q5-por-tendencia-reaccion-ho-*.csv")
    q6  = load_csv("q6-por-respeto-modelo-*.csv")
    q7  = load_csv("q7-por-performance-primario-*.csv")
    q8  = load_csv("q8-por-rango-costo-comp-*.csv")
    q9  = load_csv("q9-por-rango-pg-meta-*.csv")
    q10 = load_csv("q10-por-pais-division-categoria-tier-*.csv")
    q11 = load_csv("q11-top50-inversion-*.csv")
    q12 = load_csv("q12-top50-oxigenacion-*.csv")
    q13 = load_csv("q13-reaccion-competidores-*.csv")
    q14 = load_csv("q14-movimiento-precios-competencia-*.csv")

    # KPIs ejecutivos
    total_items  = sum(r.get("total_items",0) or 0 for r in q1)
    total_cc_tw  = sum(r.get("costo_comp_ho_tw",0) or 0 for r in q1)
    total_cc_lw  = sum(r.get("costo_comp_inicial_lw",0) or 0 for r in q1)
    delta_cc     = total_cc_tw - total_cc_lw
    total_chg_tw = sum(r.get("cambios_precios_tw",0) or 0 for r in q1)
    avg_pg       = sum(r.get("pct_pg_actual_tw",0) or 0 for r in q1) / max(len(q1),1)
    avg_mb       = sum(r.get("pct_mb_actual_tw",0) or 0 for r in q1) / max(len(q1),1)
    now_str      = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Construir secciones
    seg1_pais = build_seg1_pais(q1)
    seg1_div  = build_seg1_div(q2)
    seg1_tier = build_seg1_tier(q3)
    seg1_f1   = build_seg1_flag(q4,"flag_movimiento_precio_comp","Movimiento Precio Competencia","mpc")
    seg1_f2   = build_seg1_flag(q5,"tendencia_reaccion_ho","Tendencia Reacción HO","trh")
    seg1_f3   = build_seg1_flag(q6,"flag_respeto_pricing_modelo","Respeto Pricing Modelo","rpm")
    s2_perf   = build_seg2_performance(q7)
    s2_rcc    = build_seg2_rangos_cc(q8)
    s2_rpg    = build_seg2_rango_pg(q9)
    s2_rmeta  = build_seg2_rango_meta(q9)
    s3        = build_seg3(q10)
    s4_inv    = build_seg4_items(q11,"inversión","inv")
    s4_oxy    = build_seg4_items(q12,"oxigenación","oxy")
    s5_reac   = build_seg5_reaccion(q13)
    s5_mov    = build_seg5_movimiento(q14)

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Análisis Semanal de Impactos Modelo</title>
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
:root{{--wm-blue:#0053e2;--wm-spark:#ffc220;--wm-green:#2a8703;--wm-red:#ea1100;}}
body{{font-family:'Segoe UI',system-ui,sans-serif;background:#f1f5f9;color:#1e293b;}}
.nav-btn{{cursor:pointer;transition:all .2s;}}
.nav-btn.active{{background:#0053e2!important;color:#fff!important;border-color:#0053e2!important;}}
.seg-panel{{display:none;}}.seg-panel.active{{display:block;}}
.tab-sub{{display:inline-block;padding:5px 14px;cursor:pointer;border-bottom:2px solid transparent;font-size:.82rem;transition:.2s;}}
.tab-sub.active{{border-color:#0053e2;color:#0053e2;font-weight:700;}}
.sub-panel{{display:none;}}.sub-panel.active{{display:block;}}
.insight-box{{background:#eff6ff;border-left:4px solid #0053e2;padding:10px 14px;border-radius:4px;margin:4px 0;}}
.badge{{display:inline-block;padding:1px 7px;border-radius:9999px;font-size:.7rem;font-weight:700;}}
.badge-neg{{background:#fee2e2;color:#b91c1c;}}
.badge-pos{{background:#dcfce7;color:#15803d;}}
.badge-neu{{background:#e0e7ff;color:#3730a3;}}
th{{position:sticky;top:0;background:#f8fafc;z-index:2;white-space:nowrap;}}
input,select{{border:1px solid #cbd5e1;border-radius:6px;padding:4px 10px;font-size:.82rem;outline:none;}}
input:focus,select:focus{{border-color:#0053e2;box-shadow:0 0 0 2px #bfdbfe;}}
table{{border-collapse:collapse;}}
tbody tr:hover{{background:#f0f9ff;}}
</style>
</head>
<body class="min-h-screen">

<!-- HEADER -->
<header style="background:#0053e2;" class="text-white px-6 py-4 flex items-center gap-4 shadow-xl">
  <div class="text-3xl">🏪</div>
  <div>
    <h1 class="text-2xl font-bold tracking-tight">Análisis Semanal de Impactos Modelo</h1>
    <p class="text-blue-200 text-sm mt-0.5">Pricing CAM · Centroamérica (CR · GT · HN · SV · NI) · {now_str} · Sin MG Y TEXTIL</p>
  </div>
</header>

<!-- EXECUTIVE SUMMARY KPIs -->
<div class="px-6 py-4">
  <h2 class="text-sm font-bold text-gray-500 uppercase tracking-widest mb-3">📌 Resumen Ejecutivo</h2>
  <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-7 gap-3 mb-3">
    {kpi_card("Ítems Analizados", f"{total_items:,.0f}", "neutral")}
    {kpi_card("CC Inicial TW", fmt_m(total_cc_tw), "neg" if total_cc_tw<0 else "pos")}
    {kpi_card("CC Inicial LW", fmt_m(total_cc_lw), "neg" if total_cc_lw<0 else "pos")}
    {kpi_card("Δ CC (TW−LW)", fmt_m(delta_cc), "neg" if delta_cc<0 else "pos")}
    {kpi_card("Cambios Precio TW", f"{total_chg_tw:,.0f}", "warn")}
    {kpi_card("Avg % PG Actual", fmt_pct(avg_pg), "pos" if avg_pg>0 else "neg")}
    {kpi_card("Avg % MB Actual", fmt_pct(avg_mb), "pos" if avg_mb>0 else "neg")}
  </div>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
    {insight("GT acumula el mayor delta CC negativo (-$240K) — presión competitiva creciente; evaluar plan de reacción urgente")}
    {insight("HN y NI muestran oxigenación CC vs LW (+$67K y +$9K) — recuperación de competitividad relativa")}
    {insight("BPS MB negativo en todos los países (≈ -200 bps) — presión sistémica de margen; monitorear tendencia 4WK")}
  </div>
</div>

<!-- NAV SEGMENTOS -->
<div class="px-6 mb-4 flex flex-wrap gap-2">
  {nav_btn(1,"📊 Seg.1 General",True)}
  {nav_btn(2,"🔬 Seg.2 Calidad")}
  {nav_btn(3,"📋 Seg.3 Categoría/Comp")}
  {nav_btn(4,"🔍 Seg.4 Micro Ítem")}
  {nav_btn(5,"🏆 Seg.5 Competitivo")}
</div>

<!-- CONTENIDO SEGMENTOS -->
<div class="px-6 pb-12">

<div id="seg1" class="seg-panel active">
  <h2 class="text-base font-bold mb-3" style="color:#0053e2">Segmento 1 — Análisis General</h2>
  <div class="flex flex-wrap gap-0 border-b mb-5">
    {subtabs(1,["🌎 Por País","🏢 Por División","🎯 Por Tier","📊 Mov. Precio Comp","📈 Tendencia Reacción HO","✅ Respeto Modelo"])}
  </div>
  <div id="s1p0" class="sub-panel active">{seg1_pais}</div>
  <div id="s1p1" class="sub-panel">{seg1_div}</div>
  <div id="s1p2" class="sub-panel">{seg1_tier}</div>
  <div id="s1p3" class="sub-panel">{seg1_f1}</div>
  <div id="s1p4" class="sub-panel">{seg1_f2}</div>
  <div id="s1p5" class="sub-panel">{seg1_f3}</div>
</div>

<div id="seg2" class="seg-panel">
  <h2 class="text-base font-bold mb-3" style="color:#0053e2">Segmento 2 — Análisis de Calidad</h2>
  <div class="flex flex-wrap gap-0 border-b mb-5">
    {subtabs(2,["🏆 Performance Primario","💲 Rangos CC Inicial","📊 Rango PG Actual","🎯 Rango Meta"])}
  </div>
  <div id="s2p0" class="sub-panel active">{s2_perf}</div>
  <div id="s2p1" class="sub-panel">{s2_rcc}</div>
  <div id="s2p2" class="sub-panel">{s2_rpg}</div>
  <div id="s2p3" class="sub-panel">{s2_rmeta}</div>
</div>

<div id="seg3" class="seg-panel">
  <h2 class="text-base font-bold mb-3" style="color:#0053e2">Segmento 3 — Detalle Categoría / Competidor</h2>
  {s3}
</div>

<div id="seg4" class="seg-panel">
  <h2 class="text-base font-bold mb-3" style="color:#0053e2">Segmento 4 — Análisis Micro Ítem</h2>
  <div class="flex flex-wrap gap-0 border-b mb-5">
    {subtabs(4,["📉 Top 50 Inversión (Δ CC-)","📈 Top 50 Oxigenación (Δ CC+)"])}
  </div>
  <div id="s4p0" class="sub-panel active">{s4_inv}</div>
  <div id="s4p1" class="sub-panel">{s4_oxy}</div>
</div>

<div id="seg5" class="seg-panel">
  <h2 class="text-base font-bold mb-3" style="color:#0053e2">Segmento 5 — Análisis Competitivo</h2>
  <div class="flex flex-wrap gap-0 border-b mb-5">
    {subtabs(5,["🏪 Reacción Competidores","📊 Movimiento Precios Competencia"])}
  </div>
  <div id="s5p0" class="sub-panel active">{s5_reac}</div>
  <div id="s5p1" class="sub-panel">{s5_mov}</div>
</div>

</div><!-- /px-6 -->

<!-- FOOTER -->
<footer class="text-center text-xs text-gray-400 py-6 border-t">
  Análisis Semanal de Impactos Modelo · Pricing CAM · Generado el {now_str} · Datos: BigQuery wmt-k1-cons-data-users.k1_adhoc_tables.prcng_info_cam_a0g0dn3_impactos_modelo_semanal
</footer>

<script>
// ── Navegación principal ──────────────────────────────────────────
document.querySelectorAll('.nav-btn').forEach(b=>b.addEventListener('click',()=>{{
  document.querySelectorAll('.seg-panel').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(x=>x.classList.remove('active'));
  document.getElementById('seg'+b.dataset.seg).classList.add('active');
  b.classList.add('active');
}}));

// ── Sub-tabs ─────────────────────────────────────────────────────
document.querySelectorAll('.tab-sub').forEach(t=>t.addEventListener('click',()=>{{
  const g=t.dataset.grp;
  document.querySelectorAll(`.tab-sub[data-grp="${{g}}"]`).forEach(x=>x.classList.remove('active'));
  document.querySelectorAll(`.sub-panel[data-grp="${{g}}"]`).forEach(x=>x.classList.remove('active'));
  t.classList.add('active');
  document.getElementById(t.dataset.target).classList.add('active');
}}));

// ── CSV Export ────────────────────────────────────────────────────
function exportCSV(tableId,filename){{
  const tbl=document.getElementById(tableId);
  const rows=[...tbl.querySelectorAll('tr')].filter(r=>r.style.display!=='none');
  const csv=rows.map(r=>[...r.querySelectorAll('th,td')].map(c=>'"'+c.textContent.trim().replace(/"/g,'""')+'"').join(',')).join('\\n');
  const a=document.createElement('a');
  a.href='data:text/csv;charset=utf-8,\\uFEFF'+encodeURIComponent(csv);
  a.download=filename; a.click();
}}

// ── Filtros Seg3 ─────────────────────────────────────────────────
(function(){{
  const tbl=document.getElementById('tbl3');
  if(!tbl)return;
  const rows=[...tbl.querySelectorAll('tbody tr')];
  function filter(){{
    const p=document.getElementById('f3pais')?.value.toLowerCase()||'';
    const d=document.getElementById('f3div')?.value.toLowerCase()||'';
    const c=document.getElementById('f3cat')?.value.toLowerCase()||'';
    const t=document.getElementById('f3tier')?.value.toLowerCase()||'';
    const top=document.getElementById('f3top')?.value||'';
    let vis=rows.filter(r=>{{
      const td=[...r.querySelectorAll('td')].map(x=>x.textContent.toLowerCase());
      return(!p||td[0].includes(p))&&(!d||td[1].includes(d))&&(!c||td[2].includes(c))&&(!t||td[3].includes(t));
    }});
    if(top==='inv') vis=vis.filter(r=>parseFloat(r.dataset.delta)<0).sort((a,b)=>parseFloat(a.dataset.delta)-parseFloat(b.dataset.delta)).slice(0,10);
    if(top==='oxy') vis=vis.filter(r=>parseFloat(r.dataset.delta)>0).sort((a,b)=>parseFloat(b.dataset.delta)-parseFloat(a.dataset.delta)).slice(0,10);
    rows.forEach(r=>r.style.display='none');
    vis.forEach(r=>r.style.display='');
    const cnt=document.getElementById('f3count');
    if(cnt)cnt.textContent=vis.length.toLocaleString()+' registros';
  }}
  ['f3pais','f3div','f3cat','f3tier','f3top'].forEach(id=>{{
    const el=document.getElementById(id);
    if(el)el.addEventListener('input',filter),el.addEventListener('change',filter);
  }});
}})();

// ── Filtros Seg4 ─────────────────────────────────────────────────
['inv','oxy'].forEach(sfx=>{{
  const tbl=document.getElementById('tbl4'+sfx);
  if(!tbl)return;
  const rows=[...tbl.querySelectorAll('tbody tr')];
  function filter(){{
    const vals=['pais','div','cat','tier'].map(f=>document.getElementById('f'+sfx+f)?.value.toLowerCase()||'');
    rows.forEach(r=>{{
      const td=[...r.querySelectorAll('td')].map(x=>x.textContent.toLowerCase());
      r.style.display=vals.every((v,i)=>!v||td[i].includes(v))?'':'none';
    }});
  }}
  ['pais','div','cat','tier'].forEach(f=>{{
    const el=document.getElementById('f'+sfx+f);
    if(el)el.addEventListener('input',filter),el.addEventListener('change',filter);
  }});
}});

// ── Filtros Seg5 ─────────────────────────────────────────────────
(function(){{
  const tbl=document.getElementById('tbl5mov');
  if(!tbl)return;
  const rows=[...tbl.querySelectorAll('tbody tr')];
  function filter(){{
    const p=document.getElementById('f5pais')?.value.toLowerCase()||'';
    const c=document.getElementById('f5comp')?.value.toLowerCase()||'';
    const cls=document.getElementById('f5cls')?.value.toLowerCase()||'';
    rows.forEach(r=>{{
      const td=[...r.querySelectorAll('td')].map(x=>x.textContent.toLowerCase());
      r.style.display=(!p||td[0].includes(p))&&(!c||td[1].includes(c))&&(!cls||td[4].includes(cls))?'':'none';
    }});
  }}
  ['f5pais','f5comp','f5cls'].forEach(id=>{{
    const el=document.getElementById(id);
    if(el)el.addEventListener('input',filter),el.addEventListener('change',filter);
  }});
}})();
</script>
</body>
</html>"""

    out = os.path.join(BASE, "dashboard_impactos_semanal.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print("Dashboard generado: " + out)
    return out

if __name__ == "__main__":
    path = build()
    import subprocess, sys
    if sys.platform == "win32":
        subprocess.Popen(["cmd","/c","start",path])

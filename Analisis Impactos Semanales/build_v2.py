"""
Dashboard v2 — Análisis Semanal de Impactos Modelo
Fórmulas oficiales del wiki GitHub Redstar2026/Puppy_workspace
"""
import csv, json, os, glob
from datetime import datetime

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "v2")
OUT  = os.path.dirname(os.path.abspath(__file__))

# ── utils ─────────────────────────────────────────────────────────
def load(pattern):
    m = glob.glob(os.path.join(BASE, pattern))
    if not m: return []
    rows = []
    with open(m[0], encoding="utf-8") as f:
        for r in csv.DictReader(f):
            row = {}
            for k, v in r.items():
                if v in ("", "NULL", "None", None):
                    row[k] = None
                else:
                    try:    row[k] = int(v)
                    except: 
                        try:    row[k] = float(v)
                        except: row[k] = v
            rows.append(row)
    return rows

def js(obj): return json.dumps(obj, ensure_ascii=False, default=str)

def fmtM(v):
    if v is None: return "—"
    f = float(v); s = "-" if f < 0 else ""; a = abs(f)
    if a >= 1e6:  return f"{s}${a/1e6:.2f}M"
    if a >= 1e3:  return f"{s}${a/1e3:.1f}K"
    return f"{s}${a:.0f}"

def fmtP(v, d=2):
    if v is None: return "—"
    return f"{float(v):.{d}f}%"

def fmtN(v):
    if v is None: return "—"
    return f"{float(v):,.2f}"

def red(v):
    if v is None: return "#6b7280"
    return "#ea1100" if float(v) < 0 else ("#2a8703" if float(v) > 0 else "#6b7280")

def span_currency(v):
    if v is None: return "—"
    return f'<span style="color:{red(v)};font-weight:600">{fmtM(v)}</span>'

def span_pct(v, d=2):
    if v is None: return "—"
    return f'<span style="color:{red(v)}">{fmtP(v,d)}</span>'

def span_bps(v):
    if v is None: return "—"
    fv = float(v)
    c = "#ea1100" if fv < 0 else ("#2a8703" if fv > 0 else "#6b7280")
    sign = "▼ " if fv < 0 else ("▲ " if fv > 0 else "")
    return f'<span style="color:{c};font-weight:600">{sign}{abs(fv):.1f}</span>'

def span_b100(v):
    if v is None: return "—"
    fv = float(v)
    c = "#ea1100" if fv < 100 else ("#2a8703" if fv > 100 else "#6b7280")
    return f'<span style="color:{c}">{fv:.1f}</span>'

# ── shared metric columns ─────────────────────────────────────────
METRIC_HDRS = [
    "CC HO TW","CC Ini LW","Δ CC",
    "Cambios TW","Cambios LW","Base 100",
    "% PG Act TW","% PG HO Ini","% PG HO Ini LW",
    "% MB Act TW","% MB HO Ini","% MB HO Ini LW",
    "BPS PG","BPS MB",
    "% PG Med TW","% PG Med 4WK",
    "% MB Med TW","% MB Med 4WK",
    "Ítems"
]

def metric_tds(r):
    return (
        f'<td>{span_currency(r.get("cc_ho_tw"))}</td>'
        f'<td>{span_currency(r.get("cc_ini_lw"))}</td>'
        f'<td>{span_currency(r.get("delta_cc"))}</td>'
        f'<td class="tr">{int(r.get("cambios_tw") or 0):,}</td>'
        f'<td class="tr">{int(r.get("cambios_lw") or 0):,}</td>'
        f'<td>{span_b100(r.get("cambios_base100"))}</td>'
        f'<td>{span_pct(r.get("pct_pg_actual_tw"))}</td>'
        f'<td>{span_pct(r.get("pct_pg_ho_ini"))}</td>'
        f'<td>{span_pct(r.get("pct_pg_ho_ini_lw"))}</td>'
        f'<td>{span_pct(r.get("pct_mb_actual_tw"))}</td>'
        f'<td>{span_pct(r.get("pct_mb_ho_ini"))}</td>'
        f'<td>{span_pct(r.get("pct_mb_ho_ini_lw"))}</td>'
        f'<td>{span_bps(r.get("bps_pg"))}</td>'
        f'<td>{span_bps(r.get("bps_mb"))}</td>'
        f'<td>{span_pct(r.get("pct_pg_med_tw"))}</td>'
        f'<td>{span_pct(r.get("pct_pg_med_4wk"))}</td>'
        f'<td>{span_pct(r.get("pct_mb_med_tw"))}</td>'
        f'<td>{span_pct(r.get("pct_mb_med_4wk"))}</td>'
        f'<td class="tr text-gray-400">{int(r.get("total_items") or 0):,}</td>'
    )

def th_row(extra_cols):
    ths = "".join(f'<th>{h}</th>' for h in (extra_cols + METRIC_HDRS))
    return f'<tr>{ths}</tr>'

def insight(txt):
    return f'<div class="ins">💡 {txt}</div>'

# ── chart helpers ─────────────────────────────────────────────────
_cid = 0
def cid():
    global _cid; _cid += 1; return f"c{_cid}"

def bar_chart(labels, datasets, title="", h=260):
    i = cid()
    t_html = f'<div class="chart-title">{title}</div>' if title else ""
    return f'''<div class="chart-box">{t_html}<div style="height:{h}px"><canvas id="{i}"></canvas></div></div>
<script>(()=>{{var el=document.getElementById("{i}");if(!el)return;
new Chart(el,{{type:"bar",data:{{labels:{js(labels)},datasets:{js(datasets)}}},
options:{{responsive:true,maintainAspectRatio:false,
plugins:{{legend:{{position:"top",labels:{{boxWidth:12,font:{{size:11}}}}}}}},
scales:{{x:{{ticks:{{maxRotation:40,font:{{size:10}}}}}},y:{{ticks:{{font:{{size:10}}}}}}}}}}}});}})();</script>'''

def doughnut_chart(labels, vals, title="", h=240):
    i = cid()
    COLORS = ["#0053e2","#ffc220","#2a8703","#ea1100","#7c3aed","#0891b2","#db2777","#d97706","#65a30d","#0f766e"]
    t_html = f'<div class="chart-title">{title}</div>' if title else ""
    return f'''<div class="chart-box">{t_html}<div style="height:{h}px"><canvas id="{i}"></canvas></div></div>
<script>(()=>{{var el=document.getElementById("{i}");if(!el)return;
new Chart(el,{{type:"doughnut",data:{{labels:{js(labels)},
datasets:[{{data:{js(vals)},backgroundColor:{js(COLORS[:len(vals)])}}}]}},
options:{{responsive:true,maintainAspectRatio:false,
plugins:{{legend:{{position:"right",labels:{{boxWidth:12,font:{{size:10}}}}}}}}}}}});}})();</script>'''

def grouped_bar(labels, datasets, title="", h=260):
    i = cid()
    t_html = f'<div class="chart-title">{title}</div>' if title else ""
    return f'''<div class="chart-box">{t_html}<div style="height:{h}px"><canvas id="{i}"></canvas></div></div>
<script>(()=>{{var el=document.getElementById("{i}");if(!el)return;
new Chart(el,{{type:"bar",data:{{labels:{js(labels)},datasets:{js(datasets)}}},
options:{{responsive:true,maintainAspectRatio:false,indexAxis:"y",
plugins:{{legend:{{position:"top",labels:{{boxWidth:12,font:{{size:11}}}}}}}},
scales:{{x:{{ticks:{{font:{{size:10}}}}}},y:{{ticks:{{font:{{size:10}}}}}}}}}}}});}})();</script>'''

# ── segment 1 visual (same structure for all 6 sub-tabs) ─────────
def seg1_visual(data, dim_key, dim_label, tab_id):
    labels   = [str(r.get(dim_key) or "NULL") for r in data]
    cc_tw    = [round(r.get("cc_ho_tw") or 0) for r in data]
    cc_lw    = [round(r.get("cc_ini_lw") or 0) for r in data]
    delta_cc = [round((r.get("cc_ho_tw") or 0) - (r.get("cc_ini_lw") or 0)) for r in data]
    pg_ini   = [round(r.get("pct_pg_ho_ini") or 0, 4) for r in data]
    pg_lw    = [round(r.get("pct_pg_ho_ini_lw") or 0, 4) for r in data]
    bps_pg   = [round(r.get("bps_pg") or 0, 1) for r in data]
    bps_mb   = [round(r.get("bps_mb") or 0, 1) for r in data]
    b100     = [round(r.get("cambios_base100") or 0, 2) for r in data]
    items    = [r.get("total_items") or 0 for r in data]

    c1 = bar_chart(labels, [
        {"label":"CC HO TW","data":cc_tw,"backgroundColor":"#0053e2","borderRadius":3},
        {"label":"CC Ini LW","data":cc_lw,"backgroundColor":"#93c5fd","borderRadius":3},
    ], "Costo Competitivo HO TW vs Inicial LW")

    c2 = bar_chart(labels, [
        {"label":"Δ CC","data":delta_cc,"backgroundColor":["#2a8703" if v >= 0 else "#ea1100" for v in delta_cc],"borderRadius":3},
    ], "Delta Costo Competitivo (TW − LW)")

    c3 = bar_chart(labels, [
        {"label":"% PG HO Ini","data":pg_ini,"backgroundColor":"#0053e2","borderRadius":3},
        {"label":"% PG HO Ini LW","data":pg_lw,"backgroundColor":"#ffc220","borderRadius":3},
    ], "% PG HO INICIAL — TW vs LW")

    c4 = bar_chart(labels, [
        {"label":"BPS PG","data":bps_pg,"backgroundColor":["#2a8703" if v >= 0 else "#ea1100" for v in bps_pg],"borderRadius":3},
        {"label":"BPS MB","data":bps_mb,"backgroundColor":["#2a8703" if v >= 0 else "#7c3aed" for v in bps_mb],"borderRadius":3},
    ], "BPS PG y BPS MB vs LW")

    c5 = bar_chart(labels, [
        {"label":"Cambios Precio Base 100","data":b100,"backgroundColor":"#0891b2","borderRadius":3},
    ], "Cambios de Precio TW/LW (Base 100 = sin cambio)")

    c6 = doughnut_chart(labels, items, "Distribución de Ítems")

    # Auto-insights
    valid = [r for r in data if r.get("delta_cc") is not None]
    if valid:
        worst_cc = min(valid, key=lambda r: r.get("delta_cc") or 0)
        best_cc  = max(valid, key=lambda r: r.get("delta_cc") or 0)
        worst_bps = min(valid, key=lambda r: r.get("bps_pg") or 0)
        best_mb  = max(valid, key=lambda r: r.get("bps_mb") or 0)
        ins = (
            insight(f"Mayor inversión CC: <b>{worst_cc.get(dim_key)}</b> — Δ CC {fmtM(worst_cc.get('delta_cc'))} | BPS PG {worst_cc.get('bps_pg'):.1f} — presión competitiva elevada, evaluar plan de reacción")
            + insight(f"Mayor oxigenación CC: <b>{best_cc.get(dim_key)}</b> — Δ CC {fmtM(best_cc.get('delta_cc'))} | recuperación vs semana anterior")
            + insight(f"Mayor caída de PG: <b>{worst_bps.get(dim_key)}</b> — BPS PG ▼{abs(worst_bps.get('bps_pg') or 0):.1f} bps — revisar correlación con movimiento del competidor")
            + insight(f"Mejor mejora de MB: <b>{best_mb.get(dim_key)}</b> — BPS MB ▲{abs(best_mb.get('bps_mb') or 0):.1f} bps — oportunidad de consolidar margen")
        )
    else:
        ins = ""

    # Metrics table
    rows_html = ""
    for r in data:
        dim_val = str(r.get(dim_key) or "NULL")
        rows_html += f'<tr><td class="fw">{dim_val}</td>{metric_tds(r)}</tr>'

    tbl = f'''<div class="tbl-wrap">
      <table id="tbl_{tab_id}">
        {th_row([dim_label])}
        <tbody>{rows_html}</tbody>
      </table>
    </div>'''

    return f'''
    <div class="grid-2-2">{c1}{c2}{c3}{c4}</div>
    <div class="grid-2">{c5}{c6}</div>
    {ins}
    {tbl}'''

# ── segment 2 quality visual (same metrics) ───────────────────────
def seg2_visual(data, dim_key, dim_label, tab_id):
    return seg1_visual(data, dim_key, dim_label, tab_id)

# ── segment 3 ─────────────────────────────────────────────────────
def seg3_html(data):
    paises = sorted(set(r.get("pais","") for r in data if r.get("pais")))
    divs   = sorted(set(r.get("division","") for r in data if r.get("division")))
    fmts   = sorted(set(r.get("formato","") for r in data if r.get("formato")))
    cats   = sorted(set(r.get("categoria","") for r in data if r.get("categoria")))
    tiers  = sorted(set(r.get("tier","") for r in data if r.get("tier")))

    def opt(vals): return "".join(f'<option>{v}</option>' for v in vals)

    filters = f'''<div class="filter-bar">
      <label>País <select id="s3pais"><option value="">Todos</option>{opt(paises)}</select></label>
      <label>División <select id="s3div"><option value="">Todas</option>{opt(divs)}</select></label>
      <label>Formato <select id="s3fmt"><option value="">Todos</option>{opt(fmts)}</select></label>
      <label>Categoría <input type="text" id="s3cat" placeholder="Buscar..." style="width:160px"></label>
      <label>Tier <select id="s3tier"><option value="">Todos</option>{opt(tiers)}</select></label>
      <label>Top Categorías
        <select id="s3top">
          <option value="">Todos los registros</option>
          <option value="inv">Top 10 Mayor Inversión (Δ CC −)</option>
          <option value="oxy">Top 10 Mayor Oxigenación (Δ CC +)</option>
        </select>
      </label>
      <span id="s3cnt" class="cnt">{len(data):,} registros</span>
      <button onclick="exportCSV('tbl_s3','seg3.csv')" class="btn-export">⬇ CSV</button>
    </div>'''

    hdrs = ["País","División","Formato","Categoría","Tier","Competidor"] + METRIC_HDRS
    ths = "".join(f'<th>{h}</th>' for h in hdrs)

    rows_html = ""
    for r in data:
        delta = (r.get("cc_ho_tw") or 0) - (r.get("cc_ini_lw") or 0)
        rows_html += f'''<tr data-delta="{delta:.2f}">
          <td>{r.get("pais","")}</td><td>{r.get("division","")}</td>
          <td>{r.get("formato","")}</td><td>{r.get("categoria","")}</td>
          <td>{r.get("tier","")}</td><td>{r.get("competidor") or "—"}</td>
          {metric_tds(r)}
        </tr>'''

    return f'''{filters}
    <div class="tbl-wrap" style="max-height:520px">
      <table id="tbl_s3"><thead><tr>{ths}</tr></thead><tbody>{rows_html}</tbody></table>
    </div>'''

# ── segment 4 ─────────────────────────────────────────────────────
def seg4_html(q12):
    # Pre-compute top 50 inversion, top 50 oxigenacion, A-E summary
    valid = [r for r in q12 if r.get("delta_cc") is not None]
    neg   = sorted([r for r in valid if (r.get("delta_cc") or 0) < 0], key=lambda r: r.get("delta_cc") or 0)
    pos   = sorted([r for r in valid if (r.get("delta_cc") or 0) > 0], key=lambda r: -(r.get("delta_cc") or 0))
    top50_inv = neg[:50]
    top50_oxy = pos[:50]

    # A-E counts
    ae_counts = {}
    for r in q12:
        c = r.get("clasificacion_ae","E") or "E"
        ae_counts[c] = ae_counts.get(c, 0) + 1

    # A-E chart
    ae_labels = ["A","B","C","D","E"]
    ae_vals   = [ae_counts.get(l, 0) for l in ae_labels]
    ae_descs  = [
        "A: Δ CC− & Δ %PG− (Inversión + Presión margen)",
        "B: Δ CC− & Δ %PG+ (Inversión + Mejora margen)",
        "C: Δ CC+ & Δ %PG− (Oxigenación + Presión margen)",
        "D: Δ CC+ & Δ %PG+ (Oxigenación + Mejora margen)",
        "E: Sin cambio / Dato nulo",
    ]
    ae_colors = ["#ea1100","#ffc220","#7c3aed","#2a8703","#9ca3af"]

    ae_chart_id = cid()
    ae_chart = f'''<div class="chart-box">
      <div class="chart-title">Clasificación A-E — Ítems por escenario (Δ CC vs Δ %PG)</div>
      <div style="height:220px"><canvas id="{ae_chart_id}"></canvas></div>
    </div>
    <script>(()=>{{var el=document.getElementById("{ae_chart_id}");if(!el)return;
    new Chart(el,{{type:"bar",data:{{labels:{js(ae_labels)},
    datasets:[{{label:"Ítems",data:{js(ae_vals)},backgroundColor:{js(ae_colors)},borderRadius:4}}]}},
    options:{{responsive:true,maintainAspectRatio:false,indexAxis:"y",
    plugins:{{legend:{{display:false}}}}}}}});}})();</script>'''

    ae_defs = "".join(f'<div class="ae-def" style="border-color:{c}">'
                      f'<b style="color:{c}">{l}</b> — {d}</div>'
                      for l, d, c in zip(ae_labels, ae_descs, ae_colors))

    def item_rows(rows, sfx):
        paises = sorted(set(r.get("pais","") for r in rows if r.get("pais")))
        divs   = sorted(set(r.get("division","") for r in rows if r.get("division")))
        def opt(v): return "".join(f'<option>{x}</option>' for x in v)
        filters = f'''<div class="filter-bar">
          <label>País <select id="f{sfx}pais"><option value="">Todos</option>{opt(paises)}</select></label>
          <label>División <select id="f{sfx}div"><option value="">Todas</option>{opt(divs)}</select></label>
          <label>Categoría <input type="text" id="f{sfx}cat" placeholder="Buscar..." style="width:140px"></label>
          <label>Tier <input type="text" id="f{sfx}tier" placeholder="Tier..."></label>
          <label>Ítem <input type="text" id="f{sfx}item" placeholder="Nombre ítem..."></label>
          <label>Clasificación
            <select id="f{sfx}ae">
              <option value="">A-E: Todos</option>
              <option value="A">A — Δ CC− & Δ PG−</option>
              <option value="B">B — Δ CC− & Δ PG+</option>
              <option value="C">C — Δ CC+ & Δ PG−</option>
              <option value="D">D — Δ CC+ & Δ PG+</option>
              <option value="E">E — Sin cambio</option>
            </select>
          </label>
          <button onclick="exportCSV('tbl_s4{sfx}','seg4_{sfx}.csv')" class="btn-export">⬇ CSV</button>
        </div>'''

        s4_hdrs = ["País","Formato","Zona","División","Categoría","Tier","Ítem","Competidor","CC TW","CC LW","Δ CC","% PG HO Ini","% PG HO Ini LW","Δ %PG","% MB HO Ini","% PG Act","% MB Act","% PG Med TW","% MB Med TW","P.Actual","P.Final","P.Comp","Cambios TW","Clasif."]
        ths = "".join(f'<th>{h}</th>' for h in s4_hdrs)
        rows_html = ""
        for r in rows:
            ae = r.get("clasificacion_ae","E") or "E"
            ae_c = {"A":"#ea1100","B":"#d97706","C":"#7c3aed","D":"#2a8703","E":"#9ca3af"}.get(ae,"#9ca3af")
            rows_html += f'''<tr data-ae="{ae}">
              <td>{r.get("pais","")}</td><td>{r.get("formato","")}</td>
              <td>{r.get("zona","")}</td><td>{r.get("division","")}</td>
              <td>{r.get("categoria","")}</td><td>{r.get("tier","")}</td>
              <td class="fw">{r.get("item","")}</td>
              <td>{r.get("competidor_reaccion") or "—"}</td>
              <td>{span_currency(r.get("cc_tw"))}</td>
              <td>{span_currency(r.get("cc_lw"))}</td>
              <td>{span_currency(r.get("delta_cc"))}</td>
              <td>{span_pct(r.get("pct_pg_ho_ini"))}</td>
              <td>{span_pct(r.get("pct_pg_ho_ini_lw"))}</td>
              <td>{span_pct(r.get("delta_pct_pg"))}</td>
              <td>{span_pct(r.get("pct_mb_ho_ini"))}</td>
              <td>{span_pct(r.get("pct_pg_actual"))}</td>
              <td>{span_pct(r.get("pct_mb_actual"))}</td>
              <td>{span_pct(r.get("pct_pg_med_tw"))}</td>
              <td>{span_pct(r.get("pct_mb_med_tw"))}</td>
              <td class="tr">{fmtN(r.get("precio_actual"))}</td>
              <td class="tr">{fmtN(r.get("precio_final"))}</td>
              <td class="tr">{fmtN(r.get("precio_comp_reaccion"))}</td>
              <td class="tr">{int(r.get("cambios_tw") or 0)}</td>
              <td><span class="ae-badge" style="background:{ae_c}">{ae}</span></td>
            </tr>'''
        return f'''{filters}<div class="tbl-wrap" style="max-height:480px">
          <table id="tbl_s4{sfx}"><thead><tr>{ths}</tr></thead><tbody>{rows_html}</tbody></table>
        </div>'''

    inv_rows = item_rows(top50_inv, "inv")
    oxy_rows = item_rows(top50_oxy, "oxy")

    return f'''
    <div class="grid-2">{ae_chart}<div>{ae_defs}</div></div>
    <div class="sub-tabs" data-grp="s4">
      <span class="stab active" data-grp="s4" data-t="s4t0">📉 Top 50 Inversión (Δ CC −)</span>
      <span class="stab" data-grp="s4" data-t="s4t1">📈 Top 50 Oxigenación (Δ CC +)</span>
    </div>
    <div id="s4t0" class="stab-panel active">{inv_rows}</div>
    <div id="s4t1" class="stab-panel">{oxy_rows}</div>'''

# ── segment 5 ─────────────────────────────────────────────────────
def seg5_html(q13, q14):
    # Visual 1 — Competitor reaction TW vs LW + delta
    paises_13 = sorted(set(r.get("pais","") for r in q13 if r.get("pais")))
    COLORS = ["#0053e2","#ffc220","#2a8703","#ea1100","#7c3aed","#0891b2"]
    charts_v1 = ""
    for i, pais in enumerate(paises_13):
        rows_p = sorted([r for r in q13 if r.get("pais")==pais], key=lambda r: -(r.get("items_tw") or 0))
        labs  = [r.get("competidor","") for r in rows_p]
        tw    = [r.get("items_tw") or 0 for r in rows_p]
        lw    = [r.get("items_lw") or 0 for r in rows_p]
        delta = [r.get("delta_items") or 0 for r in rows_p]
        charts_v1 += bar_chart(labs, [
            {"label":"Ítems TW","data":tw,"backgroundColor":COLORS[i%len(COLORS)],"borderRadius":3},
            {"label":"Ítems LW","data":lw,"backgroundColor":"#e5e7eb","borderRadius":3},
        ], f"Reacción Competidores — {pais}", h=230)

    # Table V1
    hdrs_v1 = ["País","Competidor","Ítems TW","Ítems LW","Δ Ítems"]
    ths_v1 = "".join(f'<th>{h}</th>' for h in hdrs_v1)
    rows_v1 = ""
    for r in q13:
        d = r.get("delta_items") or 0
        rows_v1 += f'''<tr>
          <td class="fw">{r.get("pais","")}</td>
          <td>{r.get("competidor","")}</td>
          <td class="tr">{int(r.get("items_tw") or 0):,}</td>
          <td class="tr">{int(r.get("items_lw") or 0):,}</td>
          <td class="tr"><span style="color:{'#2a8703' if d>0 else '#ea1100' if d<0 else '#6b7280'};font-weight:600">{"▲" if d>0 else "▼" if d<0 else ""}{abs(d):,}</span></td>
        </tr>'''

    v1_ins = (insight("NIELSEN 90 domina en todos los países — benchmark universal del modelo competitivo CAM")
              + insight("Crecimiento de ítems monitoreados TW vs LW indica expansión de cobertura del modelo")
              + insight("COLMENA INTERNA presente en todos los mercados — canal interno clave para auto-monitoreo de precios"))

    tbl_v1 = f'<div class="tbl-wrap">{v1_ins}<table id="tbl_s5v1"><thead><tr>{ths_v1}</tr></thead><tbody>{rows_v1}</tbody></table></div>'

    visual1 = f'<div class="grid-3">{charts_v1}</div>{tbl_v1}'

    # Visual 2 — Price movement classification
    paises_14 = sorted(set(r.get("pais","") for r in q14 if r.get("pais")))
    comps_14  = sorted(set(r.get("competidor","") for r in q14 if r.get("competidor")))
    clases_14 = ["BAJO","SUBIO","MANTIENE","NUEVO REGISTRO","SOLO LW","SIN DATOS"]

    # Summary chart by classification
    by_cls = {}
    for r in q14:
        c = r.get("mov_precio_comp","SIN DATOS") or "SIN DATOS"
        by_cls[c] = by_cls.get(c, 0) + (r.get("total_items") or 0)

    cls_chart = doughnut_chart(
        list(by_cls.keys()), list(by_cls.values()),
        "Distribución Global — Movimiento Precios Competencia"
    )

    # Filters
    def opt(v): return "".join(f'<option>{x}</option>' for x in v)
    filters_v2 = f'''<div class="filter-bar">
      <label>País <select id="s5pais"><option value="">Todos</option>{opt(paises_14)}</select></label>
      <label>Competidor <input type="text" id="s5comp" placeholder="Buscar..." style="width:160px"></label>
      <label>División <input type="text" id="s5div" placeholder="División..."></label>
      <label>Categoría <input type="text" id="s5cat" placeholder="Categoría..."></label>
      <label>Clasificación
        <select id="s5cls">
          <option value="">Todas</option>
          {opt(clases_14)}
        </select>
      </label>
    </div>'''

    hdrs_v2 = ["País","Formato","Zona","División","Categoría","Tier","Competidor","Clasificación","Ítems"]
    ths_v2 = "".join(f'<th>{h}</th>' for h in hdrs_v2)
    BADGE_C = {"BAJO":"#ea1100","SUBIO":"#2a8703","MANTIENE":"#0053e2","NUEVO REGISTRO":"#d97706","SOLO LW":"#7c3aed","SIN DATOS":"#9ca3af"}
    rows_v2 = ""
    for r in q14:
        cls = r.get("mov_precio_comp","SIN DATOS") or "SIN DATOS"
        bc  = BADGE_C.get(cls,"#9ca3af")
        rows_v2 += f'''<tr>
          <td>{r.get("pais","")}</td><td>{r.get("formato","")}</td>
          <td>{r.get("zona","")}</td><td>{r.get("division","")}</td>
          <td>{r.get("categoria","")}</td><td>{r.get("tier","")}</td>
          <td>{r.get("competidor") or "—"}</td>
          <td><span class="cls-badge" style="background:{bc}">{cls}</span></td>
          <td class="tr">{int(r.get("total_items") or 0):,}</td>
        </tr>'''

    v2_ins = (insight("BAJO: la competencia bajó precios esta semana — activar plan de reacción según Tier y categoría prioritaria")
              + insight("SUBIO: la competencia subió precios — oportunidad de oxigenación controlada de márgenes sin perder posición")
              + insight("NUEVO REGISTRO: ítems que aparecen por primera vez en el modelo — validar con equipos de pricing local"))

    tbl_v2 = f'''{v2_ins}<div class="tbl-wrap" style="max-height:500px">
      <table id="tbl_s5v2"><thead><tr>{ths_v2}</tr></thead><tbody>{rows_v2}</tbody></table>
    </div>'''

    visual2 = f'<div class="grid-2">{cls_chart}<div>{v2_ins}</div></div>{filters_v2}{tbl_v2}'

    return f'''
    <div class="sub-tabs" data-grp="s5">
      <span class="stab active" data-grp="s5" data-t="s5t0">🏪 Visual 1 — Reacción Competidores (TW vs LW)</span>
      <span class="stab" data-grp="s5" data-t="s5t1">📊 Visual 2 — Movimiento Precios Competencia</span>
    </div>
    <div id="s5t0" class="stab-panel active">{visual1}</div>
    <div id="s5t1" class="stab-panel">{visual2}</div>'''

# ── JS for filters ────────────────────────────────────────────────
FILTER_JS = """
// ── Seg 3 filter ──────────────────────────────────────────────────
(function(){
  var tbl=document.getElementById('tbl_s3'); if(!tbl) return;
  var rows=[...tbl.querySelectorAll('tbody tr')];
  function go(){
    var p=document.getElementById('s3pais')?.value.toLowerCase()||'';
    var d=document.getElementById('s3div')?.value.toLowerCase()||'';
    var f=document.getElementById('s3fmt')?.value.toLowerCase()||'';
    var c=document.getElementById('s3cat')?.value.toLowerCase()||'';
    var t=document.getElementById('s3tier')?.value.toLowerCase()||'';
    var top=document.getElementById('s3top')?.value||'';
    var vis=rows.filter(r=>{
      var td=[...r.querySelectorAll('td')].map(x=>x.textContent.toLowerCase());
      return(!p||td[0].includes(p))&&(!d||td[1].includes(d))&&
             (!f||td[2].includes(f))&&(!c||td[3].includes(c))&&(!t||td[4].includes(t));
    });
    if(top==='inv') vis=vis.filter(r=>parseFloat(r.dataset.delta)<0).sort((a,b)=>parseFloat(a.dataset.delta)-parseFloat(b.dataset.delta)).slice(0,10);
    if(top==='oxy') vis=vis.filter(r=>parseFloat(r.dataset.delta)>0).sort((a,b)=>parseFloat(b.dataset.delta)-parseFloat(a.dataset.delta)).slice(0,10);
    rows.forEach(r=>r.style.display='none');
    vis.forEach(r=>r.style.display='');
    var cnt=document.getElementById('s3cnt');
    if(cnt) cnt.textContent=vis.length.toLocaleString()+' registros';
  }
  ['s3pais','s3div','s3fmt','s3tier','s3top'].forEach(id=>{
    var el=document.getElementById(id); if(el){el.onchange=go;el.oninput=go;}
  });
  document.getElementById('s3cat').oninput=go;
})();

// ── Seg 4 filter (inv + oxy) ──────────────────────────────────────
['inv','oxy'].forEach(sfx=>{
  (function(){
    var tbl=document.getElementById('tbl_s4'+sfx); if(!tbl) return;
    var rows=[...tbl.querySelectorAll('tbody tr')];
    function go(){
      var p=document.getElementById('f'+sfx+'pais')?.value.toLowerCase()||'';
      var d=document.getElementById('f'+sfx+'div')?.value.toLowerCase()||'';
      var c=document.getElementById('f'+sfx+'cat')?.value.toLowerCase()||'';
      var t=document.getElementById('f'+sfx+'tier')?.value.toLowerCase()||'';
      var it=document.getElementById('f'+sfx+'item')?.value.toLowerCase()||'';
      var ae=document.getElementById('f'+sfx+'ae')?.value||'';
      rows.forEach(r=>{
        var td=[...r.querySelectorAll('td')].map(x=>x.textContent.toLowerCase());
        var ok=(!p||td[0].includes(p))&&(!d||td[3].includes(d))&&
               (!c||td[4].includes(c))&&(!t||td[5].includes(t))&&
               (!it||td[6].includes(it))&&(!ae||r.dataset.ae===ae);
        r.style.display=ok?'':'none';
      });
    }
    ['pais','div','cat','tier','item','ae'].forEach(f=>{
      var el=document.getElementById('f'+sfx+f);
      if(el){el.onchange=go;el.oninput=go;}
    });
  })();
});

// ── Seg 5 v2 filter ───────────────────────────────────────────────
(function(){
  var tbl=document.getElementById('tbl_s5v2'); if(!tbl) return;
  var rows=[...tbl.querySelectorAll('tbody tr')];
  function go(){
    var p=document.getElementById('s5pais')?.value.toLowerCase()||'';
    var co=document.getElementById('s5comp')?.value.toLowerCase()||'';
    var d=document.getElementById('s5div')?.value.toLowerCase()||'';
    var c=document.getElementById('s5cat')?.value.toLowerCase()||'';
    var cl=document.getElementById('s5cls')?.value.toLowerCase()||'';
    rows.forEach(r=>{
      var td=[...r.querySelectorAll('td')].map(x=>x.textContent.toLowerCase());
      r.style.display=(!p||td[0].includes(p))&&(!co||td[6].includes(co))&&
        (!d||td[3].includes(d))&&(!c||td[4].includes(c))&&(!cl||td[7].includes(cl))?'':'none';
    });
  }
  ['s5pais','s5cls'].forEach(id=>{var el=document.getElementById(id);if(el){el.onchange=go;el.oninput=go;}});
  ['s5comp','s5div','s5cat'].forEach(id=>{var el=document.getElementById(id);if(el){el.oninput=go;}});
})();

// ── Sub-tabs ──────────────────────────────────────────────────────
document.querySelectorAll('.stab').forEach(t=>t.onclick=function(){
  var g=this.dataset.grp, tgt=this.dataset.t;
  document.querySelectorAll('.stab[data-grp="'+g+'"]').forEach(x=>x.classList.remove('active'));
  document.querySelectorAll('.stab-panel').forEach(x=>{
    if(x.id && document.querySelector('.stab[data-t="'+x.id+'"]')?.dataset.grp===g)
      x.classList.remove('active');
  });
  this.classList.add('active');
  document.getElementById(tgt)?.classList.add('active');
});

// ── Main tabs ─────────────────────────────────────────────────────
document.querySelectorAll('.mtab').forEach(t=>t.onclick=function(){
  document.querySelectorAll('.mtab').forEach(x=>x.classList.remove('active'));
  document.querySelectorAll('.mpanel').forEach(x=>x.classList.remove('active'));
  this.classList.add('active');
  document.getElementById(this.dataset.panel)?.classList.add('active');
});

// ── Seg 1 sub-tabs ────────────────────────────────────────────────
document.querySelectorAll('.s1tab').forEach(t=>t.onclick=function(){
  document.querySelectorAll('.s1tab').forEach(x=>x.classList.remove('active'));
  document.querySelectorAll('.s1panel').forEach(x=>x.classList.remove('active'));
  this.classList.add('active');
  document.getElementById(this.dataset.p)?.classList.add('active');
});

// ── Seg 2 sub-tabs ────────────────────────────────────────────────
document.querySelectorAll('.s2tab').forEach(t=>t.onclick=function(){
  document.querySelectorAll('.s2tab').forEach(x=>x.classList.remove('active'));
  document.querySelectorAll('.s2panel').forEach(x=>x.classList.remove('active'));
  this.classList.add('active');
  document.getElementById(this.dataset.p)?.classList.add('active');
});

// ── CSV export ────────────────────────────────────────────────────
function exportCSV(tid,fname){
  var tbl=document.getElementById(tid); if(!tbl) return;
  var rows=[...tbl.querySelectorAll('tr')].filter(r=>r.style.display!=='none');
  var csv=rows.map(r=>[...r.querySelectorAll('th,td')].map(c=>'"'+c.textContent.trim().replace(/"/g,'""')+'"').join(',')).join('\\n');
  var a=document.createElement('a');
  a.href='data:text/csv;charset=utf-8,\\uFEFF'+encodeURIComponent(csv);
  a.download=fname; a.click();
}
"""

# ── CSS ───────────────────────────────────────────────────────────
CSS = """
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:'Segoe UI',system-ui,sans-serif;background:#f0f4f8;color:#1e293b;font-size:13px;}
header{background:#0053e2;color:#fff;padding:16px 24px;display:flex;align-items:center;gap:16px;box-shadow:0 2px 8px rgba(0,0,0,.2);}
header h1{font-size:1.25rem;font-weight:700;letter-spacing:-.3px;}
header p{font-size:.78rem;color:#bfdbfe;margin-top:2px;}
.kpi-row{display:flex;flex-wrap:wrap;gap:10px;padding:16px 24px;background:#fff;border-bottom:1px solid #e2e8f0;}
.kpi{background:#f8fafc;border:1px solid #e2e8f0;border-left:4px solid #0053e2;border-radius:6px;padding:10px 14px;min-width:140px;}
.kpi.neg{border-color:#ea1100;}
.kpi.pos{border-color:#2a8703;}
.kpi.warn{border-color:#ffc220;}
.kpi-label{font-size:.68rem;color:#64748b;text-transform:uppercase;letter-spacing:.04em;font-weight:600;}
.kpi-val{font-size:1.3rem;font-weight:700;color:#0053e2;margin-top:3px;}
.kpi.neg .kpi-val{color:#ea1100;}
.kpi.pos .kpi-val{color:#2a8703;}
.main-tabs{display:flex;gap:0;padding:0 24px;background:#fff;border-bottom:2px solid #e2e8f0;overflow-x:auto;}
.mtab{padding:10px 18px;cursor:pointer;font-size:.82rem;font-weight:600;color:#64748b;border-bottom:3px solid transparent;white-space:nowrap;transition:.2s;}
.mtab.active{color:#0053e2;border-color:#0053e2;}
.mtab:hover{color:#0053e2;background:#f0f9ff;}
.mpanel{display:none;padding:20px 24px;}
.mpanel.active{display:block;}
.panel-title{font-size:1rem;font-weight:700;color:#0053e2;margin-bottom:14px;padding-bottom:8px;border-bottom:2px solid #e0e7ff;}
.sub-tabs{display:flex;flex-wrap:wrap;gap:2px;margin-bottom:16px;border-bottom:2px solid #e2e8f0;}
.s1tab,.s2tab,.stab{padding:7px 14px;cursor:pointer;font-size:.78rem;font-weight:600;color:#64748b;border-bottom:3px solid transparent;white-space:nowrap;transition:.2s;}
.s1tab.active,.s2tab.active,.stab.active{color:#0053e2;border-color:#0053e2;background:#f0f9ff;}
.s1panel,.s2panel,.stab-panel{display:none;}
.s1panel.active,.s2panel.active,.stab-panel.active{display:block;}
.grid-2{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-bottom:14px;}
.grid-2-2{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-bottom:14px;}
.grid-3{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:14px;}
@media(max-width:900px){.grid-2,.grid-2-2,.grid-3{grid-template-columns:1fr;}}
.chart-box{background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:14px;box-shadow:0 1px 4px rgba(0,0,0,.06);}
.chart-title{font-size:.75rem;font-weight:700;color:#475569;margin-bottom:10px;text-transform:uppercase;letter-spacing:.03em;}
.ins{background:#eff6ff;border-left:4px solid #0053e2;padding:8px 12px;border-radius:4px;margin:4px 0;font-size:.78rem;line-height:1.5;}
.tbl-wrap{overflow:auto;background:#fff;border:1px solid #e2e8f0;border-radius:8px;margin-top:12px;box-shadow:0 1px 4px rgba(0,0,0,.04);}
table{border-collapse:collapse;width:100%;}
th{position:sticky;top:0;background:#f8fafc;z-index:2;padding:7px 8px;text-align:left;font-size:.7rem;font-weight:700;color:#475569;text-transform:uppercase;letter-spacing:.04em;border-bottom:2px solid #e2e8f0;white-space:nowrap;}
td{padding:5px 8px;border-bottom:1px solid #f1f5f9;font-size:.75rem;white-space:nowrap;}
tr:hover td{background:#f8fafc;}
.fw{font-weight:600;}
.tr{text-align:right;}
.filter-bar{display:flex;flex-wrap:wrap;align-items:center;gap:10px;background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:12px 16px;margin-bottom:12px;}
.filter-bar label{display:flex;align-items:center;gap:5px;font-size:.75rem;font-weight:600;color:#475569;}
input,select{border:1px solid #cbd5e1;border-radius:5px;padding:4px 8px;font-size:.75rem;outline:none;}
input:focus,select:focus{border-color:#0053e2;box-shadow:0 0 0 2px #bfdbfe;}
.cnt{font-size:.75rem;color:#94a3b8;font-weight:600;margin-left:auto;}
.btn-export{background:#0053e2;color:#fff;border:none;border-radius:5px;padding:5px 12px;font-size:.75rem;font-weight:600;cursor:pointer;}
.btn-export:hover{background:#0042c4;}
.ae-def{border-left:4px solid #9ca3af;padding:6px 10px;margin:4px 0;border-radius:3px;font-size:.75rem;background:#fafafa;}
.ae-badge{display:inline-block;padding:1px 8px;border-radius:9999px;color:#fff;font-weight:700;font-size:.7rem;}
.cls-badge{display:inline-block;padding:2px 8px;border-radius:9999px;color:#fff;font-weight:700;font-size:.7rem;}
footer{text-align:center;font-size:.68rem;color:#94a3b8;padding:20px;border-top:1px solid #e2e8f0;margin-top:8px;}
"""

# ── BUILD ─────────────────────────────────────────────────────────
def build():
    q1  = load("v2-q1-pais-*.csv")
    q2  = load("v2-q2-division-*.csv")
    q3  = load("v2-q3-tier-*.csv")
    q4  = load("v2-q4-mov-precio-comp-*.csv")
    q5  = load("v2-q5-tendencia-ho-*.csv")
    q6  = load("v2-q6-respeto-modelo-*.csv")
    q7  = load("v2-q7-performance-*.csv")
    q8  = load("v2-q8-rangos-cc-*.csv")
    q9  = load("v2-q9-rango-pg-*.csv")
    q10 = load("v2-q10-rango-meta-*.csv")
    q11 = load("v2-q11-seg3-*.csv")
    q12 = load("v2-q12-clasificacion-ae-*.csv")
    q13 = load("v2-q13-competidores-*.csv")
    q14 = load("v2-q14-mov-precios-*.csv")

    # KPIs ejecutivos
    tot_items  = sum(r.get("total_items",0) or 0 for r in q1)
    tot_cc_tw  = sum(r.get("cc_ho_tw",0) or 0 for r in q1)
    tot_cc_lw  = sum(r.get("cc_ini_lw",0) or 0 for r in q1)
    delta_cc   = tot_cc_tw - tot_cc_lw
    tot_chg_tw = sum(r.get("cambios_tw",0) or 0 for r in q1)
    avg_pg_ini = sum((r.get("pct_pg_ho_ini") or 0) * (r.get("total_items") or 0) for r in q1) / max(tot_items,1)
    avg_bps_pg = sum(r.get("bps_pg") or 0 for r in q1) / max(len(q1),1)
    avg_bps_mb = sum(r.get("bps_mb") or 0 for r in q1) / max(len(q1),1)
    now = datetime.now().strftime("%d/%m/%Y %H:%M")

    def kpi(lbl, val, kind=""):
        return f'<div class="kpi {kind}"><div class="kpi-label">{lbl}</div><div class="kpi-val">{val}</div></div>'

    kpis = (
        kpi("Ítems Analizados", f"{tot_items:,.0f}")
        + kpi("CC HO TW", fmtM(tot_cc_tw), "neg" if tot_cc_tw<0 else "pos")
        + kpi("CC Inicial LW", fmtM(tot_cc_lw), "neg" if tot_cc_lw<0 else "pos")
        + kpi("Δ CC (TW−LW)", fmtM(delta_cc), "neg" if delta_cc<0 else "pos")
        + kpi("Cambios Precio TW", f"{tot_chg_tw:,.0f}", "warn")
        + kpi("Avg % PG HO Ini", fmtP(avg_pg_ini), "pos" if avg_pg_ini>0 else "neg")
        + kpi("Avg BPS PG", f"{'▼' if avg_bps_pg<0 else '▲'} {abs(avg_bps_pg):.1f}", "neg" if avg_bps_pg<0 else "pos")
        + kpi("Avg BPS MB", f"{'▼' if avg_bps_mb<0 else '▲'} {abs(avg_bps_mb):.1f}", "neg" if avg_bps_mb<0 else "pos")
    )

    # Build all segments
    s1 = seg1_visual(q1,"pais","País","pais")
    s1d = seg1_visual(q2,"division","División","div")
    s1t = seg1_visual(q3,"tier","Tier","tier")
    s1f1 = seg1_visual(q4,"flag_movimiento_precio_comp","Flag Mov. Precio Comp","mpc")
    s1f2 = seg1_visual(q5,"tendencia_reaccion_ho","Tendencia Reacción HO","trh")
    s1f3 = seg1_visual(q6,"flag_respeto_pricing_modelo","Respeto Modelo","rpm")

    s2p  = seg2_visual(q7,"PERFORMANCE_PRIMARIO","Performance","perf")
    s2r  = seg2_visual(q8,"RANGOS_COSTO_COMPETITIVO_INICIAL","Rango CC","rcc")
    s2pg = seg2_visual(q9,"RANGO_PG_ACTUAL","Rango PG Actual","rpg")
    s2m  = seg2_visual(q10,"RANGO_META","Rango Meta","rmeta")

    s3 = seg3_html(q11)
    s4 = seg4_html(q12)
    s5 = seg5_html(q13, q14)

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Análisis Semanal de Impactos Modelo — CAM Pricing</title>
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>{CSS}</style>
</head>
<body>

<header>
  <div style="font-size:2rem">🏪</div>
  <div>
    <h1>Análisis Semanal de Impactos Modelo — Pricing CAM</h1>
    <p>Centroamérica: CR · GT · HN · SV · NI &nbsp;|&nbsp; Sin MG Y TEXTIL &nbsp;|&nbsp; Generado: {now} &nbsp;|&nbsp;
    Fórmulas: <a href="https://github.com/Redstar2026/Puppy_workspace/wiki/Formulas" style="color:#93c5fd">Wiki GitHub</a></p>
  </div>
</header>

<!-- KPIs ejecutivos -->
<div class="kpi-row">{kpis}</div>

<!-- Insights ejecutivos -->
<div style="padding:10px 24px;display:flex;flex-wrap:wrap;gap:8px;background:#fff;border-bottom:1px solid #e2e8f0;">
  {insight("GT acumula mayor inversión competitiva (Δ CC " + fmtM(min(q1,key=lambda r:r.get('delta_cc') or 0).get('delta_cc')) + ") — evaluar plan de reacción urgente")}
  {insight("Avg BPS PG regional " + ("▼" if avg_bps_pg<0 else "▲") + f" {abs(avg_bps_pg):.1f} bps — " + ("presión sistémica sobre el Price Gap del modelo" if avg_bps_pg<0 else "mejora del Price Gap vs semana anterior"))}
  {insight("BAJA PRECIO COMP genera BPS PG ▼237.9 bps — mayor correlación entre movimiento competitivo y erosión de margen")}
  {insight("SUBE PRECIO COMP genera BPS MB ▲421.1 bps — capturar oportunidad de oxigenación en ítems con competencia alzando precios")}
</div>

<!-- Main tabs -->
<div class="main-tabs">
  <div class="mtab active" data-panel="p1">📊 Seg.1 Análisis General</div>
  <div class="mtab" data-panel="p2">🔬 Seg.2 Calidad</div>
  <div class="mtab" data-panel="p3">📋 Seg.3 Categoría / Competidor</div>
  <div class="mtab" data-panel="p4">🔍 Seg.4 Micro Ítem</div>
  <div class="mtab" data-panel="p5">🏆 Seg.5 Competitivo</div>
</div>

<!-- SEG 1 -->
<div id="p1" class="mpanel active">
  <div class="panel-title">Segmento 1 — Análisis General Comparativo Semanal</div>
  <div class="sub-tabs">
    <span class="s1tab active" data-p="s1p0">🌎 Por País</span>
    <span class="s1tab" data-p="s1p1">🏢 Por División</span>
    <span class="s1tab" data-p="s1p2">🎯 Por Tier</span>
    <span class="s1tab" data-p="s1p3">📊 Mov. Precio Comp</span>
    <span class="s1tab" data-p="s1p4">📈 Tendencia Reacción HO</span>
    <span class="s1tab" data-p="s1p5">✅ Respeto Modelo</span>
  </div>
  <div id="s1p0" class="s1panel active">{s1}</div>
  <div id="s1p1" class="s1panel">{s1d}</div>
  <div id="s1p2" class="s1panel">{s1t}</div>
  <div id="s1p3" class="s1panel">{s1f1}</div>
  <div id="s1p4" class="s1panel">{s1f2}</div>
  <div id="s1p5" class="s1panel">{s1f3}</div>
</div>

<!-- SEG 2 -->
<div id="p2" class="mpanel">
  <div class="panel-title">Segmento 2 — Nuevo Análisis de Calidad</div>
  <div class="sub-tabs">
    <span class="s2tab active" data-p="s2p0">🏆 Performance Primario</span>
    <span class="s2tab" data-p="s2p1">💲 Rangos CC Inicial</span>
    <span class="s2tab" data-p="s2p2">📊 Rango PG Actual</span>
    <span class="s2tab" data-p="s2p3">🎯 Rango Meta</span>
  </div>
  <div id="s2p0" class="s2panel active">{s2p}</div>
  <div id="s2p1" class="s2panel">{s2r}</div>
  <div id="s2p2" class="s2panel">{s2pg}</div>
  <div id="s2p3" class="s2panel">{s2m}</div>
</div>

<!-- SEG 3 -->
<div id="p3" class="mpanel">
  <div class="panel-title">Segmento 3 — Detalle Categoría / Competidor</div>
  {s3}
</div>

<!-- SEG 4 -->
<div id="p4" class="mpanel">
  <div class="panel-title">Segmento 4 — Análisis Micro Ítem</div>
  {s4}
</div>

<!-- SEG 5 -->
<div id="p5" class="mpanel">
  <div class="panel-title">Segmento 5 — Análisis Competitivo / Competidores</div>
  {s5}
</div>

<footer>
  Análisis Semanal de Impactos Modelo · Pricing CAM · Walmart · Generado {now}<br>
  Fuente: wmt-k1-cons-data-users.k1_adhoc_tables.prcng_info_cam_a0g0dn3_impactos_modelo_semanal · 
  Fórmulas: <a href="https://github.com/Redstar2026/Puppy_workspace/wiki/Formulas">Wiki GitHub Formulas</a> · 
  <a href="https://github.com/Redstar2026/Puppy_workspace/wiki/Glosario">Wiki GitHub Glosario</a>
</footer>

<script>{FILTER_JS}</script>
</body>
</html>"""

    out_path = os.path.join(OUT, "dashboard_impactos_v2.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("Dashboard v2 generado: " + out_path)
    return out_path

if __name__ == "__main__":
    p = build()
    import subprocess, sys
    if sys.platform == "win32":
        subprocess.Popen(["cmd","/c","start",p])

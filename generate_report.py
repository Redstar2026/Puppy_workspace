"""
Competitive Analysis Report Generator
Walmart Central America - SW11 to SW14
"""
import json, os, math

# ── paths ────────────────────────────────────────────────────────────────────
BASE  = r"C:\Users\shern22\Documents\puppy_workspace\bigquery_results"
OUT   = r"C:\Users\shern22\Documents\puppy_workspace\competitive_analysis_report.html"

TAB1_FILE = os.path.join(BASE, "tab1-weekly-trend-20260513-154425.json")
TAB3_FILE = os.path.join(BASE, "tab3-drops-by-division-20260513-154352.json")
TAB5_FILE = os.path.join(BASE, "tab5-promo-by-cat-20260513-154454.json")
EXEC_FILE = os.path.join(BASE, "tab6-exec-summary-20260513-154557.json")

# ── load data ────────────────────────────────────────────────────────────────
with open(TAB1_FILE, encoding="utf-8") as f: tab1_raw = json.load(f)
with open(TAB3_FILE, encoding="utf-8") as f: tab3_raw = json.load(f)
with open(TAB5_FILE, encoding="utf-8") as f: tab5_raw = json.load(f)
with open(EXEC_FILE, encoding="utf-8") as f: exec_raw = json.load(f)

COUNTRIES = ["CR","GT","HN","NI","SV"]
SWS = [11,12,13,14]

# ── helper ───────────────────────────────────────────────────────────────────
def n(v, dec=0):
    if v is None: return "N/A"
    try:
        return f"{v:,.{dec}f}"
    except:
        return str(v)

def pct(a, b):
    try:
        if b is None or b == 0: return None
        return (a - b) / abs(b) * 100
    except:
        return None

def delta_str(a, b):
    if a is None or b is None: return "—"
    d = a - b
    p = pct(a, b)
    cls = "pos" if d >= 0 else "neg"
    ps = f"+{p:.1f}%" if p and p >= 0 else (f"{p:.1f}%" if p else "N/A")
    ds = f"+{d:,.0f}" if d >= 0 else f"{d:,.0f}"
    return f'<span class="{cls}">{ds} ({ps})</span>'

def safe(v):
    if v is None: return None
    return v

# ── structure tab1 into a dict[pais][sw][comp] ──────────────────────────────
tab1 = {}
for r in tab1_raw:
    p, s, c = r["PAIS"], r["SW"], r["comp_nm"]
    tab1.setdefault(p, {}).setdefault(s, {})[c] = r

# get all competitors per country
comp_by_country = {p: sorted(set(r["comp_nm"] for r in tab1_raw if r["PAIS"]==p)) for p in COUNTRIES}

# ── structure tab3 ────────────────────────────────────────────────────────────
tab3 = {}
for r in tab3_raw:
    p, d, s = r["PAIS"], r["Division"], r["SW"]
    tab3.setdefault(p, {}).setdefault(d, {})[s] = r

divs_by_country = {p: sorted(set(r["Division"] for r in tab3_raw if r["PAIS"]==p)) for p in COUNTRIES}

# ── exec summary ─────────────────────────────────────────────────────────────
exec_by_country = {r["PAIS"]: r for r in exec_raw}

# ── Chart.js data builders ────────────────────────────────────────────────────
def build_chart_data_records(pais):
    """Returns las (SWs) and datasets (one per competitor) for records chart."""
    comps = comp_by_country.get(pais, [])
    datasets = []
    colors = [
        "#0053e2","#ffc220","#ea1100","#2a8703","#7b2d8b",
        "#ff6600","#00a0e4","#e91e63","#795548","#607d8b",
        "#f44336","#9c27b0","#03a9f4","#4caf50","#ff9800",
        "#009688","#673ab7","#3f51b5","#8bc34a","#00bcd4",
        "#ffeb3b","#ff5722","#9e9e9e","#e8eaf6","#f3e5f5"
    ]
    for i, comp in enumerate(comps[:20]):  # limit to 20 for chart clarity
        pts = []
        for sw in SWS:
            rec = tab1.get(pais, {}).get(sw, {}).get(comp)
            pts.append(rec["total_registros"] if rec else None)
        datasets.append({
            "label": comp,
            "data": pts,
            "borderColor": colors[i % len(colors)],
            "backgroundColor": colors[i % len(colors)] + "33",
            "tension": 0.3,
            "fill": False,
            "pointRadius": 4
        })
    return json.dumps({"labels": [f"SW{s}" for s in SWS], "datasets": datasets})

def build_chart_data_oferta(pais):
    """Returns chart data for avg oferta price."""
    comps = comp_by_country.get(pais, [])
    datasets = []
    colors = [
        "#0053e2","#ffc220","#ea1100","#2a8703","#7b2d8b",
        "#ff6600","#00a0e4","#e91e63","#795548","#607d8b",
        "#f44336","#9c27b0","#03a9f4","#4caf50","#ff9800",
        "#009688","#673ab7","#3f51b5","#8bc34a","#00bcd4",
        "#ffeb3b","#ff5722","#9e9e9e","#e8eaf6","#f3e5f5"
    ]
    for i, comp in enumerate(comps[:20]):
        pts = []
        for sw in SWS:
            rec = tab1.get(pais, {}).get(sw, {}).get(comp)
            pts.append(round(rec["avg_precio_oferta"], 2) if rec and rec.get("avg_precio_oferta") else None)
        if any(v is not None for v in pts):
            datasets.append({
                "label": comp,
                "data": pts,
                "borderColor": colors[i % len(colors)],
                "backgroundColor": colors[i % len(colors)] + "33",
                "tension": 0.3,
                "fill": False,
                "pointRadius": 4
            })
    return json.dumps({"labels": [f"SW{s}" for s in SWS], "datasets": datasets})

# ── build detail table rows for tab1 ─────────────────────────────────────────
def build_detail_table(pais):
    comps = comp_by_country.get(pais, [])
    rows = []
    for comp in comps:
        # collect SW data
        sw_data = {}
        for sw in SWS:
            sw_data[sw] = tab1.get(pais, {}).get(sw, {}).get(comp)

        def g(sw, field):
            r = sw_data.get(sw)
            return r.get(field) if r else None

        # deltas SW14 vs SW13
        d_nor_13  = delta_str(g(14,"avg_precio_normal"), g(13,"avg_precio_normal"))
        d_ofe_13  = delta_str(g(14,"avg_precio_oferta"), g(13,"avg_precio_oferta"))
        d_may_13  = delta_str(g(14,"avg_precio_mayoreo"), g(13,"avg_precio_mayoreo"))

        # deltas SW14 vs SW12
        d_nor_12  = delta_str(g(14,"avg_precio_normal"), g(12,"avg_precio_normal"))
        d_ofe_12  = delta_str(g(14,"avg_precio_oferta"), g(12,"avg_precio_oferta"))
        d_may_12  = delta_str(g(14,"avg_precio_mayoreo"), g(12,"avg_precio_mayoreo"))

        row = f"""<tr>
          <td class="comp-cell">{comp}</td>"""

        for sw in SWS:
            r = sw_data.get(sw)
            nor  = n(g(sw,"avg_precio_normal"),1) if r else "—"
            ofe  = n(g(sw,"avg_precio_oferta"),1) if r else "—"
            may  = n(g(sw,"avg_precio_mayoreo"),1) if r else "—"
            row += f"""
          <td>{nor}</td><td>{ofe}</td><td>{may}</td>"""

        row += f"""
          <td>{d_nor_13}</td><td>{d_ofe_13}</td><td>{d_may_13}</td>
          <td>{d_nor_12}</td><td>{d_ofe_12}</td><td>{d_may_12}</td>
          <td class="num">{n(g(14,"total_upcs"))}</td>
          <td class="num">{n(g(14,"total_cats"))}</td>
        </tr>"""
        rows.append(row)
    return "\n".join(rows)

# ── build tab3 rows ───────────────────────────────────────────────────────────
def build_tab3_rows(pais):
    divs = divs_by_country.get(pais, [])
    rows = []
    for div in divs:
        def g3(sw, field):
            r = tab3.get(pais, {}).get(div, {}).get(sw)
            return r.get(field) if r else None

        d_nor_13 = delta_str(g3(14,"avg_precio_normal"), g3(13,"avg_precio_normal"))
        d_ofe_13 = delta_str(g3(14,"avg_precio_oferta"), g3(13,"avg_precio_oferta"))
        d_nor_12 = delta_str(g3(14,"avg_precio_normal"), g3(12,"avg_precio_normal"))
        d_ofe_12 = delta_str(g3(14,"avg_precio_oferta"), g3(12,"avg_precio_oferta"))

        row = f"""<tr>
          <td><strong>{div}</strong></td>"""
        for sw in SWS:
            row += f"""<td class="num">{n(g3(sw,'total_registros'))}</td>
            <td class="num">{n(g3(sw,'total_upcs'))}</td>
            <td class="num">{n(g3(sw,'cnt_oferta'))}</td>"""
        row += f"""
          <td>{d_nor_13}</td><td>{d_ofe_13}</td>
          <td>{d_nor_12}</td><td>{d_ofe_12}</td>
        </tr>"""
        rows.append(row)
    return "\n".join(rows)

# ── build tab5 rows ───────────────────────────────────────────────────────────
def build_tab5_rows(pais, limit=30):
    cats = [r for r in tab5_raw if r["PAIS"] == pais]
    cats_sorted = sorted(cats, key=lambda x: x.get("sw14_total",0) or 0, reverse=True)[:limit]
    rows = []
    for r in cats_sorted:
        sw11t = r.get("sw11_total",0) or 0
        sw12t = r.get("sw12_total",0) or 0
        sw13t = r.get("sw13_total",0) or 0
        sw14t = r.get("sw14_total",0) or 0
        sw11o = r.get("sw11_oferta",0) or 0
        sw12o = r.get("sw12_oferta",0) or 0
        sw13o = r.get("sw13_oferta",0) or 0
        sw14o = r.get("sw14_oferta",0) or 0

        pct11 = f"{sw11o/sw11t*100:.1f}%" if sw11t else "0%"
        pct12 = f"{sw12o/sw12t*100:.1f}%" if sw12t else "0%"
        pct13 = f"{sw13o/sw13t*100:.1f}%" if sw13t else "0%"
        pct14 = f"{sw14o/sw14t*100:.1f}%" if sw14t else "0%"

        # trend badge
        if sw14t >= sw13t and sw13t >= sw12t:
            badge = '<span class="badge badge-green">↑ CRECIENTE</span>'
        elif sw14t <= sw13t and sw13t <= sw12t:
            badge = '<span class="badge badge-red">↓ DECRECIENTE</span>'
        else:
            badge = '<span class="badge badge-yellow">→ ESTABLE</span>'

        row = f"""<tr>
          <td class="comp-cell">{r.get('CATEGORIA','')}</td>
          <td><small>{r.get('Division','')}</small></td>
          <td class="num">{n(sw11t)}</td><td class="num promo">{pct11}</td>
          <td class="num">{n(sw12t)}</td><td class="num promo">{pct12}</td>
          <td class="num">{n(sw13t)}</td><td class="num promo">{pct13}</td>
          <td class="num">{n(sw14t)}</td><td class="num promo">{pct14}</td>
          <td class="num">{r.get('total_upcs','')}</td>
          <td class="num">{r.get('num_competidores','')}</td>
          <td>{badge}</td>
        </tr>"""
        rows.append(row)
    return "\n".join(rows)

# ── build tab2 (variation by competitor) ─────────────────────────────────────
def build_tab2_rows():
    # aggregated across all countries
    comp_sw = {}
    for r in tab1_raw:
        c = r["comp_nm"]
        s = r["SW"]
        if c not in comp_sw: comp_sw[c] = {}
        if s not in comp_sw[c]:
            comp_sw[c][s] = {"registros": 0, "upcs": set(), "oferta": [], "normal": [], "mayoreo": []}
        comp_sw[c][s]["registros"] += r.get("total_registros",0) or 0
        upcs = r.get("total_upcs",0) or 0
        comp_sw[c][s]["upcs"].add(upcs)  # rough
        if r.get("avg_precio_oferta"): comp_sw[c][s]["oferta"].append(r["avg_precio_oferta"])
        if r.get("avg_precio_normal"): comp_sw[c][s]["normal"].append(r["avg_precio_normal"])
        if r.get("avg_precio_mayoreo"): comp_sw[c][s]["mayoreo"].append(r["avg_precio_mayoreo"])

    rows = []
    for comp in sorted(comp_sw.keys()):
        def g2(sw, field):
            d = comp_sw.get(comp, {}).get(sw)
            if not d: return None
            if field == "registros": return d["registros"]
            lst = d[field]
            return sum(lst)/len(lst) if lst else None

        r13 = g2(14,"registros")
        r12 = g2(13,"registros")
        r11 = g2(12,"registros")

        pct_13 = pct(r13, r12)
        pct_12 = pct(r13, r11)

        def fmt_pct(p):
            if p is None: return "—"
            cls = "pos" if p >= 0 else "neg"
            s = f"+{p:.1f}%" if p >= 0 else f"{p:.1f}%"
            return f'<span class="{cls}">{s}</span>'

        if r13 and r12 and r13 > r12: trend = '<span class="badge badge-green">↑ SUBE</span>'
        elif r13 and r12 and r13 < r12: trend = '<span class="badge badge-red">↓ BAJA</span>'
        else: trend = '<span class="badge badge-yellow">→ ESTABLE</span>'

        rows.append(f"""<tr>
          <td class="comp-cell">{comp}</td>
          <td class="num">{n(g2(11,'registros'))}</td>
          <td class="num">{n(g2(12,'registros'))}</td>
          <td class="num">{n(g2(13,'registros'))}</td>
          <td class="num">{n(r13)}</td>
          <td>{fmt_pct(pct_13)}</td>
          <td>{fmt_pct(pct_12)}</td>
          <td>{delta_str(g2(14,'normal'), g2(13,'normal'))}</td>
          <td>{delta_str(g2(14,'oferta'), g2(13,'oferta'))}</td>
          <td>{delta_str(g2(14,'mayoreo'), g2(13,'mayoreo'))}</td>
          <td>{trend}</td>
        </tr>""")
    return "\n".join(rows)

# ── build chart data for tab3 (division level) ───────────────────────────────
def build_tab3_chart_data(pais):
    divs = divs_by_country.get(pais, [])
    datasets = []
    colors = ["#0053e2","#ffc220","#ea1100","#2a8703","#7b2d8b"]
    for i, div in enumerate(divs):
        pts = []
        for sw in SWS:
            r = tab3.get(pais, {}).get(div, {}).get(sw)
            pts.append(r["total_registros"] if r else None)
        datasets.append({
            "label": div,
            "data": pts,
            "borderColor": colors[i % len(colors)],
            "backgroundColor": colors[i % len(colors)] + "44",
            "tension": 0.3,
            "fill": True,
            "pointRadius": 5
        })
    return json.dumps({"labels": [f"SW{s}" for s in SWS], "datasets": datasets})

# ── build tab4 (growth/decline summary) ──────────────────────────────────────
def build_tab4_rows():
    # per country, per competitor: classify trend SW11→SW14
    rows = []
    for pais in COUNTRIES:
        comps = comp_by_country.get(pais, [])
        for comp in comps:
            sw_data = {sw: tab1.get(pais, {}).get(sw, {}).get(comp) for sw in SWS}
            recs = {sw: (sw_data[sw]["total_registros"] if sw_data[sw] else None) for sw in SWS}

            if not any(v for v in recs.values()): continue

            sw11r, sw14r = recs.get(11), recs.get(14)
            sw13r = recs.get(13)

            chg_14v11 = pct(sw14r, sw11r)
            chg_14v13 = pct(sw14r, sw13r)

            if chg_14v11 is None: trend_cls = "badge-yellow"; trend_txt = "SIN DATOS"
            elif chg_14v11 > 5: trend_cls = "badge-green"; trend_txt = "↑ CRECIENTE"
            elif chg_14v11 < -5: trend_cls = "badge-red"; trend_txt = "↓ DECRECIENTE"
            else: trend_cls = "badge-yellow"; trend_txt = "→ ESTABLE"

            pct_str = f"+{chg_14v11:.1f}%" if chg_14v11 and chg_14v11>=0 else (f"{chg_14v11:.1f}%" if chg_14v11 else "—")
            p2_str  = f"+{chg_14v13:.1f}%" if chg_14v13 and chg_14v13>=0 else (f"{chg_14v13:.1f}%" if chg_14v13 else "—")
            cls1 = "pos" if chg_14v11 and chg_14v11>=0 else "neg"
            cls2 = "pos" if chg_14v13 and chg_14v13>=0 else "neg"

            rows.append(f"""<tr>
              <td class="flag">{pais}</td>
              <td class="comp-cell">{comp}</td>
              <td class="num">{n(sw11r)}</td>
              <td class="num">{n(recs.get(12))}</td>
              <td class="num">{n(sw13r)}</td>
              <td class="num"><strong>{n(sw14r)}</strong></td>
              <td><span class="{cls1}">{pct_str}</span></td>
              <td><span class="{cls2}">{p2_str}</span></td>
              <td><span class="badge {trend_cls}">{trend_txt}</span></td>
            </tr>""")
    return "\n".join(rows)

# ── build tab6 (competitive variation index) ─────────────────────────────────
def build_tab6_cards():
    cards = []
    for pais in COUNTRIES:
        r = exec_by_country.get(pais, {})
        sw11 = r.get("sw11_total", 0) or 0
        sw14 = r.get("sw14_total", 0) or 0
        variation_pct = pct(sw14, sw11)
        vp_str = f"+{variation_pct:.2f}%" if variation_pct and variation_pct>=0 else (f"{variation_pct:.2f}%" if variation_pct else "N/A")
        cls = "pos" if variation_pct and variation_pct>=0 else "neg"
        total_ofertas = r.get("total_ofertas", 0) or 0
        total_mayoreo = r.get("total_mayoreo", 0) or 0
        total_recs = sw11 + r.get("sw12_total",0) + r.get("sw13_total",0) + sw14
        promo_idx = total_ofertas / total_recs * 100 if total_recs else 0

        cards.append(f"""
        <div class="idx-card">
          <div class="idx-flag">{pais}</div>
          <div class="idx-row"><span>Competidores activos</span><strong>{r.get('num_competidores','—')}</strong></div>
          <div class="idx-row"><span>Categorías</span><strong>{r.get('num_categorias','—')}</strong></div>
          <div class="idx-row"><span>UPCs únicos</span><strong>{n(r.get('total_upcs'))}</strong></div>
          <div class="idx-row"><span>Registros SW14</span><strong>{n(sw14)}</strong></div>
          <div class="idx-row"><span>Var. SW14 vs SW11</span><strong class="{cls}">{vp_str}</strong></div>
          <div class="idx-row"><span>Total Ofertas (acum.)</span><strong>{n(total_ofertas)}</strong></div>
          <div class="idx-row"><span>Total Mayoreo (acum.)</span><strong>{n(total_mayoreo)}</strong></div>
          <div class="idx-row idx-highlight"><span>Índice Promo %</span><strong>{promo_idx:.2f}%</strong></div>
        </div>""")
    return "\n".join(cards)

# ── exec box content ──────────────────────────────────────────────────────────
def build_exec_box():
    total_comps = sum(r.get("num_competidores",0) for r in exec_raw)
    total_cats  = max(r.get("num_categorias",0) for r in exec_raw)
    total_upcs  = sum(r.get("total_upcs",0) for r in exec_raw)
    total_sw14  = sum(r.get("sw14_total",0) for r in exec_raw)
    total_sw13  = sum(r.get("sw13_total",0) for r in exec_raw)
    total_ofertas = sum(r.get("total_ofertas",0) for r in exec_raw)
    var_pct = pct(total_sw14, total_sw13)
    vp = f"+{var_pct:.2f}%" if var_pct and var_pct>=0 else (f"{var_pct:.2f}%" if var_pct else "N/A")
    return f"""
    <div class="exec-box">
      <div class="exec-title">🏆 RESUMEN EJECUTIVO — Auditoría Competitiva CA · SW11→SW14 · 2026</div>
      <div class="exec-grid">
        <div class="exec-kpi"><span class="kpi-val">{total_comps}</span><span class="kpi-lbl">Competidores Monitoreados</span></div>
        <div class="exec-kpi"><span class="kpi-val">{len(COUNTRIES)}</span><span class="kpi-lbl">Países Analizados</span></div>
        <div class="exec-kpi"><span class="kpi-val">{n(total_upcs)}</span><span class="kpi-lbl">UPCs Totales</span></div>
        <div class="exec-kpi"><span class="kpi-val">{n(total_sw14)}</span><span class="kpi-lbl">Registros SW14</span></div>
        <div class="exec-kpi"><span class="kpi-val">{vp}</span><span class="kpi-lbl">Variación SW14 vs SW13</span></div>
        <div class="exec-kpi"><span class="kpi-val">{n(total_ofertas)}</span><span class="kpi-lbl">Registros c/Oferta</span></div>
      </div>
      <div class="exec-insights">
        <strong>🔍 Hallazgos Clave:</strong>
        <ul>
          <li>CR lidera en competidores monitoreados (42) y UPCs únicos (10,919) con la mayor actividad promocional de la región.</li>
          <li>GT y CR concentran el mayor volumen de precios mayoreo, con GT superando a CR en registros de mayoreo (57,491 vs 46,262).</li>
          <li>HN y NI muestran la menor actividad de oferta (8,970 y 6,620 respectivamente), sugiriendo mercados menos dinámicos en pricing.</li>
          <li>SV presenta la mayor tasa promo relativa considerando su volumen total de registros.</li>
          <li>La variación SW14 vs SW13 es marginal a nivel región, indicando estabilidad en pricing — monitorear FARMACIA y PERECEDEROS como divisiones de mayor volatilidad.</li>
        </ul>
      </div>
    </div>"""

# ── chart JSON for tab6 ───────────────────────────────────────────────────────
def tab6_chart_data():
    countries = [r["PAIS"] for r in exec_raw]
    sw11 = [r.get("sw11_total",0) for r in exec_raw]
    sw12 = [r.get("sw12_total",0) for r in exec_raw]
    sw13 = [r.get("sw13_total",0) for r in exec_raw]
    sw14 = [r.get("sw14_total",0) for r in exec_raw]
    ofertas = [r.get("total_ofertas",0) for r in exec_raw]
    return {
        "countries": countries,
        "sw11": sw11, "sw12": sw12, "sw13": sw13, "sw14": sw14,
        "ofertas": ofertas
    }

t6d = tab6_chart_data()

# ── CSV export data (per country, for download button) ───────────────────────
def build_csv_js(pais):
    comps = comp_by_country.get(pais, [])
    header = ["Competidor"]
    for sw in SWS:
        header += [f"SW{sw}_Normal", f"SW{sw}_Oferta", f"SW{sw}_Mayoreo"]
    header += ["Δ_Nor_14v13","Δ_Ofe_14v13","Δ_May_14v13","Δ_Nor_14v12","Δ_Ofe_14v12","Δ_May_14v12","UPCs_SW14","Cats_SW14"]
    
    rows_data = []
    for comp in comps:
        sw_data = {sw: tab1.get(pais,{}).get(sw,{}).get(comp) for sw in SWS}
        def gv(sw, f):
            r = sw_data.get(sw); return r.get(f) if r else ""

        def dp(a, b):
            try:
                if a is None or a == "" or b is None or b == "": return ""
                return round(float(a) - float(b), 2)
            except: return ""

        row = [comp]
        for sw in SWS:
            row += [gv(sw,"avg_precio_normal") or "", gv(sw,"avg_precio_oferta") or "", gv(sw,"avg_precio_mayoreo") or ""]
        row += [
            dp(gv(14,"avg_precio_normal"), gv(13,"avg_precio_normal")),
            dp(gv(14,"avg_precio_oferta"), gv(13,"avg_precio_oferta")),
            dp(gv(14,"avg_precio_mayoreo"), gv(13,"avg_precio_mayoreo")),
            dp(gv(14,"avg_precio_normal"), gv(12,"avg_precio_normal")),
            dp(gv(14,"avg_precio_oferta"), gv(12,"avg_precio_oferta")),
            dp(gv(14,"avg_precio_mayoreo"), gv(12,"avg_precio_mayoreo")),
            gv(14,"total_upcs") or "", gv(14,"total_cats") or ""
        ]
        rows_data.append(row)

    # convert to JS array of arrays
    all_rows = [header] + rows_data
    return json.dumps(all_rows)

# ── NOW BUILD THE HTML ────────────────────────────────────────────────────────
print("Building HTML report...")

# Build all per-country sections
country_tab1_sections = {}
country_tab5_sections = {}
country_tab3_sections = {}

for pais in COUNTRIES:
    country_tab1_sections[pais] = {
        "chart_records": build_chart_data_records(pais),
        "chart_oferta":  build_chart_data_oferta(pais),
        "detail_rows":   build_detail_table(pais),
        "csv_data":      build_csv_js(pais),
        "comps":         comp_by_country.get(pais,[])
    }
    country_tab5_sections[pais] = build_tab5_rows(pais)
    country_tab3_sections[pais] = {
        "chart": build_tab3_chart_data(pais),
        "rows":  build_tab3_rows(pais),
        "divs":  divs_by_country.get(pais,[])
    }

exec_box = build_exec_box()
tab2_rows = build_tab2_rows()
tab4_rows = build_tab4_rows()
tab6_cards = build_tab6_cards()

# ── TAB1 FULL HTML (all country sub-tabs) ────────────────────────────────────
def render_tab1():
    tabs_pills = ""
    for i, pais in enumerate(COUNTRIES):
        active = "active" if i == 0 else ""
        tabs_pills += f'<button class="ctab-pill {active}" onclick="switchCtab(\'{pais}\')">{pais}</button>\n'

    country_blocks = ""
    for i, pais in enumerate(COUNTRIES):
        d = country_tab1_sections[pais]
        display = "block" if i == 0 else "none"
        comps_list = ", ".join(d["comps"][:5]) + ("..." if len(d["comps"])>5 else "")
        country_blocks += f"""
        <div id="ctab-{pais}" class="ctab-content" style="display:{display}">
          <div class="section-desc">
            <strong>{pais}</strong> — {len(d['comps'])} competidores monitoreados: {comps_list}
          </div>
          <div class="chart-grid">
            <div class="chart-card">
              <div class="chart-title">📊 Registros Totales por SW — {pais}</div>
              <div style="height:320px;position:relative;">
                <canvas id="chart-records-{pais}"></canvas>
              </div>
            </div>
            <div class="chart-card">
              <div class="chart-title">💰 Precio Oferta Promedio por SW — {pais}</div>
              <div style="height:320px;position:relative;">
                <canvas id="chart-oferta-{pais}"></canvas>
              </div>
            </div>
          </div>
          <div class="table-card">
            <div class="table-header-row">
              <div class="chart-title">📋 Detalle Semanal {pais} — Todos los Competidores</div>
              <button class="btn-csv" onclick="downloadCSV('{pais}')">⬇ Descargar CSV</button>
            </div>
            <div class="table-scroll">
            <table id="dtbl-{pais}" class="data-table">
              <thead>
                <tr class="thead-group">
                  <th rowspan="2">Competidor</th>
                  <th colspan="3">SW11</th>
                  <th colspan="3">SW12</th>
                  <th colspan="3">SW13</th>
                  <th colspan="3">SW14</th>
                  <th colspan="3">Δ SW14 vs SW13</th>
                  <th colspan="3">Δ SW14 vs SW12</th>
                  <th rowspan="2">UPCs SW14</th>
                  <th rowspan="2">Cats SW14</th>
                </tr>
                <tr class="thead-sub">
                  <th>Normal</th><th>Oferta</th><th>Mayoreo</th>
                  <th>Normal</th><th>Oferta</th><th>Mayoreo</th>
                  <th>Normal</th><th>Oferta</th><th>Mayoreo</th>
                  <th>Normal</th><th>Oferta</th><th>Mayoreo</th>
                  <th>Δ Nor</th><th>Δ Ofe</th><th>Δ May</th>
                  <th>Δ Nor</th><th>Δ Ofe</th><th>Δ May</th>
                </tr>
              </thead>
              <tbody>
                {d['detail_rows']}
              </tbody>
            </table>
            </div>
          </div>
        </div>
        <script>
          (function(){{
            var rData = {d['chart_records']};
            var oData = {d['chart_oferta']};
            var csvData_{pais} = {d['csv_data']};
            window._csvData = window._csvData || {{}};
            window._csvData['{pais}'] = csvData_{pais};
            if(document.readyState==='loading'){{
              document.addEventListener('DOMContentLoaded', function(){{
                initCharts_{pais}(rData, oData);
              }});
            }} else {{
              initCharts_{pais}(rData, oData);
            }}
          }})();
          function initCharts_{pais}(rData, oData){{
            new Chart(document.getElementById('chart-records-{pais}'), {{
              type:'line', data:rData,
              options:{{ responsive:true, maintainAspectRatio:false,
                plugins:{{ legend:{{ position:'bottom', labels:{{ boxWidth:10, font:{{size:10}} }} }},
                  tooltip:{{ mode:'index', intersect:false }} }},
                scales:{{ y:{{ beginAtZero:false }}, x:{{ grid:{{ color:'#e8e8e8' }} }} }}
              }}
            }});
            new Chart(document.getElementById('chart-oferta-{pais}'), {{
              type:'line', data:oData,
              options:{{ responsive:true, maintainAspectRatio:false,
                plugins:{{ legend:{{ position:'bottom', labels:{{ boxWidth:10, font:{{size:10}} }} }},
                  tooltip:{{ mode:'index', intersect:false }} }},
                scales:{{ y:{{ beginAtZero:false }}, x:{{ grid:{{ color:'#e8e8e8' }} }} }}
              }}
            }});
          }}
        </script>
        """

    return f"""
    <div class="tab-content-section">
      <div class="ctab-pills">{tabs_pills}</div>
      {country_blocks}
    </div>"""

# ── TAB3 FULL HTML ────────────────────────────────────────────────────────────
def render_tab3():
    tabs_pills = ""
    for i, pais in enumerate(COUNTRIES):
        active = "active" if i == 0 else ""
        tabs_pills += f'<button class="ctab-pill {active}" onclick="switchCtab3(\'{pais}\')">{pais}</button>\n'

    blocks = ""
    for i, pais in enumerate(COUNTRIES):
        d = country_tab3_sections[pais]
        display = "block" if i == 0 else "none"
        blocks += f"""
        <div id="ctab3-{pais}" class="ctab-content" style="display:{display}">
          <div class="chart-card" style="max-width:800px;margin:0 auto 20px;">
            <div class="chart-title">📈 Registros por División — {pais}</div>
            <div style="height:320px;position:relative;">
              <canvas id="chart-div-{pais}"></canvas>
            </div>
          </div>
          <div class="table-card">
            <div class="chart-title">📋 Caídas/Subidas por División — {pais}</div>
            <div class="table-scroll">
            <table class="data-table">
              <thead>
                <tr class="thead-group">
                  <th rowspan="2">División</th>
                  <th colspan="3">SW11</th>
                  <th colspan="3">SW12</th>
                  <th colspan="3">SW13</th>
                  <th colspan="3">SW14</th>
                  <th colspan="2">Δ SW14 vs SW13</th>
                  <th colspan="2">Δ SW14 vs SW12</th>
                </tr>
                <tr class="thead-sub">
                  <th>Regs</th><th>UPCs</th><th>Oferta</th>
                  <th>Regs</th><th>UPCs</th><th>Oferta</th>
                  <th>Regs</th><th>UPCs</th><th>Oferta</th>
                  <th>Regs</th><th>UPCs</th><th>Oferta</th>
                  <th>Δ Nor</th><th>Δ Ofe</th>
                  <th>Δ Nor</th><th>Δ Ofe</th>
                </tr>
              </thead>
              <tbody>
                {d['rows']}
              </tbody>
            </table>
            </div>
          </div>
        </div>
        <script>
          (function(){{
            var dData = {d['chart']};
            if(document.readyState==='loading'){{
              document.addEventListener('DOMContentLoaded', function(){{
                new Chart(document.getElementById('chart-div-{pais}'), {{
                  type:'bar', data:dData,
                  options:{{ responsive:true, maintainAspectRatio:false,
                    plugins:{{ legend:{{ position:'bottom' }}, tooltip:{{ mode:'index' }} }},
                    scales:{{ y:{{ beginAtZero:true, stacked:false }}, x:{{ stacked:false }} }}
                  }}
                }});
              }});
            }} else {{
              new Chart(document.getElementById('chart-div-{pais}'), {{
                type:'bar', data:dData,
                options:{{ responsive:true, maintainAspectRatio:false,
                  plugins:{{ legend:{{ position:'bottom' }}, tooltip:{{ mode:'index' }} }},
                  scales:{{ y:{{ beginAtZero:true }}, x:{{}} }}
                }}
              }});
            }}
          }})();
        </script>
        """
    return f"""
    <div class="tab-content-section">
      <div class="ctab-pills">{tabs_pills}</div>
      {blocks}
    </div>"""

# ── TAB5 FULL HTML ────────────────────────────────────────────────────────────
def render_tab5():
    tabs_pills = ""
    for i, pais in enumerate(COUNTRIES):
        active = "active" if i == 0 else ""
        tabs_pills += f'<button class="ctab-pill {active}" onclick="switchCtab5(\'{pais}\')">{pais}</button>\n'

    blocks = ""
    for i, pais in enumerate(COUNTRIES):
        display = "block" if i == 0 else "none"
        rows = country_tab5_sections[pais]
        blocks += f"""
        <div id="ctab5-{pais}" class="ctab-content" style="display:{display}">
          <div class="table-card">
            <div class="chart-title">🏷️ Actividad Promocional por Categoría — {pais} (Top 30)</div>
            <div class="table-scroll">
            <table class="data-table">
              <thead>
                <tr class="thead-group">
                  <th rowspan="2">Categoría</th>
                  <th rowspan="2">División</th>
                  <th colspan="2">SW11</th>
                  <th colspan="2">SW12</th>
                  <th colspan="2">SW13</th>
                  <th colspan="2">SW14</th>
                  <th rowspan="2">UPCs</th>
                  <th rowspan="2">Comps</th>
                  <th rowspan="2">Tendencia</th>
                </tr>
                <tr class="thead-sub">
                  <th>Regs</th><th>%Oferta</th>
                  <th>Regs</th><th>%Oferta</th>
                  <th>Regs</th><th>%Oferta</th>
                  <th>Regs</th><th>%Oferta</th>
                </tr>
              </thead>
              <tbody>
                {rows}
              </tbody>
            </table>
            </div>
          </div>
        </div>"""

    return f"""
    <div class="tab-content-section">
      <div class="ctab-pills">{tabs_pills}</div>
      {blocks}
    </div>"""

# ── ASSEMBLE FULL HTML ────────────────────────────────────────────────────────
t6_chart = json.dumps(t6d)

tab1_html = render_tab1()
tab3_html = render_tab3()
tab5_html = render_tab5()

html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>🐾 Análisis Competitivo CA — SW11-SW14 2026</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"></script>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:'Segoe UI',Arial,sans-serif;background:#f5f5f5;color:#1a1a1a;font-size:14px}}
  
  /* HEADER */
  .header{{background:#0053e2;color:white;padding:16px 24px;display:flex;align-items:center;gap:12px;position:sticky;top:0;z-index:1000;box-shadow:0 2px 8px rgba(0,83,226,.3)}}
  .header-logo{{font-size:28px}}
  .header-title{{font-size:22px;font-weight:700;letter-spacing:-.3px}}
  .header-subtitle{{font-size:12px;opacity:.85;margin-top:2px}}
  .header-spark{{margin-left:auto;background:#ffc220;color:#1a1a1a;font-weight:700;padding:6px 14px;border-radius:20px;font-size:12px}}

  /* FILTER BAR */
  .filter-bar{{background:white;border-bottom:2px solid #e0e0e0;padding:10px 24px;display:flex;gap:12px;align-items:center;flex-wrap:wrap;position:sticky;top:64px;z-index:999;box-shadow:0 1px 4px rgba(0,0,0,.08)}}
  .filter-bar label{{font-size:12px;font-weight:600;color:#555;white-space:nowrap}}
  .filter-bar select{{border:1px solid #ccc;border-radius:6px;padding:5px 10px;font-size:13px;background:white;cursor:pointer;min-width:140px}}
  .filter-bar select:focus{{outline:2px solid #0053e2;border-color:#0053e2}}
  .filter-reset{{background:#ea1100;color:white;border:none;padding:6px 14px;border-radius:6px;cursor:pointer;font-size:12px;font-weight:600}}
  .filter-reset:hover{{background:#c41000}}

  /* EXEC BOX */
  .exec-box{{background:linear-gradient(135deg,#002b7a 0%,#0053e2 60%,#1565c0 100%);color:white;margin:20px 24px;border-radius:12px;padding:24px;box-shadow:0 4px 16px rgba(0,83,226,.25)}}
  .exec-title{{font-size:17px;font-weight:700;margin-bottom:16px;display:flex;align-items:center;gap:8px}}
  .exec-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:16px}}
  .exec-kpi{{background:rgba(255,255,255,.12);border-radius:8px;padding:12px;text-align:center}}
  .kpi-val{{display:block;font-size:22px;font-weight:700;color:#ffc220}}
  .kpi-lbl{{font-size:11px;opacity:.85;margin-top:4px;display:block}}
  .exec-insights{{background:rgba(0,0,0,.2);border-radius:8px;padding:12px;font-size:13px}}
  .exec-insights ul{{margin-left:18px;margin-top:8px;line-height:1.7}}

  /* MAIN TABS */
  .main-tabs{{padding:0 24px;margin-top:20px}}
  .tab-pills{{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:0;background:white;padding:12px 16px;border-radius:10px 10px 0 0;box-shadow:0 -1px 4px rgba(0,0,0,.06)}}
  .tab-pill{{background:#e8eef9;color:#0053e2;border:none;padding:8px 18px;border-radius:20px;cursor:pointer;font-size:13px;font-weight:600;transition:all .2s}}
  .tab-pill:hover{{background:#b3c9f5}}
  .tab-pill.active{{background:#0053e2;color:white}}
  .tab-body{{background:white;border-radius:0 0 10px 10px;box-shadow:0 2px 8px rgba(0,0,0,.08);min-height:400px;padding:20px}}

  /* COUNTRY SUB-TABS */
  .ctab-pills{{display:flex;gap:6px;margin-bottom:16px;flex-wrap:wrap}}
  .ctab-pill{{background:#e8f5e9;color:#2a8703;border:none;padding:6px 16px;border-radius:16px;cursor:pointer;font-size:12px;font-weight:700;transition:all .2s;border:1px solid #c8e6c9}}
  .ctab-pill:hover{{background:#c8e6c9}}
  .ctab-pill.active{{background:#2a8703;color:white;border-color:#2a8703}}

  /* CHARTS */
  .chart-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:16px;margin-bottom:20px}}
  .chart-card{{background:#fafafa;border:1px solid #e8e8e8;border-radius:10px;padding:16px}}
  .chart-title{{font-size:14px;font-weight:700;color:#0053e2;margin-bottom:12px}}
  .section-desc{{background:#e8eef9;border-left:4px solid #0053e2;padding:8px 14px;border-radius:4px;font-size:13px;margin-bottom:14px}}

  /* TABLES */
  .table-card{{background:#fafafa;border:1px solid #e8e8e8;border-radius:10px;padding:16px;margin-top:4px}}
  .table-header-row{{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}}
  .table-scroll{{overflow-x:auto;border-radius:6px}}
  .data-table{{width:100%;border-collapse:collapse;font-size:12px;min-width:900px}}
  .data-table th{{background:#0053e2;color:white;padding:7px 10px;text-align:center;white-space:nowrap;position:sticky;top:0}}
  .data-table .thead-group th{{background:#002b7a;font-size:12px}}
  .data-table .thead-sub th{{background:#0053e2;font-size:11px;font-weight:500}}
  .data-table td{{padding:6px 10px;border-bottom:1px solid #ececec;text-align:center;white-space:nowrap}}
  .data-table tbody tr:nth-child(even){{background:#eef3ff}}
  .data-table tbody tr:hover{{background:#dce8ff}}
  .comp-cell{{text-align:left!important;font-weight:600;white-space:nowrap;max-width:180px;overflow:hidden;text-overflow:ellipsis}}
  .num{{font-variant-numeric:tabular-nums}}
  .promo{{color:#7b2d8b;font-weight:600}}
  .flag{{font-weight:700;color:#0053e2}}

  /* DELTAS */
  .pos{{color:#2a8703;font-weight:600}}
  .neg{{color:#ea1100;font-weight:600}}

  /* BADGES */
  .badge{{display:inline-block;padding:3px 9px;border-radius:12px;font-size:11px;font-weight:700}}
  .badge-green{{background:#e8f5e9;color:#2a8703;border:1px solid #a5d6a7}}
  .badge-red{{background:#ffebee;color:#ea1100;border:1px solid #ef9a9a}}
  .badge-yellow{{background:#fff8e1;color:#995213;border:1px solid #ffe082}}
  .badge-blue{{background:#e3f2fd;color:#0053e2;border:1px solid #90caf9}}

  /* BUTTONS */
  .btn-csv{{background:#0053e2;color:white;border:none;padding:7px 16px;border-radius:6px;cursor:pointer;font-size:12px;font-weight:600;display:flex;align-items:center;gap:6px}}
  .btn-csv:hover{{background:#0041b5}}

  /* INDEX CARDS */
  .idx-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;padding:4px}}
  .idx-card{{background:white;border:1px solid #e0e8ff;border-radius:10px;padding:16px;box-shadow:0 2px 8px rgba(0,83,226,.08)}}
  .idx-flag{{font-size:26px;font-weight:900;color:#0053e2;margin-bottom:10px;text-align:center;letter-spacing:2px;border-bottom:3px solid #ffc220;padding-bottom:6px}}
  .idx-row{{display:flex;justify-content:space-between;align-items:center;padding:5px 0;border-bottom:1px solid #f0f0f0;font-size:13px}}
  .idx-row:last-child{{border-bottom:none}}
  .idx-highlight{{background:#fff8e1;border-radius:6px;padding:6px 8px;margin-top:4px}}

  /* TAB CONTENT */
  .tab-content{{display:none}}
  .tab-content.active{{display:block}}
  .tab-content-section{{padding:4px 0}}

  /* FOOTER */
  .footer{{text-align:center;padding:20px;color:#888;font-size:12px;margin-top:30px}}

  /* RESPONSIVE */
  @media(max-width:768px){{
    .chart-grid{{grid-template-columns:1fr}}
    .filter-bar{{flex-direction:column;align-items:flex-start}}
  }}
</style>
</head>
<body>

<!-- HEADER -->
<div class="header">
  <div class="header-logo">🐾</div>
  <div>
    <div class="header-title">Análisis Competitivo — Centroamérica</div>
    <div class="header-subtitle">Auditoría de Precios · Semanas 11-14 · 2026 · Sin MG ni TEXTIL</div>
  </div>
  <div class="header-spark">WALMART PRICING INTEL</div>
</div>

<!-- FILTER BAR -->
<div class="filter-bar">
  <label>🌎 País:</label>
  <select id="fPais" onchange="applyFilters()">
    <option value="">Todos</option>
    <option>CR</option><option>GT</option><option>HN</option><option>NI</option><option>SV</option>
  </select>
  <label>🏢 División:</label>
  <select id="fDivision" onchange="applyFilters()">
    <option value="">Todas</option>
    <option>ABARROTES</option><option>CONSUMO</option><option>FARMACIA</option>
    <option>PERECEDEROS</option><option>ELECTRONICA</option>
  </select>
  <label>🏪 Competidor:</label>
  <select id="fComp" onchange="applyFilters()">
    <option value="">Todos</option>
  </select>
  <label>🏷️ Categoría:</label>
  <select id="fCat" onchange="applyFilters()">
    <option value="">Todas</option>
  </select>
  <button class="filter-reset" onclick="resetFilters()">↺ Limpiar</button>
  <span style="margin-left:auto;font-size:11px;color:#888">Generado: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')} | Datos: SW11→SW14 2026</span>
</div>

<!-- EXEC BOX -->
{exec_box}

<!-- MAIN TABS -->
<div class="main-tabs">
  <div class="tab-pills">
    <button class="tab-pill active" onclick="switchTab(0)">📈 Tendencia Semanal por País</button>
    <button class="tab-pill" onclick="switchTab(1)">🔄 Variación SW vs SW</button>
    <button class="tab-pill" onclick="switchTab(2)">📉 Caídas por País+División</button>
    <button class="tab-pill" onclick="switchTab(3)">🚀 Tendencias Crecientes vs Decrecientes</button>
    <button class="tab-pill" onclick="switchTab(4)">🏷️ Actividad Promocional</button>
    <button class="tab-pill" onclick="switchTab(5)">🧮 Índice de Variación Competitiva</button>
  </div>
  <div class="tab-body">

    <!-- TAB 1 -->
    <div class="tab-content active" id="tab-0">
      {tab1_html}
    </div>

    <!-- TAB 2 -->
    <div class="tab-content" id="tab-1">
      <div class="tab-content-section">
        <div class="chart-grid">
          <div class="chart-card">
            <div class="chart-title">📊 Registros SW14 por Competidor (Global)</div>
            <div style="height:320px;position:relative;">
              <canvas id="chart-tab2-bar"></canvas>
            </div>
          </div>
          <div class="chart-card">
            <div class="chart-title">📈 Evolución de Registros por Semana (Global)</div>
            <div style="height:320px;position:relative;">
              <canvas id="chart-tab2-trend"></canvas>
            </div>
          </div>
        </div>
        <div class="table-card">
          <div class="chart-title">🔄 Variación SW vs SW por Competidor — Vista Global</div>
          <div class="table-scroll">
          <table class="data-table">
            <thead>
              <tr class="thead-group">
                <th rowspan="2">Competidor</th>
                <th colspan="4">Registros por SW</th>
                <th colspan="2">Variación (%)</th>
                <th colspan="3">Δ Precios SW14 vs SW13</th>
                <th rowspan="2">Tendencia</th>
              </tr>
              <tr class="thead-sub">
                <th>SW11</th><th>SW12</th><th>SW13</th><th>SW14</th>
                <th>14 vs 13</th><th>14 vs 12</th>
                <th>Δ Normal</th><th>Δ Oferta</th><th>Δ Mayoreo</th>
              </tr>
            </thead>
            <tbody>
              {tab2_rows}
            </tbody>
          </table>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 3 -->
    <div class="tab-content" id="tab-2">
      {tab3_html}
    </div>

    <!-- TAB 4 -->
    <div class="tab-content" id="tab-3">
      <div class="tab-content-section">
        <div class="chart-grid">
          <div class="chart-card">
            <div class="chart-title">🚀 Competidores Crecientes vs Decrecientes — SW14 vs SW11</div>
            <div style="height:320px;position:relative;">
              <canvas id="chart-tab4-donut"></canvas>
            </div>
          </div>
          <div class="chart-card">
            <div class="chart-title">📊 Variación Porcentual SW14 vs SW11 por País</div>
            <div style="height:320px;position:relative;">
              <canvas id="chart-tab4-bar"></canvas>
            </div>
          </div>
        </div>
        <div class="table-card">
          <div class="chart-title">📋 Detalle de Tendencias por País y Competidor</div>
          <div class="table-scroll">
          <table class="data-table">
            <thead>
              <tr class="thead-sub">
                <th>País</th><th>Competidor</th>
                <th>SW11</th><th>SW12</th><th>SW13</th><th>SW14</th>
                <th>Var% 14v11</th><th>Var% 14v13</th>
                <th>Tendencia</th>
              </tr>
            </thead>
            <tbody>
              {tab4_rows}
            </tbody>
          </table>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 5 -->
    <div class="tab-content" id="tab-4">
      {tab5_html}
    </div>

    <!-- TAB 6 -->
    <div class="tab-content" id="tab-5">
      <div class="tab-content-section">
        <div class="chart-grid">
          <div class="chart-card">
            <div class="chart-title">📊 Registros por País — Evolución SW11→SW14</div>
            <div style="height:320px;position:relative;">
              <canvas id="chart-tab6-lines"></canvas>
            </div>
          </div>
          <div class="chart-card">
            <div class="chart-title">🏷️ Total Ofertas vs Total Mayoreo por País</div>
            <div style="height:320px;position:relative;">
              <canvas id="chart-tab6-promo"></canvas>
            </div>
          </div>
        </div>
        <div class="idx-grid">
          {tab6_cards}
        </div>
      </div>
    </div>

  </div><!-- end tab-body -->
</div><!-- end main-tabs -->

<div class="footer">
  🐾 Reporte generado por BigQuery Explorer Puppy · Walmart Central America · Datos: SW11-SW14 2026 · Divisiones excluidas: MG, TEXTIL
</div>

<script>
// ── TAB SWITCHING ────────────────────────────────────────────────────────────
function switchTab(idx) {{
  document.querySelectorAll('.tab-content').forEach((el,i) => {{
    el.classList.toggle('active', i===idx);
  }});
  document.querySelectorAll('.tab-pill').forEach((el,i) => {{
    el.classList.toggle('active', i===idx);
  }});
  if(idx===5 && !window._tab6Inited) {{ initTab6Charts(); window._tab6Inited=true; }}
  if(idx===1 && !window._tab2Inited) {{ initTab2Charts(); window._tab2Inited=true; }}
  if(idx===3 && !window._tab4Inited) {{ initTab4Charts(); window._tab4Inited=true; }}
}}

// ── COUNTRY SUB-TAB SWITCHING ────────────────────────────────────────────────
function switchCtab(pais) {{
  document.querySelectorAll('[id^="ctab-"]').forEach(el => {{
    if(!el.id.includes('3-') && !el.id.includes('5-')) el.style.display='none';
  }});
  document.querySelectorAll('.ctab-pill').forEach(el => el.classList.remove('active'));
  var el = document.getElementById('ctab-'+pais);
  if(el) el.style.display='block';
  event.target.classList.add('active');
}}
function switchCtab3(pais) {{
  ['CR','GT','HN','NI','SV'].forEach(p => {{
    var el=document.getElementById('ctab3-'+p);
    if(el) el.style.display='none';
  }});
  event.target.closest('.ctab-pills').querySelectorAll('.ctab-pill').forEach(b=>b.classList.remove('active'));
  var el=document.getElementById('ctab3-'+pais);
  if(el) el.style.display='block';
  event.target.classList.add('active');
}}
function switchCtab5(pais) {{
  ['CR','GT','HN','NI','SV'].forEach(p => {{
    var el=document.getElementById('ctab5-'+p);
    if(el) el.style.display='none';
  }});
  event.target.closest('.ctab-pills').querySelectorAll('.ctab-pill').forEach(b=>b.classList.remove('active'));
  var el=document.getElementById('ctab5-'+pais);
  if(el) el.style.display='block';
  event.target.classList.add('active');
}}

// ── CSV DOWNLOAD ─────────────────────────────────────────────────────────────
function downloadCSV(pais) {{
  var data = (window._csvData || {{}})[pais];
  if(!data || !data.length) {{ alert('No hay datos disponibles'); return; }}
  var csv = data.map(row => row.map(v => {{
    if(v===null||v===undefined) return '';
    var s=String(v);
    if(s.includes(',') || s.includes('"') || s.includes('\\n')) return '"'+s.replace(/"/g,'""')+'"';
    return s;
  }}).join(',')).join('\\n');
  var blob = new Blob([csv], {{type:'text/csv;charset=utf-8;'}});
  var url = URL.createObjectURL(blob);
  var a = document.createElement('a');
  a.href=url; a.download='detalle_'+pais+'_SW11-14.csv';
  document.body.appendChild(a); a.click(); document.body.removeChild(a);
  URL.revokeObjectURL(url);
}}

// ── FILTER LOGIC ─────────────────────────────────────────────────────────────
function applyFilters() {{
  var pais = document.getElementById('fPais').value;
  var div = document.getElementById('fDivision').value;
  // Filter visible table rows across all data tables
  document.querySelectorAll('.data-table tbody tr').forEach(row => {{
    var txt = row.innerText.toLowerCase();
    var show = true;
    // Basic text-based filter
    if(pais && !txt.includes(pais.toLowerCase())) show=false;
    if(div && !txt.includes(div.toLowerCase())) show=false;
    row.style.display = show ? '' : 'none';
  }});
}}
function resetFilters() {{
  ['fPais','fDivision','fComp','fCat'].forEach(id => {{
    document.getElementById(id).value='';
  }});
  document.querySelectorAll('.data-table tbody tr').forEach(row => row.style.display='');
}}

// ── TAB2 CHARTS ───────────────────────────────────────────────────────────────
function initTab2Charts() {{
  var t6d = {t6_chart};
  // Bar chart: SW14 by country
  new Chart(document.getElementById('chart-tab2-bar'), {{
    type:'bar',
    data:{{
      labels: t6d.countries,
      datasets:[
        {{label:'SW14',data:t6d.sw14,backgroundColor:'#0053e2'}},
        {{label:'SW13',data:t6d.sw13,backgroundColor:'#ffc220'}},
        {{label:'SW12',data:t6d.sw12,backgroundColor:'#2a8703'}},
        {{label:'SW11',data:t6d.sw11,backgroundColor:'#ea110044'}}
      ]
    }},
    options:{{responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{position:'bottom'}}}},
      scales:{{y:{{beginAtZero:true}}}}
    }}
  }});
  // Line trend
  new Chart(document.getElementById('chart-tab2-trend'), {{
    type:'line',
    data:{{
      labels:['SW11','SW12','SW13','SW14'],
      datasets: t6d.countries.map((c,i)=>{{
        var cols=['#0053e2','#ffc220','#ea1100','#2a8703','#7b2d8b'];
        return {{
          label:c,
          data:[t6d.sw11[i],t6d.sw12[i],t6d.sw13[i],t6d.sw14[i]],
          borderColor:cols[i],backgroundColor:cols[i]+'33',
          tension:0.3,fill:false,pointRadius:5
        }};
      }})
    }},
    options:{{responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{position:'bottom'}}}},
      scales:{{y:{{beginAtZero:false}}}}
    }}
  }});
}}

// ── TAB4 CHARTS ───────────────────────────────────────────────────────────────
function initTab4Charts() {{
  var rows = document.querySelectorAll('#tab-3 .data-table tbody tr');
  var growing=0, declining=0, stable=0;
  var countryRecs = {{}};
  rows.forEach(row => {{
    var cells = row.querySelectorAll('td');
    if(cells.length < 9) return;
    var pais = cells[0].innerText.trim();
    var badge = cells[8].innerText.trim();
    if(badge.includes('CRECIENTE')) growing++;
    else if(badge.includes('DECRECIENTE')) declining++;
    else stable++;
  }});
  new Chart(document.getElementById('chart-tab4-donut'), {{
    type:'doughnut',
    data:{{
      labels:['Creciente','Decreciente','Estable'],
      datasets:[{{
        data:[growing,declining,stable],
        backgroundColor:['#2a8703','#ea1100','#ffc220'],
        borderWidth:2,borderColor:'white'
      }}]
    }},
    options:{{responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{position:'bottom'}},
        tooltip:{{callbacks:{{label:function(c){{return c.label+': '+c.raw+' competidores'}}}}}}
      }}
    }}
  }});
  var t6d = {t6_chart};
  var varPct = t6d.countries.map((c,i)=>{{
    var diff = t6d.sw14[i]-t6d.sw11[i];
    return t6d.sw11[i]>0 ? +(diff/t6d.sw11[i]*100).toFixed(2) : 0;
  }});
  new Chart(document.getElementById('chart-tab4-bar'), {{
    type:'bar',
    data:{{
      labels:t6d.countries,
      datasets:[{{
        label:'Var% SW14 vs SW11',
        data:varPct,
        backgroundColor:varPct.map(v=>v>=0?'#2a8703':'#ea1100'),
        borderRadius:6
      }}]
    }},
    options:{{responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{display:false}}}},
      scales:{{y:{{beginAtZero:true, ticks:{{callback:v=>v+'%'}}}}}}
    }}
  }});
}}

// ── TAB6 CHARTS ───────────────────────────────────────────────────────────────
function initTab6Charts() {{
  var t6d = {t6_chart};
  var cols=['#0053e2','#ffc220','#ea1100','#2a8703','#7b2d8b'];
  // Multi-line by country
  new Chart(document.getElementById('chart-tab6-lines'), {{
    type:'line',
    data:{{
      labels:['SW11','SW12','SW13','SW14'],
      datasets: t6d.countries.map((c,i)=>{{
        return {{
          label:c,
          data:[t6d.sw11[i],t6d.sw12[i],t6d.sw13[i],t6d.sw14[i]],
          borderColor:cols[i],backgroundColor:cols[i]+'22',
          tension:0.3,fill:true,pointRadius:5,borderWidth:2.5
        }};
      }})
    }},
    options:{{responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{position:'bottom'}}}},
      scales:{{y:{{beginAtZero:false}}}}
    }}
  }});
  // Stacked bar for promo
  new Chart(document.getElementById('chart-tab6-promo'), {{
    type:'bar',
    data:{{
      labels:t6d.countries,
      datasets:[
        {{label:'Total Ofertas',data:t6d.ofertas,backgroundColor:'#ffc220',borderRadius:4}},
        {{label:'SW14 Registros',data:t6d.sw14,backgroundColor:'#0053e288',borderRadius:4}}
      ]
    }},
    options:{{responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{position:'bottom'}}}},
      scales:{{y:{{beginAtZero:true}}}}
    }}
  }});
}}
</script>
</body>
</html>"""

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

print(f"DONE: Report saved to: {OUT}")
print(f"   Size: {len(html)/1024:.0f} KB")

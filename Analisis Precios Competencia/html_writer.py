"""
html_writer.py  —  Genera el HTML de análisis competitivo SW12-SW15.
"""
import json, math
from data_loader import _pct_fmt, _fmt, _s, COUNTRY_NAMES

FLAG_EMOJI = {"CR": "🇨🇷", "GT": "🇬🇹", "HN": "🇭🇳", "NI": "🇳🇮", "SV": "🇸🇻"}

WEEKS = ["SW12", "SW13", "SW14", "SW15"]
WEEK_KEYS = ["sw12", "sw13", "sw14", "sw15"]

# ── Helpers de datos ──────────────────────────────────────────────────────────

def _total(row, wk):
    n = _s(row.get(f"{wk}_nor")) or 0
    o = _s(row.get(f"{wk}_ofe")) or 0
    m = _s(row.get(f"{wk}_may")) or 0
    return (n or 0) + (o or 0) + (m or 0)


def _country_chart_data(rows):
    """Series por semana para gráfica de línea de cada país."""
    competitors = [r["competidor"] for r in rows]
    series = {wk: [_total(r, wk) for r in rows] for wk in WEEK_KEYS}
    totals = {wk: sum(v for v in series[wk] if v) for wk in WEEK_KEYS}
    return competitors, series, totals


def _kpis(data):
    total_comps = sum(len(v) for v in data["countries"].values())
    upcs = sum(
        (r.get("upcs_sw15") or 0) for rows in data["countries"].values()
        for r in rows
    )
    sw15_regs = sum(
        (_s(r.get("sw15_nor")) or 0) + (_s(r.get("sw15_ofe")) or 0)
        + (_s(r.get("sw15_may")) or 0)
        for rows in data["countries"].values() for r in rows
    )
    sw15_ofe = sum(
        (_s(r.get("sw15_ofe")) or 0)
        for rows in data["countries"].values() for r in rows
    )
    # Variación promedio simple 15 vs 14
    deltas = []
    for rows in data["countries"].values():
        for r in rows:
            v = _s(r.get("d1514_nor_pct"))
            if v is not None:
                deltas.append(float(v))
    avg_delta = sum(deltas) / len(deltas) if deltas else 0
    return {
        "total_comps": total_comps,
        "paises": 5,
        "upcs": upcs,
        "sw15_regs": sw15_regs,
        "sw15_ofe": sw15_ofe,
        "avg_delta": avg_delta,
    }


# ── Bloques HTML ──────────────────────────────────────────────────────────────

def _build_table_rows(rows, code):
    html = ""
    for r in rows:
        sw12 = _total(r, "sw12"); sw13 = _total(r, "sw13")
        sw14 = _total(r, "sw14"); sw15 = _total(r, "sw15")

        def delta_cls(v):
            if v is None: return ""
            return "pos" if float(v) > 0 else ("neg" if float(v) < 0 else "")

        d1514n = r.get("d1514_nor"); d1514o = r.get("d1514_ofe"); d1514m = r.get("d1514_may")
        d1514np = r.get("d1514_nor_pct")
        d1513n = r.get("d1513_nor"); d1513np = r.get("d1513_nor_pct")

        html += f"""<tr>
          <td class="comp-cell">{r["competidor"]}</td>
          <td class="num">{_fmt(sw12)}</td><td class="num">{_fmt(sw13)}</td>
          <td class="num">{_fmt(sw14)}</td><td class="num">{_fmt(sw15)}</td>
          <td class="num {delta_cls(d1514n)}">{_fmt(d1514n, 0) if _s(d1514n) else "—"}</td>
          <td class="num {delta_cls(d1514o)}">{_fmt(d1514o, 0) if _s(d1514o) else "—"}</td>
          <td class="num {delta_cls(d1514m)}">{_fmt(d1514m, 0) if _s(d1514m) else "—"}</td>
          <td class="num {delta_cls(d1514np)}">{_pct_fmt(d1514np)}</td>
          <td class="num {delta_cls(d1513n)}">{_fmt(d1513n, 0) if _s(d1513n) else "—"}</td>
          <td class="num {delta_cls(d1513np)}">{_pct_fmt(d1513np)}</td>
          <td class="num">{_fmt(r.get("upcs_sw15"))}</td>
          <td class="num">{_fmt(r.get("cats_sw15"))}</td>
        </tr>"""
    return html


def _build_country_tab(code, rows):
    name = COUNTRY_NAMES[code]
    flag = FLAG_EMOJI[code]
    comps, series, totals = _country_chart_data(rows)
    chart_data = json.dumps({
        "labels": WEEKS,
        "totals": [totals[wk] for wk in WEEK_KEYS],
        "competitors": comps,
        "sw12": series["sw12"], "sw13": series["sw13"],
        "sw14": series["sw14"], "sw15": series["sw15"],
    })
    table_rows = _build_table_rows(rows, code)

    return f"""
<div id="ctab-{code}" class="country-tab">
  <div class="section-desc">
    {flag} <strong>{name}</strong> — {len(rows)} competidores monitoreados |
    Total UPCs SW15: {_fmt(sum((r.get("upcs_sw15") or 0) for r in rows))}
  </div>
  <div class="chart-grid">
    <div class="chart-card">
      <div class="chart-title">📈 Evolución Total de Registros — {name}</div>
      <div style="height:230px"><canvas id="chart-line-{code}"></canvas></div>
    </div>
    <div class="chart-card">
      <div class="chart-title">📊 SW15 por Competidor (Normal+Oferta+Mayoreo)</div>
      <div style="height:230px"><canvas id="chart-bar-{code}"></canvas></div>
    </div>
  </div>
  <script>
  (function(){{
    var d = {chart_data};
    // Line chart - evolución total por semana
    new Chart(document.getElementById("chart-line-{code}"),{{
      type:"line",
      data:{{
        labels:d.labels,
        datasets:[{{
          label:"Total Registros",
          data:d.totals,
          borderColor:"#0053e2",fill:true,
          backgroundColor:"rgba(0,83,226,0.1)",
          pointBackgroundColor:"#ffc220",pointRadius:5,tension:0.3
        }}]
      }},
      options:{{responsive:true,maintainAspectRatio:false,
        plugins:{{legend:{{display:false}}}},
        scales:{{y:{{beginAtZero:false}}}}
      }}
    }});
    // Bar chart - top competidores SW15
    var idxSort = d.sw15.map((_,i)=>i).sort((a,b)=>d.sw15[b]-d.sw15[a]).slice(0,10);
    new Chart(document.getElementById("chart-bar-{code}"),{{
      type:"bar",
      data:{{
        labels:idxSort.map(i=>d.competitors[i]),
        datasets:[{{
          label:"SW15",data:idxSort.map(i=>d.sw15[i]),
          backgroundColor:"#0053e2"
        }},{{
          label:"SW14",data:idxSort.map(i=>d.sw14[i]),
          backgroundColor:"rgba(0,83,226,0.35)"
        }}]
      }},
      options:{{responsive:true,maintainAspectRatio:false,
        plugins:{{legend:{{position:"top"}}}},
        scales:{{x:{{ticks:{{maxRotation:45}}}},y:{{beginAtZero:true}}}}
      }}
    }});
  }})();
  </script>
  <div class="table-card">
    <div class="table-header-row">
      <strong style="color:#0053e2">🗂️ Detalle por Competidor — {name}</strong>
    </div>
    <div class="table-scroll">
      <table class="data-table" id="tbl-{code}">
        <thead>
          <tr class="thead-group">
            <th rowspan="2">Competidor</th>
            <th colspan="4">Registros Totales por SW</th>
            <th colspan="3">Δ Abs 15/14</th>
            <th>Δ% 15/14</th>
            <th>Δ Nor 15/13</th>
            <th>Δ% 15/13</th>
            <th>UPCs</th><th>Cats</th>
          </tr>
          <tr class="thead-sub">
            <th>SW12</th><th>SW13</th><th>SW14</th><th>SW15</th>
            <th>Normal</th><th>Oferta</th><th>Mayoreo</th>
            <th>Normal%</th><th>Normal</th><th>Normal%</th>
            <th>SW15</th><th>SW15</th>
          </tr>
        </thead>
        <tbody>{table_rows}</tbody>
      </table>
    </div>
  </div>
</div>"""


def _build_tendencias_tab(tend_rows):
    crecientes = [r for r in tend_rows if r["clasificacion"] == "CRECIENTE"]
    decrecientes = [r for r in tend_rows if r["clasificacion"] == "DECRECIENTE"]

    def tend_row(r):
        badge = "badge-green" if r["clasificacion"] == "CRECIENTE" else "badge-red"
        icon = "🚀" if r["clasificacion"] == "CRECIENTE" else "📉"
        sos_badge = "badge-blue" if r["tendencia_sostenida"] == "Si" else "badge-yellow"
        d_cls = "pos" if (r["d_total"] or 0) > 0 else "neg"
        return (
            f"<tr>"
            f"<td>{icon} <span class='badge {badge}'>{r['clasificacion']}</span></td>"
            f"<td>{FLAG_EMOJI.get(r['pais'], r['pais'])} {r['pais']}</td>"
            f"<td class='comp-cell'>{r['competidor']}</td>"
            f"<td><span class='badge {sos_badge}'>{'✅ Sí' if r['tendencia_sostenida']=='Si' else '⚠️ No'}</span></td>"
            f"<td class='num'>{_fmt(r['sw12_total'])}</td>"
            f"<td class='num'>{_fmt(r['sw15_total'])}</td>"
            f"<td class='num {d_cls}'>{_fmt(r['d_total'])}</td>"
            f"<td class='num {d_cls}'>{_pct_fmt(r['d_pct_total'])}</td>"
            f"<td class='num'>{_fmt(r['upcs_sw15'])}</td>"
            f"</tr>"
        )

    rows_html = "".join(tend_row(r) for r in (crecientes + decrecientes))
    # Chart data for tendencias
    top_cr = sorted(crecientes, key=lambda r: (r["d_pct_total"] or 0), reverse=True)[:8]
    top_dc = sorted(decrecientes, key=lambda r: (r["d_pct_total"] or 0))[:8]

    cr_labels = json.dumps([f"{r['pais']}-{r['competidor'][:12]}" for r in top_cr])
    cr_vals   = json.dumps([round(float(r["d_pct_total"] or 0) * 100, 1) for r in top_cr])
    dc_labels = json.dumps([f"{r['pais']}-{r['competidor'][:12]}" for r in top_dc])
    dc_vals   = json.dumps([round(float(r["d_pct_total"] or 0) * 100, 1) for r in top_dc])

    return f"""
<div class="section-desc">
  🚀 <strong>{len(crecientes)} competidores crecientes</strong> |
  📉 <strong>{len(decrecientes)} competidores decrecientes</strong> —
  Comparativo SW12 vs SW15
</div>
<div class="chart-grid">
  <div class="chart-card">
    <div class="chart-title">🚀 Top Crecientes — Δ% Total SW12→SW15</div>
    <div style="height:240px"><canvas id="chart-crec"></canvas></div>
  </div>
  <div class="chart-card">
    <div class="chart-title">📉 Top Decrecientes — Δ% Total SW12→SW15</div>
    <div style="height:240px"><canvas id="chart-decr"></canvas></div>
  </div>
</div>
<script>
new Chart(document.getElementById("chart-crec"),{{
  type:"bar",
  data:{{labels:{cr_labels},datasets:[{{
    label:"Δ% SW12→SW15",data:{cr_vals},
    backgroundColor:"#2a8703"
  }}]}},
  options:{{
    indexAxis:"y",responsive:true,maintainAspectRatio:false,
    plugins:{{legend:{{display:false}}}},
    scales:{{x:{{ticks:{{callback:v=>v+"%"}}}}}}
  }}
}});
new Chart(document.getElementById("chart-decr"),{{
  type:"bar",
  data:{{labels:{dc_labels},datasets:[{{
    label:"Δ% SW12→SW15",data:{dc_vals},
    backgroundColor:"#ea1100"
  }}]}},
  options:{{
    indexAxis:"y",responsive:true,maintainAspectRatio:false,
    plugins:{{legend:{{display:false}}}},
    scales:{{x:{{ticks:{{callback:v=>v+"%"}}}}}}
  }}
}});
</script>
<div class="table-card">
  <div class="table-scroll">
    <table class="data-table">
      <thead>
        <tr class="thead-group">
          <th>Clasificación</th><th>País</th><th>Competidor</th>
          <th>Sostenida</th><th>SW12 Total</th><th>SW15 Total</th>
          <th>Δ Total</th><th>Δ% Total</th><th>UPCs SW15</th>
        </tr>
      </thead>
      <tbody>{rows_html}</tbody>
    </table>
  </div>
</div>"""


def _build_delta_tab(data):
    """Tab de variación SW15 vs SW14 y SW15 vs SW13 resumido por país."""
    html = ""
    for code, rows in data["countries"].items():
        name = COUNTRY_NAMES[code]; flag = FLAG_EMOJI[code]
        # Cálculo de totales de deltas por país
        tot_d1514 = sum((_s(r.get("d1514_nor")) or 0) for r in rows)
        tot_d1513 = sum((_s(r.get("d1513_nor")) or 0) for r in rows)
        pct_d1514 = [_s(r.get("d1514_nor_pct")) for r in rows]
        pct_d1513 = [_s(r.get("d1513_nor_pct")) for r in rows]
        avg_1514 = sum(float(v) for v in pct_d1514 if v) / max(len([v for v in pct_d1514 if v]), 1)
        avg_1513 = sum(float(v) for v in pct_d1513 if v) / max(len([v for v in pct_d1513 if v]), 1)
        col1514 = "pos" if tot_d1514 >= 0 else "neg"
        col1513 = "pos" if tot_d1513 >= 0 else "neg"

        comp_rows = ""
        for r in rows:
            d14 = _s(r.get("d1514_nor")); d14p = _s(r.get("d1514_nor_pct"))
            d13 = _s(r.get("d1513_nor")); d13p = _s(r.get("d1513_nor_pct"))
            cls14 = "pos" if d14 and float(d14) > 0 else ("neg" if d14 and float(d14) < 0 else "")
            cls13 = "pos" if d13 and float(d13) > 0 else ("neg" if d13 and float(d13) < 0 else "")
            comp_rows += (
                f"<tr>"
                f"<td class='comp-cell'>{r['competidor']}</td>"
                f"<td class='num'>{_fmt(r.get('sw14_nor'))}</td>"
                f"<td class='num'>{_fmt(r.get('sw15_nor'))}</td>"
                f"<td class='num {cls14}'>{_fmt(d14) if _s(d14) else '—'}</td>"
                f"<td class='num {cls14}'>{_pct_fmt(d14p)}</td>"
                f"<td class='num {cls13}'>{_fmt(d13) if _s(d13) else '—'}</td>"
                f"<td class='num {cls13}'>{_pct_fmt(d13p)}</td>"
                f"<td class='num'>{_fmt(r.get('sw15_ofe'))}</td>"
                f"<td class='num'>{_fmt(r.get('sw15_may'))}</td>"
                f"</tr>"
            )

        html += f"""
<details open style="margin-bottom:16px;background:white;border:1px solid #e0e0e0;border-radius:8px;overflow:hidden">
  <summary style="background:#0053e2;color:white;padding:10px 16px;cursor:pointer;font-weight:700;font-size:14px;list-style:none">
    {flag} {name} — Δ Nor SW15/14: <span class="{col1514}">{_fmt(tot_d1514)}</span> ({_pct_fmt(avg_1514)})
    &nbsp;|&nbsp; Δ Nor SW15/13: <span class="{col1513}">{_fmt(tot_d1513)}</span> ({_pct_fmt(avg_1513)})
  </summary>
  <div style="padding:12px;overflow-x:auto">
    <table class="data-table" style="min-width:700px">
      <thead>
        <tr class="thead-group">
          <th rowspan="2">Competidor</th>
          <th colspan="2">Normal (Registros)</th>
          <th colspan="2">Δ SW15 vs SW14</th>
          <th colspan="2">Δ SW15 vs SW13</th>
          <th>Oferta SW15</th><th>Mayoreo SW15</th>
        </tr>
        <tr class="thead-sub">
          <th>SW14</th><th>SW15</th>
          <th>Δ Abs</th><th>Δ%</th>
          <th>Δ Abs</th><th>Δ%</th>
          <th>Registros</th><th>Registros</th>
        </tr>
      </thead>
      <tbody>{comp_rows}</tbody>
    </table>
  </div>
</details>"""
    return html


def _build_promo_tab(data):
    """Actividad promocional por país en SW15."""
    html = """<div class="section-desc">
      🏷️ Actividad de Ofertas y Mayoreo en SW15 por competidor y país
    </div>"""
    # Chart: oferta vs mayoreo por país
    labels = []; ofe_vals = []; may_vals = []
    for code, rows in data["countries"].items():
        labels.append(f"{FLAG_EMOJI[code]} {code}")
        ofe_vals.append(sum((_s(r.get("sw15_ofe")) or 0) for r in rows))
        may_vals.append(sum((_s(r.get("sw15_may")) or 0) for r in rows))

    html += f"""
<div class="chart-grid">
  <div class="chart-card">
    <div class="chart-title">🏷️ Oferta + Mayoreo SW15 por País</div>
    <div style="height:240px"><canvas id="chart-promo-pais"></canvas></div>
  </div>
  <div class="chart-card">
    <div class="chart-title">📊 Proporción Oferta vs Mayoreo</div>
    <div style="height:240px"><canvas id="chart-promo-pie"></canvas></div>
  </div>
</div>
<script>
new Chart(document.getElementById("chart-promo-pais"),{{
  type:"bar",
  data:{{
    labels:{json.dumps(labels)},
    datasets:[
      {{label:"Oferta SW15",data:{json.dumps(ofe_vals)},backgroundColor:"#7b2d8b"}},
      {{label:"Mayoreo SW15",data:{json.dumps(may_vals)},backgroundColor:"#ffc220"}}
    ]
  }},
  options:{{responsive:true,maintainAspectRatio:false,
    plugins:{{legend:{{position:"top"}}}},
    scales:{{x:{{stacked:true}},y:{{stacked:true,beginAtZero:true}}}}
  }}
}});
new Chart(document.getElementById("chart-promo-pie"),{{
  type:"doughnut",
  data:{{
    labels:{json.dumps(labels)},
    datasets:[{{
      data:{json.dumps(ofe_vals)},
      backgroundColor:["#0053e2","#2a8703","#ffc220","#ea1100","#7b2d8b"]
    }}]
  }},
  options:{{responsive:true,maintainAspectRatio:false,
    plugins:{{legend:{{position:"right"}},title:{{display:true,text:"Distribución Oferta SW15"}}}}
  }}
}});
</script>"""
    return html


def write_html(data, out_path):
    kpis = _kpis(data)
    avg_d_str = _pct_fmt(kpis["avg_delta"])

    # ── Country tabs content ───────────────────────────────────────────────────
    country_tabs_btns = ""
    country_tabs_content = ""
    for i, (code, rows) in enumerate(data["countries"].items()):
        active = "active" if i == 0 else ""
        flag = FLAG_EMOJI[code]
        country_tabs_btns += (
            f'<button class="ctab-pill {active}" '
            f'onclick="switchCtab(\'{code}\')">{flag} {code}</button>'
        )
        country_tabs_content += f'<div id="ctab-{code}" class="country-tab {active}">'
        country_tabs_content += _build_country_tab(code, rows).replace(
            f'id="ctab-{code}"', ""
        )
        country_tabs_content += "</div>"

    delta_content = _build_delta_tab(data)
    tend_content  = _build_tendencias_tab(data["tendencias"])
    promo_content = _build_promo_tab(data)

    # ── Insights ejecutivos dinámicos ─────────────────────────────────────────
    top_grow = sorted(
        data["tendencias"],
        key=lambda r: (r["d_pct_total"] or 0), reverse=True
    )[:3]
    top_decl = sorted(
        data["tendencias"],
        key=lambda r: (r["d_pct_total"] or 0)
    )[:3]

    insights_html = "<ul>"
    for r in top_grow:
        insights_html += (
            f"<li>{FLAG_EMOJI.get(r['pais'],r['pais'])} <strong>{r['competidor']}</strong> "
            f"({r['pais']}) lidera crecimiento con {_pct_fmt(r['d_pct_total'])} "
            f"entre SW12→SW15.</li>"
        )
    for r in top_decl:
        insights_html += (
            f"<li>{FLAG_EMOJI.get(r['pais'],r['pais'])} <strong>{r['competidor']}</strong> "
            f"({r['pais']}) reporta caída de {_pct_fmt(r['d_pct_total'])} "
            f"entre SW12→SW15.</li>"
        )
    insights_html += (
        f"<li>La variación promedio normal SW15 vs SW14 en la región es "
        f"<strong>{avg_d_str}</strong> — comparativo más reciente.</li>"
    )
    insights_html += "</ul>"

    resumen_cards = ""
    for r in data["resumen"]:
        code = r["pais"].split("(")[1].rstrip(")") if "(" in r["pais"] else r["pais"]
        flag = FLAG_EMOJI.get(code, "🌎")
        td = r["tendencia_general"]
        td_cls = "pos" if "+" in str(td) else "neg"
        resumen_cards += f"""
        <div class="idx-card">
          <div class="idx-flag">{flag} {code}</div>
          <div class="idx-row"><span>Competidores</span><strong>{r['competidores']}</strong></div>
          <div class="idx-row"><span>Normal SW15</span><strong>{_fmt(r['total_normal_sw15'])}</strong></div>
          <div class="idx-row"><span>Ofertas SW15</span><strong>{_fmt(r['total_ofertas_sw15'])}</strong></div>
          <div class="idx-row"><span>Mayoreo SW15</span><strong>{_fmt(r['total_mayoreo_sw15'])}</strong></div>
          <div class="idx-row"><span>UPCs Prom</span><strong>{_fmt(r['upcs_prom_sw15'])}</strong></div>
          <div class="idx-highlight">
            Tendencia: <span class="{td_cls}" style="font-weight:700">{td}</span>
          </div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>🐾 Análisis Competitivo CA — SW12-SW15 2026</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"></script>
{_css()}
</head>
<body>
<div class="header">
  <div class="header-logo">🐾</div>
  <div>
    <div class="header-title">Análisis Competitivo — Centroamérica</div>
    <div class="header-subtitle">Auditoría de Precios · Semanas 12-15 · 2026 · Sin MG ni TEXTIL</div>
  </div>
  <div class="header-spark">WALMART PRICING INTEL</div>
</div>

<div class="filter-bar">
  <span style="font-size:11px;color:#888;margin-left:auto">
    Generado: 2026-05-15 | Datos: SW12→SW15 2026 | Δ comparativos: SW15/14 y SW15/13
  </span>
</div>

<div class="exec-box">
  <div class="exec-title">🏆 RESUMEN EJECUTIVO — Auditoría Competitiva CA · SW12→SW15 · 2026</div>
  <div class="exec-grid">
    <div class="exec-kpi"><span class="kpi-val">{kpis['total_comps']}</span><span class="kpi-lbl">Competidores Monitoreados</span></div>
    <div class="exec-kpi"><span class="kpi-val">{kpis['paises']}</span><span class="kpi-lbl">Países Analizados</span></div>
    <div class="exec-kpi"><span class="kpi-val">{_fmt(kpis['upcs'])}</span><span class="kpi-lbl">UPCs Totales SW15</span></div>
    <div class="exec-kpi"><span class="kpi-val">{_fmt(kpis['sw15_regs'])}</span><span class="kpi-lbl">Registros SW15</span></div>
    <div class="exec-kpi"><span class="kpi-val">{avg_d_str}</span><span class="kpi-lbl">Variación Prom. SW15/14</span></div>
    <div class="exec-kpi"><span class="kpi-val">{_fmt(kpis['sw15_ofe'])}</span><span class="kpi-lbl">Registros c/Oferta SW15</span></div>
  </div>
  <div class="exec-insights">
    <strong>🔍 Hallazgos Clave SW12→SW15:</strong>
    {insights_html}
  </div>
</div>

<div class="idx-grid" style="padding:0 24px 16px">
  {resumen_cards}
</div>

<div class="main-tabs">
  <div class="tab-pills">
    <button class="tab-pill active" onclick="switchTab(0)">🌎 Detalle por País</button>
    <button class="tab-pill" onclick="switchTab(1)">🔄 Δ SW15/14 y SW15/13</button>
    <button class="tab-pill" onclick="switchTab(2)">🚀 Tendencias Crecientes / Decrecientes</button>
    <button class="tab-pill" onclick="switchTab(3)">🏷️ Actividad Promocional SW15</button>
  </div>

  <div class="tab-body">

    <!-- TAB 0: Países -->
    <div class="tab-content active" id="tab-0">
      <div class="ctab-pills">
        {country_tabs_btns}
      </div>
      {country_tabs_content}
    </div>

    <!-- TAB 1: Deltas -->
    <div class="tab-content" id="tab-1">
      <div class="section-desc">
        🔄 Comparativos: <strong>SW15 vs SW14</strong> (variación semanal) y
        <strong>SW15 vs SW13</strong> (tendencia de 2 semanas) — Solo precios Normal
      </div>
      {delta_content}
    </div>

    <!-- TAB 2: Tendencias -->
    <div class="tab-content" id="tab-2">
      {tend_content}
    </div>

    <!-- TAB 3: Promo -->
    <div class="tab-content" id="tab-3">
      {promo_content}
    </div>

  </div>
</div>

<div class="footer">
  🐾 Rintyn · Análisis Competitivo CA · SW12–SW15 · 2026 · Walmart Pricing Intelligence
</div>

<script>
function switchTab(idx){{
  document.querySelectorAll(".tab-content").forEach((el,i)=>{{
    el.classList.toggle("active", i===idx);
  }});
  document.querySelectorAll(".tab-pill").forEach((el,i)=>{{
    el.classList.toggle("active", i===idx);
  }});
}}
function switchCtab(code){{
  document.querySelectorAll(".country-tab").forEach(el=>el.classList.remove("active"));
  document.querySelectorAll(".ctab-pill").forEach(el=>el.classList.remove("active"));
  var el = document.getElementById("ctab-"+code);
  if(el) el.classList.add("active");
  event.currentTarget.classList.add("active");
}}
</script>
</body>
</html>"""

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[OK] HTML guardado: {out_path}", flush=True)


def _css():
    return """<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',Arial,sans-serif;background:#f5f5f5;color:#1a1a1a;font-size:14px}
.header{background:#0053e2;color:white;padding:16px 24px;display:flex;align-items:center;gap:12px;position:sticky;top:0;z-index:1000;box-shadow:0 2px 8px rgba(0,83,226,.3)}
.header-logo{font-size:28px}.header-title{font-size:22px;font-weight:700;letter-spacing:-.3px}
.header-subtitle{font-size:12px;opacity:.85;margin-top:2px}
.header-spark{margin-left:auto;background:#ffc220;color:#1a1a1a;font-weight:700;padding:6px 14px;border-radius:20px;font-size:12px}
.filter-bar{background:white;border-bottom:2px solid #e0e0e0;padding:10px 24px;display:flex;gap:12px;align-items:center;flex-wrap:wrap}
.exec-box{background:linear-gradient(135deg,#002b7a 0%,#0053e2 60%,#1565c0 100%);color:white;margin:20px 24px;border-radius:12px;padding:24px;box-shadow:0 4px 16px rgba(0,83,226,.25)}
.exec-title{font-size:17px;font-weight:700;margin-bottom:16px;display:flex;align-items:center;gap:8px}
.exec-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:16px}
.exec-kpi{background:rgba(255,255,255,.12);border-radius:8px;padding:12px;text-align:center}
.kpi-val{display:block;font-size:22px;font-weight:700;color:#ffc220}
.kpi-lbl{font-size:11px;opacity:.85;margin-top:4px;display:block}
.exec-insights{background:rgba(0,0,0,.2);border-radius:8px;padding:12px;font-size:13px}
.exec-insights ul{margin-left:18px;margin-top:8px;line-height:1.8}
.idx-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;padding:4px}
.idx-card{background:white;border:1px solid #e0e8ff;border-radius:10px;padding:16px;box-shadow:0 2px 8px rgba(0,83,226,.08)}
.idx-flag{font-size:22px;font-weight:900;color:#0053e2;margin-bottom:10px;text-align:center;border-bottom:3px solid #ffc220;padding-bottom:6px}
.idx-row{display:flex;justify-content:space-between;align-items:center;padding:4px 0;border-bottom:1px solid #f0f0f0;font-size:12px}
.idx-row:last-child{border-bottom:none}
.idx-highlight{background:#fff8e1;border-radius:6px;padding:6px 8px;margin-top:6px;font-size:12px}
.main-tabs{padding:0 24px 30px}
.tab-pills{display:flex;gap:6px;flex-wrap:wrap;background:white;padding:12px 16px;border-radius:10px 10px 0 0;box-shadow:0 -1px 4px rgba(0,0,0,.06)}
.tab-pill{background:#e8eef9;color:#0053e2;border:none;padding:8px 18px;border-radius:20px;cursor:pointer;font-size:13px;font-weight:600;transition:all .2s}
.tab-pill:hover{background:#b3c9f5}.tab-pill.active{background:#0053e2;color:white}
.tab-body{background:white;border-radius:0 0 10px 10px;box-shadow:0 2px 8px rgba(0,0,0,.08);min-height:400px;padding:20px}
.tab-content{display:none}.tab-content.active{display:block}
.ctab-pills{display:flex;gap:6px;margin-bottom:16px;flex-wrap:wrap}
.ctab-pill{background:#e8f5e9;color:#2a8703;border:1px solid #c8e6c9;padding:6px 16px;border-radius:16px;cursor:pointer;font-size:12px;font-weight:700;transition:all .2s}
.ctab-pill:hover{background:#c8e6c9}.ctab-pill.active{background:#2a8703;color:white;border-color:#2a8703}
.country-tab{display:none}.country-tab.active{display:block}
.chart-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:16px;margin-bottom:20px}
.chart-card{background:#fafafa;border:1px solid #e8e8e8;border-radius:10px;padding:16px}
.chart-title{font-size:14px;font-weight:700;color:#0053e2;margin-bottom:12px}
.section-desc{background:#e8eef9;border-left:4px solid #0053e2;padding:8px 14px;border-radius:4px;font-size:13px;margin-bottom:14px}
.table-card{background:#fafafa;border:1px solid #e8e8e8;border-radius:10px;padding:16px;margin-top:4px}
.table-header-row{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}
.table-scroll{overflow-x:auto;border-radius:6px}
.data-table{width:100%;border-collapse:collapse;font-size:12px;min-width:800px}
.data-table th{background:#0053e2;color:white;padding:7px 10px;text-align:center;white-space:nowrap}
.data-table .thead-group th{background:#002b7a;font-size:12px}
.data-table .thead-sub th{background:#0053e2;font-size:10px;font-weight:500}
.data-table td{padding:6px 10px;border-bottom:1px solid #ececec;text-align:center;white-space:nowrap}
.data-table tbody tr:nth-child(even){background:#eef3ff}
.data-table tbody tr:hover{background:#dce8ff}
.comp-cell{text-align:left!important;font-weight:600;white-space:nowrap;max-width:180px;overflow:hidden;text-overflow:ellipsis}
.num{font-variant-numeric:tabular-nums}
.pos{color:#2a8703;font-weight:600}.neg{color:#ea1100;font-weight:600}
.badge{display:inline-block;padding:3px 9px;border-radius:12px;font-size:11px;font-weight:700}
.badge-green{background:#e8f5e9;color:#2a8703;border:1px solid #a5d6a7}
.badge-red{background:#ffebee;color:#ea1100;border:1px solid #ef9a9a}
.badge-blue{background:#e3f2fd;color:#0053e2;border:1px solid #90caf9}
.badge-yellow{background:#fff8e1;color:#995213;border:1px solid #ffe082}
.footer{text-align:center;padding:20px;color:#888;font-size:12px;margin-top:10px}
details>summary{{list-style:none}}
details>summary::-webkit-details-marker{{display:none}}
</style>"""

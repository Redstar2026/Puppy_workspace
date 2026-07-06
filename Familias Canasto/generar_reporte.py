"""
Generador de reporte - Consistencia de Precios por Familias.
Walmart CAM - Pricing Analytics | Datos: 2026-07-04
Sin dependencias externas: Chart.js embebido, CSS propio.
"""

import pandas as pd
import json
import os
import re
import webbrowser
from datetime import datetime

BASE   = os.path.dirname(os.path.abspath(__file__))
BQ_DIR = os.path.join(BASE, "bigquery_results")

# ---------------------------------------------------------------------------
# Carga de datos
# ---------------------------------------------------------------------------

def load_data():
    director  = pd.read_csv(os.path.join(BQ_DIR, "director_summary.csv"))
    problemas = pd.read_csv(os.path.join(BQ_DIR, "familias_con_problemas.csv"))
    conversion = pd.read_csv(os.path.join(BQ_DIR, "conversion_factor_items.csv"))
    return director, problemas, conversion


# ---------------------------------------------------------------------------
# KPIs globales
# ---------------------------------------------------------------------------

def compute_kpis(director: pd.DataFrame) -> dict:
    skus_mismo  = director["SKUS_MISMO_TAMANO"].sum()
    alineados   = director["SKUS_ALINEADOS"].sum()
    no_alineados = director["SKUS_NO_ALINEADOS"].sum()
    return {
        "total_skus":            int(director["TOTAL_SKUS"].sum()),
        "total_fam":             int(director["TOTAL_FAMILIAS"].sum()),
        "skus_mismo_tamano":     int(skus_mismo),
        "skus_tamano_diferente": int(director["SKUS_TAMANO_DIFERENTE"].sum()),
        "alineados":             int(alineados),
        "no_alineados":          int(no_alineados),
        "pct_global":            round(alineados / skus_mismo * 100, 2) if skus_mismo else 0.0,
        "familias_con_problemas": 25404,
    }


# ---------------------------------------------------------------------------
# Observaciones automaticas
# ---------------------------------------------------------------------------

def build_observations(director, problemas, conversion, kpis) -> list:
    obs = []
    pais_names = {"CR": "Costa Rica", "GT": "Guatemala",
                  "HN": "Honduras",   "SV": "El Salvador", "NI": "Nicaragua"}
    for _, row in director.iterrows():
        pct = float(row["PCT_ALINEACION_PAIS"])
        pais = pais_names.get(row["PAIS"], row["PAIS"])
        sev  = "INFO" if pct >= 93 else ("ALERTA" if pct >= 91 else "CRITICO")
        obs.append({"tipo": "Alineacion por Pais", "severidad": sev,
                    "mensaje": f"{pais}: {pct:.2f}% alineacion ({int(row['SKUS_NO_ALINEADOS']):,} SKUs desalineados)"})

    summary_csv = os.path.join(BQ_DIR, "familias_summary.csv")
    if os.path.exists(summary_csv):
        s = pd.read_csv(summary_csv)
        sin_prim = int((s["TIENE_SKU_PRIMARIO"] == 0).sum()) if "TIENE_SKU_PRIMARIO" in s.columns else 0
        obs.append({"tipo": "Familias sin SKU Primario", "severidad": "ALERTA",
                    "mensaje": f"Familias donde el item primario no tiene precio en Insumos (muestra 10k): {sin_prim}"})

    if "SKUS_SIN_PRECIO" in problemas.columns:
        n = int(problemas["SKUS_SIN_PRECIO"].sum())
        obs.append({"tipo": "SKUs sin precio", "severidad": "ALERTA" if n > 0 else "OK",
                    "mensaje": f"SKUs sin PRECIO_GPI_C_IMP en top 5k familias: {n:,}"})

    if "SKUS_SIN_VENTAS" in problemas.columns:
        n = int(problemas["SKUS_SIN_VENTAS"].sum())
        obs.append({"tipo": "SKUs sin ventas", "severidad": "INFO",
                    "mensaje": f"SKUs con ventas nulas en top 5k familias: {n:,} (pueden ser items nuevos o descontinuados)"})

    if "PRECIOS_DISTINTOS" in problemas.columns:
        top5 = problemas.nlargest(5, "PRECIOS_DISTINTOS")[["PAIS", "MARCA", "PRECIOS_DISTINTOS"]]
        filas = " | ".join(f"{r.PAIS}-{r.MARCA} ({int(r.PRECIOS_DISTINTOS)} precios)" for _, r in top5.iterrows())
        obs.append({"tipo": "Familias con mas precios distintos", "severidad": "CRITICO",
                    "mensaje": f"Top 5: {filas}"})

    if "EVALUACION_PRECIO" in conversion.columns:
        revisar = int((conversion["EVALUACION_PRECIO"] == "REVISAR").sum())
        if revisar > 0:
            obs.append({"tipo": "Items tamano diferente a revisar", "severidad": "ALERTA",
                        "mensaje": f"{revisar:,} items con factor de conversion tienen precio MENOR al primario"})

    obs.append({"tipo": "Alineacion Global", "severidad": "OK",
                "mensaje": f"Alineacion global (mismo tamano, 5 paises): {kpis['pct_global']:.2f}% "
                           f"({kpis['alineados']:,} de {kpis['skus_mismo_tamano']:,} SKUs)"})
    return obs


# ---------------------------------------------------------------------------
# JSON helper  (escapa </script> para evitar romper el tag en HTML)
# ---------------------------------------------------------------------------

def safe_json(obj) -> str:
    raw = json.dumps(obj, ensure_ascii=False)
    return raw.replace("</", "<\\/")


def df_to_records(df: pd.DataFrame, cols: list, max_rows: int = 2000) -> str:
    available = [c for c in cols if c in df.columns]
    sub = df[available].head(max_rows).copy()
    for c in sub.select_dtypes(include="float").columns:
        sub[c] = sub[c].round(4)
    sub = sub.where(pd.notna(sub), other=None)
    return safe_json(sub.to_dict(orient="records"))


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------

def director_rows(director: pd.DataFrame) -> str:
    flag = {"CR": "CR", "GT": "GT", "HN": "HN", "SV": "SV", "NI": "NI"}
    names = {"CR": "Costa Rica", "GT": "Guatemala", "HN": "Honduras",
             "SV": "El Salvador", "NI": "Nicaragua"}
    rows = []
    for _, r in director.iterrows():
        pct = float(r["PCT_ALINEACION_PAIS"])
        bar_color = "#2a8703" if pct >= 93 else ("#e6a817" if pct >= 91 else "#ea1100")
        bar = (f'<div class="bar-wrap"><div class="bar-fill" '
               f'style="width:{pct:.1f}%;background:{bar_color}"></div>'
               f'<span class="bar-label">{pct:.2f}%</span></div>')
        rows.append(
            f"<tr>"
            f"<td><b>{names.get(r['PAIS'], r['PAIS'])}</b></td>"
            f"<td class='tr'>{int(r['TOTAL_FAMILIAS']):,}</td>"
            f"<td class='tr'>{int(r['TOTAL_SKUS']):,}</td>"
            f"<td class='tr'>{int(r['SKUS_MISMO_TAMANO']):,}</td>"
            f"<td class='tr green'>{int(r['SKUS_ALINEADOS']):,}</td>"
            f"<td class='tr red'>{int(r['SKUS_NO_ALINEADOS']):,}</td>"
            f"<td>{bar}</td>"
            f"</tr>"
        )
    return "\n".join(rows)


def obs_cards(observations: list) -> str:
    sev_cls = {"CRITICO": "obs-crit", "ALERTA": "obs-warn", "INFO": "obs-info", "OK": "obs-ok"}
    cards = []
    for o in observations:
        cls = sev_cls.get(o["severidad"], "obs-info")
        cards.append(
            f'<div class="obs-card {cls}">'
            f'<div class="obs-hdr"><span class="obs-tipo">{o["tipo"]}</span>'
            f'<span class="obs-sev">{o["severidad"]}</span></div>'
            f'<p class="obs-msg">{o["mensaje"]}</p></div>'
        )
    return "\n".join(cards)


# ---------------------------------------------------------------------------
# Genera HTML completo
# ---------------------------------------------------------------------------

def generate_html(kpis, director, problemas, conversion, observations) -> str:

    # --- datos embebidos ---
    prob_cols = ["PAIS", "Formato", "ZONA", "CODIGO_FAMILIA", "MARCA", "CATEGORIA",
                 "DESC_PRIMARIO", "PRECIO_PRIMARIO", "TOTAL_SKUS",
                 "SKUS_MISMO_TAMANO", "ALINEADOS", "NO_ALINEADOS",
                 "PCT_ALINEACION", "VENTAS_FAMILIA", "PRECIOS_DISTINTOS"]
    conv_cols = ["PAIS", "Formato", "ZONA", "CODIGO_FAMILIA", "DESC_PRIMARIO",
                 "PRECIO_PRIMARIO", "TAMANO_PRIMARIO", "MEDIDA_PRIMARIO",
                 "ITEM", "AGRUPACION", "SIGNING_DESC", "PRECIO_GPI_C_IMP",
                 "TAMANO_TOTAL", "MEDIDA", "FACTOR_DE_CONVERSION", "AHORRO_DIFERENCIAL",
                 "RATIO_PRECIO_VS_PRIMARIO", "PRECIO_NORMALIZADO", "PRECIO_ESPERADO",
                 "EVALUACION_PRECIO", "Ventas", "Rotaciones"]

    prob_json = df_to_records(problemas, prob_cols, 2000)
    conv_json = df_to_records(conversion, conv_cols, 2000)
    dir_json  = df_to_records(director,  list(director.columns), 10)

    # --- chart data ---
    c_labels = safe_json(director["PAIS"].tolist())
    c_pcts   = safe_json(director["PCT_ALINEACION_PAIS"].round(2).tolist())
    c_ali    = safe_json(director["SKUS_ALINEADOS"].tolist())
    c_nali   = safe_json(director["SKUS_NO_ALINEADOS"].tolist())

    # --- misc ---
    dir_rows_html = director_rows(director)
    obs_html      = obs_cards(observations)
    now           = datetime.now().strftime("%d/%m/%Y %H:%M")
    g             = kpis["pct_global"]
    gauge_color   = "#2a8703" if g >= 93 else ("#e6a817" if g >= 91 else "#ea1100")

    # --- Chart.js inline ---
    chartjs_path = os.path.join(BASE, "chartjs.min.js")
    if os.path.exists(chartjs_path):
        with open(chartjs_path, "r", encoding="utf-8", errors="replace") as f:
            chartjs_src = f.read()
        chartjs_tag = f"<script>{chartjs_src}</script>"
    else:
        chartjs_tag = '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>'

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Consistencia de Precios por Familias - CAM Pricing</title>
{chartjs_tag}
<style>
/* ---- reset / base ---- */
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',system-ui,sans-serif;background:#f1f5f9;color:#1e293b;font-size:14px}}
/* ---- layout ---- */
.page{{max-width:1400px;margin:0 auto;padding:24px 20px}}
.grid-2{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}
.grid-kpi{{display:grid;grid-template-columns:repeat(auto-fit,minmax(175px,1fr));gap:14px;margin-bottom:24px}}
@media(max-width:900px){{.grid-2{{grid-template-columns:1fr}}}}
/* ---- card ---- */
.card{{background:#fff;border-radius:12px;padding:20px 22px;
       box-shadow:0 1px 6px rgba(0,0,50,.09);border:1px solid #e2e8f0}}
/* ---- KPI card ---- */
.kpi-val{{font-size:1.9rem;font-weight:700;line-height:1.1}}
.kpi-lbl{{font-size:.72rem;color:#64748b;margin-top:5px;text-transform:uppercase;letter-spacing:.05em}}
.kpi-sub{{font-size:.68rem;color:#94a3b8;margin-top:3px}}
/* ---- header ---- */
.hdr{{background:#0053e2;padding:16px 28px;display:flex;align-items:center;gap:14px}}
.hdr-spark{{width:42px;height:42px;background:#ffc220;border-radius:50%;
            display:flex;align-items:center;justify-content:center;
            font-size:20px;font-weight:700;color:#0053e2;flex-shrink:0}}
.hdr h1{{color:#fff;font-size:1.15rem;font-weight:700}}
.hdr p{{color:#93c5fd;font-size:.76rem;margin-top:2px}}
/* ---- section title ---- */
.sec-title{{font-size:.9rem;font-weight:700;color:#0053e2;margin-bottom:14px}}
/* ---- bar ---- */
.bar-wrap{{position:relative;background:#f1f5f9;border-radius:6px;height:22px;min-width:140px}}
.bar-fill{{position:absolute;left:0;top:0;height:100%;border-radius:6px;opacity:.85}}
.bar-label{{position:absolute;right:7px;top:3px;font-size:.71rem;font-weight:700}}
/* ---- table ---- */
.tbl-wrap{{overflow-x:auto;max-height:480px;overflow-y:auto;border-radius:8px;border:1px solid #e2e8f0}}
table{{border-collapse:collapse;width:100%;min-width:600px}}
thead th{{background:#0053e2;color:#fff;padding:9px 12px;font-size:.74rem;
           text-align:left;position:sticky;top:0;z-index:2;white-space:nowrap}}
tbody td{{padding:7px 12px;font-size:.74rem;border-bottom:1px solid #f1f5f9;white-space:nowrap}}
tbody tr:hover td{{background:#eff6ff}}
.tr{{text-align:right}} .green{{color:#166534;font-weight:600}} .red{{color:#991b1b;font-weight:600}}
/* ---- badges ---- */
.badge{{display:inline-block;padding:2px 8px;border-radius:20px;font-size:.68rem;font-weight:700}}
.b-green{{background:#dcfce7;color:#166534}} .b-yellow{{background:#fef9c3;color:#854d0e}}
.b-red{{background:#fee2e2;color:#991b1b}} .b-gray{{background:#f1f5f9;color:#64748b}}
.b-blue{{background:#dbeafe;color:#1e40af}}
.eval-ok{{background:#dcfce7;color:#166534;padding:2px 7px;border-radius:12px;font-size:.68rem;font-weight:700}}
.eval-warn{{background:#fef9c3;color:#854d0e;padding:2px 7px;border-radius:12px;font-size:.68rem;font-weight:700}}
.eval-bad{{background:#fee2e2;color:#991b1b;padding:2px 7px;border-radius:12px;font-size:.68rem;font-weight:700}}
.agrup-prim{{background:#dbeafe;color:#1e40af;padding:2px 8px;border-radius:12px;font-size:.68rem;font-weight:700}}
.agrup-sec{{background:#f1f5f9;color:#475569;padding:2px 8px;border-radius:12px;font-size:.68rem;font-weight:600}}
/* ---- tabs ---- */
.tabs{{display:flex;gap:3px;flex-wrap:wrap;margin-bottom:0}}
.tab-btn{{padding:9px 20px;border-radius:8px 8px 0 0;font-weight:600;font-size:.8rem;
          cursor:pointer;border:1px solid #e2e8f0;border-bottom:none;background:#e8edf5;
          color:#475569;transition:background .15s}}
.tab-btn.active{{background:#0053e2;color:#fff;border-color:#0053e2}}
.tab-panel{{display:none;background:#fff;border-radius:0 12px 12px 12px;
            padding:22px;border:1px solid #e2e8f0}}
.tab-panel.active{{display:block}}
/* ---- controls ---- */
.ctrl-bar{{display:flex;gap:10px;align-items:center;margin-bottom:14px;flex-wrap:wrap}}
.sbox{{padding:7px 13px;border:1px solid #cbd5e1;border-radius:7px;font-size:.8rem;
       width:240px;outline:none}}
.sbox:focus{{border-color:#0053e2;box-shadow:0 0 0 2px #0053e225}}
.sel{{padding:7px 10px;border:1px solid #cbd5e1;border-radius:7px;font-size:.8rem;
      background:#fff;outline:none;cursor:pointer}}
.btn-dl{{padding:6px 14px;border-radius:7px;border:1px solid #0053e2;background:#fff;
         color:#0053e2;font-size:.78rem;font-weight:700;cursor:pointer}}
.btn-dl:hover{{background:#eff6ff}}
.rec-count{{font-size:.75rem;color:#64748b}}
/* ---- paginator ---- */
.paginator{{display:flex;gap:5px;align-items:center;margin-top:12px;flex-wrap:wrap}}
.paginator button{{padding:4px 11px;border-radius:5px;border:1px solid #cbd5e1;
                  background:#fff;font-size:.75rem;cursor:pointer}}
.paginator button.active{{background:#0053e2;color:#fff;border-color:#0053e2}}
.pg-info{{font-size:.74rem;color:#64748b;margin-left:auto}}
/* ---- observations ---- */
.obs-card{{border-radius:9px;padding:13px 17px;margin-bottom:11px;border-left:4px solid}}
.obs-crit{{background:#fff1f2;border-color:#ea1100}}
.obs-warn{{background:#fffbeb;border-color:#f59e0b}}
.obs-info{{background:#eff6ff;border-color:#0053e2}}
.obs-ok{{background:#f0fdf4;border-color:#2a8703}}
.obs-hdr{{display:flex;justify-content:space-between;align-items:center;margin-bottom:5px}}
.obs-tipo{{font-weight:700;font-size:.8rem}}
.obs-sev{{font-size:.68rem;padding:2px 8px;border-radius:20px;font-weight:700;background:rgba(0,0,0,.08)}}
.obs-msg{{font-size:.78rem;color:#334155;line-height:1.6}}
/* ---- nota metodologica ---- */
.nota{{margin-top:22px;padding:15px 18px;background:#f8fafc;border-radius:9px;
       border:1px solid #e2e8f0;font-size:.74rem;color:#64748b}}
.nota ul{{padding-left:16px;line-height:1.9;margin-top:6px}}
/* ---- info banner ---- */
.info-banner{{font-size:.78rem;color:#1e40af;background:#eff6ff;padding:10px 14px;
              border-radius:8px;border-left:4px solid #0053e2;margin-bottom:13px;line-height:1.6}}
</style>
</head>
<body>

<!-- HEADER -->
<div class="hdr">
  <div class="hdr-spark">W</div>
  <div>
    <h1>Analisis de Consistencia de Precios por Familias</h1>
    <p>CAM Pricing Analytics &nbsp;|&nbsp; Datos: 2026-07-04 &nbsp;|&nbsp; Generado: {now}</p>
  </div>
</div>

<div class="page">

<!-- KPI CARDS -->
<div class="grid-kpi" style="margin-top:22px">
  <div class="card">
    <div class="kpi-val" style="color:{gauge_color}">{kpis['pct_global']:.2f}%</div>
    <div class="kpi-lbl">Alineacion Global</div>
    <div class="kpi-sub">SKUs mismo tamano - 5 paises</div>
  </div>
  <div class="card">
    <div class="kpi-val" style="color:#0053e2">{kpis['total_fam']:,}</div>
    <div class="kpi-lbl">Total Familias</div>
    <div class="kpi-sub">Pais x Formato x Zona x Familia</div>
  </div>
  <div class="card">
    <div class="kpi-val" style="color:#1e293b">{kpis['total_skus']:,}</div>
    <div class="kpi-lbl">Total SKUs</div>
    <div class="kpi-sub">Todos los paises</div>
  </div>
  <div class="card">
    <div class="kpi-val" style="color:#2a8703">{kpis['alineados']:,}</div>
    <div class="kpi-lbl">SKUs Alineados</div>
    <div class="kpi-sub">Precio = Primario, mismo tamano</div>
  </div>
  <div class="card">
    <div class="kpi-val" style="color:#ea1100">{kpis['no_alineados']:,}</div>
    <div class="kpi-lbl">SKUs No Alineados</div>
    <div class="kpi-sub">Oportunidad de homologacion</div>
  </div>
  <div class="card">
    <div class="kpi-val" style="color:#995213">{kpis['familias_con_problemas']:,}</div>
    <div class="kpi-lbl">Familias con Problemas</div>
    <div class="kpi-sub">Al menos 1 SKU desalineado</div>
  </div>
  <div class="card">
    <div class="kpi-val" style="color:#7c3aed">{kpis['skus_tamano_diferente']:,}</div>
    <div class="kpi-lbl">SKUs Tamano Diferente</div>
    <div class="kpi-sub">Factor/Ahorro != 1 (packs, gramajes)</div>
  </div>
</div>

<!-- CHART + DIRECTOR -->
<div class="grid-2" style="margin-bottom:22px">
  <div class="card">
    <div class="sec-title">Alineacion de Precios por Pais (SKUs mismo tamano)</div>
    <div style="position:relative;height:270px">
      <canvas id="chartPais"></canvas>
    </div>
  </div>
  <div class="card">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
      <span class="sec-title" style="margin:0">Resumen Ejecutivo por Pais - Vista para Directores</span>
      <button class="btn-dl" onclick="downloadCSV('dir')">Descargar CSV</button>
    </div>
    <div class="tbl-wrap">
    <table id="tableDir">
      <thead><tr>
        <th>Pais</th><th>Familias</th><th>Total SKUs</th>
        <th>Mismo Tam.</th><th>Alineados</th><th>No Alineados</th>
        <th style="min-width:160px">% Alineacion</th>
      </tr></thead>
      <tbody>{dir_rows_html}</tbody>
    </table>
    </div>
  </div>
</div>

<!-- TABS -->
<div class="tabs">
  <button class="tab-btn active" onclick="switchTab('tab-prob',this)">Familias con Problemas (top 2,000 de 25,404)</button>
  <button class="tab-btn" onclick="switchTab('tab-conv',this)">Items Tamano Diferente (top 2,000 de 10,575)</button>
  <button class="tab-btn" onclick="switchTab('tab-obs',this)">Observaciones Automaticas</button>
</div>

<!-- TAB: Familias con Problemas -->
<div id="tab-prob" class="tab-panel active">
  <div class="ctrl-bar">
    <input class="sbox" id="srchProb" placeholder="Buscar marca, familia, descripcion..." oninput="applyFilter('prob')"/>
    <select class="sel" id="paisProb" onchange="applyFilter('prob')">
      <option value="">Todos los paises</option>
      <option>CR</option><option>GT</option><option>HN</option><option>SV</option><option>NI</option>
    </select>
    <button class="btn-dl" onclick="downloadCSV('prob')">Descargar CSV</button>
    <span class="rec-count" id="cntProb"></span>
  </div>
  <div class="tbl-wrap">
    <table id="tblProb">
      <thead><tr>
        <th>Pais</th><th>Formato</th><th>Zona</th><th>Cod. Familia</th>
        <th>Marca</th><th>Categoria</th><th>Descripcion Primario</th>
        <th>Precio Primario</th><th>Total SKUs</th><th>Mismo Tam.</th>
        <th>Alineados</th><th>No Alineados</th><th>% Alineacion</th>
        <th>Precios Dist.</th><th>Ventas Familia</th>
      </tr></thead>
      <tbody id="bodyProb"></tbody>
    </table>
  </div>
  <div class="paginator" id="pgProb"></div>
</div>

<!-- TAB: Items Tamano Diferente -->
<div id="tab-conv" class="tab-panel">
  <div class="info-banner">
    <b>Vista especial - Items de tamano diferente:</b> Estos SKUs tienen
    <code>FACTOR_DE_CONVERSION != 1</code> o <code>AHORRO_DIFERENCIAL != 1</code>,
    indicando una presentacion de mayor tamano (pack, doble, etc.).
    Para estos items es <b>correcto y esperado</b> que el precio sea mayor al primario.
    Se marca como REVISAR cuando el precio es menor al primario.
  </div>
  <div class="ctrl-bar">
    <input class="sbox" id="srchConv" placeholder="Buscar item, marca, descripcion..." oninput="applyFilter('conv')"/>
    <select class="sel" id="paisConv" onchange="applyFilter('conv')">
      <option value="">Todos los paises</option>
      <option>CR</option><option>GT</option><option>HN</option><option>SV</option><option>NI</option>
    </select>
    <select class="sel" id="evalConv" onchange="applyFilter('conv')">
      <option value="">Todas las evaluaciones</option>
      <option>MAYOR (esperado para packs)</option>
      <option>PRECIO CORRECTO (normalizado)</option>
      <option>REVISAR</option>
    </select>
    <button class="btn-dl" onclick="downloadCSV('conv')">Descargar CSV</button>
    <span class="rec-count" id="cntConv"></span>
  </div>
  <div class="tbl-wrap">
    <table id="tblConv">
      <thead><tr>
        <th>Pais</th><th>Formato</th><th>Zona</th><th>Cod. Familia</th>
        <th>Descripcion Primario</th><th>Precio Primario</th>
        <th>Tam. Primario</th><th>Medida</th>
        <th>Item</th><th>Agrupacion</th><th>Descripcion Item</th>
        <th>Precio Item</th><th>Tam. Total</th>
        <th>Factor Conv.</th><th>Ahorro Dif.</th>
        <th>Ratio P/Primario</th><th>Precio Norm.</th><th>Precio Esperado</th>
        <th>Evaluacion</th><th>Ventas</th>
      </tr></thead>
      <tbody id="bodyConv"></tbody>
    </table>
  </div>
  <div class="paginator" id="pgConv"></div>
</div>

<!-- TAB: Observaciones -->
<div id="tab-obs" class="tab-panel">
  <div class="sec-title">Observaciones automaticas detectadas durante el analisis</div>
  {obs_html}
</div>

<!-- NOTA METODOLOGICA -->
<div class="nota">
  <b>Notas metodologicas:</b>
  <ul>
    <li><b>SKU Primario:</b> El item donde <code>ITEM = ITEM_PRIMARIO</code> (campo <code>AGRUPACION = PRIMARIO</code>).</li>
    <li><b>Mismo tamano:</b> <code>FACTOR_DE_CONVERSION = 1</code> AND <code>AHORRO_DIFERENCIAL = 1</code>.</li>
    <li><b>Alineado:</b> <code>PRECIO_GPI_C_IMP</code> del SKU secundario igual al precio del primario, mismo Pais-Formato-Zona.</li>
    <li><b>% Alineacion =</b> SKUs alineados (mismo tamano) / Total SKUs mismo tamano x 100.</li>
    <li><b>Items tamano diferente:</b> Precio mayor al primario es correcto. Se normaliza por <code>FACTOR_DE_CONVERSION</code>.</li>
    <li>Fuente: <code>prcng_info_cam_insumos_diario</code> + <code>prcng_info_cam_a0g0dn3_canasto_universal_extendido</code> | Fecha: 2026-07-04</li>
  </ul>
</div>

</div><!-- /page -->

<script>
// ============================================================
// DATOS EMBEBIDOS
// ============================================================
const probData = {prob_json};
const convData = {conv_json};
const dirData  = {dir_json};

// ============================================================
// CHART (Chart.js ya embebido en <head>)
// ============================================================
(function() {{
  var canvas = document.getElementById('chartPais');
  if (!canvas) return;
  var ctx = canvas.getContext('2d');
  new Chart(ctx, {{
    type: 'bar',
    data: {{
      labels: {c_labels},
      datasets: [
        {{
          label: 'Alineados',
          data: {c_ali},
          backgroundColor: '#2a8703',
          borderRadius: 4
        }},
        {{
          label: 'No Alineados',
          data: {c_nali},
          backgroundColor: '#ea1100',
          borderRadius: 4
        }}
      ]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{
        legend: {{ position: 'top' }},
        tooltip: {{
          callbacks: {{
            afterBody: function(items) {{
              var pcts = {c_pcts};
              return 'Alineacion: ' + pcts[items[0].dataIndex] + '%';
            }}
          }}
        }}
      }},
      scales: {{
        x: {{ stacked: true }},
        y: {{ stacked: true, ticks: {{ callback: function(v) {{ return v.toLocaleString('es'); }} }} }}
      }}
    }}
  }});
}})();

// ============================================================
// ESTADO TABLAS
// ============================================================
var PAGE = 50;
var tblState = {{
  prob: {{ data: probData, filtered: probData.slice(), page: 0 }},
  conv: {{ data: convData, filtered: convData.slice(), page: 0 }}
}};

// ============================================================
// HELPERS
// ============================================================
function esc(v) {{
  if (v === null || v === undefined || v === '') return '\u2014';
  return String(v)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}}

function fmtNum(v, dec) {{
  if (v === null || v === undefined || v === '') return '\u2014';
  var n = parseFloat(v);
  if (isNaN(n)) return esc(v);
  return n.toLocaleString('es', {{minimumFractionDigits: dec||0, maximumFractionDigits: dec||0}});
}}

function pctBadge(v) {{
  if (v === null || v === undefined || v === '') return '<span class="badge b-gray">N/D</span>';
  var n = parseFloat(v);
  var cls = n >= 95 ? 'b-green' : n >= 85 ? 'b-yellow' : 'b-red';
  return '<span class="badge ' + cls + '">' + n.toFixed(1) + '%</span>';
}}

function evalBadge(v) {{
  if (!v) return '<span class="badge b-gray">\u2014</span>';
  var s = String(v);
  if (s.indexOf('CORRECTO') >= 0) return '<span class="eval-ok">' + esc(s) + '</span>';
  if (s.indexOf('MAYOR')    >= 0) return '<span class="eval-warn">' + esc(s) + '</span>';
  return '<span class="eval-bad">' + esc(s) + '</span>';
}}

function agrupBadge(v) {{
  if (!v) return '<span class="badge b-gray">\u2014</span>';
  var s = String(v).toUpperCase();
  if (s === 'PRIMARIO')   return '<span class="agrup-prim">PRIMARIO</span>';
  return '<span class="agrup-sec">SECUNDARIO</span>';
}}

// ============================================================
// RENDER ROWS
// ============================================================
function renderProbRow(r) {{
  return '<tr>'
    + '<td><b>' + esc(r.PAIS) + '</b></td>'
    + '<td>' + esc(r.Formato) + '</td>'
    + '<td>' + esc(r.ZONA) + '</td>'
    + '<td style="font-family:monospace">' + esc(r.CODIGO_FAMILIA) + '</td>'
    + '<td><b>' + esc(r.MARCA) + '</b></td>'
    + '<td style="font-size:.7rem">' + esc(r.CATEGORIA) + '</td>'
    + '<td style="max-width:200px;overflow:hidden;text-overflow:ellipsis" title="' + esc(r.DESC_PRIMARIO) + '">' + esc(r.DESC_PRIMARIO) + '</td>'
    + '<td class="tr">' + fmtNum(r.PRECIO_PRIMARIO, 2) + '</td>'
    + '<td class="tr">' + fmtNum(r.TOTAL_SKUS) + '</td>'
    + '<td class="tr">' + fmtNum(r.SKUS_MISMO_TAMANO) + '</td>'
    + '<td class="tr green">' + fmtNum(r.ALINEADOS) + '</td>'
    + '<td class="tr red">' + fmtNum(r.NO_ALINEADOS) + '</td>'
    + '<td>' + pctBadge(r.PCT_ALINEACION) + '</td>'
    + '<td class="tr">' + fmtNum(r.PRECIOS_DISTINTOS) + '</td>'
    + '<td class="tr">' + fmtNum(r.VENTAS_FAMILIA, 0) + '</td>'
    + '</tr>';
}}

function renderConvRow(r) {{
  return '<tr>'
    + '<td><b>' + esc(r.PAIS) + '</b></td>'
    + '<td>' + esc(r.Formato) + '</td>'
    + '<td>' + esc(r.ZONA) + '</td>'
    + '<td style="font-family:monospace">' + esc(r.CODIGO_FAMILIA) + '</td>'
    + '<td style="max-width:150px;overflow:hidden;text-overflow:ellipsis" title="' + esc(r.DESC_PRIMARIO) + '">' + esc(r.DESC_PRIMARIO) + '</td>'
    + '<td class="tr">' + fmtNum(r.PRECIO_PRIMARIO, 2) + '</td>'
    + '<td class="tr">' + fmtNum(r.TAMANO_PRIMARIO, 0) + '</td>'
    + '<td>' + esc(r.MEDIDA_PRIMARIO) + '</td>'
    + '<td style="font-family:monospace">' + esc(r.ITEM) + '</td>'
    + '<td>' + agrupBadge(r.AGRUPACION) + '</td>'
    + '<td style="max-width:180px;overflow:hidden;text-overflow:ellipsis" title="' + esc(r.SIGNING_DESC) + '">' + esc(r.SIGNING_DESC) + '</td>'
    + '<td class="tr" style="color:#0053e2;font-weight:700">' + fmtNum(r.PRECIO_GPI_C_IMP, 2) + '</td>'
    + '<td class="tr">' + fmtNum(r.TAMANO_TOTAL, 0) + '</td>'
    + '<td class="tr" style="color:#7c3aed;font-weight:700">' + fmtNum(r.FACTOR_DE_CONVERSION, 2) + '</td>'
    + '<td class="tr">' + fmtNum(r.AHORRO_DIFERENCIAL, 2) + '</td>'
    + '<td class="tr">' + fmtNum(r.RATIO_PRECIO_VS_PRIMARIO, 3) + '</td>'
    + '<td class="tr">' + fmtNum(r.PRECIO_NORMALIZADO, 2) + '</td>'
    + '<td class="tr">' + fmtNum(r.PRECIO_ESPERADO, 2) + '</td>'
    + '<td>' + evalBadge(r.EVALUACION_PRECIO) + '</td>'
    + '<td class="tr">' + fmtNum(r.Ventas, 0) + '</td>'
    + '</tr>';
}}

// ============================================================
// TABLA ENGINE
// ============================================================
function renderTable(key) {{
  var s   = tblState[key];
  var id  = key === 'prob' ? 'Prob' : 'Conv';
  var fn  = key === 'prob' ? renderProbRow : renderConvRow;
  var start = s.page * PAGE;
  var slice = s.filtered.slice(start, start + PAGE);
  document.getElementById('body' + id).innerHTML = slice.map(fn).join('');
  buildPager(key);
  var cnt = document.getElementById('cnt' + id);
  if (cnt) cnt.textContent = 'Mostrando ' + (start+1) + '\u2013'
    + Math.min(start + PAGE, s.filtered.length) + ' de '
    + s.filtered.length.toLocaleString('es') + ' registros';
}}

function buildPager(key) {{
  var s     = tblState[key];
  var id    = key === 'prob' ? 'Prob' : 'Conv';
  var pages = Math.ceil(s.filtered.length / PAGE);
  var cur   = s.page;
  var el    = document.getElementById('pg' + id);
  if (!el) return;
  var html = '';
  var shown = [];
  [0, cur-1, cur, cur+1, pages-1].forEach(function(p) {{
    if (p >= 0 && p < pages && shown.indexOf(p) < 0) shown.push(p);
  }});
  shown.sort(function(a,b){{return a-b;}});
  var last = -1;
  shown.forEach(function(p) {{
    if (last >= 0 && p - last > 1) html += '<span style="color:#94a3b8">&hellip;</span>';
    html += '<button class="' + (cur===p?'active':'') + '" onclick="goPage(\'' + key + '\',' + p + ')">' + (p+1) + '</button>';
    last = p;
  }});
  html += '<span class="pg-info">Pagina ' + (cur+1) + ' / ' + pages + '</span>';
  el.innerHTML = html;
}}

function goPage(key, page) {{
  tblState[key].page = page;
  renderTable(key);
}}

// ============================================================
// FILTROS
// ============================================================
function applyFilter(key) {{
  var isProb = key === 'prob';
  var term  = (document.getElementById(isProb ? 'srchProb' : 'srchConv').value || '').toLowerCase();
  var pais  = document.getElementById(isProb ? 'paisProb' : 'paisConv').value || '';
  var evalF = isProb ? '' : (document.getElementById('evalConv').value || '');
  var src   = tblState[key].data;
  tblState[key].filtered = src.filter(function(r) {{
    var str = JSON.stringify(r).toLowerCase();
    return (!term || str.indexOf(term) >= 0)
        && (!pais  || r.PAIS === pais)
        && (!evalF || r.EVALUACION_PRECIO === evalF);
  }});
  tblState[key].page = 0;
  renderTable(key);
}}

// ============================================================
// DESCARGA CSV
// ============================================================
function downloadCSV(which) {{
  var rows, name;
  if (which === 'dir')  {{ rows = dirData;                                          name = 'director_alineacion_pais.csv'; }}
  else if (which === 'prob') {{ rows = tblState.prob.filtered;                     name = 'familias_con_problemas.csv'; }}
  else                       {{ rows = tblState.conv.filtered;                     name = 'items_tamano_diferente.csv'; }}
  if (!rows || !rows.length) return;
  var keys = Object.keys(rows[0]);
  function esc2(v) {{
    var s = (v === null || v === undefined) ? '' : String(v);
    if (s.indexOf(',') >= 0 || s.indexOf('"') >= 0 || s.indexOf('\\n') >= 0)
      return '"' + s.replace(/"/g, '""') + '"';
    return s;
  }}
  var csv = [keys.join(',')]
    .concat(rows.map(function(r) {{ return keys.map(function(k) {{ return esc2(r[k]); }}).join(','); }}))
    .join('\\n');
  var blob = new Blob(['\ufeff' + csv], {{type:'text/csv;charset=utf-8;'}});
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = name;
  a.click();
}}

// ============================================================
// TABS
// ============================================================
function switchTab(id, btn) {{
  document.querySelectorAll('.tab-panel').forEach(function(p) {{ p.classList.remove('active'); }});
  document.querySelectorAll('.tab-btn').forEach(function(b)   {{ b.classList.remove('active'); }});
  document.getElementById(id).classList.add('active');
  btn.classList.add('active');
}}

// ============================================================
// INIT
// ============================================================
renderTable('prob');
renderTable('conv');
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Cargando datos...")
    director, problemas, conversion = load_data()
    print(f"  Director : {len(director)} paises")
    print(f"  Problemas: {len(problemas):,} familias")
    print(f"  Conversion: {len(conversion):,} items")

    kpis = compute_kpis(director)
    print(f"\nKPIs:")
    print(f"  Alineacion global : {kpis['pct_global']:.2f}%")
    print(f"  Total SKUs        : {kpis['total_skus']:,}")
    print(f"  Alineados         : {kpis['alineados']:,}")
    print(f"  No alineados      : {kpis['no_alineados']:,}")

    observations = build_observations(director, problemas, conversion, kpis)
    print(f"\n  Observaciones: {len(observations)}")

    html = generate_html(kpis, director, problemas, conversion, observations)

    out = os.path.join(BASE, "reporte_familias_precios.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(out) / 1024
    print(f"\nReporte generado: {out}")
    print(f"  Tamano: {size_kb:.0f} KB")
    print("  Abriendo en el navegador...")
    webbrowser.open(f"file:///{out.replace(os.sep, '/')}")


if __name__ == "__main__":
    main()

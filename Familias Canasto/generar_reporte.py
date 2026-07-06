"""
Generador de reporte de Consistencia de Precios por Familias.
Walmart CAM – Pricing Analytics
Fecha de análisis: 2026-07-04
"""

import pandas as pd
import json
import os
import webbrowser
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
BQ_DIR = os.path.join(BASE, "bigquery_results")

# ─── Carga de datos ──────────────────────────────────────────────────────────

def load_data():
    director = pd.read_csv(os.path.join(BQ_DIR, "director_summary.csv"))
    problemas = pd.read_csv(os.path.join(BQ_DIR, "familias_con_problemas.csv"))
    conversion = pd.read_csv(os.path.join(BQ_DIR, "conversion_factor_items.csv"))
    return director, problemas, conversion


# ─── Métricas globales ────────────────────────────────────────────────────────

def compute_kpis(director: pd.DataFrame) -> dict:
    total_skus = director["TOTAL_SKUS"].sum()
    total_fam = director["TOTAL_FAMILIAS"].sum()
    skus_mismo = director["SKUS_MISMO_TAMANO"].sum()
    skus_diff = director["SKUS_TAMANO_DIFERENTE"].sum()
    alineados = director["SKUS_ALINEADOS"].sum()
    no_alineados = director["SKUS_NO_ALINEADOS"].sum()
    pct_global = round(alineados / skus_mismo * 100, 2) if skus_mismo > 0 else 0.0
    return {
        "total_skus": int(total_skus),
        "total_fam": int(total_fam),
        "skus_mismo_tamano": int(skus_mismo),
        "skus_tamano_diferente": int(skus_diff),
        "alineados": int(alineados),
        "no_alineados": int(no_alineados),
        "pct_global": pct_global,
        "familias_con_problemas": 25404,   # total real de BQ sin LIMIT
    }


# ─── Observaciones automáticas ────────────────────────────────────────────────

def build_observations(director: pd.DataFrame, problemas: pd.DataFrame,
                        conversion: pd.DataFrame, kpis: dict) -> list:
    obs = []
    # Por país
    for _, row in director.iterrows():
        pct = row["PCT_ALINEACION_PAIS"]
        pais = row["PAIS"]
        nivel = "" if pct >= 93 else ("" if pct >= 91 else "")
        obs.append({
            "tipo": "Alineación País",
            "severidad": "INFO" if pct >= 93 else ("ALERTA" if pct >= 91 else "CRÍTICO"),
            "mensaje": f"{nivel} {pais}: {pct}% alineación en SKUs mismo tamaño "
                       f"({int(row['SKUS_NO_ALINEADOS']):,} SKUs desalineados)",
        })

    # Familias sin primario: estimado del summary
    # (los primeros 10k del summary_csv incluyen muchos sin primario)
    sum_csv = pd.read_csv(os.path.join(BQ_DIR, "familias_summary.csv"))
    sin_primario = int((sum_csv["TIENE_SKU_PRIMARIO"] == 0).sum()) if "TIENE_SKU_PRIMARIO" in sum_csv.columns else "N/D"
    obs.append({
        "tipo": "Familias sin SKU Primario",
        "severidad": "ALERTA",
        "mensaje": f" Se detectaron familias donde el ítem primario no tiene precio en Insumos "
                   f"(ITEM_PRIMARIO no aparece en la fecha 2026-07-04). "
                   f"Muestra de 10k familias: {sin_primario} casos detectados.",
    })

    # Familias con 1 solo SKU
    single_sku = int((problemas["TOTAL_SKUS"] == 1).sum()) if "TOTAL_SKUS" in problemas.columns else 0
    obs.append({
        "tipo": "Familias con 1 solo SKU",
        "severidad": "INFO",
        "mensaje": f"ℹ En las top 5k familias problemáticas hay {single_sku} con solo 1 SKU "
                   f"(no aplica comparación de precios).",
    })

    # SKUs sin precio
    sin_precio_total = int(problemas["SKUS_SIN_PRECIO"].sum()) if "SKUS_SIN_PRECIO" in problemas.columns else 0
    obs.append({
        "tipo": "SKUs sin precio",
        "severidad": "ALERTA" if sin_precio_total > 0 else "OK",
        "mensaje": f"{'' if sin_precio_total > 0 else ''} SKUs sin PRECIO_GPI_C_IMP "
                   f"en top 5k familias problemáticas: {sin_precio_total:,}",
    })

    # SKUs sin ventas
    sin_ventas_total = int(problemas["SKUS_SIN_VENTAS"].sum()) if "SKUS_SIN_VENTAS" in problemas.columns else 0
    obs.append({
        "tipo": "SKUs sin ventas",
        "severidad": "INFO",
        "mensaje": f"ℹ SKUs con ventas nulas en top 5k familias: {sin_ventas_total:,} "
                   f"(pueden ser items nuevos o descontinuados).",
    })

    # Precios distintos extremos
    if "PRECIOS_DISTINTOS" in problemas.columns:
        top_precios = problemas.nlargest(5, "PRECIOS_DISTINTOS")[
            ["PAIS", "CODIGO_FAMILIA", "DESC_PRIMARIO", "MARCA", "PRECIOS_DISTINTOS"]
        ]
        filas = " | ".join(
            f"{r.PAIS}-{r.MARCA} ({int(r.PRECIOS_DISTINTOS)} precios distintos)"
            for _, r in top_precios.iterrows()
        )
        obs.append({
            "tipo": "Familias con más precios distintos",
            "severidad": "CRÍTICO",
            "mensaje": f" Top 5 familias con mayor variedad de precios: {filas}",
        })

    # Evaluación conversión
    if "EVALUACION_PRECIO" in conversion.columns:
        revisar = int((conversion["EVALUACION_PRECIO"] == "REVISAR").sum())
        if revisar > 0:
            obs.append({
                "tipo": "Items tamaño diferente a revisar",
                "severidad": "ALERTA",
                "mensaje": f" {revisar:,} items con factor de conversión tienen precio "
                           f"MENOR al primario (se esperaría mayor para packs). Revisar.",
            })

    # Posibles duplicados (mismo ITEM en múltiples filas)
    if "ITEM" in problemas.columns and "CODIGO_FAMILIA" in problemas.columns:
        dup_count = problemas.duplicated(subset=["PAIS", "Formato", "ZONA",
                                                  "CODIGO_FAMILIA"]).sum()
        obs.append({
            "tipo": "Registros duplicados en muestra",
            "severidad": "INFO",
            "mensaje": f"ℹ Filas duplicadas por (PAIS, Formato, ZONA, CODIGO_FAMILIA) "
                       f"en top 5k: {dup_count} (esperado=0 ya que son la clave de agrupación).",
        })

    # Global
    obs.append({
        "tipo": "Alineación Global",
        "severidad": "OK",
        "mensaje": f" Alineación global (mismo tamaño, 5 países): {kpis['pct_global']}% "
                   f"({kpis['alineados']:,} de {kpis['skus_mismo_tamano']:,} SKUs alineados).",
    })

    return obs


# ─── Helpers de datos para JS ────────────────────────────────────────────────

def df_to_json(df: pd.DataFrame, cols: list, max_rows: int = 2000) -> str:
    sub = df[cols].head(max_rows).fillna("")
    # Redondear floats
    for c in sub.columns:
        if sub[c].dtype == float:
            sub[c] = sub[c].round(2)
    return json.dumps(sub.to_dict(orient="records"), ensure_ascii=False)


# ─── HTML helpers ─────────────────────────────────────────────────────────────

def pct_badge(val) -> str:
    try:
        v = float(val)
    except (ValueError, TypeError):
        return '<span class="badge badge-gray">N/D</span>'
    color = "green" if v >= 95 else ("yellow" if v >= 85 else "red")
    return f'<span class="badge badge-{color}">{v:.1f}%</span>'


def director_rows(director: pd.DataFrame) -> str:
    pais_names = {"CR": "Costa Rica ", "GT": "Guatemala ",
                  "HN": "Honduras ", "SV": "El Salvador ", "NI": "Nicaragua "}
    rows = []
    for _, r in director.iterrows():
        pais = pais_names.get(r["PAIS"], r["PAIS"])
        pct = float(r["PCT_ALINEACION_PAIS"])
        bar_color = "#2a8703" if pct >= 93 else ("#ffc220" if pct >= 91 else "#ea1100")
        bar = (f'<div class="bar-wrap"><div class="bar-fill" '
               f'style="width:{pct}%;background:{bar_color}"></div>'
               f'<span class="bar-label">{pct:.2f}%</span></div>')
        rows.append(
            f"<tr>"
            f"<td class='font-semibold'>{pais}</td>"
            f"<td class='text-right'>{int(r['TOTAL_FAMILIAS']):,}</td>"
            f"<td class='text-right'>{int(r['TOTAL_SKUS']):,}</td>"
            f"<td class='text-right'>{int(r['SKUS_MISMO_TAMANO']):,}</td>"
            f"<td class='text-right text-green-700 font-medium'>{int(r['SKUS_ALINEADOS']):,}</td>"
            f"<td class='text-right text-red-600 font-medium'>{int(r['SKUS_NO_ALINEADOS']):,}</td>"
            f"<td>{bar}</td>"
            f"</tr>"
        )
    return "\n".join(rows)


def obs_cards(observations: list) -> str:
    sev_class = {
        "CRÍTICO": "obs-critico", "ALERTA": "obs-alerta",
        "INFO": "obs-info", "OK": "obs-ok",
    }
    cards = []
    for o in observations:
        cls = sev_class.get(o["severidad"], "obs-info")
        cards.append(
            f'<div class="obs-card {cls}">'
            f'<div class="obs-header"><span class="obs-tipo">{o["tipo"]}</span>'
            f'<span class="obs-sev">{o["severidad"]}</span></div>'
            f'<p class="obs-msg">{o["mensaje"]}</p></div>'
        )
    return "\n".join(cards)


# ─── Generación HTML ─────────────────────────────────────────────────────────

def generate_html(kpis: dict, director: pd.DataFrame, problemas: pd.DataFrame,
                  conversion: pd.DataFrame, observations: list) -> str:

    country_labels = json.dumps(director["PAIS"].tolist())
    country_pct = json.dumps(director["PCT_ALINEACION_PAIS"].round(2).tolist())
    country_alineados = json.dumps(director["SKUS_ALINEADOS"].tolist())
    country_no_alineados = json.dumps(director["SKUS_NO_ALINEADOS"].tolist())

    prob_cols = ["PAIS", "Formato", "ZONA", "CODIGO_FAMILIA", "MARCA",
                 "CATEGORIA", "DESC_PRIMARIO", "PRECIO_PRIMARIO",
                 "TOTAL_SKUS", "SKUS_MISMO_TAMANO", "ALINEADOS",
                 "NO_ALINEADOS", "PCT_ALINEACION", "VENTAS_FAMILIA", "PRECIOS_DISTINTOS"]
    prob_cols = [c for c in prob_cols if c in problemas.columns]
    prob_json = df_to_json(problemas, prob_cols, max_rows=2000)

    conv_cols = ["PAIS", "Formato", "ZONA", "CODIGO_FAMILIA", "DESC_PRIMARIO",
                 "PRECIO_PRIMARIO", "TAMANO_PRIMARIO", "MEDIDA_PRIMARIO",
                 "ITEM", "SIGNING_DESC", "PRECIO_GPI_C_IMP",
                 "TAMANO_TOTAL", "MEDIDA", "FACTOR_DE_CONVERSION",
                 "AHORRO_DIFERENCIAL", "RATIO_PRECIO_VS_PRIMARIO",
                 "PRECIO_NORMALIZADO", "PRECIO_ESPERADO", "EVALUACION_PRECIO",
                 "Ventas", "Rotaciones"]
    conv_cols = [c for c in conv_cols if c in conversion.columns]
    conv_json = df_to_json(conversion, conv_cols, max_rows=2000)

    dir_rows_html = director_rows(director)
    obs_html = obs_cards(observations)
    now = datetime.now().strftime("%d/%m/%Y %H:%M")

    # color por pct global
    g = kpis["pct_global"]
    gauge_color = "#2a8703" if g >= 93 else ("#ffc220" if g >= 91 else "#ea1100")

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Análisis de Consistencia de Precios por Familias – CAM Pricing</title>
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  body{{font-family:'Segoe UI',system-ui,sans-serif;background:#f8fafc;color:#1e293b}}
  .wm-blue{{color:#0053e2}} .wm-spark{{color:#ffc220}}
  .kpi-card{{background:#fff;border-radius:12px;padding:20px 24px;
             box-shadow:0 1px 4px rgba(0,0,50,.08);border:1px solid #e2e8f0}}
  .kpi-val{{font-size:2rem;font-weight:700;line-height:1.1}}
  .kpi-label{{font-size:.78rem;color:#64748b;margin-top:4px;text-transform:uppercase;letter-spacing:.04em}}
  .tab-btn{{padding:10px 22px;border-radius:8px 8px 0 0;font-weight:600;font-size:.85rem;
            cursor:pointer;border:none;background:#e2e8f0;color:#475569;transition:all .2s}}
  .tab-btn.active{{background:#0053e2;color:#fff}}
  .tab-panel{{display:none;background:#fff;border-radius:0 12px 12px 12px;
              padding:24px;border:1px solid #e2e8f0;box-shadow:0 1px 4px rgba(0,0,50,.06)}}
  .tab-panel.active{{display:block}}
  table{{border-collapse:collapse;width:100%}}
  th{{background:#0053e2;color:#fff;padding:8px 12px;font-size:.78rem;
      text-align:left;position:sticky;top:0}}
  td{{padding:7px 12px;font-size:.78rem;border-bottom:1px solid #f1f5f9}}
  tr:hover td{{background:#f0f6ff}}
  .badge{{padding:2px 8px;border-radius:20px;font-size:.72rem;font-weight:600}}
  .badge-green{{background:#dcfce7;color:#166534}}
  .badge-yellow{{background:#fef9c3;color:#854d0e}}
  .badge-red{{background:#fee2e2;color:#991b1b}}
  .badge-gray{{background:#f1f5f9;color:#64748b}}
  .eval-ok{{background:#dcfce7;color:#166534;padding:2px 7px;border-radius:12px;font-size:.7rem;font-weight:600}}
  .eval-warn{{background:#fef9c3;color:#854d0e;padding:2px 7px;border-radius:12px;font-size:.7rem;font-weight:600}}
  .eval-bad{{background:#fee2e2;color:#991b1b;padding:2px 7px;border-radius:12px;font-size:.7rem;font-weight:600}}
  .bar-wrap{{position:relative;background:#f1f5f9;border-radius:6px;height:22px;min-width:120px}}
  .bar-fill{{position:absolute;left:0;top:0;height:100%;border-radius:6px;opacity:.85}}
  .bar-label{{position:absolute;right:6px;top:2px;font-size:.72rem;font-weight:700;color:#1e293b}}
  .search-box{{padding:7px 14px;border:1px solid #cbd5e1;border-radius:8px;
               font-size:.82rem;width:260px;outline:none}}
  .search-box:focus{{border-color:#0053e2;box-shadow:0 0 0 2px #0053e220}}
  .obs-card{{border-radius:10px;padding:14px 18px;margin-bottom:12px;border-left:4px solid}}
  .obs-critico{{background:#fff1f2;border-color:#ea1100}}
  .obs-alerta{{background:#fffbeb;border-color:#f59e0b}}
  .obs-info{{background:#eff6ff;border-color:#0053e2}}
  .obs-ok{{background:#f0fdf4;border-color:#2a8703}}
  .obs-header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}}
  .obs-tipo{{font-weight:700;font-size:.82rem}}
  .obs-sev{{font-size:.7rem;padding:2px 8px;border-radius:20px;font-weight:600;
             background:rgba(0,0,0,.08)}}
  .obs-msg{{font-size:.81rem;color:#334155;line-height:1.5}}
  .tbl-wrap{{overflow-x:auto;max-height:500px;overflow-y:auto}}
  .paginator{{display:flex;gap:6px;align-items:center;margin-top:14px;flex-wrap:wrap}}
  .paginator button{{padding:4px 12px;border-radius:6px;border:1px solid #cbd5e1;
                    background:#fff;font-size:.78rem;cursor:pointer}}
  .paginator button.active{{background:#0053e2;color:#fff;border-color:#0053e2}}
  .page-info{{font-size:.78rem;color:#64748b;margin-left:auto}}
  select.filter-sel{{padding:7px 10px;border:1px solid #cbd5e1;border-radius:8px;
                     font-size:.82rem;outline:none;background:#fff}}
</style>
</head>
<body class="min-h-screen">

<!-- HEADER -->
<header style="background:#0053e2;padding:18px 32px;display:flex;align-items:center;gap:16px">
  <svg width="42" height="42" viewBox="0 0 42 42" fill="none">
    <circle cx="21" cy="21" r="21" fill="#ffc220"/>
    <text x="50%" y="57%" text-anchor="middle" fill="#0053e2"
          font-size="22" font-weight="bold" font-family="Arial">W</text>
  </svg>
  <div>
    <h1 style="color:#fff;font-size:1.25rem;font-weight:700;margin:0">
      Análisis de Consistencia de Precios por Familias
    </h1>
    <p style="color:#93c5fd;font-size:.8rem;margin:2px 0 0">
      CAM Pricing Analytics &nbsp;·&nbsp; Datos: 2026-07-04 &nbsp;·&nbsp; Generado: {now}
    </p>
  </div>
</header>

<main style="max-width:1400px;margin:0 auto;padding:28px 24px">

<!-- KPI CARDS -->
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px;margin-bottom:28px">
  <div class="kpi-card">
    <div class="kpi-val" style="color:{gauge_color}">{kpis['pct_global']:.2f}%</div>
    <div class="kpi-label">Alineación Global</div>
    <div style="font-size:.72rem;color:#64748b;margin-top:4px">SKUs mismo tamaño</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-val wm-blue">{kpis['total_fam']:,}</div>
    <div class="kpi-label">Total Familias</div>
    <div style="font-size:.72rem;color:#64748b;margin-top:4px">Combinaciones País·Formato·Zona·Familia</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-val" style="color:#1e293b">{kpis['total_skus']:,}</div>
    <div class="kpi-label">Total SKUs</div>
    <div style="font-size:.72rem;color:#64748b;margin-top:4px">Todos los países</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-val" style="color:#2a8703">{kpis['alineados']:,}</div>
    <div class="kpi-label">SKUs Alineados</div>
    <div style="font-size:.72rem;color:#64748b;margin-top:4px">Precio = Primario, mismo tamaño</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-val" style="color:#ea1100">{kpis['no_alineados']:,}</div>
    <div class="kpi-label">SKUs No Alineados</div>
    <div style="font-size:.72rem;color:#ea1100">Oportunidad de homologación</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-val" style="color:#995213">{kpis['familias_con_problemas']:,}</div>
    <div class="kpi-label">Familias con Problemas</div>
    <div style="font-size:.72rem;color:#64748b;margin-top:4px">Al menos 1 SKU desalineado</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-val" style="color:#7c3aed">{kpis['skus_tamano_diferente']:,}</div>
    <div class="kpi-label">SKUs Tamaño Diferente</div>
    <div style="font-size:.72rem;color:#64748b;margin-top:4px">Factor/Ahorro ≠ 1 (packs, gramajes)</div>
  </div>
</div>

<!-- CHART + DIRECTOR TABLE -->
<div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:28px">
  <div class="kpi-card">
    <h2 style="font-size:.95rem;font-weight:700;color:#0053e2;margin-bottom:14px">
       Alineación de Precios por País (SKUs mismo tamaño)
    </h2>
    <div style="height:260px"><canvas id="chartPais"></canvas></div>
  </div>
  <div class="kpi-card">
    <h2 style="font-size:.95rem;font-weight:700;color:#0053e2;margin-bottom:14px">
       Resumen Ejecutivo por País — Vista para Directores
    </h2>
    <div class="tbl-wrap">
    <table>
      <thead><tr>
        <th>País</th><th>Familias</th><th>Total SKUs</th>
        <th>Mismo Tam.</th><th>Alineados</th><th>No Alineados</th>
        <th style="min-width:160px">% Alineación</th>
      </tr></thead>
      <tbody>{dir_rows_html}</tbody>
    </table>
    </div>
  </div>
</div>

<!-- TABS -->
<div style="margin-bottom:0;display:flex;gap:4px;flex-wrap:wrap">
  <button class="tab-btn active" onclick="switchTab('tab-problemas',this)">
     Familias con Problemas (top 2,000 de 25,404)
  </button>
  <button class="tab-btn" onclick="switchTab('tab-conversion',this)">
     Items Tamaño Diferente (top 2,000 de 10,575)
  </button>
  <button class="tab-btn" onclick="switchTab('tab-obs',this)">
     Observaciones Automáticas
  </button>
</div>

<!-- TAB: Familias con Problemas -->
<div id="tab-problemas" class="tab-panel active">
  <div style="display:flex;gap:12px;align-items:center;margin-bottom:14px;flex-wrap:wrap">
    <input class="search-box" id="searchProb" placeholder=" Buscar marca, familia, desc..."
           oninput="filterTable('tableProb','searchProb','paisFilterProb')"/>
    <select class="filter-sel" id="paisFilterProb" onchange="filterTable('tableProb','searchProb','paisFilterProb')">
      <option value="">Todos los países</option>
      <option>CR</option><option>GT</option><option>HN</option>
      <option>SV</option><option>NI</option>
    </select>
    <span id="countProb" style="font-size:.78rem;color:#64748b"></span>
  </div>
  <div class="tbl-wrap">
  <table id="tableProb">
    <thead><tr>
      <th>País</th><th>Formato</th><th>Zona</th>
      <th>Familia</th><th>Marca</th><th>Categoría</th>
      <th>SKU Primario (desc.)</th><th>Precio Primario</th>
      <th>Total SKUs</th><th>Mismo Tam.</th>
      <th>Alineados</th><th>No Alineados</th>
      <th>% Alineación</th><th>Precios Dist.</th>
      <th>Ventas Familia</th>
    </tr></thead>
    <tbody id="bodyProb"></tbody>
  </table>
  </div>
  <div class="paginator" id="paginatorProb"></div>
</div>

<!-- TAB: Items Tamaño Diferente -->
<div id="tab-conversion" class="tab-panel">
  <p style="font-size:.82rem;color:#475569;margin-bottom:12px;background:#eff6ff;
            padding:10px 14px;border-radius:8px;border-left:4px solid #0053e2">
    ℹ <strong>Vista especial:</strong> Estos items tienen <code>FACTOR_DE_CONVERSION ≠ 1</code>
    o <code>AHORRO_DIFERENCIAL ≠ 1</code>, lo que indica que son de un tamaño o gramaje
    diferente al primario (ej: pack de 3, presentación doble, etc.).
    Para estos ítems, que el precio sea <em>mayor</em> al primario es <strong>correcto y esperado</strong>.
    Se etiqueta como "REVISAR" cuando el precio es <em>menor</em> al primario.
  </p>
  <div style="display:flex;gap:12px;align-items:center;margin-bottom:14px;flex-wrap:wrap">
    <input class="search-box" id="searchConv" placeholder=" Buscar ítem, marca, familia..."
           oninput="filterTable('tableConv','searchConv','paisFilterConv')"/>
    <select class="filter-sel" id="paisFilterConv" onchange="filterTable('tableConv','searchConv','paisFilterConv')">
      <option value="">Todos los países</option>
      <option>CR</option><option>GT</option><option>HN</option>
      <option>SV</option><option>NI</option>
    </select>
    <select class="filter-sel" id="evalFilter" onchange="filterTable('tableConv','searchConv','paisFilterConv')">
      <option value="">Todas las evaluaciones</option>
      <option>MAYOR (esperado para packs)</option>
      <option>PRECIO CORRECTO (normalizado)</option>
      <option>REVISAR</option>
    </select>
    <span id="countConv" style="font-size:.78rem;color:#64748b"></span>
  </div>
  <div class="tbl-wrap">
  <table id="tableConv">
    <thead><tr>
      <th>País</th><th>Formato</th><th>Zona</th>
      <th>Familia</th><th>SKU Primario</th><th>Precio Primario</th>
      <th>Tam. Primario</th><th>Medida</th>
      <th>Item</th><th>Descripción Item</th>
      <th>Precio Item</th><th>Tam. Total</th>
      <th>Factor Conv.</th><th>Ahorro Dif.</th>
      <th>Ratio P/Primario</th><th>Precio Norm.</th>
      <th>Precio Esperado</th><th>Evaluación</th>
      <th>Ventas</th>
    </tr></thead>
    <tbody id="bodyConv"></tbody>
  </table>
  </div>
  <div class="paginator" id="paginatorConv"></div>
</div>

<!-- TAB: Observaciones -->
<div id="tab-obs" class="tab-panel">
  <h3 style="font-size:.95rem;font-weight:700;color:#0053e2;margin-bottom:16px">
     Observaciones automáticas detectadas durante el análisis
  </h3>
  {obs_html}
</div>

<!-- NOTA METODOLÓGICA -->
<div style="margin-top:24px;padding:16px 20px;background:#f8fafc;border-radius:10px;
            border:1px solid #e2e8f0;font-size:.78rem;color:#64748b">
  <strong>Notas metodológicas:</strong>
  <ul style="margin-top:6px;padding-left:16px;line-height:1.8">
    <li><strong>SKU Primario:</strong> El ítem donde <code>ITEM = ITEM_PRIMARIO</code>
        (campo <code>AGRUPACION = 'PRIMARIO'</code>).</li>
    <li><strong>Mismo tamaño:</strong> <code>FACTOR_DE_CONVERSION = 1</code>
        AND <code>AHORRO_DIFERENCIAL = 1</code>.</li>
    <li><strong>Alineado:</strong> <code>PRECIO_GPI_C_IMP</code> del SKU secundario
        igual al precio del primario, dentro del mismo País·Formato·Zona.</li>
    <li><strong>% Alineación =</strong> SKUs alineados (mismo tamaño) / Total SKUs mismo tamaño.</li>
    <li><strong>Items tamaño diferente:</strong> Se espera precio mayor. Se normaliza
        dividiendo por <code>FACTOR_DE_CONVERSION</code>.</li>
    <li>Datos fuente: <code>prcng_info_cam_insumos_diario</code> +
        <code>prcng_info_cam_a0g0dn3_canasto_universal_extendido</code> · Fecha: 2026-07-04</li>
  </ul>
</div>

</main>

<script>
// ─── Datos ───────────────────────────────────────────────────────────────────
const probData = {prob_json};
const convData = {conv_json};

// ─── Chart ──────────────────────────────────────────────────────────────────
const ctx = document.getElementById('chartPais').getContext('2d');
new Chart(ctx, {{
  type: 'bar',
  data: {{
    labels: {country_labels},
    datasets: [
      {{
        label: 'Alineados',
        data: {country_alineados},
        backgroundColor: '#2a8703',
        borderRadius: 4,
      }},
      {{
        label: 'No Alineados',
        data: {country_no_alineados},
        backgroundColor: '#ea1100',
        borderRadius: 4,
      }}
    ]
  }},
  options: {{
    responsive: true, maintainAspectRatio: false,
    plugins: {{
      legend: {{ position: 'top' }},
      tooltip: {{
        callbacks: {{
          afterBody: (items) => {{
            const pcts = {country_pct};
            const i = items[0].dataIndex;
            return `Alineación: ${{pcts[i]}}%`;
          }}
        }}
      }}
    }},
    scales: {{
      x: {{ stacked: true }},
      y: {{ stacked: true, ticks: {{ callback: v => v.toLocaleString() }} }}
    }}
  }}
}});

// ─── Paginación genérica ─────────────────────────────────────────────────────
const PAGE_SIZE = 50;
const state = {{}};

function initTable(tableId, data, renderRow, paginatorId, countId) {{
  state[tableId] = {{ data, filtered: [...data], page: 0 }};
  renderPage(tableId, renderRow, paginatorId, countId);
}}

function renderPage(tableId, renderRow, paginatorId, countId) {{
  const s = state[tableId];
  const tbody = document.getElementById('body' + tableId.replace('table',''));
  const start = s.page * PAGE_SIZE;
  const slice = s.filtered.slice(start, start + PAGE_SIZE);
  tbody.innerHTML = slice.map(renderRow).join('');
  buildPaginator(tableId, renderRow, paginatorId, countId);
  if (countId) {{
    document.getElementById(countId).textContent =
      `Mostrando ${{start+1}}–${{Math.min(start+PAGE_SIZE, s.filtered.length)}} de ${{s.filtered.length.toLocaleString()}} registros`;
  }}
}}

function buildPaginator(tableId, renderRow, paginatorId, countId) {{
  const s = state[tableId];
  const pages = Math.ceil(s.filtered.length / PAGE_SIZE);
  const el = document.getElementById(paginatorId);
  if (!el) return;
  let btns = '';
  const cur = s.page;
  const show = new Set([0, pages-1, cur-1, cur, cur+1, cur+2].filter(p => p>=0 && p<pages));
  let last = -1;
  [...show].sort((a,b)=>a-b).forEach(p => {{
    if (last>=0 && p-last>1) btns += '<span style="color:#94a3b8">…</span>';
    btns += `<button class="${{cur===p?'active':''}}"
               onclick="goPage('${{tableId}}','${{renderRow.name}}','${{paginatorId}}','${{countId}}',${{p}})">${{p+1}}</button>`;
    last = p;
  }});
  el.innerHTML = btns + `<span class="page-info">Página ${{cur+1}} / ${{pages}}</span>`;
}}

function goPage(tableId, renderRowName, paginatorId, countId, page) {{
  const fns = {{ renderProbRow, renderConvRow }};
  state[tableId].page = page;
  renderPage(tableId, fns[renderRowName], paginatorId, countId);
  document.getElementById(tableId)?.scrollIntoView({{behavior:'smooth',block:'nearest'}});
}}

// ─── Filtros ─────────────────────────────────────────────────────────────────
function filterTable(tableId, searchId, paisId) {{
  const term = document.getElementById(searchId)?.value.toLowerCase() || '';
  const pais = document.getElementById(paisId)?.value || '';
  const evalF = document.getElementById('evalFilter')?.value || '';
  const src = state[tableId].data;
  state[tableId].filtered = src.filter(r => {{
    const str = JSON.stringify(r).toLowerCase();
    const matchTerm = !term || str.includes(term);
    const matchPais = !pais || r.PAIS === pais;
    const matchEval = !evalF || r.EVALUACION_PRECIO === evalF;
    return matchTerm && matchPais && matchEval;
  }});
  state[tableId].page = 0;
  const fnMap = {{ tableProb: renderProbRow, tableConv: renderConvRow }};
  const pidMap = {{ tableProb: 'paginatorProb', tableConv: 'paginatorConv' }};
  const cidMap = {{ tableProb: 'countProb', tableConv: 'countConv' }};
  renderPage(tableId, fnMap[tableId], pidMap[tableId], cidMap[tableId]);
}}

// ─── Render: Familias con Problemas ──────────────────────────────────────────
function pctBadge(v) {{
  if (v==='' || v===null || v===undefined) return '<span class="badge badge-gray">N/D</span>';
  const n = parseFloat(v);
  const cls = n>=95?'green':n>=85?'yellow':'red';
  return `<span class="badge badge-${{cls}}">${{n.toFixed(1)}}%</span>`;
}}

function fmt(v, dec=0) {{
  if (v==='' || v===null || v===undefined) return '—';
  const n = parseFloat(v);
  return isNaN(n) ? v : n.toLocaleString('es', {{minimumFractionDigits:dec,maximumFractionDigits:dec}});
}}

function renderProbRow(r) {{
  return `<tr>
    <td class="font-semibold">${{r.PAIS||'—'}}</td>
    <td>${{r.Formato||'—'}}</td>
    <td style="white-space:nowrap">${{r.ZONA||'—'}}</td>
    <td style="font-family:monospace;font-size:.73rem">${{r.CODIGO_FAMILIA||'—'}}</td>
    <td><strong>${{r.MARCA||'—'}}</strong></td>
    <td style="font-size:.73rem">${{r.CATEGORIA||'—'}}</td>
    <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap"
        title="${{r.DESC_PRIMARIO||''}}">${{r.DESC_PRIMARIO||'—'}}</td>
    <td class="text-right font-medium">${{fmt(r.PRECIO_PRIMARIO,2)}}</td>
    <td class="text-right">${{fmt(r.TOTAL_SKUS)}}</td>
    <td class="text-right">${{fmt(r.SKUS_MISMO_TAMANO)}}</td>
    <td class="text-right text-green-700">${{fmt(r.ALINEADOS)}}</td>
    <td class="text-right text-red-600 font-semibold">${{fmt(r.NO_ALINEADOS)}}</td>
    <td>${{pctBadge(r.PCT_ALINEACION)}}</td>
    <td class="text-right">${{fmt(r.PRECIOS_DISTINTOS)}}</td>
    <td class="text-right">${{fmt(r.VENTAS_FAMILIA,0)}}</td>
  </tr>`;
}}

// ─── Render: Items Conversión ─────────────────────────────────────────────────
function evalBadge(v) {{
  if (!v) return '<span class="badge badge-gray">—</span>';
  if (v.includes('CORRECTO')) return `<span class="eval-ok">${{v}}</span>`;
  if (v.includes('MAYOR')) return `<span class="eval-warn">${{v}}</span>`;
  return `<span class="eval-bad">${{v}}</span>`;
}}

function renderConvRow(r) {{
  return `<tr>
    <td class="font-semibold">${{r.PAIS||'—'}}</td>
    <td>${{r.Formato||'—'}}</td>
    <td style="white-space:nowrap">${{r.ZONA||'—'}}</td>
    <td style="font-family:monospace;font-size:.73rem">${{r.CODIGO_FAMILIA||'—'}}</td>
    <td style="max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap"
        title="${{r.DESC_PRIMARIO||''}}">${{r.DESC_PRIMARIO||'—'}}</td>
    <td class="text-right font-medium">${{fmt(r.PRECIO_PRIMARIO,2)}}</td>
    <td class="text-right">${{fmt(r.TAMANO_PRIMARIO,0)}}</td>
    <td>${{r.MEDIDA_PRIMARIO||'—'}}</td>
    <td style="font-family:monospace;font-size:.73rem">${{r.ITEM||'—'}}</td>
    <td style="max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap"
        title="${{r.SIGNING_DESC||''}}">${{r.SIGNING_DESC||'—'}}</td>
    <td class="text-right font-semibold" style="color:#0053e2">${{fmt(r.PRECIO_GPI_C_IMP,2)}}</td>
    <td class="text-right">${{fmt(r.TAMANO_TOTAL,0)}}</td>
    <td class="text-right font-medium" style="color:#7c3aed">${{fmt(r.FACTOR_DE_CONVERSION,2)}}</td>
    <td class="text-right">${{fmt(r.AHORRO_DIFERENCIAL,2)}}</td>
    <td class="text-right">${{fmt(r.RATIO_PRECIO_VS_PRIMARIO,3)}}</td>
    <td class="text-right">${{fmt(r.PRECIO_NORMALIZADO,2)}}</td>
    <td class="text-right">${{fmt(r.PRECIO_ESPERADO,2)}}</td>
    <td>${{evalBadge(r.EVALUACION_PRECIO)}}</td>
    <td class="text-right">${{fmt(r.Ventas,0)}}</td>
  </tr>`;
}}

// ─── Tabs ─────────────────────────────────────────────────────────────────────
function switchTab(panelId, btn) {{
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById(panelId).classList.add('active');
  btn.classList.add('active');
}}

// ─── Init ─────────────────────────────────────────────────────────────────────
initTable('tableProb', probData, renderProbRow, 'paginatorProb', 'countProb');
initTable('tableConv', convData, renderConvRow, 'paginatorConv', 'countConv');
</script>
</body>
</html>"""
    return html


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("Cargando datos...")
    director, problemas, conversion = load_data()

    print(f"  Director: {len(director)} países")
    print(f"  Problemas: {len(problemas):,} familias")
    print(f"  Conversion: {len(conversion):,} items")

    kpis = compute_kpis(director)
    print(f"\nKPIs globales:")
    print(f"  Alineación global: {kpis['pct_global']}%")
    print(f"  Total SKUs: {kpis['total_skus']:,}")
    print(f"  Alineados: {kpis['alineados']:,}")
    print(f"  No alineados: {kpis['no_alineados']:,}")

    observations = build_observations(director, problemas, conversion, kpis)
    print(f"\n  Observaciones generadas: {len(observations)}")

    html = generate_html(kpis, director, problemas, conversion, observations)

    out_path = os.path.join(BASE, "reporte_familias_precios.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n Reporte generado: {out_path}")
    print(f"   Tamaño: {os.path.getsize(out_path) / 1024:.1f} KB")

    webbrowser.open(f"file:///{out_path.replace(os.sep, '/')}")
    print("   Abriendo en el navegador...")


if __name__ == "__main__":
    main()

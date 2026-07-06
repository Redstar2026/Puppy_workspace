"""
Reporte de Consistencia de Precios por Familias - CAM Pricing
Fecha de datos: 2026-07-04
Entregables: 10 segun el prompt reestructurado
"""
import os, json, webbrowser
from datetime import datetime
import pandas as pd

BASE   = os.path.dirname(os.path.abspath(__file__))
BQ_DIR = os.path.join(BASE, "bq_results")

# ── GLOBALES (calculados de BQ director query) ─────────────────────────────
GLOBALES = {
    "total_familias":          522762,
    "total_skus":              699819,
    "skus_validos":            689244,
    "skus_pack_gramaje":       10575,
    "skus_alineados":          636072,
    "skus_no_alineados":       43384,
    "familias_100_alineadas":  515655,
    "familias_con_diferencias": 26857,
    "pct_global":              93.61,
}

# ── LOAD DATA ──────────────────────────────────────────────────────────────
def load():
    director  = pd.read_csv(os.path.join(BQ_DIR, "01_director_pais.csv"))
    familias  = pd.read_csv(os.path.join(BQ_DIR, "02_resumen_familias.csv"))
    packs     = pd.read_csv(os.path.join(BQ_DIR, "03_packs_gramajes.csv"))
    detalle   = pd.read_csv(os.path.join(BQ_DIR, "04_detalle_desalineados.csv"))
    return director, familias, packs, detalle

# ── JSON SAFE ──────────────────────────────────────────────────────────────
def to_json(df, cols, n=1500):
    avail = [c for c in cols if c in df.columns]
    sub = df[avail].head(n).copy()
    for c in sub.select_dtypes("float").columns:
        sub[c] = sub[c].round(4)
    sub = sub.where(pd.notna(sub), other=None)
    raw = json.dumps(sub.to_dict("records"), ensure_ascii=False)
    return raw.replace("</", "<\\/")

# ── CHART.JS INLINE ────────────────────────────────────────────────────────
def chartjs():
    p = os.path.join(BASE, "chartjs.min.js")
    if os.path.exists(p):
        with open(p, encoding="utf-8", errors="replace") as f:
            return f"<script>{f.read()}</script>"
    return ""

# ── OBSERVACIONES ──────────────────────────────────────────────────────────
def observaciones(director, familias, packs, detalle):
    obs = []
    # Por pais
    pnames = {"CR":"Costa Rica","GT":"Guatemala","HN":"Honduras","SV":"El Salvador","NI":"Nicaragua"}
    for _, r in director.sort_values("PCT_ALINEACION").iterrows():
        p   = r["PAIS"]
        pct = float(r["PCT_ALINEACION"])
        sev = "OK" if pct >= 94 else ("ALERTA" if pct >= 92 else "CRITICO")
        obs.append({"sev": sev, "titulo": f"Alineacion {pnames.get(p,p)}",
                    "msg": f"{pct:.2f}% | {int(r['SKUS_NO_ALINEADOS']):,} SKUs desalineados en {int(r['FAMILIAS_CON_DIFERENCIAS']):,} familias"})
    # Sin primario
    sin_prim = int((familias["TIENE_SKU_PRIMARIO"] == 0).sum()) if "TIENE_SKU_PRIMARIO" in familias.columns else 0
    obs.append({"sev":"ALERTA","titulo":"Familias sin SKU Primario",
                "msg":f"{sin_prim} familias en muestra sin item primario registrado en Insumos"})
    # SKUs sin precio
    if "SKUS_SIN_PRECIO" in familias.columns:
        n = int(familias["SKUS_SIN_PRECIO"].sum())
        obs.append({"sev":"ALERTA" if n>0 else "OK","titulo":"SKUs sin precio",
                    "msg":f"{n:,} SKUs sin PRECIO_GPI_C_IMP en top 5k familias"})
    # Packs con precio menor al primario (REVISAR)
    if "EVALUACION" in packs.columns:
        revisar = int((packs["EVALUACION"].str.contains("REVISAR", na=False)).sum())
        obs.append({"sev":"ALERTA" if revisar>0 else "OK","titulo":"Packs con precio MENOR al primario",
                    "msg":f"{revisar:,} items de pack/gramaje tienen precio MENOR al primario (esperado: mayor). Revisar."})
    # Top familias problema
    if "PRECIOS_DISTINTOS" in familias.columns:
        top3 = familias.nlargest(3,"PRECIOS_DISTINTOS")[["PAIS","MARCA","PRECIOS_DISTINTOS","PCT_ALINEACION"]]
        for _,r in top3.iterrows():
            obs.append({"sev":"CRITICO","titulo":f"Multiples precios - {r['MARCA']} ({r['PAIS']})",
                        "msg":f"{int(r['PRECIOS_DISTINTOS'])} precios distintos dentro de la familia | Alineacion: {r['PCT_ALINEACION']}%"})
    # Global
    obs.append({"sev":"INFO","titulo":"Alineacion Global (mismo tamano)",
                "msg":f"{GLOBALES['pct_global']:.2f}% | {GLOBALES['skus_alineados']:,} de {GLOBALES['skus_validos']:,} SKUs alineados"})
    obs.append({"sev":"INFO","titulo":"SKUs excluidos del indicador (pack/gramaje)",
                "msg":f"{GLOBALES['skus_pack_gramaje']:,} SKUs con Factor/Ahorro != 1 — analizados en vista exclusiva"})
    return obs

# ── GENERATE HTML ──────────────────────────────────────────────────────────
def html(director, familias, packs, detalle, obs_list):
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    g   = GLOBALES

    # chart data
    dir_sorted = director.sort_values("PCT_ALINEACION")
    c_labels = json.dumps(dir_sorted["PAIS"].tolist())
    c_ali    = json.dumps(dir_sorted["SKUS_ALINEADOS"].tolist())
    c_nali   = json.dumps(dir_sorted["SKUS_NO_ALINEADOS"].tolist())
    c_pcts   = json.dumps(dir_sorted["PCT_ALINEACION"].round(2).tolist())

    # JSON data
    fam_cols  = ["PAIS","Formato","ZONA","CODIGO_FAMILIA","MARCA","CATEGORIA",
                 "DESC_PRIMARIO","SKU_PRIMARIO","PRECIO_PRIMARIO","VENTAS_PRIMARIO",
                 "TOTAL_SKUS","SKUS_VALIDOS","SKUS_PACK_GRAMAJE","PRECIOS_DISTINTOS",
                 "SKUS_ALINEADOS","SKUS_NO_ALINEADOS","PCT_ALINEACION",
                 "SKUS_SIN_PRECIO","SKUS_SIN_VENTAS","VENTAS_FAMILIA","ESTADOS_PRESENTES"]
    pack_cols = ["PAIS","Formato","ZONA","CODIGO_FAMILIA","DESC_PRIMARIO","SKU_PRIMARIO",
                 "PRECIO_PRIMARIO","TAMANO_PRIMARIO","MEDIDA_PRIMARIO",
                 "SKU_SECUNDARIO","AGRUPACION","DESC_SECUNDARIO","PRECIO_SECUNDARIO",
                 "TAMANO_SECUNDARIO","MEDIDA_SECUNDARIO","FACTOR_DE_CONVERSION",
                 "AHORRO_DIFERENCIAL","DIFERENCIA_ABSOLUTA","DIFERENCIA_PCT",
                 "EVALUACION","Ventas","Rotaciones","MARCA","CATEGORIA"]
    det_cols  = ["PAIS","Formato","ZONA","CODIGO_FAMILIA","ITEM","AGRUPACION","SIGNING_DESC",
                 "CATEGORIA","MARCA","PRECIO_GPI_C_IMP","PRECIO_PRIMARIO","SKU_PRIMARIO",
                 "DESC_PRIMARIO","ESTADO_PRECIO","DIFERENCIA_PRECIO","DIFERENCIA_PCT",
                 "CANTIDAD_SKUS_MISMO_PRECIO","CANTIDAD_PRECIOS_DISTINTOS",
                 "Ventas","Rotaciones","OBSERVACIONES"]

    j_fam  = to_json(familias, fam_cols,  1500)
    j_pack = to_json(packs,    pack_cols, 1500)
    j_det  = to_json(detalle,  det_cols,  1500)
    j_dir  = to_json(director, list(director.columns), 10)

    # observaciones html
    sev_cls = {"CRITICO":"obs-crit","ALERTA":"obs-alerta","OK":"obs-ok","INFO":"obs-info"}
    obs_html = "\n".join(
        f'<div class="obs-card {sev_cls.get(o["sev"],"obs-info")}">'
        f'<div class="obs-hdr"><span class="obs-tipo">{o["titulo"]}</span>'
        f'<span class="obs-tag">{o["sev"]}</span></div>'
        f'<p class="obs-msg">{o["msg"]}</p></div>'
        for o in obs_list
    )

    gc = "#2a8703" if g["pct_global"]>=94 else ("#e6a817" if g["pct_global"]>=92 else "#ea1100")

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Consistencia de Precios por Familias - CAM Pricing 2026-07-04</title>
{chartjs()}
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',system-ui,sans-serif;background:#f0f4f8;color:#1e293b;font-size:14px}}
/* header */
.hdr{{background:#0053e2;padding:14px 28px;display:flex;align-items:center;gap:14px;position:sticky;top:0;z-index:100;box-shadow:0 2px 8px rgba(0,0,80,.18)}}
.spark{{width:40px;height:40px;background:#ffc220;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:19px;font-weight:800;color:#0053e2;flex-shrink:0}}
.hdr h1{{color:#fff;font-size:1.1rem;font-weight:700}}
.hdr small{{color:#93c5fd;font-size:.72rem}}
/* layout */
.page{{max-width:1440px;margin:0 auto;padding:20px 18px}}
.g2{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.g3{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}}
.g4{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}}
.gkpi{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-bottom:20px}}
@media(max-width:900px){{.g2,.g3{{grid-template-columns:1fr}}}}
/* card */
.card{{background:#fff;border-radius:12px;padding:18px 20px;border:1px solid #e2e8f0;box-shadow:0 1px 5px rgba(0,0,50,.07)}}
/* kpi */
.kpi-v{{font-size:1.85rem;font-weight:800;line-height:1.1}}
.kpi-l{{font-size:.68rem;text-transform:uppercase;letter-spacing:.05em;color:#64748b;margin-top:4px}}
.kpi-s{{font-size:.65rem;color:#94a3b8;margin-top:3px}}
/* section */
.sec{{margin-top:20px}}
.sec-title{{font-size:.95rem;font-weight:700;color:#0053e2;margin-bottom:14px;display:flex;align-items:center;gap:8px}}
.sec-num{{background:#0053e2;color:#fff;border-radius:50%;width:22px;height:22px;display:inline-flex;align-items:center;justify-content:center;font-size:.7rem;font-weight:800;flex-shrink:0}}
/* tabs */
.tabs{{display:flex;gap:3px;flex-wrap:wrap;margin-bottom:-1px;margin-top:20px}}
.tbtn{{padding:8px 18px;border-radius:8px 8px 0 0;font-weight:600;font-size:.78rem;cursor:pointer;border:1px solid #e2e8f0;border-bottom:none;background:#e8edf5;color:#475569}}
.tbtn.active{{background:#0053e2;color:#fff;border-color:#0053e2}}
.tpanel{{display:none;background:#fff;border-radius:0 12px 12px 12px;padding:20px;border:1px solid #e2e8f0}}
.tpanel.active{{display:block}}
/* table */
.tw{{overflow-x:auto;max-height:460px;overflow-y:auto;border-radius:8px;border:1px solid #e2e8f0}}
table{{border-collapse:collapse;width:100%;min-width:500px}}
thead th{{background:#0053e2;color:#fff;padding:8px 11px;font-size:.72rem;text-align:left;position:sticky;top:0;z-index:2;white-space:nowrap}}
tbody td{{padding:6px 11px;font-size:.72rem;border-bottom:1px solid #f1f5f9;white-space:nowrap}}
tr:hover td{{background:#f0f6ff}}
.tr{{text-align:right}} .green{{color:#166534;font-weight:700}} .red{{color:#991b1b;font-weight:700}} .blue{{color:#1e40af;font-weight:700}}
/* badges */
.b{{display:inline-block;padding:2px 8px;border-radius:20px;font-size:.67rem;font-weight:700}}
.b-g{{background:#dcfce7;color:#166534}} .b-y{{background:#fef9c3;color:#854d0e}}
.b-r{{background:#fee2e2;color:#991b1b}} .b-z{{background:#f1f5f9;color:#64748b}}
.b-b{{background:#dbeafe;color:#1e40af}} .b-p{{background:#ede9fe;color:#5b21b6}}
/* controls */
.ctrl{{display:flex;gap:9px;align-items:center;margin-bottom:12px;flex-wrap:wrap}}
.sbox{{padding:6px 12px;border:1px solid #cbd5e1;border-radius:7px;font-size:.78rem;width:220px;outline:none}}
.sbox:focus{{border-color:#0053e2}}
.sel{{padding:6px 9px;border:1px solid #cbd5e1;border-radius:7px;font-size:.78rem;background:#fff;outline:none;cursor:pointer}}
.bdl{{padding:5px 13px;border-radius:7px;border:1px solid #0053e2;background:#fff;color:#0053e2;font-size:.76rem;font-weight:700;cursor:pointer}}
.bdl:hover{{background:#eff6ff}}
.rc{{font-size:.72rem;color:#64748b}}
/* paginator */
.pg{{display:flex;gap:4px;align-items:center;margin-top:11px;flex-wrap:wrap}}
.pg button{{padding:3px 10px;border-radius:5px;border:1px solid #cbd5e1;background:#fff;font-size:.72rem;cursor:pointer}}
.pg button.active{{background:#0053e2;color:#fff;border-color:#0053e2}}
.pgi{{font-size:.7rem;color:#64748b;margin-left:auto}}
/* bar */
.bw{{position:relative;background:#f1f5f9;border-radius:6px;height:20px;min-width:120px}}
.bf{{position:absolute;left:0;top:0;height:100%;border-radius:6px}}
.bl{{position:absolute;right:6px;top:2px;font-size:.68rem;font-weight:700}}
/* obs */
.obs-card{{border-radius:9px;padding:12px 16px;margin-bottom:10px;border-left:4px solid}}
.obs-crit{{background:#fff1f2;border-color:#ea1100}}
.obs-alerta{{background:#fffbeb;border-color:#f59e0b}}
.obs-ok{{background:#f0fdf4;border-color:#2a8703}}
.obs-info{{background:#eff6ff;border-color:#0053e2}}
.obs-hdr{{display:flex;justify-content:space-between;align-items:center;margin-bottom:4px}}
.obs-tipo{{font-weight:700;font-size:.78rem}}
.obs-tag{{font-size:.66rem;padding:2px 8px;border-radius:20px;font-weight:700;background:rgba(0,0,0,.08)}}
.obs-msg{{font-size:.75rem;color:#334155;line-height:1.5}}
/* nota */
.nota{{margin-top:20px;padding:14px 18px;background:#f8fafc;border-radius:9px;border:1px solid #e2e8f0;font-size:.72rem;color:#64748b;line-height:1.8}}
.nota b{{color:#1e293b}}
/* sql */
.sqlbox{{background:#0f172a;color:#e2e8f0;border-radius:10px;padding:16px 18px;font-family:monospace;font-size:.71rem;line-height:1.7;overflow-x:auto;white-space:pre}}
.cm{{color:#64748b}} .kw{{color:#7dd3fc}} .fn{{color:#c084fc}} .st{{color:#86efac}}
/* info banner */
.info{{background:#eff6ff;border-left:4px solid #0053e2;border-radius:8px;padding:10px 14px;font-size:.75rem;color:#1e40af;margin-bottom:13px;line-height:1.6}}
/* recom */
.recom-card{{background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px 18px;margin-bottom:10px}}
.recom-title{{font-weight:700;font-size:.82rem;color:#0053e2;margin-bottom:6px}}
.recom-body{{font-size:.76rem;color:#334155;line-height:1.6}}
</style>
</head>
<body>

<div class="hdr">
  <div class="spark">W</div>
  <div>
    <h1>Analisis de Consistencia de Precios por Familias</h1>
    <small>CAM Pricing Analytics &nbsp;|&nbsp; Datos: 2026-07-04 &nbsp;|&nbsp; Generado: {now} &nbsp;|&nbsp; Rol: Consultor Senior Pricing &amp; BigQuery</small>
  </div>
</div>

<div class="page">

<!-- ══ KPIs GLOBALES ══════════════════════════════════════════════════════ -->
<div class="gkpi" style="margin-top:18px">
  <div class="card"><div class="kpi-v" style="color:{gc}">{g['pct_global']:.2f}%</div><div class="kpi-l">Alineacion Global</div><div class="kpi-s">SKUs mismo tamano, excluye packs</div></div>
  <div class="card"><div class="kpi-v" style="color:#0053e2">{g['total_familias']:,}</div><div class="kpi-l">Total Familias</div><div class="kpi-s">Pais x Formato x Zona x Cod.Familia</div></div>
  <div class="card"><div class="kpi-v" style="color:#1e293b">{g['total_skus']:,}</div><div class="kpi-l">Total SKUs</div><div class="kpi-s">Todos los paises</div></div>
  <div class="card"><div class="kpi-v" style="color:#2a8703">{g['skus_alineados']:,}</div><div class="kpi-l">SKUs Alineados</div><div class="kpi-s">Precio = Primario, mismo tamano</div></div>
  <div class="card"><div class="kpi-v" style="color:#ea1100">{g['skus_no_alineados']:,}</div><div class="kpi-l">SKUs No Alineados</div><div class="kpi-s">Oportunidad de homologacion</div></div>
  <div class="card"><div class="kpi-v" style="color:#995213">{g['familias_con_diferencias']:,}</div><div class="kpi-l">Familias con Diferencias</div><div class="kpi-s">Al menos 1 SKU desalineado</div></div>
  <div class="card"><div class="kpi-v" style="color:#166534">{g['familias_100_alineadas']:,}</div><div class="kpi-l">Familias 100% Alineadas</div><div class="kpi-s">Sin desviaciones</div></div>
  <div class="card"><div class="kpi-v" style="color:#7c3aed">{g['skus_pack_gramaje']:,}</div><div class="kpi-l">SKUs Pack/Gramaje</div><div class="kpi-s">Excluidos del indicador (Factor/Ahorro != 1)</div></div>
</div>

<!-- ══ 1. ESTRATEGIA ═══════════════════════════════════════════════════════ -->
<div class="sec card">
  <div class="sec-title"><span class="sec-num">1</span> Estrategia Utilizada</div>
  <div style="font-size:.78rem;color:#334155;line-height:1.8">
    <p>El analisis se construyo en BigQuery con una arquitectura de <b>CTEs encadenadas</b> que permite reproducibilidad y escalabilidad. La logica se divide en 5 capas:</p>
    <ol style="padding-left:20px;margin-top:8px">
      <li><b>formatos_zonas</b> — Catalogo DISTINCT de combinaciones validas Pais-Formato-Zona-Item desde Insumos</li>
      <li><b>canasto_explosionado</b> — INNER JOIN del Canasto contra el catalogo: cada item del canasto se replica por cada Formato-Zona donde aparece en Insumos</li>
      <li><b>insumos</b> — Metricas de precio, rotacion y ventas filtradas por fecha</li>
      <li><b>Familias</b> — LEFT JOIN del canasto explosionado con insumos: conserva el 100% de registros del canasto</li>
      <li><b>primarios</b> — Snapshot del SKU Primario por familia (donde ITEM = ITEM_PRIMARIO)</li>
    </ol>
    <p style="margin-top:10px"><b>Regla critica implementada:</b> Los SKUs con Factor_Conversion != 1 o Ahorro_Diferencial != 1 (packs, gramajes) se <b>excluyen del denominador del % de alineacion</b> pero se <b>muestran en la vista exclusiva de packs</b> con la leyenda "Esperado precio distinto por pack o tamano diferente".</p>
  </div>
</div>

<!-- ══ 2. LOGICA DE NEGOCIO ════════════════════════════════════════════════ -->
<div class="sec card">
  <div class="sec-title"><span class="sec-num">2</span> Logica de Negocio Aplicada</div>
  <div class="g2" style="gap:18px;font-size:.76rem;color:#334155;line-height:1.7">
    <div>
      <b style="color:#0053e2">Definicion de Familia:</b>
      <ul style="padding-left:16px;margin-top:4px">
        <li>Pais + Formato + Zona + Codigo_Familia (ITEM_PRIMARIO)</li>
        <li>Debe tener exactamente 1 SKU Primario (ITEM = ITEM_PRIMARIO)</li>
        <li>Si no tiene Primario → marcada como inconsistencia</li>
      </ul>
      <br/>
      <b style="color:#0053e2">SKU Primario:</b>
      <ul style="padding-left:16px;margin-top:4px">
        <li>Campo AGRUPACION = 'PRIMARIO' en el canasto</li>
        <li>Condicion: ITEM = ITEM_PRIMARIO</li>
        <li>Es la referencia de precio para toda la familia</li>
      </ul>
    </div>
    <div>
      <b style="color:#ea1100">Regla 1 — Mismo tamano:</b>
      <ul style="padding-left:16px;margin-top:4px">
        <li>Factor_Conversion = 1 AND Ahorro_Diferencial = 1</li>
        <li>DEBEN tener el mismo precio que el Primario</li>
        <li>Si difieren → ESTADO_PRECIO = "Diferente al Primario" → Oportunidad de homologacion</li>
      </ul>
      <br/>
      <b style="color:#7c3aed">Regla 2 — Packs/Gramajes (CRITICA):</b>
      <ul style="padding-left:16px;margin-top:4px">
        <li>Factor_Conversion != 1 OR Ahorro_Diferencial != 1</li>
        <li>Precio mayor al primario es CORRECTO y ESPERADO</li>
        <li>NO afectan el % de alineacion de la familia</li>
        <li>Se muestran en vista exclusiva con leyenda explicativa</li>
      </ul>
    </div>
  </div>
</div>

<!-- ══ 3. SQL DOCUMENTADO ═══════════════════════════════════════════════════ -->
<div class="sec card">
  <div class="sec-title"><span class="sec-num">3</span> SQL Completamente Documentado</div>
  <pre class="sqlbox"><span class="cm">-- ============================================================
-- ANALISIS DE CONSISTENCIA DE PRECIOS POR FAMILIAS - CAM
-- Fecha: 2026-07-04 | Autor: Consultor Senior Pricing & BQ
-- Arquitectura: 5 CTEs encadenadas + Window Functions
-- ============================================================</span>

<span class="kw">WITH</span>
<span class="cm">-- CTE 1: Catalogo DISTINCT de combinaciones validas en Insumos
-- Proposito: evitar explotar el canasto con combinaciones fantasma</span>
formatos_zonas <span class="kw">AS</span> (
    <span class="kw">SELECT DISTINCT</span> Pais, Formato, nomb_zone, item
    <span class="kw">FROM</span> <span class="st">`wmt-k1-cons-data-users.k1_adhoc_tables.prcng_info_cam_insumos_diario`</span>
    <span class="kw">WHERE</span> EXTRACT_DATE = <span class="st">"2026-07-04 00:00:00 UTC"</span>
),

<span class="cm">-- CTE 2: Explosion del Canasto x combinaciones de Insumos
-- INNER JOIN: solo items que existen en Insumos para esa fecha
-- Resultado: cada item del canasto replicado por Formato-Zona</span>
canasto_explosionado <span class="kw">AS</span> (
    <span class="kw">SELECT</span> c.*, fz.Formato, fz.nomb_zone
    <span class="kw">FROM</span> <span class="st">`...canasto_universal_extendido`</span> c
    <span class="kw">INNER JOIN</span> formatos_zonas fz <span class="kw">ON</span> c.Pais = fz.Pais <span class="kw">AND</span> c.item = fz.item
),

<span class="cm">-- CTE 3: Metricas de precio y ventas por item-formato-zona
-- LEFT JOIN posterior para conservar el 100% del canasto</span>
insumos <span class="kw">AS</span> (
    <span class="kw">SELECT</span> Pais, Formato, nomb_zone, Item,
           PRECIO_GPI_C_IMP, Rotaciones, Ventas, Sell_QTY
    <span class="kw">FROM</span> <span class="st">`...prcng_info_cam_insumos_diario`</span>
    <span class="kw">WHERE</span> EXTRACT_DATE = <span class="st">"2026-07-04 00:00:00 UTC"</span>
),

<span class="cm">-- CTE 4: Tabla base completa (LEFT JOIN = no se pierde ningun registro)</span>
Familias <span class="kw">AS</span> (
    <span class="kw">SELECT</span> ce.*, i.PRECIO_GPI_C_IMP, i.Rotaciones, i.Ventas, i.Sell_QTY
    <span class="kw">FROM</span> canasto_explosionado ce
    <span class="kw">LEFT JOIN</span> insumos i
        <span class="kw">ON</span> ce.Pais=i.Pais <span class="kw">AND</span> ce.Formato=i.Formato
        <span class="kw">AND</span> ce.nomb_zone=i.nomb_zone <span class="kw">AND</span> ce.Item=i.Item
),

<span class="cm">-- CTE 5: Snapshot del SKU Primario por familia
-- SKU Primario = el item donde ITEM = ITEM_PRIMARIO</span>
primarios <span class="kw">AS</span> (
    <span class="kw">SELECT</span> PAIS, Formato, nomb_zone, ITEM_PRIMARIO,
           ITEM <span class="kw">AS</span> SKU_PRIMARIO,
           PRECIO_GPI_C_IMP <span class="kw">AS</span> PRECIO_PRIMARIO,
           Ventas <span class="kw">AS</span> VENTAS_PRIMARIO,
           Rotaciones <span class="kw">AS</span> ROTACIONES_PRIMARIO,
           SIGNING_DESC <span class="kw">AS</span> DESC_PRIMARIO
    <span class="kw">FROM</span> Familias <span class="kw">WHERE</span> ITEM = ITEM_PRIMARIO
),

<span class="cm">-- CTE 6: Detalle enriquecido con WINDOW FUNCTIONS
-- ESTADO_PRECIO, OBSERVACIONES, agrupacion por precio</span>
detalle_enriquecido <span class="kw">AS</span> (
    <span class="kw">SELECT</span>
        f.*,
        p.SKU_PRIMARIO, p.PRECIO_PRIMARIO, p.DESC_PRIMARIO,

        <span class="cm">-- REGLA CRITICA: identificar packs/gramajes ANTES de calcular ESTADO</span>
        <span class="kw">CASE</span>
            <span class="kw">WHEN NOT</span>(<span class="fn">COALESCE</span>(f.FACTOR_DE_CONVERSION,1)=1
                 <span class="kw">AND</span> <span class="fn">COALESCE</span>(f.AHORRO_DIFERENCIAL,1)=1)
                <span class="kw">THEN</span> <span class="st">'Esperado precio distinto por pack o tamano diferente'</span>
            <span class="kw">WHEN</span> p.SKU_PRIMARIO <span class="kw">IS NULL THEN</span> <span class="st">'Sin primario - inconsistencia'</span>
            <span class="kw">WHEN</span> f.PRECIO_GPI_C_IMP <span class="kw">IS NULL THEN</span> <span class="st">'Sin precio'</span>
            <span class="kw">WHEN</span> f.PRECIO_GPI_C_IMP = p.PRECIO_PRIMARIO <span class="kw">THEN</span> <span class="st">'Igual al Primario'</span>
            <span class="kw">ELSE</span> <span class="st">'Diferente al Primario'</span>
        <span class="kw">END AS</span> ESTADO_PRECIO,

        <span class="cm">-- WINDOW: cantidad de SKUs con el mismo precio en la familia</span>
        <span class="fn">COUNT</span>(*) <span class="kw">OVER</span> (
            <span class="kw">PARTITION BY</span> f.PAIS, f.Formato, f.nomb_zone,
                         f.ITEM_PRIMARIO, f.PRECIO_GPI_C_IMP
        ) <span class="kw">AS</span> CANTIDAD_SKUS_MISMO_PRECIO,

        <span class="cm">-- WINDOW: precios distintos en la familia (via CTE auxiliar)</span>
        precio_dist_fam.CANTIDAD_PRECIOS_DISTINTOS

    <span class="kw">FROM</span> Familias f
    <span class="kw">LEFT JOIN</span> primarios p
        <span class="kw">ON</span> f.PAIS=p.PAIS <span class="kw">AND</span> f.Formato=p.Formato
        <span class="kw">AND</span> f.nomb_zone=p.nomb_zone <span class="kw">AND</span> f.ITEM_PRIMARIO=p.ITEM_PRIMARIO
    <span class="kw">LEFT JOIN</span> (
        <span class="kw">SELECT</span> PAIS, Formato, nomb_zone, ITEM_PRIMARIO,
               <span class="fn">COUNT</span>(<span class="kw">DISTINCT</span> PRECIO_GPI_C_IMP) <span class="kw">AS</span> CANTIDAD_PRECIOS_DISTINTOS
        <span class="kw">FROM</span> Familias <span class="kw">GROUP BY</span> 1,2,3,4
    ) precio_dist_fam
        <span class="kw">ON</span> f.PAIS=precio_dist_fam.PAIS
        <span class="kw">AND</span> f.Formato=precio_dist_fam.Formato
        <span class="kw">AND</span> f.nomb_zone=precio_dist_fam.nomb_zone
        <span class="kw">AND</span> f.ITEM_PRIMARIO=precio_dist_fam.ITEM_PRIMARIO
)
<span class="kw">SELECT</span> * <span class="kw">FROM</span> detalle_enriquecido;

<span class="cm">-- % ALINEACION (excluye packs):
-- SAFE_DIVIDE(SKUs donde mismo_tamano AND precio=primario,
--             SKUs donde mismo_tamano AND tiene_primario) * 100</span></pre>
</div>

<!-- ══ TABS (Entregables 4-7) ══════════════════════════════════════════════ -->
<div class="tabs">
  <button class="tbtn active" onclick="stab('t4',this)">4. Tabla Detalle</button>
  <button class="tbtn" onclick="stab('t5',this)">5. Resumen por Familia</button>
  <button class="tbtn" onclick="stab('t6',this)">6. Vista Packs / Gramajes</button>
  <button class="tbtn" onclick="stab('t7',this)">7. Indicadores Ejecutivos</button>
</div>

<!-- TAB 4: DETALLE -->
<div id="t4" class="tpanel active">
  <div class="info"><b>Base de detalle — SKUs desalineados de mismo tamano:</b> Muestra top 1,500 por ventas de los 43,384 totales.
  Todos tienen ESTADO_PRECIO = "Diferente al Primario", Factor=1, Ahorro=1 y SKU Primario presente.</div>
  <div class="ctrl">
    <input class="sbox" id="s4" placeholder="Buscar item, marca, descripcion..." oninput="filt('t4')"/>
    <select class="sel" id="p4" onchange="filt('t4')">
      <option value="">Todos los paises</option><option>CR</option><option>GT</option>
      <option>HN</option><option>SV</option><option>NI</option>
    </select>
    <button class="bdl" onclick="dlcsv('t4')">Descargar CSV</button>
    <span class="rc" id="rc4"></span>
  </div>
  <div class="tw"><table><thead><tr>
    <th>Pais</th><th>Formato</th><th>Zona</th><th>Cod. Familia</th>
    <th>Agrupacion</th><th>Descripcion SKU</th><th>Precio SKU</th>
    <th>SKU Primario</th><th>Precio Primario</th><th>Dif. $</th><th>Dif. %</th>
    <th>Estado Precio</th><th>SKUs mismo precio</th><th>Precios distintos</th>
    <th>Ventas</th><th>Rotaciones</th><th>Observaciones</th>
  </tr></thead><tbody id="b4"></tbody></table></div>
  <div class="pg" id="g4"></div>
</div>

<!-- TAB 5: RESUMEN FAMILIA -->
<div id="t5" class="tpanel">
  <div class="info"><b>Resumen ejecutivo por familia:</b> Top 1,500 familias con mas SKUs no alineados de los 26,857 totales con diferencias.</div>
  <div class="ctrl">
    <input class="sbox" id="s5" placeholder="Buscar marca, familia, descripcion..." oninput="filt('t5')"/>
    <select class="sel" id="p5" onchange="filt('t5')">
      <option value="">Todos los paises</option><option>CR</option><option>GT</option>
      <option>HN</option><option>SV</option><option>NI</option>
    </select>
    <button class="bdl" onclick="dlcsv('t5')">Descargar CSV</button>
    <span class="rc" id="rc5"></span>
  </div>
  <div class="tw"><table><thead><tr>
    <th>Pais</th><th>Formato</th><th>Zona</th><th>Cod. Familia</th><th>Marca</th>
    <th>Categoria</th><th>Descripcion Primario</th><th>Precio Primario</th>
    <th>Total SKUs</th><th>SKUs Validos</th><th>SKUs Pack</th>
    <th>Alineados</th><th>No Alineados</th><th>% Alineacion</th>
    <th>Precios Distintos</th><th>Ventas Familia</th>
  </tr></thead><tbody id="b5"></tbody></table></div>
  <div class="pg" id="g5"></div>
</div>

<!-- TAB 6: PACKS / GRAMAJES -->
<div id="t6" class="tpanel">
  <div class="info"><b>Vista exclusiva de Packs y Gramajes (Regla 2 — CRITICA):</b>
  Estos SKUs tienen Factor_Conversion != 1 o Ahorro_Diferencial != 1.
  El precio mayor al primario es <b>CORRECTO y ESPERADO</b> para packs.
  Solo los marcados como <b>REVISAR</b> requieren atencion (precio menor al primario en pack).
  <b>Estos registros NO afectan el % de alineacion global.</b></div>
  <div class="ctrl">
    <input class="sbox" id="s6" placeholder="Buscar item, descripcion, marca..." oninput="filt('t6')"/>
    <select class="sel" id="p6" onchange="filt('t6')">
      <option value="">Todos los paises</option><option>CR</option><option>GT</option>
      <option>HN</option><option>SV</option><option>NI</option>
    </select>
    <select class="sel" id="e6" onchange="filt('t6')">
      <option value="">Todas las evaluaciones</option>
      <option>Mayor al primario - Esperado para pack</option>
      <option>Igual al primario - Verificar factor</option>
      <option>REVISAR: Precio menor al primario</option>
    </select>
    <button class="bdl" onclick="dlcsv('t6')">Descargar CSV</button>
    <span class="rc" id="rc6"></span>
  </div>
  <div class="tw"><table><thead><tr>
    <th>Pais</th><th>Formato</th><th>Zona</th><th>Cod. Familia</th>
    <th>SKU Primario</th><th>Descripcion Primario</th><th>Precio Primario</th>
    <th>Tam. Primario</th><th>SKU Secundario</th><th>Agrupacion</th>
    <th>Descripcion Secundario</th><th>Precio Secundario</th><th>Tam. Secundario</th>
    <th>Factor Conv.</th><th>% Ahorro</th><th>Dif. Abs.</th><th>Dif. %</th>
    <th>Evaluacion</th><th>Ventas</th>
  </tr></thead><tbody id="b6"></tbody></table></div>
  <div class="pg" id="g6"></div>
</div>

<!-- TAB 7: DIRECTORES -->
<div id="t7" class="tpanel">
  <div class="g2" style="margin-bottom:18px">
    <div class="card">
      <div class="sec-title" style="margin-bottom:12px">Alineacion por Pais (SKUs mismo tamano)</div>
      <div style="height:260px;position:relative"><canvas id="ch1"></canvas></div>
    </div>
    <div class="card">
      <div class="sec-title" style="margin-bottom:12px">Distribucion: Alineados vs No Alineados (Dona)</div>
      <div style="height:260px;position:relative"><canvas id="ch2"></canvas></div>
    </div>
  </div>
  <div class="card" style="margin-bottom:14px">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
      <span class="sec-title" style="margin:0">Resumen por Pais — Vista para Directores</span>
      <button class="bdl" onclick="dlcsv('t7')">Descargar CSV</button>
    </div>
    <div class="tw"><table id="tdir">
      <thead><tr>
        <th>Pais</th><th>Familias</th><th>Total SKUs</th><th>SKUs Validos</th>
        <th>Pack/Gramaje</th><th>Alineados</th><th>No Alineados</th>
        <th>Fam. 100% Alineadas</th><th>Fam. con Diferencias</th>
        <th style="min-width:150px">% Alineacion</th>
      </tr></thead>
      <tbody id="bdir"></tbody>
    </table></div>
  </div>
  <!-- Global KPIs para directores -->
  <div class="g4">
    <div class="card" style="text-align:center">
      <div class="kpi-v" style="color:#0053e2;font-size:1.5rem">{g['pct_global']:.2f}%</div>
      <div class="kpi-l">Alineacion Global CAM</div>
    </div>
    <div class="card" style="text-align:center">
      <div class="kpi-v" style="color:#166534;font-size:1.5rem">{g['familias_100_alineadas']:,}</div>
      <div class="kpi-l">Familias 100% Alineadas</div>
    </div>
    <div class="card" style="text-align:center">
      <div class="kpi-v" style="color:#995213;font-size:1.5rem">{g['familias_con_diferencias']:,}</div>
      <div class="kpi-l">Familias con Diferencias</div>
    </div>
    <div class="card" style="text-align:center">
      <div class="kpi-v" style="color:#7c3aed;font-size:1.5rem">{g['skus_pack_gramaje']:,}</div>
      <div class="kpi-l">SKUs Pack/Gramaje (excluidos)</div>
    </div>
  </div>
</div>

<!-- ══ 8. OBSERVACIONES ═════════════════════════════════════════════════════ -->
<div class="sec card">
  <div class="sec-title"><span class="sec-num">8</span> Observaciones Automaticas</div>
  {obs_html}
</div>

<!-- ══ 9. RECOMENDACIONES PRICING ══════════════════════════════════════════ -->
<div class="sec card">
  <div class="sec-title"><span class="sec-num">9</span> Recomendaciones para el Equipo de Pricing</div>
  <div class="g2">
    <div>
      <div class="recom-card"><div class="recom-title">Prioridad 1 — Guatemala (92.54%)</div>
      <div class="recom-body">Es el pais con menor alineacion. Con 8,448 SKUs desalineados en 4,942 familias, es el mayor foco de oportunidad. Revisar primero las familias de Bebidas Carbonatadas (Coca-Cola 355ML aparece con hasta 6 precios distintos en la misma familia-formato-zona).</div></div>
      <div class="recom-card"><div class="recom-title">Prioridad 2 — Honduras (92.96%)</div>
      <div class="recom-body">5,541 SKUs no alineados. Se recomienda validar si las diferencias estan correlacionadas con zonas especificas (A-Roja vs otras), lo que indicaria una politica de precios diferenciada por zona sin reflejo en el canasto.</div></div>
      <div class="recom-card"><div class="recom-title">Packs con precio MENOR al primario</div>
      <div class="recom-body">La vista de Packs/Gramajes revela items con EVALUACION = "REVISAR". Un pack que cuesta menos que la unidad individual es una inconsistencia de precio que puede generar perdida de margen o confusion al consumidor. Requiere correccion urgente.</div></div>
    </div>
    <div>
      <div class="recom-card"><div class="recom-title">Homologacion sistematica por familia</div>
      <div class="recom-body">Para familias con PCT_ALINEACION &lt; 50% y VENTAS altas, el equipo de Pricing debe revisar si la diferencia es intencional (estrategia diferenciada) o un error de carga. El proceso puede automatizarse usando la tabla de resumen como insumo semanal.</div></div>
      <div class="recom-card"><div class="recom-title">Familias con mas de 3 precios distintos</div>
      <div class="recom-body">Estas familias tienen el mayor potencial de optimizacion. Un precio unico por familia (del mismo tamano) simplifica la comunicacion al consumidor y reduce el riesgo de quejas por diferencias en anaquel.</div></div>
      <div class="recom-card"><div class="recom-title">Nicaragua como benchmark</div>
      <div class="recom-body">Con 94.82% de alineacion y el surtido mas pequeno, Nicaragua puede servir como modelo de gestion. Analizar que practicas de gestion del canasto tiene NI que no aplican en GT o HN.</div></div>
    </div>
  </div>
</div>

<!-- ══ 10. RECOMENDACIONES SQL ══════════════════════════════════════════════ -->
<div class="sec card">
  <div class="sec-title"><span class="sec-num">10</span> Recomendaciones para Optimizar el SQL en BigQuery</div>
  <div class="g2">
    <div class="recom-card"><div class="recom-title">Particionado de la tabla Insumos</div>
    <div class="recom-body">La tabla <code>prcng_info_cam_insumos_diario</code> no tiene particion por EXTRACT_DATE. Cada ejecucion escanea ~80-118 GB. Crear particion diaria reduciria el costo a &lt;5 GB por query. Solicitar al equipo de datos.</div></div>
    <div class="recom-card"><div class="recom-title">Materializar la CTE de Familias</div>
    <div class="recom-body">La CTE base "Familias" se usa multiples veces. Materializarla como tabla temporal o tabla de staging reduce el re-escaneo de la tabla de Insumos.</div></div>
    <div class="recom-card"><div class="recom-title">COUNT DISTINCT con Window Functions</div>
    <div class="recom-body">BigQuery no soporta COUNT(DISTINCT ...) dentro de OVER(). Usar una CTE auxiliar de GROUP BY y hacer JOIN posterior (ya implementado en el SQL documentado).</div></div>
    <div class="recom-card"><div class="recom-title">Evitar SELECT * en produccion</div>
    <div class="recom-body">El SELECT * del canasto (103 columnas) incrementa el costo de transferencia. En produccion, seleccionar solo las columnas necesarias para el analisis.</div></div>
    <div class="recom-card"><div class="recom-title">Scheduled Query semanal</div>
    <div class="recom-body">La logica es completamente parametrizable por fecha. Se puede configurar como Scheduled Query en BQ con parametro @fecha_objetivo y escritura automatica a una tabla de resultados para seguimiento historico.</div></div>
    <div class="recom-card"><div class="recom-title">Clustering por PAIS + ITEM_PRIMARIO</div>
    <div class="recom-body">Si la tabla de resultados se materializa, aplicar clustering por PAIS y ITEM_PRIMARIO mejora drasticamente el rendimiento de las consultas de drill-down por familia.</div></div>
  </div>
</div>

<div class="nota">
  <b>Notas metodologicas:</b><br/>
  <b>SKU Primario:</b> ITEM = ITEM_PRIMARIO (campo AGRUPACION = 'PRIMARIO' en el canasto) &nbsp;|&nbsp;
  <b>Mismo tamano:</b> FACTOR_DE_CONVERSION = 1 AND AHORRO_DIFERENCIAL = 1 &nbsp;|&nbsp;
  <b>% Alineacion:</b> SKUs alineados (mismo tamano + tiene primario) / Total SKUs validos (mismo tamano + tiene primario) x 100 &nbsp;|&nbsp;
  <b>Fuente:</b> prcng_info_cam_insumos_diario + prcng_info_cam_a0g0dn3_canasto_universal_extendido &nbsp;|&nbsp;
  <b>Fecha:</b> 2026-07-04
</div>
</div>

<script>
// ── DATOS ────────────────────────────────────────────────────────────────────
const D4 = {j_det};
const D5 = {j_fam};
const D6 = {j_pack};
const D7 = {j_dir};

// ── ESTADO TABLAS ────────────────────────────────────────────────────────────
const PAGE = 50;
const ST = {{
  t4: {{data:D4, filtered:D4.slice(), page:0}},
  t5: {{data:D5, filtered:D5.slice(), page:0}},
  t6: {{data:D6, filtered:D6.slice(), page:0}},
  t7: {{data:D7, filtered:D7.slice(), page:0}},
}};

// ── HELPERS ──────────────────────────────────────────────────────────────────
function e(v){{
  if(v===null||v===undefined||v==='') return '\u2014';
  return String(v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}}
function n(v,d){{
  if(v===null||v===undefined||v==='') return '\u2014';
  var x=parseFloat(v); if(isNaN(x)) return e(v);
  return x.toLocaleString('es',{{minimumFractionDigits:d||0,maximumFractionDigits:d||0}});
}}
function pct(v){{
  if(v===null||v===undefined||v==='') return '<span class="b b-z">N/D</span>';
  var x=parseFloat(v);
  var c=x>=94?'b-g':x>=85?'b-y':'b-r';
  return '<span class="b '+c+'">'+x.toFixed(1)+'%</span>';
}}
function agb(v){{
  if(!v) return '<span class="b b-z">\u2014</span>';
  return String(v).toUpperCase()==='PRIMARIO'
    ? '<span class="b b-b">PRIMARIO</span>'
    : '<span class="b b-z">SECUNDARIO</span>';
}}
function evb(v){{
  if(!v) return '<span class="b b-z">\u2014</span>';
  var s=String(v);
  if(s.indexOf('REVISAR')>=0) return '<span class="b b-r">'+e(s)+'</span>';
  if(s.indexOf('Mayor')>=0||s.indexOf('Esperado')>=0) return '<span class="b b-y">'+e(s)+'</span>';
  if(s.indexOf('Igual')>=0) return '<span class="b b-g">'+e(s)+'</span>';
  return '<span class="b b-z">'+e(s)+'</span>';
}}
function estb(v){{
  if(!v) return '<span class="b b-z">\u2014</span>';
  var s=String(v);
  if(s.indexOf('Diferente')>=0) return '<span class="b b-r">Diferente al Primario</span>';
  if(s.indexOf('Igual')>=0) return '<span class="b b-g">Igual al Primario</span>';
  if(s.indexOf('pack')>=0||s.indexOf('tamano')>=0) return '<span class="b b-p">Pack/Gramaje</span>';
  return '<span class="b b-z">'+e(s)+'</span>';
}}

// ── RENDER ROWS ──────────────────────────────────────────────────────────────
function r4(r){{
  var dif=r.DIFERENCIA_PRECIO!==null&&r.DIFERENCIA_PRECIO!==undefined?parseFloat(r.DIFERENCIA_PRECIO):null;
  var difStyle=dif===null?'':(dif>0?'style="color:#166534"':'style="color:#991b1b"');
  return '<tr>'
    +'<td><b>'+e(r.PAIS)+'</b></td><td>'+e(r.Formato)+'</td><td>'+e(r.ZONA)+'</td>'
    +'<td style="font-family:monospace">'+e(r.CODIGO_FAMILIA)+'</td>'
    +'<td>'+agb(r.AGRUPACION)+'</td>'
    +'<td style="max-width:180px;overflow:hidden;text-overflow:ellipsis" title="'+e(r.SIGNING_DESC)+'">'+e(r.SIGNING_DESC)+'</td>'
    +'<td class="tr blue">'+n(r.PRECIO_GPI_C_IMP,2)+'</td>'
    +'<td style="font-family:monospace;font-size:.68rem">'+e(r.SKU_PRIMARIO)+'</td>'
    +'<td class="tr">'+n(r.PRECIO_PRIMARIO,2)+'</td>'
    +'<td class="tr" '+difStyle+'>'+n(r.DIFERENCIA_PRECIO,2)+'</td>'
    +'<td class="tr" '+difStyle+'>'+n(r.DIFERENCIA_PCT,1)+'%</td>'
    +'<td>'+estb(r.ESTADO_PRECIO)+'</td>'
    +'<td class="tr">'+n(r.CANTIDAD_SKUS_MISMO_PRECIO)+'</td>'
    +'<td class="tr">'+n(r.CANTIDAD_PRECIOS_DISTINTOS)+'</td>'
    +'<td class="tr">'+n(r.Ventas,0)+'</td>'
    +'<td class="tr">'+n(r.Rotaciones,0)+'</td>'
    +'<td style="font-size:.68rem;max-width:160px;overflow:hidden;text-overflow:ellipsis">'+e(r.OBSERVACIONES)+'</td>'
    +'</tr>';
}}

function r5(r){{
  return '<tr>'
    +'<td><b>'+e(r.PAIS)+'</b></td><td>'+e(r.Formato)+'</td><td>'+e(r.ZONA)+'</td>'
    +'<td style="font-family:monospace">'+e(r.CODIGO_FAMILIA)+'</td>'
    +'<td><b>'+e(r.MARCA)+'</b></td>'
    +'<td style="font-size:.68rem">'+e(r.CATEGORIA)+'</td>'
    +'<td style="max-width:180px;overflow:hidden;text-overflow:ellipsis" title="'+e(r.DESC_PRIMARIO)+'">'+e(r.DESC_PRIMARIO)+'</td>'
    +'<td class="tr">'+n(r.PRECIO_PRIMARIO,2)+'</td>'
    +'<td class="tr">'+n(r.TOTAL_SKUS)+'</td>'
    +'<td class="tr">'+n(r.SKUS_VALIDOS)+'</td>'
    +'<td class="tr" style="color:#7c3aed">'+n(r.SKUS_PACK_GRAMAJE)+'</td>'
    +'<td class="tr green">'+n(r.SKUS_ALINEADOS)+'</td>'
    +'<td class="tr red">'+n(r.SKUS_NO_ALINEADOS)+'</td>'
    +'<td>'+pct(r.PCT_ALINEACION)+'</td>'
    +'<td class="tr">'+n(r.PRECIOS_DISTINTOS)+'</td>'
    +'<td class="tr">'+n(r.VENTAS_FAMILIA,0)+'</td>'
    +'</tr>';
}}

function r6(r){{
  return '<tr>'
    +'<td><b>'+e(r.PAIS)+'</b></td><td>'+e(r.Formato)+'</td><td>'+e(r.ZONA)+'</td>'
    +'<td style="font-family:monospace">'+e(r.CODIGO_FAMILIA)+'</td>'
    +'<td style="font-family:monospace;font-size:.68rem">'+e(r.SKU_PRIMARIO)+'</td>'
    +'<td style="max-width:160px;overflow:hidden;text-overflow:ellipsis" title="'+e(r.DESC_PRIMARIO)+'">'+e(r.DESC_PRIMARIO)+'</td>'
    +'<td class="tr">'+n(r.PRECIO_PRIMARIO,2)+'</td>'
    +'<td class="tr">'+n(r.TAMANO_PRIMARIO,0)+' '+e(r.MEDIDA_PRIMARIO)+'</td>'
    +'<td style="font-family:monospace;font-size:.68rem">'+e(r.SKU_SECUNDARIO)+'</td>'
    +'<td>'+agb(r.AGRUPACION)+'</td>'
    +'<td style="max-width:180px;overflow:hidden;text-overflow:ellipsis" title="'+e(r.DESC_SECUNDARIO)+'">'+e(r.DESC_SECUNDARIO)+'</td>'
    +'<td class="tr blue">'+n(r.PRECIO_SECUNDARIO,2)+'</td>'
    +'<td class="tr">'+n(r.TAMANO_SECUNDARIO,0)+' '+e(r.MEDIDA_SECUNDARIO)+'</td>'
    +'<td class="tr" style="color:#7c3aed;font-weight:700">'+n(r.FACTOR_DE_CONVERSION,2)+'</td>'
    +'<td class="tr">'+n(r.AHORRO_DIFERENCIAL,2)+'</td>'
    +'<td class="tr">'+n(r.DIFERENCIA_ABSOLUTA,2)+'</td>'
    +'<td class="tr">'+n(r.DIFERENCIA_PCT,1)+'%</td>'
    +'<td>'+evb(r.EVALUACION)+'</td>'
    +'<td class="tr">'+n(r.Ventas,0)+'</td>'
    +'</tr>';
}}

// ── TABLA ENGINE ─────────────────────────────────────────────────────────────
var RFNS = {{t4:r4,t5:r5,t6:r6}};

function render(key){{
  var s=ST[key], rfn=RFNS[key];
  if(!rfn) return;
  var bid='b'+key.substring(1);
  var start=s.page*PAGE, slice=s.filtered.slice(start,start+PAGE);
  document.getElementById(bid).innerHTML=slice.map(rfn).join('');
  buildPg(key);
  var rc=document.getElementById('rc'+key.substring(1));
  if(rc) rc.textContent='Mostrando '+(start+1)+'\u2013'+Math.min(start+PAGE,s.filtered.length)
    +' de '+s.filtered.length.toLocaleString('es')+' registros';
}}

function buildPg(key){{
  var s=ST[key], pages=Math.ceil(s.filtered.length/PAGE), cur=s.page;
  var el=document.getElementById('g'+key.substring(1));
  if(!el) return;
  var shown=[],h='';
  [0,cur-1,cur,cur+1,pages-1].forEach(function(p){{if(p>=0&&p<pages&&shown.indexOf(p)<0)shown.push(p);}});
  shown.sort(function(a,b){{return a-b;}});
  var last=-1;
  shown.forEach(function(p){{
    if(last>=0&&p-last>1)h+='<span style="color:#94a3b8">&hellip;</span>';
    h+='<button class="'+(cur===p?'active':'')+'" onclick="go(\''+key+'\','+p+')">'+(p+1)+'</button>';
    last=p;
  }});
  h+='<span class="pgi">Pag '+(cur+1)+'/'+pages+'</span>';
  el.innerHTML=h;
}}

function go(key,p){{ST[key].page=p;render(key);}}

function filt(key){{
  var n=key.substring(1);
  var term=(document.getElementById('s'+n)||{{}}).value||'';
  var pais=(document.getElementById('p'+n)||{{}}).value||'';
  var evalF=key==='t6'?((document.getElementById('e6')||{{}}).value||''):'';
  term=term.toLowerCase();
  ST[key].filtered=ST[key].data.filter(function(r){{
    var str=JSON.stringify(r).toLowerCase();
    return(!term||str.indexOf(term)>=0)&&(!pais||r.PAIS===pais)&&(!evalF||r.EVALUACION===evalF);
  }});
  ST[key].page=0; render(key);
}}

// ── DIRECTOR TABLE ───────────────────────────────────────────────────────────
function renderDir(){{
  var pnames={{CR:'Costa Rica',GT:'Guatemala',HN:'Honduras',SV:'El Salvador',NI:'Nicaragua'}};
  var rows=D7.sort ? D7.slice().sort(function(a,b){{return a.PCT_ALINEACION-b.PCT_ALINEACION;}}) : D7;
  document.getElementById('bdir').innerHTML=rows.map(function(r){{
    var pct2=parseFloat(r.PCT_ALINEACION)||0;
    var bc=pct2>=94?'#2a8703':pct2>=92?'#e6a817':'#ea1100';
    var bar='<div class="bw"><div class="bf" style="width:'+pct2+'%;background:'+bc+'"></div>'
            +'<div class="bl">'+pct2.toFixed(2)+'%</div></div>';
    return '<tr>'
      +'<td><b>'+(pnames[r.PAIS]||r.PAIS)+'</b></td>'
      +'<td class="tr">'+n(r.TOTAL_FAMILIAS)+'</td>'
      +'<td class="tr">'+n(r.TOTAL_SKUS)+'</td>'
      +'<td class="tr">'+n(r.SKUS_VALIDOS)+'</td>'
      +'<td class="tr" style="color:#7c3aed">'+n(r.SKUS_PACK_GRAMAJE)+'</td>'
      +'<td class="tr green">'+n(r.SKUS_ALINEADOS)+'</td>'
      +'<td class="tr red">'+n(r.SKUS_NO_ALINEADOS)+'</td>'
      +'<td class="tr">'+n(r.FAMILIAS_100_ALINEADAS)+'</td>'
      +'<td class="tr">'+n(r.FAMILIAS_CON_DIFERENCIAS)+'</td>'
      +'<td>'+bar+'</td>'
      +'</tr>';
  }}).join('');
}}

// ── CHARTS ───────────────────────────────────────────────────────────────────
(function(){{
  var labels={c_labels}, ali={c_ali}, nali={c_nali}, pcts={c_pcts};
  // Chart 1: barras apiladas
  new Chart(document.getElementById('ch1').getContext('2d'),{{
    type:'bar',
    data:{{labels:labels,datasets:[
      {{label:'Alineados',data:ali,backgroundColor:'#2a8703',borderRadius:4}},
      {{label:'No Alineados',data:nali,backgroundColor:'#ea1100',borderRadius:4}}
    ]}},
    options:{{responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{position:'top'}},
        tooltip:{{callbacks:{{afterBody:function(i){{return 'Alineacion: '+pcts[i[0].dataIndex]+'%';}}}}}}
      }},
      scales:{{x:{{stacked:true}},y:{{stacked:true,ticks:{{callback:function(v){{return v.toLocaleString('es');}}}}}}}}
    }}
  }});
  // Chart 2: dona global
  new Chart(document.getElementById('ch2').getContext('2d'),{{
    type:'doughnut',
    data:{{
      labels:['SKUs Alineados','SKUs No Alineados','Packs/Gramajes'],
      datasets:[{{data:[{g['skus_alineados']},{g['skus_no_alineados']},{g['skus_pack_gramaje']}],
        backgroundColor:['#2a8703','#ea1100','#7c3aed'],borderWidth:2,borderColor:'#fff'}}]
    }},
    options:{{responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{position:'bottom'}},
        tooltip:{{callbacks:{{label:function(ctx){{
          return ctx.label+': '+ctx.parsed.toLocaleString('es')+' SKUs';
        }}}}}}
      }}
    }}
  }});
}})();

// ── CSV DOWNLOAD ─────────────────────────────────────────────────────────────
function dlcsv(key){{
  var map={{t4:'detalle_desalineados',t5:'resumen_familias',t6:'packs_gramajes',t7:'director_pais'}};
  var rows=key==='t7'?D7:ST[key].filtered;
  if(!rows||!rows.length)return;
  var keys=Object.keys(rows[0]);
  function esc2(v){{var s=(v===null||v===undefined)?'':String(v);return(s.indexOf(',')>=0||s.indexOf('"')>=0||s.indexOf('\\n')>=0)?'"'+s.replace(/"/g,'""')+'"':s;}}
  var csv=[keys.join(',')].concat(rows.map(function(r){{return keys.map(function(k){{return esc2(r[k]);}}).join(',');}})).join('\\n');
  var blob=new Blob(['\ufeff'+csv],{{type:'text/csv;charset=utf-8;'}});
  var a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=map[key]+'.csv';a.click();
}}

// ── TABS ─────────────────────────────────────────────────────────────────────
function stab(id,btn){{
  document.querySelectorAll('.tpanel').forEach(function(p){{p.classList.remove('active');}});
  document.querySelectorAll('.tbtn').forEach(function(b){{b.classList.remove('active');}});
  document.getElementById(id).classList.add('active');btn.classList.add('active');
}}

// ── INIT ─────────────────────────────────────────────────────────────────────
render('t4'); render('t5'); render('t6'); renderDir();
</script>
</body></html>"""


# ── MAIN ───────────────────────────────────────────────────────────────────
def main():
    print("Cargando CSVs...")
    director, familias, packs, detalle = load()
    print(f"  Director : {len(director)} paises")
    print(f"  Familias : {len(familias):,} filas")
    print(f"  Packs    : {len(packs):,} filas")
    print(f"  Detalle  : {len(detalle):,} filas")

    obs = observaciones(director, familias, packs, detalle)
    print(f"  Obs      : {len(obs)} observaciones")

    out = os.path.join(BASE, "reporte_familias_precios.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html(director, familias, packs, detalle, obs))

    kb = os.path.getsize(out) / 1024
    print(f"\nReporte: {out}")
    print(f"  Tamano : {kb:.0f} KB")
    webbrowser.open(f"file:///{out.replace(os.sep, '/')}")
    print("  Abierto en navegador.")

if __name__ == "__main__":
    main()

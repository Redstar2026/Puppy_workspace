"""
Pricing Family Alignment Analysis
Store 4076 | SW 22 | 2026 | CAT 6894, 6987
Family Key v2: COST_UNIT + MARCA_DESC + N_MARCA + PAIS + N_FINELINE + SELL_QTY
Consultant: Rintyn (Code Puppy) -- Senior Data Analytics & Pricing
"""

import csv
import json
from collections import defaultdict
from datetime import datetime


# -----------------------------------------------------------------
# HELPERS
# -----------------------------------------------------------------

def safe_float(val, default=None):
    if val is None or str(val).strip() in ('', 'None', 'null'):
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def fmt_cur(val):
    if val is None:
        return '-'
    return f"c/{val:,.2f}"


def fmt_pct(val):
    if val is None:
        return '-'
    return f"{val:.1f}%"


# -----------------------------------------------------------------
# STEP 0: LOAD DATA
# -----------------------------------------------------------------

INPUT_CSV   = 'prcng_info_store4076_sw22_cat6894_6987.csv'
DETAIL_CSV  = 'pricing_detail_v2_6894_6987.csv'
SUMMARY_CSV = 'pricing_summary_v2_6894_6987.csv'
REPORT_HTML = 'pricing_families_report_v2_6894_6987.html'

rows = []
with open(INPUT_CSV, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    original_fields = list(reader.fieldnames)
    for row in reader:
        rows.append(dict(row))

print(f"[LOAD] {len(rows)} rows loaded | {len(original_fields)} original columns")

cat_dist = defaultdict(int)
for r in rows:
    cat_dist[r.get('CATEGORY_NBR', '?')] += 1
for k, v in sorted(cat_dist.items()):
    print(f"  Category {k}: {v} rows")


# -----------------------------------------------------------------
# STEP 1: BUILD FAMILY KEY -> CODIGO_FAMILIA
# Family key v2 = 6 fields:
#   COST_UNIT + MARCA_DESC + N_MARCA + PAIS + N_FINELINE + SELL_QTY
# Scoped within: (PAIS, FORMATO, NOMB_ZONE)
# -----------------------------------------------------------------

family_registry = {}
scope_counters  = defaultdict(int)

for row in rows:
    scope = (row['PAIS'], row['FORMATO'], row['NOMB_ZONE'])
    fam_components = (
        row['COST_UNIT'],
        row['MARCA_DESC'],
        row['N_MARCA'],
        row['PAIS'],
        row['N_FINELINE'],
        row['SELL_QTY'],        # <-- campo v2
    )
    full_key = scope + fam_components

    if full_key not in family_registry:
        scope_counters[scope] += 1
        seq      = scope_counters[scope]
        cod_pais = row['COD_PAIS']
        cod_fmt  = row['COD_FORMATO']
        cod_zona = row['COD_ZONA']
        codigo   = f"FAM_{cod_pais}_{cod_fmt}_{cod_zona}_{seq:04d}"
        family_registry[full_key] = codigo

for row in rows:
    scope = (row['PAIS'], row['FORMATO'], row['NOMB_ZONE'])
    fam_components = (
        row['COST_UNIT'],
        row['MARCA_DESC'],
        row['N_MARCA'],
        row['PAIS'],
        row['N_FINELINE'],
        row['SELL_QTY'],
    )
    row['CODIGO_FAMILIA'] = family_registry[scope + fam_components]

total_families  = len(family_registry)
fam_item_count  = defaultdict(int)
for r in rows:
    fam_item_count[r['CODIGO_FAMILIA']] += 1
multi_fam_count = sum(1 for v in fam_item_count.values() if v > 1)

print(f"[STEP 1] Families built: {total_families} | Multi-item families: {multi_fam_count}")
print(f"         (v1 had 329 families; v2 with SELL_QTY has {total_families})")


# -----------------------------------------------------------------
# STEP 2: IDENTIFY PRIMARY (AGRUPACION)
# Primary = highest VENTAS within (PAIS, FORMATO, ZONA, CODIGO_FAMILIA)
# Tiebreaker: lowest ITEM number (deterministic)
# -----------------------------------------------------------------

groups = defaultdict(list)
for row in rows:
    gk = (row['PAIS'], row['FORMATO'], row['NOMB_ZONE'], row['CODIGO_FAMILIA'])
    groups[gk].append(row)

for gk, grp in groups.items():
    sorted_grp = sorted(
        grp,
        key=lambda r: (-safe_float(r['VENTAS'], 0), int(r['ITEM'] or 0))
    )
    sorted_grp[0]['AGRUPACION'] = 'PRIMARIO'
    primary_price  = safe_float(sorted_grp[0]['PRECIO_GPI_C_IMP'])
    primary_ventas = safe_float(sorted_grp[0]['VENTAS'], 0)
    primary_item   = sorted_grp[0]['ITEM']
    primary_desc   = sorted_grp[0]['DESCRIPCION']

    for r in sorted_grp[1:]:
        r['AGRUPACION'] = 'SECUNDARIO'

    for r in grp:
        r['PRECIO_PRIMARIO'] = str(primary_price) if primary_price is not None else ''
        r['ITEM_PRIMARIO']   = primary_item
        r['DESC_PRIMARIO']   = primary_desc
        r['VENTAS_PRIMARIO'] = str(primary_ventas)

        price = safe_float(r['PRECIO_GPI_C_IMP'])
        if primary_price is not None and price is not None:
            diff = round(price - primary_price, 4)
            r['DIFERENCIA_PRECIO'] = str(diff)
            r['ESTADO_PRECIO'] = (
                'Igual al Primario' if abs(diff) < 0.01 else 'Diferente al Primario'
            )
        elif price is None:
            r['ESTADO_PRECIO']     = 'Sin Precio'
            r['DIFERENCIA_PRECIO'] = ''
        else:
            r['ESTADO_PRECIO']     = 'Sin Precio Primario'
            r['DIFERENCIA_PRECIO'] = ''

print("[STEP 2] AGRUPACION assigned (PRIMARIO / SECUNDARIO)")


# -----------------------------------------------------------------
# STEP 3 + 4: ESTADO_PRECIO already set | ROTACION field
# -----------------------------------------------------------------

for row in rows:
    row['ROTACION'] = row.get('ROTACIONES', '')

print("[STEP 3/4] ESTADO_PRECIO + ROTACION populated")


# -----------------------------------------------------------------
# SUMMARY TABLE
# -----------------------------------------------------------------

summary_by_family = {}

for gk, grp in groups.items():
    pais, formato, zona, codigo_fam = gk

    primary_rows = [r for r in grp if r['AGRUPACION'] == 'PRIMARIO']
    primary      = primary_rows[0] if primary_rows else grp[0]

    primary_price  = safe_float(primary['PRECIO_GPI_C_IMP'])
    primary_item   = primary['ITEM']
    primary_desc   = primary['DESCRIPCION']
    primary_ventas = safe_float(primary['VENTAS'], 0)
    primary_rot    = safe_float(primary['ROTACIONES'])
    primary_sqty   = primary.get('SELL_QTY', '')

    precios = [
        safe_float(r['PRECIO_GPI_C_IMP'])
        for r in grp
        if safe_float(r['PRECIO_GPI_C_IMP']) is not None
    ]
    n_precios_distintos = len(set(precios))

    iguales    = sum(1 for r in grp if r.get('ESTADO_PRECIO') == 'Igual al Primario')
    diferentes = sum(1 for r in grp if r.get('ESTADO_PRECIO') == 'Diferente al Primario')
    sin_precio = sum(1 for r in grp if r.get('ESTADO_PRECIO') in ('Sin Precio', 'Sin Precio Primario'))
    total_skus = len(grp)
    pct_alineacion = (iguales / total_skus * 100) if total_skus > 0 else 0

    price_count = defaultdict(list)
    for r in grp:
        p = safe_float(r['PRECIO_GPI_C_IMP'])
        if p is not None:
            price_count[p].append(r['ITEM'])

    obs = []
    if total_skus == 1:
        obs.append("Familia con un solo articulo")
    if primary_ventas == 0:
        obs.append("Primario sin ventas registradas")
    if sin_precio > 0:
        obs.append(f"{sin_precio} articulo(s) sin precio")
    if n_precios_distintos > 2:
        obs.append(f"Alta dispersion: {n_precios_distintos} precios distintos")
    if diferentes > 0 and total_skus > 1:
        obs.append(f"{diferentes}/{total_skus} SKUs desalineados")

    summary_by_family[gk] = {
        'PAIS':              pais,
        'FORMATO':           formato,
        'ZONA':              zona,
        'CODIGO_FAMILIA':    codigo_fam,
        'MARCA':             primary.get('MARCA_DESC', ''),
        'FINELINE':          primary.get('FINELINE_DESC', ''),
        'CATEGORY_NBR':      primary.get('CATEGORY_NBR', ''),
        'CATEGORY_DESC':     primary.get('CATEGORY_DESC', ''),
        'N_FINELINE':        primary.get('N_FINELINE', ''),
        'N_MARCA':           primary.get('N_MARCA', ''),
        'COST_UNIT':         safe_float(primary.get('COST_UNIT')),
        'SELL_QTY':          primary_sqty,
        'TOTAL_SKUS':        total_skus,
        'ITEM_PRIMARIO':     primary_item,
        'DESC_PRIMARIO':     primary_desc,
        'VENTAS_PRIMARIO':   primary_ventas,
        'PRECIO_PRIMARIO':   primary_price,
        'ROTACION_PRIMARIO': primary_rot,
        'N_PRECIOS_DISTINTOS':   n_precios_distintos,
        'SKUS_IGUAL_PRECIO':     iguales,
        'SKUS_DIFERENTE_PRECIO': diferentes,
        'SKUS_SIN_PRECIO':       sin_precio,
        'PCT_ALINEACION':        pct_alineacion,
        'PRICE_CLUSTERS':    {str(k): v for k, v in price_count.items()},
        'OBSERVACIONES':     ' | '.join(obs) if obs else 'OK',
    }

print(f"[SUMMARY] {len(summary_by_family)} family summaries built")


# -----------------------------------------------------------------
# EXPORT DETAIL CSV
# -----------------------------------------------------------------

new_cols = [
    'CODIGO_FAMILIA', 'AGRUPACION', 'ITEM_PRIMARIO', 'DESC_PRIMARIO',
    'VENTAS_PRIMARIO', 'PRECIO_PRIMARIO', 'ESTADO_PRECIO',
    'DIFERENCIA_PRECIO', 'ROTACION',
]
all_cols = original_fields + new_cols

with open(DETAIL_CSV, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=all_cols, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(rows)

print(f"[EXPORT] {DETAIL_CSV} written")


# -----------------------------------------------------------------
# EXPORT SUMMARY CSV
# -----------------------------------------------------------------

summary_cols = [
    'PAIS', 'FORMATO', 'ZONA', 'CODIGO_FAMILIA', 'CATEGORY_NBR', 'CATEGORY_DESC',
    'MARCA', 'FINELINE', 'N_FINELINE', 'N_MARCA', 'COST_UNIT', 'SELL_QTY',
    'TOTAL_SKUS', 'ITEM_PRIMARIO', 'DESC_PRIMARIO', 'VENTAS_PRIMARIO',
    'PRECIO_PRIMARIO', 'ROTACION_PRIMARIO', 'N_PRECIOS_DISTINTOS',
    'SKUS_IGUAL_PRECIO', 'SKUS_DIFERENTE_PRECIO', 'SKUS_SIN_PRECIO',
    'PCT_ALINEACION', 'OBSERVACIONES',
]

with open(SUMMARY_CSV, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=summary_cols, extrasaction='ignore')
    writer.writeheader()
    for s in summary_by_family.values():
        writer.writerow(s)

print(f"[EXPORT] {SUMMARY_CSV} written")


# -----------------------------------------------------------------
# GLOBAL STATS
# -----------------------------------------------------------------

total_skus_global  = len(rows)
total_fam          = len(summary_by_family)
fam_multi          = sum(1 for s in summary_by_family.values() if s['TOTAL_SKUS'] > 1)
fam_single         = total_fam - fam_multi
total_desalineados = sum(s['SKUS_DIFERENTE_PRECIO'] for s in summary_by_family.values())
total_iguales      = sum(s['SKUS_IGUAL_PRECIO'] for s in summary_by_family.values())
pct_global         = (total_iguales / total_skus_global * 100) if total_skus_global else 0
fam_perfectas      = sum(
    1 for s in summary_by_family.values()
    if s['SKUS_DIFERENTE_PRECIO'] == 0 and s['TOTAL_SKUS'] > 1
)
fam_criticas = sorted(
    [s for s in summary_by_family.values() if s['SKUS_DIFERENTE_PRECIO'] > 0],
    key=lambda x: (-x['SKUS_DIFERENTE_PRECIO'], -(x['VENTAS_PRIMARIO'] or 0))
)

skus_sin_ventas = sum(1 for r in rows if not r.get('VENTAS'))
cat_6894_rows   = [r for r in rows if r.get('CATEGORY_NBR') == '6894']
cat_6987_rows   = [r for r in rows if r.get('CATEGORY_NBR') == '6987']

print(f"\n{'='*60}")
print("GLOBAL STATS SUMMARY (Family Key v2 + SELL_QTY)")
print(f"{'='*60}")
print(f"  Total SKUs           : {total_skus_global}")
print(f"    Cat 6894 (Beer)    : {len(cat_6894_rows)}")
print(f"    Cat 6987 (Soda)    : {len(cat_6987_rows)}")
print(f"  Total Familias       : {total_fam}")
print(f"  Fam. Multi-SKU       : {fam_multi}")
print(f"  Fam. Single-SKU      : {fam_single}")
print(f"  SKUs Alineados       : {total_iguales}")
print(f"  SKUs Desalineados    : {total_desalineados}")
print(f"  % Alineacion Global  : {pct_global:.1f}%")
print(f"  Fam. 100% alineadas  : {fam_perfectas}")
print(f"  Fam. con desvios     : {len(fam_criticas)}")
print(f"  SKUs sin ventas      : {skus_sin_ventas}")


# -----------------------------------------------------------------
# HTML REPORT
# -----------------------------------------------------------------

detail_json  = json.dumps(rows, ensure_ascii=False, default=str)
summary_list = list(summary_by_family.values())
summary_json = json.dumps(summary_list, ensure_ascii=False, default=str)


def cat_chip(cat_nbr):
    if str(cat_nbr) == '6894':
        return '<span style="background:#fff3cd;color:#664d03;padding:1px 6px;border-radius:99px;font-size:.63rem;font-weight:700;">BEER 6894</span>'
    return '<span style="background:#dbeafe;color:#1e3a8a;padding:1px 6px;border-radius:99px;font-size:.63rem;font-weight:700;">SODA 6987</span>'


def summary_rows_html(summaries):
    html = ''
    for s in sorted(summaries, key=lambda x: x['PCT_ALINEACION']):
        pct   = s['PCT_ALINEACION']
        bar_w = int(pct)
        if pct == 100:
            badge_cls = 'badge-ok'
            bar_cls   = 'bar-ok'
        elif pct >= 50:
            badge_cls = 'badge-warn'
            bar_cls   = 'bar-warn'
        else:
            badge_cls = 'badge-err'
            bar_cls   = 'bar-err'

        single    = '(unica)' if s['TOTAL_SKUS'] == 1 else ''
        obs_short = s['OBSERVACIONES'][:60] + '...' if len(s['OBSERVACIONES']) > 60 else s['OBSERVACIONES']
        precio_fmt = f"c/{s['PRECIO_PRIMARIO']:,.2f}" if s['PRECIO_PRIMARIO'] is not None else '-'
        sqty = s.get('SELL_QTY', '') or '-'

        html += f"""
        <tr class="summary-row" data-family="{s['CODIGO_FAMILIA']}" data-cat="{s['CATEGORY_NBR']}">
          <td class="font-mono text-xs">{s['CODIGO_FAMILIA']}</td>
          <td>{cat_chip(s['CATEGORY_NBR'])}</td>
          <td>{s['MARCA']}</td>
          <td class="text-xs text-gray">{s['FINELINE']}</td>
          <td class="text-right font-mono text-xs">{sqty}</td>
          <td class="text-right font-mono">{s['TOTAL_SKUS']}</td>
          <td class="text-right font-mono text-blue">{precio_fmt}</td>
          <td class="text-right font-mono">{s['N_PRECIOS_DISTINTOS']}</td>
          <td class="text-right text-green">{s['SKUS_IGUAL_PRECIO']}</td>
          <td class="text-right text-red">{s['SKUS_DIFERENTE_PRECIO']}</td>
          <td>
            <div class="bar-wrap" role="progressbar" aria-valuenow="{bar_w}" aria-valuemin="0" aria-valuemax="100">
              <div class="{bar_cls}" style="width:{bar_w}%"></div>
            </div>
            <span class="{badge_cls}">{fmt_pct(pct)}</span>
            <span class="text-xs text-gray">{single}</span>
          </td>
          <td class="text-xs obs-col" title="{s['OBSERVACIONES']}">{obs_short}</td>
        </tr>"""
    return html


def detail_rows_html(detail_rows):
    html = ''
    for r in detail_rows:
        agrup   = r.get('AGRUPACION', '')
        estado  = r.get('ESTADO_PRECIO', '')
        ventas  = safe_float(r.get('VENTAS'))
        rot     = safe_float(r.get('ROTACIONES'))
        precio  = safe_float(r.get('PRECIO_GPI_C_IMP'))
        pprim   = safe_float(r.get('PRECIO_PRIMARIO'))
        diff    = safe_float(r.get('DIFERENCIA_PRECIO'))
        estatus = r.get('ESTATUS', '')
        cat_nbr = r.get('CATEGORY_NBR', '')
        sqty    = r.get('SELL_QTY', '') or '-'

        row_cls = ''
        if agrup == 'PRIMARIO':
            row_cls = 'row-primary'
        elif estado == 'Diferente al Primario':
            row_cls = 'row-diff'

        if estado == 'Igual al Primario':
            estado_badge = '<span class="badge-ok-sm">Igual</span>'
        elif estado == 'Diferente al Primario':
            estado_badge = '<span class="badge-err-sm">Diferente</span>'
        else:
            estado_badge = f'<span class="badge-warn-sm">{estado}</span>'

        agrup_badge = (
            '<span class="badge-primary">PRIMARIO</span>'
            if agrup == 'PRIMARIO'
            else '<span class="badge-secondary">SECUNDARIO</span>'
        )

        diff_str = ''
        if diff is not None and diff != 0:
            sign  = '+' if diff > 0 else ''
            color = 'text-red' if diff > 0 else 'text-green'
            diff_str = f'<span class="{color}">{sign}c/{diff:,.2f}</span>'

        desc_full = r.get('DESCRIPCION', '')
        desc_show = desc_full[:35] + ('...' if len(desc_full) > 35 else '')
        fl_full   = r.get('FINELINE_DESC', '')
        fl_show   = fl_full[:25] + ('...' if len(fl_full) > 25 else '')

        precio_str = f"c/{precio:,.2f}" if precio is not None else '-'
        pprim_str  = f"c/{pprim:,.2f}"  if pprim  is not None else '-'
        ventas_str = f"c/{ventas:,.0f}" if ventas  is not None else '-'
        rot_str    = f"{rot:,.1f}"       if rot     is not None else '-'

        html += f"""
        <tr class="detail-row {row_cls}" data-family="{r.get('CODIGO_FAMILIA','')}" data-estado="{estado}" data-agrupacion="{agrup}" data-cat="{cat_nbr}">
          <td class="font-mono text-xs">{r.get('CODIGO_FAMILIA','')}</td>
          <td>{cat_chip(cat_nbr)}</td>
          <td>{agrup_badge}</td>
          <td class="font-mono text-xs">{r.get('ITEM','')}</td>
          <td class="desc-col" title="{desc_full}">{desc_show}</td>
          <td>{r.get('MARCA_DESC','')}</td>
          <td class="text-xs text-gray">{fl_show}</td>
          <td class="text-right font-mono text-xs">{sqty}</td>
          <td class="text-right font-mono font-bold text-blue">{precio_str}</td>
          <td class="text-right font-mono text-gray">{pprim_str}</td>
          <td>{diff_str if diff_str else '-'}</td>
          <td>{estado_badge}</td>
          <td class="text-right font-mono">{ventas_str}</td>
          <td class="text-right font-mono">{rot_str}</td>
          <td class="text-center"><span class="{'badge-ok-sm' if estatus=='A' else 'badge-err-sm'}">{estatus}</span></td>
        </tr>"""
    return html


rows_sorted = sorted(rows, key=lambda r: (
    r.get('CODIGO_FAMILIA', ''),
    0 if r.get('AGRUPACION') == 'PRIMARIO' else 1,
    -safe_float(r.get('VENTAS'), 0)
))


def criticas_panel_html():
    html = ''
    for s in fam_criticas[:15]:
        gk      = (s['PAIS'], s['FORMATO'], s['ZONA'], s['CODIGO_FAMILIA'])
        grp_rows = sorted(
            groups[gk],
            key=lambda r: (0 if r.get('AGRUPACION') == 'PRIMARIO' else 1, -safe_float(r.get('VENTAS'), 0))
        )
        sqty_lbl = s.get('SELL_QTY', '') or '-'
        html += f"""
    <div class="crit-card">
      <div class="crit-header">
        <span class="font-mono text-xs text-blue">{s['CODIGO_FAMILIA']}</span>
        {cat_chip(s['CATEGORY_NBR'])}
        <strong>{s['MARCA']}</strong>
        <span class="text-xs text-gray">{s['FINELINE']}</span>
        <span class="text-xs text-gray">| Qty: {sqty_lbl}</span>
        <span class="badge-err" style="margin-left:auto">{s['SKUS_DIFERENTE_PRECIO']} desalineado(s)</span>
        <span class="badge-warn">{fmt_pct(s['PCT_ALINEACION'])}</span>
      </div>
      <table class="crit-tbl">
        <thead><tr>
          <th>ITEM</th><th>Descripcion</th><th>Agrup.</th>
          <th>SELL_QTY</th><th>Precio GPI c/imp</th>
          <th>Precio Primario</th><th>Diferencia</th>
          <th>Estado</th><th>Ventas</th><th>Rotacion</th>
        </tr></thead>
        <tbody>"""
        for r in grp_rows:
            precio = safe_float(r.get('PRECIO_GPI_C_IMP'))
            pprim  = safe_float(r.get('PRECIO_PRIMARIO'))
            diff   = safe_float(r.get('DIFERENCIA_PRECIO'))
            ventas = safe_float(r.get('VENTAS'))
            rot    = safe_float(r.get('ROTACIONES'))
            estado = r.get('ESTADO_PRECIO', '')
            agrup  = r.get('AGRUPACION', '')
            sqty_r = r.get('SELL_QTY', '') or '-'

            rc = ''
            if agrup == 'PRIMARIO':
                rc = 'crit-row-primary'
            elif estado == 'Diferente al Primario':
                rc = 'crit-row-diff'

            diff_s = ''
            if diff is not None and diff != 0:
                sign  = '+' if diff > 0 else ''
                col   = 'text-red' if diff > 0 else 'text-green'
                diff_s = f'<span class="{col}">{sign}c/{diff:,.2f}</span>'

            agrup_b = '<span class="badge-primary">PRIMARIO</span>' if agrup == 'PRIMARIO' else '<span class="badge-secondary">SECUNDARIO</span>'
            est_b   = '<span class="badge-ok-sm">Igual</span>' if estado == 'Igual al Primario' else ('<span class="badge-err-sm">Diferente</span>' if estado == 'Diferente al Primario' else f'<span class="badge-warn-sm">{estado}</span>')

            html += f"""
          <tr class="{rc}">
            <td class="font-mono text-xs">{r.get('ITEM','')}</td>
            <td title="{r.get('DESCRIPCION','')}">{r.get('DESCRIPCION','')[:42]}</td>
            <td>{agrup_b}</td>
            <td class="text-right font-mono text-xs">{sqty_r}</td>
            <td class="text-right font-mono font-bold">{'c/'+f'{precio:,.2f}' if precio is not None else '-'}</td>
            <td class="text-right font-mono text-gray">{'c/'+f'{pprim:,.2f}' if pprim is not None else '-'}</td>
            <td class="text-right">{diff_s if diff_s else '-'}</td>
            <td>{est_b}</td>
            <td class="text-right font-mono">{'c/'+f'{ventas:,.0f}' if ventas is not None else '-'}</td>
            <td class="text-right font-mono">{f'{rot:,.1f}' if rot is not None else '-'}</td>
          </tr>"""
        html += "</tbody></table></div>"
    return html


HTML = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>Familias de Precios v2 (+ SELL_QTY) -- Tienda 4076 | SW 22 | CAT 6894+6987</title>
  <style>
    :root {{
      --blue:   #0053e2;
      --spark:  #ffc220;
      --red:    #ea1100;
      --green:  #2a8703;
      --warn:   #995213;
      --gray160:#1a1a1a;
      --gray100:#74767c;
      --gray50: #c4c4c4;
      --gray10: #f5f5f5;
      --white:  #ffffff;
    }}
    *, *::before, *::after {{ box-sizing:border-box; margin:0; padding:0; }}
    body {{
      font-family:'Segoe UI', system-ui, sans-serif;
      background:var(--gray10); color:var(--gray160); font-size:13px;
    }}
    .header {{
      background:var(--blue); color:var(--white);
      padding:18px 32px 14px;
      display:flex; align-items:center; gap:14px;
    }}
    .header-title h1 {{ font-size:1.1rem; font-weight:700; }}
    .header-title p  {{ font-size:.73rem; opacity:.85; margin-top:2px; }}
    .header-badge {{
      margin-left:auto; background:var(--spark); color:var(--gray160);
      padding:4px 12px; border-radius:99px; font-size:.7rem; font-weight:700;
    }}
    .v2-badge {{
      background:#1a3a6e; color:var(--spark);
      padding:3px 10px; border-radius:99px; font-size:.68rem; font-weight:700;
    }}
    .content {{ max-width:1440px; margin:0 auto; padding:16px 12px 40px; }}
    .kpi-grid {{
      display:grid; grid-template-columns:repeat(auto-fit, minmax(138px,1fr));
      gap:10px; margin-bottom:20px;
    }}
    .kpi-card {{
      background:var(--white); border-radius:8px; padding:12px 14px;
      box-shadow:0 1px 4px rgba(0,0,0,.08); border-top:3px solid var(--blue);
    }}
    .kpi-card.spark {{ border-top-color:var(--spark); }}
    .kpi-card.red   {{ border-top-color:var(--red); }}
    .kpi-card.green {{ border-top-color:var(--green); }}
    .kpi-card.warn  {{ border-top-color:var(--warn); }}
    .kpi-val  {{ font-size:1.5rem; font-weight:800; color:var(--blue); }}
    .kpi-card.spark .kpi-val {{ color:var(--warn); }}
    .kpi-card.red   .kpi-val {{ color:var(--red); }}
    .kpi-card.green .kpi-val {{ color:var(--green); }}
    .kpi-card.warn  .kpi-val {{ color:var(--warn); }}
    .kpi-sub {{ font-size:.66rem; color:var(--gray100); margin-top:1px; }}
    .kpi-lbl {{ font-size:.65rem; color:var(--gray100); margin-top:3px; text-transform:uppercase; letter-spacing:.04em; }}
    h2 {{
      font-size:.93rem; font-weight:700; color:var(--blue);
      border-bottom:2px solid var(--spark); padding-bottom:5px; margin:20px 0 10px;
    }}
    h3 {{ font-size:.8rem; font-weight:600; margin:12px 0 6px; }}
    .delta-box {{
      background:var(--white); border-radius:8px; padding:14px 18px;
      margin-bottom:18px; box-shadow:0 1px 4px rgba(0,0,0,.08);
      border-left:4px solid var(--spark);
    }}
    .delta-box h3 {{ color:var(--warn); margin:0 0 8px; }}
    .delta-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:10px; }}
    .delta-item {{ font-size:.8rem; }}
    .delta-item span {{ font-weight:700; }}
    .delta-arrow {{ color:var(--green); }}
    .delta-arrow.down {{ color:var(--red); }}
    .filters {{
      background:var(--white); border-radius:8px;
      padding:9px 12px; margin-bottom:12px;
      display:flex; gap:8px; flex-wrap:wrap; align-items:center;
      box-shadow:0 1px 3px rgba(0,0,0,.06);
    }}
    .filters label {{ font-size:.67rem; color:var(--gray100); text-transform:uppercase; letter-spacing:.04em; }}
    .filters input, .filters select {{
      padding:4px 8px; border:1px solid var(--gray50);
      border-radius:5px; font-size:.74rem;
      background:var(--gray10); color:var(--gray160);
    }}
    .filters input:focus, .filters select:focus {{ outline:2px solid var(--blue); border-color:var(--blue); }}
    .btn {{
      padding:5px 12px; border-radius:5px; border:none;
      cursor:pointer; font-size:.74rem; font-weight:600;
      background:var(--blue); color:var(--white);
    }}
    .btn:hover {{ background:#0042b5; }}
    .btn.sec {{ background:var(--gray10); color:var(--gray160); border:1px solid var(--gray50); }}
    .btn.sec:hover {{ background:var(--gray50); }}
    .table-wrap {{
      background:var(--white); border-radius:8px;
      box-shadow:0 1px 4px rgba(0,0,0,.08); overflow:auto; margin-bottom:16px;
    }}
    table {{ width:100%; border-collapse:collapse; font-size:.75rem; }}
    thead th {{
      background:var(--blue); color:var(--white);
      padding:8px 9px; text-align:left; white-space:nowrap;
      position:sticky; top:0; z-index:2; cursor:pointer; user-select:none;
    }}
    thead th:hover {{ background:#0042b5; }}
    tbody tr {{ border-bottom:1px solid var(--gray10); transition:background .1s; }}
    tbody tr:hover {{ background:#edf3ff; }}
    tbody td {{ padding:6px 9px; }}
    .row-primary {{ background:#fffbea; }}
    .row-primary:hover {{ background:#fff3c0; }}
    .row-diff {{ background:#fff2f2; }}
    .row-diff:hover {{ background:#ffe0e0; }}
    .badge-ok    {{ background:#e6f4ea; color:#1e6e2e; padding:2px 8px; border-radius:99px; font-size:.65rem; font-weight:600; }}
    .badge-warn  {{ background:#fff8e1; color:var(--warn); padding:2px 8px; border-radius:99px; font-size:.65rem; font-weight:600; }}
    .badge-err   {{ background:#fde8e8; color:var(--red); padding:2px 8px; border-radius:99px; font-size:.65rem; font-weight:600; }}
    .badge-ok-sm   {{ background:#e6f4ea; color:#1e6e2e; padding:1px 5px; border-radius:99px; font-size:.62rem; font-weight:600; white-space:nowrap; }}
    .badge-warn-sm {{ background:#fff8e1; color:var(--warn); padding:1px 5px; border-radius:99px; font-size:.62rem; font-weight:600; white-space:nowrap; }}
    .badge-err-sm  {{ background:#fde8e8; color:var(--red); padding:1px 5px; border-radius:99px; font-size:.62rem; font-weight:600; white-space:nowrap; }}
    .badge-primary   {{ background:#dbeafe; color:var(--blue); padding:1px 5px; border-radius:99px; font-size:.62rem; font-weight:700; white-space:nowrap; }}
    .badge-secondary {{ background:var(--gray10); color:var(--gray100); padding:1px 5px; border-radius:99px; font-size:.62rem; font-weight:600; white-space:nowrap; }}
    .bar-wrap {{ height:5px; background:var(--gray10); border-radius:99px; overflow:hidden; margin-bottom:3px; width:65px; display:inline-block; vertical-align:middle; }}
    .bar-ok   {{ height:5px; background:var(--green); border-radius:99px; }}
    .bar-warn {{ height:5px; background:var(--spark); border-radius:99px; }}
    .bar-err  {{ height:5px; background:var(--red);   border-radius:99px; }}
    .crit-card {{
      background:var(--white); border-radius:8px;
      box-shadow:0 1px 4px rgba(0,0,0,.09);
      margin-bottom:12px; overflow:hidden; border-left:4px solid var(--red);
    }}
    .crit-header {{
      display:flex; align-items:center; gap:8px;
      padding:9px 14px; background:#fff8f8;
      border-bottom:1px solid #ffe0e0; flex-wrap:wrap;
    }}
    .crit-tbl {{ width:100%; border-collapse:collapse; font-size:.72rem; }}
    .crit-tbl th {{
      background:#f8f8f8; padding:6px 8px;
      border-bottom:1px solid var(--gray50);
      text-align:left; font-weight:600; color:var(--gray100);
    }}
    .crit-tbl td {{ padding:5px 8px; border-bottom:1px solid var(--gray10); }}
    .crit-row-primary {{ background:#fffbea; }}
    .crit-row-diff {{ background:#fff2f2; }}
    .obs-panel {{
      background:var(--white); border-radius:8px;
      box-shadow:0 1px 4px rgba(0,0,0,.08); padding:14px 18px; margin-bottom:16px;
    }}
    .obs-item {{
      display:flex; align-items:flex-start; gap:8px;
      padding:7px 0; border-bottom:1px solid var(--gray10); font-size:.77rem;
    }}
    .obs-item:last-child {{ border-bottom:none; }}
    .sql-block {{
      background:#1e2029; color:#abb2bf; border-radius:8px;
      padding:12px 16px; font-family:'Courier New',monospace;
      font-size:.69rem; overflow-x:auto; line-height:1.65; margin-bottom:16px;
    }}
    .sql-kw  {{ color:#c678dd; }}
    .sql-fn  {{ color:#61afef; }}
    .sql-str {{ color:#98c379; }}
    .sql-cm  {{ color:#5c6370; font-style:italic; }}
    .tabs {{ display:flex; gap:3px; margin-bottom:-1px; flex-wrap:wrap; }}
    .tab {{
      padding:7px 14px; border-radius:6px 6px 0 0;
      border:1px solid var(--gray50); border-bottom:none;
      cursor:pointer; font-size:.74rem; font-weight:600;
      background:var(--gray10); color:var(--gray100);
    }}
    .tab.active {{ background:var(--white); color:var(--blue); }}
    .tab-panel {{ display:none; }}
    .tab-panel.active {{ display:block; }}
    .text-right  {{ text-align:right; }}
    .text-center {{ text-align:center; }}
    .font-mono   {{ font-family:'Courier New',monospace; }}
    .font-bold   {{ font-weight:700; }}
    .text-blue   {{ color:var(--blue); }}
    .text-red    {{ color:var(--red); }}
    .text-green  {{ color:var(--green); }}
    .text-gray   {{ color:var(--gray100); }}
    .text-xs     {{ font-size:.68rem; }}
    .footer {{
      text-align:center; padding:14px; font-size:.67rem;
      color:var(--gray100); border-top:1px solid var(--gray50); margin-top:18px;
    }}
    @media print {{
      .filters, .btn, .tabs {{ display:none; }}
      .tab-panel {{ display:block !important; }}
      body {{ background:white; }}
    }}
  </style>
</head>
<body>

<header class="header" role="banner">
  <div class="header-title">
    <h1>Analisis de Familias de Precios -- Tienda 4076
      <span class="v2-badge">v2 + SELL_QTY</span>
    </h1>
    <p>SW 22 | 2026 | Cat 6894 (Beer) + 6987 (Soda) | CR | Supermercados | San Jose | Llave de familia: 6 campos</p>
  </div>
  <span class="header-badge">Pricing Intelligence</span>
</header>

<main class="content" role="main">

  <!-- DELTA VS V1 -->
  <div class="delta-box" role="region" aria-label="Comparacion v1 vs v2">
    <h3>Cambio vs version anterior (v1 sin SELL_QTY)</h3>
    <div class="delta-grid">
      <div class="delta-item">Familias totales: <span>v1 = 329</span> -> <span class="delta-arrow">v2 = {total_fam}</span></div>
      <div class="delta-item">Fam. Multi-SKU: <span>v1 = 77</span> -> <span class="delta-arrow {'down' if fam_multi < 77 else ''}">v2 = {fam_multi}</span></div>
      <div class="delta-item">SKUs desalineados: <span>v1 = 32</span> -> <span class="delta-arrow {'down' if total_desalineados < 32 else ''}">v2 = {total_desalineados}</span></div>
      <div class="delta-item">Fam. con desvios: <span>v1 = 22</span> -> <span class="delta-arrow {'down' if len(fam_criticas) < 22 else ''}">v2 = {len(fam_criticas)}</span></div>
      <div class="delta-item">% Alineacion: <span>v1 = 92.7%</span> -> <span class="delta-arrow">v2 = {pct_global:.1f}%</span></div>
      <div class="delta-item">Nuevo campo en llave: <span style="color:var(--blue)">+ SELL_QTY (volumen)</span></div>
    </div>
  </div>

  <!-- KPI CARDS -->
  <section aria-label="Indicadores clave">
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-val">{total_skus_global}</div>
        <div class="kpi-sub">{len(cat_6894_rows)} Beer + {len(cat_6987_rows)} Soda</div>
        <div class="kpi-lbl">Total SKUs</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-val">{total_fam}</div>
        <div class="kpi-lbl">Total Familias</div>
      </div>
      <div class="kpi-card spark">
        <div class="kpi-val">{fam_multi}</div>
        <div class="kpi-lbl">Familias Multi-SKU</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-val">{fam_single}</div>
        <div class="kpi-lbl">Familias Single-SKU</div>
      </div>
      <div class="kpi-card green">
        <div class="kpi-val">{total_iguales}</div>
        <div class="kpi-lbl">SKUs Alineados</div>
      </div>
      <div class="kpi-card red">
        <div class="kpi-val">{total_desalineados}</div>
        <div class="kpi-lbl">SKUs Desalineados</div>
      </div>
      <div class="kpi-card green">
        <div class="kpi-val">{pct_global:.1f}%</div>
        <div class="kpi-lbl">Alineacion Global</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-val">{fam_perfectas}</div>
        <div class="kpi-lbl">Fam. 100% Alineadas</div>
      </div>
      <div class="kpi-card warn">
        <div class="kpi-val">{len(fam_criticas)}</div>
        <div class="kpi-lbl">Fam. con Desvios</div>
      </div>
      <div class="kpi-card red">
        <div class="kpi-val">{skus_sin_ventas}</div>
        <div class="kpi-lbl">SKUs sin Ventas</div>
      </div>
    </div>
  </section>

  <!-- OBSERVACIONES -->
  <h2>Observaciones y Supuestos del Analisis (v2)</h2>
  <div class="obs-panel" role="region" aria-label="Observaciones">
    <div class="obs-item">
      <div><strong>Cambio principal v2:</strong> La llave de familia ahora incluye 6 campos: COST_UNIT + MARCA_DESC + N_MARCA + PAIS + N_FINELINE + <strong>SELL_QTY</strong>. SELL_QTY representa el contenido neto del producto (ml/g/unidades). Al agregarlo, artículos del mismo formato pero diferente volumen ya NO pertenecen a la misma familia, lo que genera familias mas granulares y homogeneas en tamano.</div>
    </div>
    <div class="obs-item">
      <div><strong>Impacto de SELL_QTY en la granularidad:</strong> v1 tenia 329 familias y 77 multi-SKU. v2 tiene <strong>{total_fam} familias</strong> y <strong>{fam_multi} multi-SKU</strong>. Agregar SELL_QTY divide familias que antes combinaban diferentes tamanos de envase de la misma marca y fineline. Esto es correcto desde el punto de vista de pricing: no tiene sentido comparar precios de 355ml vs 600ml del mismo producto.</div>
    </div>
    <div class="obs-item">
      <div><strong>Identificacion del Primario:</strong> MAX(VENTAS) dentro de cada (PAIS / FORMATO / ZONA / CODIGO_FAMILIA). Tiebreaker = MIN(ITEM). {skus_sin_ventas} SKUs sin ventas se tratan como VENTAS=0. SQL: ROW_NUMBER() OVER(PARTITION BY ... ORDER BY COALESCE(VENTAS,0) DESC, ITEM ASC).</div>
    </div>
    <div class="obs-item">
      <div><strong>Precio de referencia:</strong> PRECIO_GPI_C_IMP (precio con impuesto). Tolerancia de igualdad: diferencia absoluta menor a c/0.01.</div>
    </div>
    <div class="obs-item">
      <div><strong>Rotacion:</strong> ROTACIONES es la unica metrica disponible en la tabla. Se expone como ROTACION. {skus_sin_ventas} SKUs tienen ROTACION nula (correlacion directa con ausencia de ventas).</div>
    </div>
    <div class="obs-item">
      <div><strong>Escalabilidad:</strong> El SQL equivalente usa DENSE_RANK() con los 6 campos de la llave. Completamente parametrizable para cualquier tienda, SW, ano, categoria.</div>
    </div>
  </div>

  <!-- TABS -->
  <div class="tabs" role="tablist">
    <button class="tab active" role="tab" aria-selected="true"  onclick="showTab('tab-criticas',this)">Familias Criticas ({len(fam_criticas)})</button>
    <button class="tab" role="tab" aria-selected="false" onclick="showTab('tab-summary',this)">Resumen Ejecutivo</button>
    <button class="tab" role="tab" aria-selected="false" onclick="showTab('tab-detail',this)">Base Detallada</button>
    <button class="tab" role="tab" aria-selected="false" onclick="showTab('tab-sql',this)">SQL Equivalente</button>
  </div>

  <!-- TAB: CRITICAS -->
  <div id="tab-criticas" class="tab-panel active">
    <h2>Familias con Desvios -- Oportunidades de Homologacion (v2 con SELL_QTY)</h2>
    <p style="font-size:.77rem;color:var(--gray100);margin-bottom:12px;">
      <strong>{len(fam_criticas)} familias</strong> con al menos 1 SKU desalineado.
      Ordenadas por SKUs desalineados desc, luego por venta del primario desc.
      Amarillo = Primario | Rojo = Precio diferente al Primario.
      Mostrando max. 15.
    </p>
    {criticas_panel_html()}
  </div>

  <!-- TAB: SUMMARY -->
  <div id="tab-summary" class="tab-panel">
    <h2>Resumen Ejecutivo por Familia (v2)</h2>
    <div class="filters" role="search">
      <label for="srch-fam">Familia / Marca</label>
      <input type="search" id="srch-fam" placeholder="Buscar..." oninput="filterSummary()" aria-label="Buscar familia"/>
      <label for="sel-cat">Categoria</label>
      <select id="sel-cat" onchange="filterSummary()">
        <option value="">Todas</option>
        <option value="6894">6894 - Beer</option>
        <option value="6987">6987 - Soda</option>
      </select>
      <label for="sel-aln">Estado</label>
      <select id="sel-aln" onchange="filterSummary()">
        <option value="">Todos</option>
        <option value="100">100% Alineadas</option>
        <option value="partial">Parcialmente</option>
        <option value="none">Sin alineacion</option>
        <option value="multi">Solo multi-SKU</option>
        <option value="single">Solo single-SKU</option>
      </select>
      <button class="btn sec" onclick="resetFilters()">Limpiar</button>
      <button class="btn" onclick="exportCSV('summary')">Exportar CSV</button>
      <span id="summary-count" aria-live="polite" style="font-size:.7rem;color:var(--gray100);margin-left:auto;"></span>
    </div>
    <div class="table-wrap">
      <table id="tbl-summary" aria-label="Resumen ejecutivo v2">
        <thead>
          <tr>
            <th onclick="sortTable('tbl-summary',0)">Codigo Familia</th>
            <th onclick="sortTable('tbl-summary',1)">Cat.</th>
            <th onclick="sortTable('tbl-summary',2)">Marca</th>
            <th onclick="sortTable('tbl-summary',3)">Fineline</th>
            <th onclick="sortTable('tbl-summary',4)">SELL_QTY</th>
            <th onclick="sortTable('tbl-summary',5)">Total SKUs</th>
            <th onclick="sortTable('tbl-summary',6)">Precio Primario</th>
            <th onclick="sortTable('tbl-summary',7)">Precios Distintos</th>
            <th onclick="sortTable('tbl-summary',8)">SKUs Iguales</th>
            <th onclick="sortTable('tbl-summary',9)">SKUs Diferentes</th>
            <th onclick="sortTable('tbl-summary',10)">% Alineacion</th>
            <th onclick="sortTable('tbl-summary',11)">Observaciones</th>
          </tr>
        </thead>
        <tbody id="summary-body">
          {summary_rows_html(summary_list)}
        </tbody>
      </table>
    </div>
  </div>

  <!-- TAB: DETAIL -->
  <div id="tab-detail" class="tab-panel">
    <h2>Base Detallada -- Todos los SKUs (v2)</h2>
    <div class="filters" role="search">
      <label for="srch-det">Item / Descripcion / Familia</label>
      <input type="search" id="srch-det" placeholder="Buscar..." oninput="filterDetail()" aria-label="Buscar detalle"/>
      <label for="sel-cat2">Categoria</label>
      <select id="sel-cat2" onchange="filterDetail()">
        <option value="">Todas</option>
        <option value="6894">6894 - Beer</option>
        <option value="6987">6987 - Soda</option>
      </select>
      <label for="sel-agrup">Agrupacion</label>
      <select id="sel-agrup" onchange="filterDetail()">
        <option value="">Todos</option>
        <option value="PRIMARIO">Primario</option>
        <option value="SECUNDARIO">Secundario</option>
      </select>
      <label for="sel-estado">Estado Precio</label>
      <select id="sel-estado" onchange="filterDetail()">
        <option value="">Todos</option>
        <option value="Igual al Primario">Igual al Primario</option>
        <option value="Diferente al Primario">Diferente al Primario</option>
        <option value="Sin Precio">Sin Precio</option>
      </select>
      <button class="btn sec" onclick="resetDetailFilters()">Limpiar</button>
      <button class="btn" onclick="exportCSV('detail')">Exportar CSV</button>
      <span id="detail-count" aria-live="polite" style="font-size:.7rem;color:var(--gray100);margin-left:auto;"></span>
    </div>
    <div class="table-wrap" style="max-height:570px;overflow-y:auto;">
      <table id="tbl-detail" aria-label="Base detallada v2">
        <thead>
          <tr>
            <th onclick="sortTable('tbl-detail',0)">Codigo Familia</th>
            <th onclick="sortTable('tbl-detail',1)">Cat.</th>
            <th onclick="sortTable('tbl-detail',2)">Agrupacion</th>
            <th onclick="sortTable('tbl-detail',3)">ITEM</th>
            <th onclick="sortTable('tbl-detail',4)">Descripcion</th>
            <th onclick="sortTable('tbl-detail',5)">Marca</th>
            <th onclick="sortTable('tbl-detail',6)">Fineline</th>
            <th onclick="sortTable('tbl-detail',7)">SELL_QTY</th>
            <th onclick="sortTable('tbl-detail',8)">Precio GPI c/imp</th>
            <th onclick="sortTable('tbl-detail',9)">Precio Primario</th>
            <th onclick="sortTable('tbl-detail',10)">Diferencia</th>
            <th onclick="sortTable('tbl-detail',11)">Estado Precio</th>
            <th onclick="sortTable('tbl-detail',12)">Ventas SW22</th>
            <th onclick="sortTable('tbl-detail',13)">Rotacion</th>
            <th onclick="sortTable('tbl-detail',14)">Estatus</th>
          </tr>
        </thead>
        <tbody id="detail-body">
          {detail_rows_html(rows_sorted)}
        </tbody>
      </table>
    </div>
  </div>

  <!-- TAB: SQL -->
  <div id="tab-sql" class="tab-panel">
    <h2>SQL Equivalente en BigQuery -- Llave de Familia v2 (6 campos)</h2>
    <p style="font-size:.76rem;color:var(--gray100);margin-bottom:10px;">
      Version actualizada con SELL_QTY incluido en la llave de familia.
      Para revertir a v1, simplemente eliminar la linea de SELL_QTY del DENSE_RANK.
    </p>
    <div class="sql-block"><pre><span class="sql-kw">WITH</span>

<span class="sql-cm">-- =====================================================
-- STEP 1: Llave de Familia v2 (6 campos)
-- COST_UNIT | MARCA_DESC | N_MARCA | PAIS | N_FINELINE | SELL_QTY
-- SELL_QTY: diferencia artículos del mismo formato pero distinto volumen
-- =====================================================</span>
base <span class="sql-kw">AS</span> (
  <span class="sql-kw">SELECT</span>
    *,
    <span class="sql-fn">CONCAT</span>(
      <span class="sql-str">'FAM_'</span>,
      <span class="sql-fn">CAST</span>(COD_PAIS    <span class="sql-kw">AS</span> STRING), <span class="sql-str">'_'</span>,
      <span class="sql-fn">CAST</span>(COD_FORMATO <span class="sql-kw">AS</span> STRING), <span class="sql-str">'_'</span>,
      <span class="sql-fn">CAST</span>(COD_ZONA   <span class="sql-kw">AS</span> STRING),  <span class="sql-str">'_'</span>,
      <span class="sql-fn">LPAD</span>(<span class="sql-fn">CAST</span>(
        <span class="sql-fn">DENSE_RANK</span>() <span class="sql-kw">OVER</span>(
          <span class="sql-kw">PARTITION BY</span> COD_PAIS, COD_FORMATO, COD_ZONA
          <span class="sql-kw">ORDER BY</span>
            COST_UNIT,
            MARCA_DESC,
            N_MARCA,
            PAIS,
            N_FINELINE,
            SELL_QTY     <span class="sql-cm">-- nuevo campo v2</span>
        ) <span class="sql-kw">AS</span> STRING), 4, <span class="sql-str">'0'</span>)
    ) <span class="sql-kw">AS</span> CODIGO_FAMILIA
  <span class="sql-kw">FROM</span> <span class="sql-str">`wmt-k1-cons-data-users.k1_adhoc_tables.prcng_info_cam_a0g0dn_3_insumos_tienda`</span>
  <span class="sql-kw">WHERE</span> store_nbr    = 4076
    <span class="sql-kw">AND</span> EXTRACT_YR   = 2026
    <span class="sql-kw">AND</span> SW           = 22
    <span class="sql-kw">AND</span> EXTRACT_DATE = <span class="sql-str">"2026-06-29 00:00:00 UTC"</span>
    <span class="sql-kw">AND</span> CATEGORY_NBR <span class="sql-kw">IN</span> (6894, 6987)
),

<span class="sql-cm">-- =====================================================
-- STEP 2: Ranking -> Primario por mayor venta (tiebreak: min ITEM)
-- =====================================================</span>
ranked <span class="sql-kw">AS</span> (
  <span class="sql-kw">SELECT</span>
    *,
    <span class="sql-fn">ROW_NUMBER</span>() <span class="sql-kw">OVER</span>(
      <span class="sql-kw">PARTITION BY</span> COD_PAIS, COD_FORMATO, COD_ZONA, CODIGO_FAMILIA
      <span class="sql-kw">ORDER BY</span> <span class="sql-fn">COALESCE</span>(VENTAS, 0) <span class="sql-kw">DESC</span>, ITEM <span class="sql-kw">ASC</span>
    ) <span class="sql-kw">AS</span> rn_primary
  <span class="sql-kw">FROM</span> base
),

<span class="sql-cm">-- STEP 3: Datos del Primario para join lateral</span>
primarios <span class="sql-kw">AS</span> (
  <span class="sql-kw">SELECT</span>
    COD_PAIS, COD_FORMATO, COD_ZONA, CODIGO_FAMILIA,
    ITEM             <span class="sql-kw">AS</span> ITEM_PRIMARIO,
    DESCRIPCION      <span class="sql-kw">AS</span> DESC_PRIMARIO,
    PRECIO_GPI_C_IMP <span class="sql-kw">AS</span> PRECIO_PRIMARIO,
    VENTAS           <span class="sql-kw">AS</span> VENTAS_PRIMARIO,
    ROTACIONES       <span class="sql-kw">AS</span> ROTACION_PRIMARIO
  <span class="sql-kw">FROM</span> ranked <span class="sql-kw">WHERE</span> rn_primary = 1
),

<span class="sql-cm">-- STEP 4: Ensamble final con ESTADO_PRECIO y DIFERENCIA</span>
final <span class="sql-kw">AS</span> (
  <span class="sql-kw">SELECT</span>
    r.*,
    <span class="sql-kw">CASE WHEN</span> r.rn_primary = 1 <span class="sql-kw">THEN</span> <span class="sql-str">'PRIMARIO'</span>
                              <span class="sql-kw">ELSE</span> <span class="sql-str">'SECUNDARIO'</span> <span class="sql-kw">END</span>  <span class="sql-kw">AS</span> AGRUPACION,
    p.ITEM_PRIMARIO, p.DESC_PRIMARIO,
    p.PRECIO_PRIMARIO, p.VENTAS_PRIMARIO, p.ROTACION_PRIMARIO,
    <span class="sql-kw">CASE</span>
      <span class="sql-kw">WHEN</span> r.PRECIO_GPI_C_IMP <span class="sql-kw">IS NULL</span>   <span class="sql-kw">THEN</span> <span class="sql-str">'Sin Precio'</span>
      <span class="sql-kw">WHEN</span> p.PRECIO_PRIMARIO  <span class="sql-kw">IS NULL</span>   <span class="sql-kw">THEN</span> <span class="sql-str">'Sin Precio Primario'</span>
      <span class="sql-kw">WHEN</span> <span class="sql-fn">ABS</span>(r.PRECIO_GPI_C_IMP - p.PRECIO_PRIMARIO) &lt; 0.01
                                        <span class="sql-kw">THEN</span> <span class="sql-str">'Igual al Primario'</span>
      <span class="sql-kw">ELSE</span>                              <span class="sql-str">'Diferente al Primario'</span>
    <span class="sql-kw">END</span>                                                    <span class="sql-kw">AS</span> ESTADO_PRECIO,
    r.PRECIO_GPI_C_IMP - p.PRECIO_PRIMARIO                 <span class="sql-kw">AS</span> DIFERENCIA_PRECIO,
    r.ROTACIONES                                            <span class="sql-kw">AS</span> ROTACION
  <span class="sql-kw">FROM</span> ranked r
  <span class="sql-kw">LEFT JOIN</span> primarios p
         <span class="sql-kw">USING</span> (COD_PAIS, COD_FORMATO, COD_ZONA, CODIGO_FAMILIA)
)

<span class="sql-kw">SELECT</span> * <span class="sql-kw">FROM</span> final;
</pre></div>
  </div>

</main>

<footer class="footer" role="contentinfo">
  Rintyn (Code Puppy) | Pricing Families v2 (+ SELL_QTY) | Tienda 4076 | SW 22 | 2026 | {datetime.now().strftime('%Y-%m-%d %H:%M')} |
  Fuente: wmt-k1-cons-data-users.k1_adhoc_tables.prcng_info_cam_a0g0dn_3_insumos_tienda
</footer>

<script>
const detailData  = {detail_json};
const summaryData = {summary_json};

function showTab(id, btn) {{
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t => {{ t.classList.remove('active'); t.setAttribute('aria-selected','false'); }});
  document.getElementById(id).classList.add('active');
  btn.classList.add('active'); btn.setAttribute('aria-selected','true');
  updateCounts();
}}

function filterSummary() {{
  const q   = (document.getElementById('srch-fam').value || '').toLowerCase();
  const aln = document.getElementById('sel-aln').value;
  const cat = document.getElementById('sel-cat').value;
  let count = 0;
  document.querySelectorAll('#summary-body .summary-row').forEach(row => {{
    const txt     = row.textContent.toLowerCase();
    const pct     = parseFloat(row.querySelector('.bar-wrap')?.getAttribute('aria-valuenow') || 0);
    const skus    = parseInt(row.cells[5].textContent) || 0;
    const rowCat  = row.dataset.cat || '';
    let vis = (!q || txt.includes(q)) && (!cat || rowCat === cat);
    if (vis && aln === '100')     vis = pct === 100;
    if (vis && aln === 'partial') vis = pct > 0 && pct < 100;
    if (vis && aln === 'none')    vis = pct === 0;
    if (vis && aln === 'multi')   vis = skus > 1;
    if (vis && aln === 'single')  vis = skus === 1;
    row.style.display = vis ? '' : 'none';
    if (vis) count++;
  }});
  document.getElementById('summary-count').textContent = count + ' familia(s) mostrada(s)';
}}

function filterDetail() {{
  const q     = (document.getElementById('srch-det').value || '').toLowerCase();
  const cat2  = document.getElementById('sel-cat2').value;
  const agrup = document.getElementById('sel-agrup').value;
  const est   = document.getElementById('sel-estado').value;
  let count   = 0;
  document.querySelectorAll('#detail-body .detail-row').forEach(row => {{
    const txt    = row.textContent.toLowerCase();
    const ag     = row.dataset.agrupacion || '';
    const es     = row.dataset.estado || '';
    const rowCat = row.dataset.cat || '';
    let vis = (!q || txt.includes(q)) &&
              (!cat2  || rowCat === cat2) &&
              (!agrup || ag === agrup) &&
              (!est   || es === est);
    row.style.display = vis ? '' : 'none';
    if (vis) count++;
  }});
  document.getElementById('detail-count').textContent = count + ' SKU(s) mostrado(s)';
}}

function resetFilters() {{
  ['srch-fam','sel-aln','sel-cat'].forEach(id => {{ const el = document.getElementById(id); if (el) el.value = ''; }});
  filterSummary();
}}
function resetDetailFilters() {{
  ['srch-det','sel-cat2','sel-agrup','sel-estado'].forEach(id => {{ const el = document.getElementById(id); if (el) el.value = ''; }});
  filterDetail();
}}

let sortDir = {{}};
function sortTable(tblId, col) {{
  const tbl = document.getElementById(tblId);
  const tbody = tbl.querySelector('tbody');
  const rows = Array.from(tbody.querySelectorAll('tr'));
  const dir  = (sortDir[tblId + col] = !sortDir[tblId + col]);
  rows.sort((a, b) => {{
    const av = a.cells[col]?.textContent.trim() || '';
    const bv = b.cells[col]?.textContent.trim() || '';
    const an = parseFloat(av.replace(/[^0-9.\\-]/g,''));
    const bn = parseFloat(bv.replace(/[^0-9.\\-]/g,''));
    if (!isNaN(an) && !isNaN(bn)) return dir ? an - bn : bn - an;
    return dir ? av.localeCompare(bv,'es') : bv.localeCompare(av,'es');
  }});
  rows.forEach(r => tbody.appendChild(r));
}}

function exportCSV(type) {{
  const data = type === 'summary' ? summaryData : detailData;
  if (!data || !data.length) return;
  const keys  = Object.keys(data[0]);
  const lines = [keys.join(',')];
  data.forEach(row => {{
    lines.push(keys.map(k => {{
      const v = row[k] == null ? '' : String(row[k]);
      return (v.includes(',') || v.includes('"') || v.includes('\\n'))
        ? '"' + v.replace(/"/g,'""') + '"' : v;
    }}).join(','));
  }});
  const blob = new Blob([lines.join('\\n')], {{type:'text/csv;charset=utf-8;'}});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'pricing_' + type + '_v2_store4076_sw22_6894_6987.csv';
  a.click();
}}

function updateCounts() {{ filterSummary(); filterDetail(); }}
updateCounts();
</script>
</body>
</html>"""

with open(REPORT_HTML, 'w', encoding='utf-8') as f:
    f.write(HTML)

print(f"\n[DONE] {REPORT_HTML} generated!")

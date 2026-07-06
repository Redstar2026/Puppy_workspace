"""
Pricing Family Alignment Analysis
Store 4076 | SW 22 | 2026 | CAT 894, 6987
Consultant: Rintyn (Code Puppy) — Senior Data Analytics & Pricing
"""

import csv
import json
from collections import defaultdict
from datetime import datetime


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def safe_float(val, default=None):
    if val is None or str(val).strip() in ('', 'None', 'null'):
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def fmt_cur(val):
    if val is None:
        return '–'
    return f"₡{val:,.2f}"


def fmt_pct(val):
    if val is None:
        return '–'
    return f"{val:.1f}%"


# ─────────────────────────────────────────────────────────────
# STEP 0: LOAD DATA
# ─────────────────────────────────────────────────────────────

rows = []
with open('prcng_info_store4076_sw22_cat894_6987.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    original_fields = list(reader.fieldnames)
    for row in reader:
        rows.append(dict(row))

print(f"[LOAD] {len(rows)} rows loaded | {len(original_fields)} original columns")


# ─────────────────────────────────────────────────────────────
# STEP 1: BUILD FAMILY KEY → CODIGO_FAMILIA
# Family key = (COST_UNIT, MARCA_DESC, N_MARCA, PAIS, N_FINELINE)
# Scoped within: (PAIS, FORMATO, NOMB_ZONE)
# ─────────────────────────────────────────────────────────────

# Registry: full_key → CODIGO_FAMILIA
family_registry = {}
scope_counters = defaultdict(int)

for row in rows:
    scope = (row['PAIS'], row['FORMATO'], row['NOMB_ZONE'])
    fam_components = (
        row['COST_UNIT'],
        row['MARCA_DESC'],
        row['N_MARCA'],
        row['PAIS'],
        row['N_FINELINE'],
    )
    full_key = scope + fam_components

    if full_key not in family_registry:
        scope_counters[scope] += 1
        seq = scope_counters[scope]
        cod_pais    = row['COD_PAIS']
        cod_formato = row['COD_FORMATO']
        cod_zona    = row['COD_ZONA']
        codigo = f"FAM_{cod_pais}_{cod_formato}_{cod_zona}_{seq:04d}"
        family_registry[full_key] = codigo

# Assign CODIGO_FAMILIA
for row in rows:
    scope = (row['PAIS'], row['FORMATO'], row['NOMB_ZONE'])
    fam_components = (
        row['COST_UNIT'],
        row['MARCA_DESC'],
        row['N_MARCA'],
        row['PAIS'],
        row['N_FINELINE'],
    )
    row['CODIGO_FAMILIA'] = family_registry[scope + fam_components]

total_families = len(family_registry)
print(f"[STEP 1] Families built: {total_families} | "
      f"Multi-item families: {sum(1 for v in defaultdict(list, {k: [r for r in rows if r['CODIGO_FAMILIA'] == v] for k, v in family_registry.items()}).values() if len(v) > 1)}")


# ─────────────────────────────────────────────────────────────
# STEP 2: IDENTIFY PRIMARY (AGRUPACION)
# Primary = highest VENTAS within (PAIS, FORMATO, ZONA, CODIGO_FAMILIA)
# Tiebreaker: lowest ITEM number (deterministic)
# ─────────────────────────────────────────────────────────────

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
    primary_price   = safe_float(sorted_grp[0]['PRECIO_GPI_C_IMP'])
    primary_ventas  = safe_float(sorted_grp[0]['VENTAS'], 0)
    primary_item    = sorted_grp[0]['ITEM']
    primary_desc    = sorted_grp[0]['DESCRIPCION']

    for r in sorted_grp[1:]:
        r['AGRUPACION'] = 'SECUNDARIO'

    for r in grp:
        r['PRECIO_PRIMARIO']  = str(primary_price) if primary_price is not None else ''
        r['ITEM_PRIMARIO']    = primary_item
        r['DESC_PRIMARIO']    = primary_desc
        r['VENTAS_PRIMARIO']  = str(primary_ventas)

        price = safe_float(r['PRECIO_GPI_C_IMP'])
        if primary_price is not None and price is not None:
            diff = round(price - primary_price, 4)
            r['DIFERENCIA_PRECIO'] = str(diff)
            r['ESTADO_PRECIO'] = 'Igual al Primario' if abs(diff) < 0.01 else 'Diferente al Primario'
        elif price is None:
            r['ESTADO_PRECIO']    = 'Sin Precio'
            r['DIFERENCIA_PRECIO'] = ''
        else:
            r['ESTADO_PRECIO']    = 'Sin Precio Primario'
            r['DIFERENCIA_PRECIO'] = ''

print("[STEP 2] AGRUPACION assigned (PRIMARIO / SECUNDARIO)")


# ─────────────────────────────────────────────────────────────
# STEP 3 + 4: ESTADO_PRECIO + ROTACION (already done above)
# ROTACIONES is the rotation field in the table
# ─────────────────────────────────────────────────────────────

for row in rows:
    row['ROTACION'] = row.get('ROTACIONES', '')

print("[STEP 3/4] ESTADO_PRECIO + ROTACION fields populated")


# ─────────────────────────────────────────────────────────────
# SUMMARY TABLE
# ─────────────────────────────────────────────────────────────

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

    precios = [safe_float(r['PRECIO_GPI_C_IMP']) for r in grp if safe_float(r['PRECIO_GPI_C_IMP']) is not None]
    n_precios_distintos = len(set(precios))

    iguales    = sum(1 for r in grp if r.get('ESTADO_PRECIO') == 'Igual al Primario')
    diferentes = sum(1 for r in grp if r.get('ESTADO_PRECIO') == 'Diferente al Primario')
    sin_precio = sum(1 for r in grp if r.get('ESTADO_PRECIO') in ('Sin Precio', 'Sin Precio Primario'))

    total_skus = len(grp)
    pct_alineacion = (iguales / total_skus * 100) if total_skus > 0 else 0

    # Count how many share each exact price (for peer-price clustering)
    price_count = defaultdict(list)
    for r in grp:
        p = safe_float(r['PRECIO_GPI_C_IMP'])
        if p is not None:
            price_count[p].append(r['ITEM'])

    # Observations
    obs = []
    if total_skus == 1:
        obs.append("Familia con un solo artículo")
    if primary_ventas == 0:
        obs.append("Primario sin ventas registradas")
    if sin_precio > 0:
        obs.append(f"{sin_precio} artículo(s) sin precio registrado")
    if n_precios_distintos > 2:
        obs.append(f"Alta dispersión: {n_precios_distintos} precios distintos")
    if diferentes > 0 and total_skus > 1:
        obs.append(f"{diferentes}/{total_skus} SKUs desalineados")

    marca      = primary.get('MARCA_DESC', '')
    fineline   = primary.get('FINELINE_DESC', '')
    cost_unit  = safe_float(primary.get('COST_UNIT'))
    n_fineline = primary.get('N_FINELINE', '')
    n_marca    = primary.get('N_MARCA', '')

    summary_by_family[gk] = {
        'PAIS': pais,
        'FORMATO': formato,
        'ZONA': zona,
        'CODIGO_FAMILIA': codigo_fam,
        'MARCA': marca,
        'FINELINE': fineline,
        'N_FINELINE': n_fineline,
        'N_MARCA': n_marca,
        'COST_UNIT': cost_unit,
        'TOTAL_SKUS': total_skus,
        'ITEM_PRIMARIO': primary_item,
        'DESC_PRIMARIO': primary_desc,
        'VENTAS_PRIMARIO': primary_ventas,
        'PRECIO_PRIMARIO': primary_price,
        'ROTACION_PRIMARIO': primary_rot,
        'N_PRECIOS_DISTINTOS': n_precios_distintos,
        'SKUS_IGUAL_PRECIO': iguales,
        'SKUS_DIFERENTE_PRECIO': diferentes,
        'SKUS_SIN_PRECIO': sin_precio,
        'PCT_ALINEACION': pct_alineacion,
        'PRICE_CLUSTERS': {str(k): v for k, v in price_count.items()},
        'OBSERVACIONES': ' | '.join(obs) if obs else 'OK',
    }

print(f"[SUMMARY] {len(summary_by_family)} family summaries built")


# ─────────────────────────────────────────────────────────────
# EXPORT DETAIL CSV
# ─────────────────────────────────────────────────────────────

new_cols = ['CODIGO_FAMILIA', 'AGRUPACION', 'ITEM_PRIMARIO', 'DESC_PRIMARIO',
            'VENTAS_PRIMARIO', 'PRECIO_PRIMARIO', 'ESTADO_PRECIO',
            'DIFERENCIA_PRECIO', 'ROTACION']
all_cols = original_fields + new_cols

with open('pricing_detail_output.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=all_cols, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(rows)

print("[EXPORT] pricing_detail_output.csv written")


# ─────────────────────────────────────────────────────────────
# EXPORT SUMMARY CSV
# ─────────────────────────────────────────────────────────────

summary_cols = [
    'PAIS', 'FORMATO', 'ZONA', 'CODIGO_FAMILIA', 'MARCA', 'FINELINE',
    'N_FINELINE', 'N_MARCA', 'COST_UNIT',
    'TOTAL_SKUS', 'ITEM_PRIMARIO', 'DESC_PRIMARIO', 'VENTAS_PRIMARIO',
    'PRECIO_PRIMARIO', 'ROTACION_PRIMARIO', 'N_PRECIOS_DISTINTOS',
    'SKUS_IGUAL_PRECIO', 'SKUS_DIFERENTE_PRECIO', 'SKUS_SIN_PRECIO',
    'PCT_ALINEACION', 'OBSERVACIONES',
]

with open('pricing_summary_output.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=summary_cols, extrasaction='ignore')
    writer.writeheader()
    for s in summary_by_family.values():
        writer.writerow(s)

print("[EXPORT] pricing_summary_output.csv written")


# ─────────────────────────────────────────────────────────────
# GLOBAL STATS for HTML
# ─────────────────────────────────────────────────────────────

total_skus         = len(rows)
total_fam          = len(summary_by_family)
fam_multi          = sum(1 for s in summary_by_family.values() if s['TOTAL_SKUS'] > 1)
fam_single         = total_fam - fam_multi
total_desalineados = sum(s['SKUS_DIFERENTE_PRECIO'] for s in summary_by_family.values())
total_iguales      = sum(s['SKUS_IGUAL_PRECIO'] for s in summary_by_family.values())
pct_global         = (total_iguales / total_skus * 100) if total_skus else 0
fam_perfectas      = sum(1 for s in summary_by_family.values() if s['SKUS_DIFERENTE_PRECIO'] == 0 and s['TOTAL_SKUS'] > 1)
fam_criticas       = sorted(
    [s for s in summary_by_family.values() if s['SKUS_DIFERENTE_PRECIO'] > 0],
    key=lambda x: (-x['SKUS_DIFERENTE_PRECIO'], -(x['VENTAS_PRIMARIO'] or 0))
)

print(f"\n{'='*60}")
print("GLOBAL STATS SUMMARY")
print(f"{'='*60}")
print(f"  Total SKUs        : {total_skus}")
print(f"  Total Familias    : {total_fam}")
print(f"  Fam. Multi-SKU    : {fam_multi}")
print(f"  Fam. Single-SKU   : {fam_single}")
print(f"  SKUs Alineados    : {total_iguales}")
print(f"  SKUs Desalineados : {total_desalineados}")
print(f"  % Alineación Glbl : {pct_global:.1f}%")
print(f"  Fam. 100% alneada : {fam_perfectas}")
print(f"  Fam. con desvíos  : {len(fam_criticas)}")


# ─────────────────────────────────────────────────────────────
# HTML REPORT
# ─────────────────────────────────────────────────────────────

# Serialize data for JS
detail_json   = json.dumps(rows, ensure_ascii=False, default=str)
summary_list  = list(summary_by_family.values())
summary_json  = json.dumps(summary_list, ensure_ascii=False, default=str)

# Summary rows HTML
def summary_rows_html(summaries):
    html = ''
    for s in sorted(summaries, key=lambda x: x['PCT_ALINEACION']):
        pct   = s['PCT_ALINEACION']
        bar_w = int(pct)
        if pct == 100:
            badge_cls  = 'badge-ok'
            bar_cls    = 'bar-ok'
        elif pct >= 50:
            badge_cls  = 'badge-warn'
            bar_cls    = 'bar-warn'
        else:
            badge_cls  = 'badge-err'
            bar_cls    = 'bar-err'

        single = '(familia única)' if s['TOTAL_SKUS'] == 1 else ''
        obs_short = s['OBSERVACIONES'][:60] + '…' if len(s['OBSERVACIONES']) > 60 else s['OBSERVACIONES']

        html += f"""
        <tr class="summary-row" data-family="{s['CODIGO_FAMILIA']}">
          <td class="font-mono text-xs">{s['CODIGO_FAMILIA']}</td>
          <td>{s['MARCA']}</td>
          <td class="text-xs text-gray-500">{s['FINELINE']}</td>
          <td class="text-right font-mono">{s['TOTAL_SKUS']}</td>
          <td class="text-right font-mono text-blue">{fmt_cur(s['PRECIO_PRIMARIO'])}</td>
          <td class="text-right font-mono">{s['N_PRECIOS_DISTINTOS']}</td>
          <td class="text-right text-green">{s['SKUS_IGUAL_PRECIO']}</td>
          <td class="text-right text-red">{s['SKUS_DIFERENTE_PRECIO']}</td>
          <td>
            <div class="bar-wrap" role="progressbar" aria-valuenow="{bar_w}" aria-valuemin="0" aria-valuemax="100">
              <div class="{bar_cls}" style="width:{bar_w}%"></div>
            </div>
            <span class="{badge_cls}">{fmt_pct(pct)}</span>
            {single}
          </td>
          <td class="text-xs obs-col" title="{s['OBSERVACIONES']}">{obs_short}</td>
        </tr>"""
    return html


def detail_rows_html(detail_rows):
    html = ''
    for r in detail_rows:
        agrup = r.get('AGRUPACION', '')
        estado = r.get('ESTADO_PRECIO', '')
        ventas = safe_float(r.get('VENTAS'))
        rot    = safe_float(r.get('ROTACIONES'))
        precio = safe_float(r.get('PRECIO_GPI_C_IMP'))
        pprim  = safe_float(r.get('PRECIO_PRIMARIO'))
        diff   = safe_float(r.get('DIFERENCIA_PRECIO'))
        estatus = r.get('ESTATUS', '')

        row_cls = ''
        if agrup == 'PRIMARIO':
            row_cls = 'row-primary'
        elif estado == 'Diferente al Primario':
            row_cls = 'row-diff'

        estado_badge = ''
        if estado == 'Igual al Primario':
            estado_badge = '<span class="badge-ok-sm"> Igual</span>'
        elif estado == 'Diferente al Primario':
            estado_badge = '<span class="badge-err-sm"> Diferente</span>'
        else:
            estado_badge = f'<span class="badge-warn-sm">{estado}</span>'

        agrup_badge = ''
        if agrup == 'PRIMARIO':
            agrup_badge = '<span class="badge-primary"> PRIMARIO</span>'
        else:
            agrup_badge = '<span class="badge-secondary">SECUNDARIO</span>'

        diff_str = ''
        if diff is not None and diff != 0:
            sign = '+' if diff > 0 else ''
            diff_str = f'<span class="{"text-red" if diff > 0 else "text-green"}">{sign}₡{diff:,.2f}</span>'

        html += f"""
        <tr class="detail-row {row_cls}" data-family="{r.get('CODIGO_FAMILIA','')}" data-estado="{estado}" data-agrupacion="{agrup}">
          <td class="font-mono text-xs">{r.get('CODIGO_FAMILIA','')}</td>
          <td>{agrup_badge}</td>
          <td class="font-mono text-xs">{r.get('ITEM','')}</td>
          <td class="desc-col" title="{r.get('DESCRIPCION','')}">{r.get('DESCRIPCION','')[:35]}{'…' if len(r.get('DESCRIPCION','')) > 35 else ''}</td>
          <td>{r.get('MARCA_DESC','')}</td>
          <td class="text-xs text-gray-500">{r.get('FINELINE_DESC','')[:25]}{'…' if len(r.get('FINELINE_DESC','')) > 25 else ''}</td>
          <td class="text-right font-mono font-bold text-blue">{fmt_cur(precio)}</td>
          <td class="text-right font-mono text-gray">{fmt_cur(pprim)}</td>
          <td>{diff_str if diff_str else '–'}</td>
          <td>{estado_badge}</td>
          <td class="text-right font-mono">{'₡{:,.0f}'.format(ventas) if ventas else '–'}</td>
          <td class="text-right font-mono">{'{:,.1f}'.format(rot) if rot is not None else '–'}</td>
          <td class="text-center"><span class="{'badge-ok-sm' if estatus=='A' else 'badge-err-sm'}">{estatus}</span></td>
        </tr>"""
    return html


# Sort detail rows: by family, then primary first, then by ventas desc
rows_sorted = sorted(rows, key=lambda r: (
    r.get('CODIGO_FAMILIA', ''),
    0 if r.get('AGRUPACION') == 'PRIMARIO' else 1,
    -safe_float(r.get('VENTAS'), 0)
))

HTML = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>Análisis de Familias de Precios — Tienda 4076 | SW 22 | 2026</title>
  <style>
    /* ── Walmart palette ── */
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
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Segoe UI', system-ui, sans-serif;
      background: var(--gray10);
      color: var(--gray160);
      font-size: 13px;
    }}

    /* ── HEADER ── */
    .header {{
      background: var(--blue);
      color: var(--white);
      padding: 20px 32px 16px;
      display: flex;
      align-items: center;
      gap: 16px;
    }}
    .header-logo {{ font-size: 2rem; }}
    .header-title h1 {{ font-size: 1.2rem; font-weight: 700; }}
    .header-title p  {{ font-size: 0.78rem; opacity: .85; margin-top: 2px; }}
    .header-badge {{
      margin-left: auto;
      background: var(--spark);
      color: var(--gray160);
      padding: 4px 12px;
      border-radius: 99px;
      font-size: 0.72rem;
      font-weight: 700;
    }}

    /* ── CONTENT ── */
    .content {{ max-width: 1400px; margin: 0 auto; padding: 20px 16px 40px; }}

    /* ── KPI CARDS ── */
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 12px;
      margin-bottom: 24px;
    }}
    .kpi-card {{
      background: var(--white);
      border-radius: 8px;
      padding: 14px 16px;
      box-shadow: 0 1px 4px rgba(0,0,0,.08);
      border-top: 3px solid var(--blue);
    }}
    .kpi-card.spark {{ border-top-color: var(--spark); }}
    .kpi-card.red   {{ border-top-color: var(--red); }}
    .kpi-card.green {{ border-top-color: var(--green); }}
    .kpi-card.warn  {{ border-top-color: var(--warn); }}
    .kpi-val  {{ font-size: 1.6rem; font-weight: 800; color: var(--blue); }}
    .kpi-card.spark .kpi-val {{ color: var(--warn); }}
    .kpi-card.red   .kpi-val {{ color: var(--red); }}
    .kpi-card.green .kpi-val {{ color: var(--green); }}
    .kpi-lbl  {{ font-size: 0.7rem; color: var(--gray100); margin-top: 2px; text-transform: uppercase; letter-spacing: .04em; }}

    /* ── SECTION TITLES ── */
    h2 {{
      font-size: 1rem;
      font-weight: 700;
      color: var(--blue);
      border-bottom: 2px solid var(--spark);
      padding-bottom: 6px;
      margin: 24px 0 12px;
    }}
    h3 {{ font-size: .85rem; font-weight: 600; margin: 16px 0 8px; color: var(--gray160); }}

    /* ── FILTERS BAR ── */
    .filters {{
      background: var(--white);
      border-radius: 8px;
      padding: 10px 14px;
      margin-bottom: 16px;
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      align-items: center;
      box-shadow: 0 1px 3px rgba(0,0,0,.07);
    }}
    .filters label {{ font-size: .72rem; color: var(--gray100); text-transform: uppercase; letter-spacing:.04em; }}
    .filters input, .filters select {{
      padding: 5px 9px;
      border: 1px solid var(--gray50);
      border-radius: 5px;
      font-size: .78rem;
      background: var(--gray10);
      color: var(--gray160);
    }}
    .filters input:focus, .filters select:focus {{
      outline: 2px solid var(--blue);
      border-color: var(--blue);
    }}
    .btn {{
      padding: 5px 14px;
      border-radius: 5px;
      border: none;
      cursor: pointer;
      font-size: .78rem;
      font-weight: 600;
      background: var(--blue);
      color: var(--white);
    }}
    .btn:hover {{ background: #0042b5; }}
    .btn.secondary {{ background: var(--gray10); color: var(--gray160); border: 1px solid var(--gray50); }}
    .btn.secondary:hover {{ background: var(--gray50); }}

    /* ── TABLES ── */
    .table-wrap {{
      background: var(--white);
      border-radius: 8px;
      box-shadow: 0 1px 4px rgba(0,0,0,.08);
      overflow: auto;
      margin-bottom: 20px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: .78rem;
    }}
    thead th {{
      background: var(--blue);
      color: var(--white);
      padding: 9px 10px;
      text-align: left;
      white-space: nowrap;
      position: sticky;
      top: 0;
      z-index: 2;
      cursor: pointer;
      user-select: none;
    }}
    thead th:hover {{ background: #0042b5; }}
    thead th::after {{ content: ' ⇅'; font-size:.65rem; opacity:.6; }}
    tbody tr {{ border-bottom: 1px solid var(--gray10); transition: background .1s; }}
    tbody tr:hover {{ background: #edf3ff; }}
    tbody td {{ padding: 7px 10px; }}

    /* Row variants */
    .row-primary {{ background: #fffbea; }}
    .row-primary:hover {{ background: #fff3c0; }}
    .row-diff {{ background: #fff2f2; }}
    .row-diff:hover {{ background: #ffe0e0; }}

    /* Badges */
    .badge-ok    {{ background:#e6f4ea; color:#1e6e2e; padding:2px 8px; border-radius:99px; font-size:.68rem; font-weight:600; }}
    .badge-warn  {{ background:#fff8e1; color:var(--warn); padding:2px 8px; border-radius:99px; font-size:.68rem; font-weight:600; }}
    .badge-err   {{ background:#fde8e8; color:var(--red); padding:2px 8px; border-radius:99px; font-size:.68rem; font-weight:600; }}
    .badge-ok-sm   {{ background:#e6f4ea; color:#1e6e2e; padding:1px 6px; border-radius:99px; font-size:.66rem; font-weight:600; white-space:nowrap; }}
    .badge-warn-sm {{ background:#fff8e1; color:var(--warn); padding:1px 6px; border-radius:99px; font-size:.66rem; font-weight:600; white-space:nowrap; }}
    .badge-err-sm  {{ background:#fde8e8; color:var(--red); padding:1px 6px; border-radius:99px; font-size:.66rem; font-weight:600; white-space:nowrap; }}
    .badge-primary   {{ background:#dbeafe; color:var(--blue); padding:1px 6px; border-radius:99px; font-size:.66rem; font-weight:700; white-space:nowrap; }}
    .badge-secondary {{ background:var(--gray10); color:var(--gray100); padding:1px 6px; border-radius:99px; font-size:.66rem; font-weight:600; white-space:nowrap; }}

    /* Progress bars */
    .bar-wrap {{ height:6px; background:var(--gray10); border-radius:99px; overflow:hidden; margin-bottom:3px; width:80px; display:inline-block; vertical-align:middle; }}
    .bar-ok   {{ height:6px; background:var(--green); border-radius:99px; }}
    .bar-warn {{ height:6px; background:var(--spark); border-radius:99px; }}
    .bar-err  {{ height:6px; background:var(--red); border-radius:99px; }}

    /* Utility */
    .text-right  {{ text-align:right; }}
    .text-center {{ text-align:center; }}
    .font-mono   {{ font-family:'Courier New',monospace; }}
    .font-bold   {{ font-weight:700; }}
    .text-blue   {{ color:var(--blue); }}
    .text-red    {{ color:var(--red); }}
    .text-green  {{ color:var(--green); }}
    .text-gray   {{ color:var(--gray100); }}
    .text-xs     {{ font-size:.7rem; }}

    /* ── OBSERVATIONS PANEL ── */
    .obs-panel {{
      background: var(--white);
      border-radius: 8px;
      box-shadow: 0 1px 4px rgba(0,0,0,.08);
      padding: 16px 20px;
      margin-bottom: 20px;
    }}
    .obs-item {{
      display: flex;
      align-items: flex-start;
      gap: 8px;
      padding: 8px 0;
      border-bottom: 1px solid var(--gray10);
      font-size: .8rem;
    }}
    .obs-item:last-child {{ border-bottom: none; }}
    .obs-icon {{ font-size: 1rem; flex-shrink: 0; }}

    /* ── SQL BLOCK ── */
    .sql-block {{
      background: #1e2029;
      color: #abb2bf;
      border-radius: 8px;
      padding: 14px 18px;
      font-family: 'Courier New', monospace;
      font-size: .72rem;
      overflow-x: auto;
      line-height: 1.6;
      margin-bottom: 20px;
    }}
    .sql-kw  {{ color: #c678dd; }}
    .sql-fn  {{ color: #61afef; }}
    .sql-str {{ color: #98c379; }}
    .sql-cm  {{ color: #5c6370; font-style:italic; }}

    /* ── TABS ── */
    .tabs {{ display:flex; gap:4px; margin-bottom:-1px; }}
    .tab {{
      padding: 8px 16px;
      border-radius: 6px 6px 0 0;
      border: 1px solid var(--gray50);
      border-bottom: none;
      cursor: pointer;
      font-size:.78rem;
      font-weight:600;
      background: var(--gray10);
      color: var(--gray100);
    }}
    .tab.active {{ background: var(--white); color: var(--blue); border-color: var(--gray50); }}
    .tab-panel {{ display:none; }}
    .tab-panel.active {{ display:block; }}

    /* ── FOOTER ── */
    .footer {{
      text-align: center;
      padding: 16px;
      font-size: .7rem;
      color: var(--gray100);
      border-top: 1px solid var(--gray50);
      margin-top: 24px;
    }}

    /* ── PRINT ── */
    @media print {{
      .filters, .btn, .tabs {{ display:none; }}
      .tab-panel {{ display:block !important; }}
      body {{ background: white; }}
    }}
  </style>
</head>
<body>

<header class="header" role="banner">
  <span class="header-logo" aria-hidden="true"></span>
  <div class="header-title">
    <h1>Análisis de Familias de Precios — Tienda 4076</h1>
    <p>SW 22 · 2026 · Categorías 894 &amp; 6987 · Costa Rica · Supermercados · Zona San José</p>
  </div>
  <span class="header-badge">Pricing Intelligence</span>
</header>

<main class="content" role="main">

  <!-- KPI CARDS -->
  <section aria-label="Indicadores clave">
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-val">{total_skus}</div>
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
        <div class="kpi-lbl">% Alineación Global</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-val">{fam_perfectas}</div>
        <div class="kpi-lbl">Fam. 100% Alineadas</div>
      </div>
      <div class="kpi-card warn">
        <div class="kpi-val">{len(fam_criticas)}</div>
        <div class="kpi-lbl">Fam. con Desvíos</div>
      </div>
      <div class="kpi-card red">
        <div class="kpi-val">{sum(1 for r in rows if not r.get('VENTAS'))}</div>
        <div class="kpi-lbl">SKUs sin Ventas</div>
      </div>
    </div>
  </section>

  <!-- OBSERVACIONES -->
  <h2> Observaciones y Supuestos del Análisis</h2>
  <div class="obs-panel" role="region" aria-label="Observaciones">

    <div class="obs-item">
      <span class="obs-icon"></span>
      <div><strong>Construcción de Familias:</strong> La llave de familia se construye con 5 campos: COST_UNIT + MARCA_DESC + N_MARCA + PAIS + N_FINELINE. Cada familia es única dentro del contexto (PAIS / FORMATO / ZONA). Se encontraron <strong>{total_fam} familias</strong>, de las cuales <strong>{fam_multi} contienen más de un SKU</strong> y <strong>{fam_single} son familias de un solo artículo</strong>.</div>
    </div>

    <div class="obs-item">
      <span class="obs-icon"></span>
      <div><strong>SKUs sin VENTAS ni ROTACIONES ({sum(1 for r in rows if not r.get('VENTAS'))}):</strong> {sum(1 for r in rows if not r.get('VENTAS'))} artículos no tienen ventas registradas en SW 22. En estos casos, VENTAS = 0 para efectos del ranking. Si un grupo completo no tiene ventas, el PRIMARIO se elige por ITEM más bajo (criterio determinístico). Esto puede indicar artículos inactivos (ESTATUS = I), artículos sin surtido en tienda, o productos con venta real = 0.</div>
    </div>

    <div class="obs-item">
      <span class="obs-icon"></span>
      <div><strong>Campo PRECIO_GPI_C_IMP:</strong> Es el precio de referencia para evaluar alineación. Este precio incluye impuestos (con IMP). Se usa como precio canónico de comparación dentro de cada familia.</div>
    </div>

    <div class="obs-item">
      <span class="obs-icon"></span>
      <div><strong>Empates de ventas:</strong> En caso de empate en VENTAS, el desempate se realiza usando el número de ITEM más bajo (ascendente). Este criterio es 100% determinístico y reproducible en SQL (<code>ROW_NUMBER() OVER(PARTITION BY ... ORDER BY VENTAS DESC, ITEM ASC)</code>).</div>
    </div>

    <div class="obs-item">
      <span class="obs-icon"></span>
      <div><strong>Dimensión única en el dataset:</strong> Todos los registros corresponden a PAIS=CR, FORMATO=SUPERMERCADOS, ZONA=SAN JOSE, TIENDA=4076. El análisis está preparado para escalar a múltiples países/formatos/zonas sin cambios en la lógica.</div>
    </div>

    <div class="obs-item">
      <span class="obs-icon"></span>
      <div><strong>Rotación:</strong> La tabla contiene el campo ROTACIONES como única métrica de rotación disponible. Se incluye directamente como ROTACION en la base de salida. {sum(1 for r in rows if not r.get('ROTACIONES'))} artículos tienen ROTACION nula (coincide con los artículos sin VENTAS, son artículos inactivos o sin movimiento).</div>
    </div>

    <div class="obs-item">
      <span class="obs-icon"></span>
      <div><strong>Categoría 894:</strong> El query incluyó CATEGORY_NBR IN (894, 6987). Los 162 registros encontrados pertenecen exclusivamente a la categoría 6987 (BEVERAGES - CARBONATED-D95). No se encontraron registros para la categoría 894 en esta tienda/semana/fecha.</div>
    </div>

    <div class="obs-item">
      <span class="obs-icon"></span>
      <div><strong>Tolerancia de precio:</strong> Se considera "Igual al Primario" cuando la diferencia absoluta entre PRECIO_GPI_C_IMP del artículo y el del primario es menor a ₡0.01. Esto maneja posibles imprecisiones de punto flotante.</div>
    </div>
  </div>

  <!-- TABS -->
  <div class="tabs" role="tablist">
    <button class="tab active" role="tab" aria-selected="true" onclick="showTab('tab-summary',this)"> Resumen Ejecutivo</button>
    <button class="tab" role="tab" aria-selected="false" onclick="showTab('tab-detail',this)"> Base Detallada</button>
    <button class="tab" role="tab" aria-selected="false" onclick="showTab('tab-sql',this)"> SQL Equivalente</button>
  </div>

  <!-- TAB: SUMMARY -->
  <div id="tab-summary" class="tab-panel active">
    <h2> Resumen Ejecutivo por Familia</h2>

    <div class="filters" role="search" aria-label="Filtros resumen">
      <label for="srch-fam">Familia / Marca</label>
      <input type="search" id="srch-fam" placeholder="Buscar…" oninput="filterSummary()" aria-label="Buscar familia o marca"/>
      <label for="sel-aln">Estado</label>
      <select id="sel-aln" onchange="filterSummary()" aria-label="Filtrar por estado de alineación">
        <option value="">Todos</option>
        <option value="100">100% Alineadas</option>
        <option value="partial">Parcialmente alineadas</option>
        <option value="none">Sin alineación</option>
        <option value="multi">Solo multi-SKU</option>
        <option value="single">Solo single-SKU</option>
      </select>
      <button class="btn secondary" onclick="resetFilters()">Limpiar filtros</button>
      <button class="btn" onclick="exportCSV('summary')">⬇ Exportar CSV</button>
      <span id="summary-count" aria-live="polite" style="font-size:.72rem;color:var(--gray100);margin-left:auto;"></span>
    </div>

    <div class="table-wrap">
      <table id="tbl-summary" aria-label="Resumen ejecutivo de familias de precios">
        <thead>
          <tr>
            <th onclick="sortTable('tbl-summary',0)">Código Familia</th>
            <th onclick="sortTable('tbl-summary',1)">Marca</th>
            <th onclick="sortTable('tbl-summary',2)">Fineline</th>
            <th onclick="sortTable('tbl-summary',3)">Total SKUs</th>
            <th onclick="sortTable('tbl-summary',4)">Precio Primario</th>
            <th onclick="sortTable('tbl-summary',5)">Precios Distintos</th>
            <th onclick="sortTable('tbl-summary',6)">SKUs Iguales</th>
            <th onclick="sortTable('tbl-summary',7)">SKUs Diferentes</th>
            <th onclick="sortTable('tbl-summary',8)">% Alineación</th>
            <th onclick="sortTable('tbl-summary',9)">Observaciones</th>
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
    <h2> Base Detallada — Todos los SKUs</h2>

    <div class="filters" role="search" aria-label="Filtros detalle">
      <label for="srch-det">Item / Descripción / Familia</label>
      <input type="search" id="srch-det" placeholder="Buscar…" oninput="filterDetail()" aria-label="Buscar en detalle"/>
      <label for="sel-agrup">Agrupación</label>
      <select id="sel-agrup" onchange="filterDetail()" aria-label="Filtrar por agrupación">
        <option value="">Todos</option>
        <option value="PRIMARIO"> Primario</option>
        <option value="SECUNDARIO">Secundario</option>
      </select>
      <label for="sel-estado">Estado Precio</label>
      <select id="sel-estado" onchange="filterDetail()" aria-label="Filtrar por estado de precio">
        <option value="">Todos</option>
        <option value="Igual al Primario">Igual al Primario</option>
        <option value="Diferente al Primario">Diferente al Primario</option>
        <option value="Sin Precio">Sin Precio</option>
      </select>
      <button class="btn secondary" onclick="resetDetailFilters()">Limpiar</button>
      <button class="btn" onclick="exportCSV('detail')">⬇ Exportar CSV</button>
      <span id="detail-count" aria-live="polite" style="font-size:.72rem;color:var(--gray100);margin-left:auto;"></span>
    </div>

    <div class="table-wrap" style="max-height:600px;overflow-y:auto;">
      <table id="tbl-detail" aria-label="Base detallada de SKUs con análisis de precios">
        <thead>
          <tr>
            <th onclick="sortTable('tbl-detail',0)">Código Familia</th>
            <th onclick="sortTable('tbl-detail',1)">Agrupación</th>
            <th onclick="sortTable('tbl-detail',2)">ITEM</th>
            <th onclick="sortTable('tbl-detail',3)">Descripción</th>
            <th onclick="sortTable('tbl-detail',4)">Marca</th>
            <th onclick="sortTable('tbl-detail',5)">Fineline</th>
            <th onclick="sortTable('tbl-detail',6)">Precio (GPI c/imp)</th>
            <th onclick="sortTable('tbl-detail',7)">Precio Primario</th>
            <th onclick="sortTable('tbl-detail',8)">Diferencia</th>
            <th onclick="sortTable('tbl-detail',9)">Estado Precio</th>
            <th onclick="sortTable('tbl-detail',10)">Ventas SW22</th>
            <th onclick="sortTable('tbl-detail',11)">Rotación</th>
            <th onclick="sortTable('tbl-detail',12)">Estatus</th>
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
    <h2> SQL Equivalente en BigQuery</h2>
    <p style="font-size:.8rem;color:var(--gray100);margin-bottom:12px;">
      Esta lógica reproduce exactamente el análisis de familias y puede ejecutarse directamente en BigQuery.
      Diseñado para ser escalable a múltiples países, formatos y zonas.
    </p>

    <h3>Paso 1 — Base con Código de Familia</h3>
    <div class="sql-block"><pre><span class="sql-kw">WITH</span> base <span class="sql-kw">AS</span> (
  <span class="sql-kw">SELECT</span>
    <span class="sql-cm">-- Dimensiones de scope</span>
    PAIS, FORMATO, NOMB_ZONE,
    <span class="sql-cm">-- Campos originales</span>
    *,
    <span class="sql-cm">-- STEP 1: Llave de familia (5 campos) dentro del scope</span>
    <span class="sql-fn">CONCAT</span>(
      <span class="sql-fn">CAST</span>(COD_PAIS    <span class="sql-kw">AS</span> STRING), <span class="sql-str">'_'</span>,
      <span class="sql-fn">CAST</span>(COD_FORMATO <span class="sql-kw">AS</span> STRING), <span class="sql-str">'_'</span>,
      <span class="sql-fn">CAST</span>(COD_ZONA   <span class="sql-kw">AS</span> STRING),  <span class="sql-str">'_'</span>,
      <span class="sql-fn">DENSE_RANK</span>() <span class="sql-kw">OVER</span>(
        <span class="sql-kw">PARTITION BY</span> COD_PAIS, COD_FORMATO, COD_ZONA
        <span class="sql-kw">ORDER BY</span> COST_UNIT, MARCA_DESC, N_MARCA, PAIS, N_FINELINE
      )
    ) <span class="sql-kw">AS</span> CODIGO_FAMILIA_RAW
  <span class="sql-kw">FROM</span> <span class="sql-str">`wmt-k1-cons-data-users.k1_adhoc_tables.prcng_info_cam_a0g0dn_3_insumos_tienda`</span>
  <span class="sql-kw">WHERE</span> store_nbr = 4076
    <span class="sql-kw">AND</span> EXTRACT_YR = 2026
    <span class="sql-kw">AND</span> SW = 22
    <span class="sql-kw">AND</span> EXTRACT_DATE = <span class="sql-str">"2026-06-29 00:00:00 UTC"</span>
    <span class="sql-kw">AND</span> CATEGORY_NBR <span class="sql-kw">IN</span> (894, 6987)
),

<span class="sql-cm">-- STEP 2: Identificar PRIMARIO (mayor ventas, tiebreak ITEM ASC)</span>
ranked <span class="sql-kw">AS</span> (
  <span class="sql-kw">SELECT</span>
    *,
    <span class="sql-fn">ROW_NUMBER</span>() <span class="sql-kw">OVER</span>(
      <span class="sql-kw">PARTITION BY</span> PAIS, FORMATO, NOMB_ZONE, CODIGO_FAMILIA_RAW
      <span class="sql-kw">ORDER BY</span>
        <span class="sql-fn">COALESCE</span>(VENTAS, 0) <span class="sql-kw">DESC</span>,
        ITEM <span class="sql-kw">ASC</span>     <span class="sql-cm">-- tiebreaker determinístico</span>
    ) <span class="sql-kw">AS</span> rn_primary
  <span class="sql-kw">FROM</span> base
),

<span class="sql-cm">-- STEP 3: Extraer datos del PRIMARIO para hacer join</span>
primarios <span class="sql-kw">AS</span> (
  <span class="sql-kw">SELECT</span>
    PAIS, FORMATO, NOMB_ZONE, CODIGO_FAMILIA_RAW,
    ITEM             <span class="sql-kw">AS</span> ITEM_PRIMARIO,
    DESCRIPCION      <span class="sql-kw">AS</span> DESC_PRIMARIO,
    PRECIO_GPI_C_IMP <span class="sql-kw">AS</span> PRECIO_PRIMARIO,
    VENTAS           <span class="sql-kw">AS</span> VENTAS_PRIMARIO,
    ROTACIONES       <span class="sql-kw">AS</span> ROTACION_PRIMARIO
  <span class="sql-kw">FROM</span> ranked
  <span class="sql-kw">WHERE</span> rn_primary = 1
),

<span class="sql-cm">-- STEP 4: Join y calcular ESTADO_PRECIO</span>
final <span class="sql-kw">AS</span> (
  <span class="sql-kw">SELECT</span>
    r.*,
    <span class="sql-fn">CONCAT</span>(<span class="sql-str">'FAM_'</span>, r.CODIGO_FAMILIA_RAW) <span class="sql-kw">AS</span> CODIGO_FAMILIA,
    <span class="sql-kw">CASE WHEN</span> r.rn_primary = 1 <span class="sql-kw">THEN</span> <span class="sql-str">'PRIMARIO'</span> <span class="sql-kw">ELSE</span> <span class="sql-str">'SECUNDARIO'</span> <span class="sql-kw">END</span> <span class="sql-kw">AS</span> AGRUPACION,
    p.ITEM_PRIMARIO,
    p.DESC_PRIMARIO,
    p.PRECIO_PRIMARIO,
    p.VENTAS_PRIMARIO,
    p.ROTACION_PRIMARIO,
    <span class="sql-kw">CASE</span>
      <span class="sql-kw">WHEN</span> r.PRECIO_GPI_C_IMP <span class="sql-kw">IS NULL</span> <span class="sql-kw">THEN</span> <span class="sql-str">'Sin Precio'</span>
      <span class="sql-kw">WHEN</span> p.PRECIO_PRIMARIO  <span class="sql-kw">IS NULL</span> <span class="sql-kw">THEN</span> <span class="sql-str">'Sin Precio Primario'</span>
      <span class="sql-kw">WHEN</span> <span class="sql-fn">ABS</span>(r.PRECIO_GPI_C_IMP - p.PRECIO_PRIMARIO) &lt; 0.01
                                         <span class="sql-kw">THEN</span> <span class="sql-str">'Igual al Primario'</span>
      <span class="sql-kw">ELSE</span>                                       <span class="sql-str">'Diferente al Primario'</span>
    <span class="sql-kw">END</span> <span class="sql-kw">AS</span> ESTADO_PRECIO,
    r.PRECIO_GPI_C_IMP - p.PRECIO_PRIMARIO <span class="sql-kw">AS</span> DIFERENCIA_PRECIO,
    r.ROTACIONES <span class="sql-kw">AS</span> ROTACION
  <span class="sql-kw">FROM</span> ranked r
  <span class="sql-kw">LEFT JOIN</span> primarios p
         <span class="sql-kw">USING</span> (PAIS, FORMATO, NOMB_ZONE, CODIGO_FAMILIA_RAW)
)

<span class="sql-cm">-- ══ SALIDA 1: Base Detallada ══</span>
<span class="sql-kw">SELECT</span> * <span class="sql-kw">FROM</span> final;


<span class="sql-cm">-- ══ SALIDA 2: Resumen Ejecutivo ══</span>
<span class="sql-kw">SELECT</span>
  PAIS, FORMATO, NOMB_ZONE <span class="sql-kw">AS</span> ZONA,
  CODIGO_FAMILIA,
  <span class="sql-fn">MAX</span>(MARCA_DESC)    <span class="sql-kw">AS</span> MARCA,
  <span class="sql-fn">MAX</span>(FINELINE_DESC) <span class="sql-kw">AS</span> FINELINE,
  <span class="sql-fn">COUNT</span>(*)           <span class="sql-kw">AS</span> TOTAL_SKUS,
  <span class="sql-fn">ANY_VALUE</span>(ITEM_PRIMARIO)    <span class="sql-kw">AS</span> ITEM_PRIMARIO,
  <span class="sql-fn">ANY_VALUE</span>(DESC_PRIMARIO)    <span class="sql-kw">AS</span> DESC_PRIMARIO,
  <span class="sql-fn">ANY_VALUE</span>(VENTAS_PRIMARIO)  <span class="sql-kw">AS</span> VENTAS_PRIMARIO,
  <span class="sql-fn">ANY_VALUE</span>(PRECIO_PRIMARIO)  <span class="sql-kw">AS</span> PRECIO_PRIMARIO,
  <span class="sql-fn">COUNT</span>(<span class="sql-kw">DISTINCT</span> PRECIO_GPI_C_IMP)                                <span class="sql-kw">AS</span> N_PRECIOS_DISTINTOS,
  <span class="sql-fn">COUNTIF</span>(ESTADO_PRECIO = <span class="sql-str">'Igual al Primario'</span>)                   <span class="sql-kw">AS</span> SKUS_IGUAL_PRECIO,
  <span class="sql-fn">COUNTIF</span>(ESTADO_PRECIO = <span class="sql-str">'Diferente al Primario'</span>)               <span class="sql-kw">AS</span> SKUS_DIFERENTE_PRECIO,
  <span class="sql-fn">COUNTIF</span>(ESTADO_PRECIO <span class="sql-kw">IN</span> (<span class="sql-str">'Sin Precio'</span>, <span class="sql-str">'Sin Precio Primario'</span>)) <span class="sql-kw">AS</span> SKUS_SIN_PRECIO,
  <span class="sql-fn">ROUND</span>(
    <span class="sql-fn">COUNTIF</span>(ESTADO_PRECIO = <span class="sql-str">'Igual al Primario'</span>) * 100.0 / <span class="sql-fn">COUNT</span>(*),
    2
  ) <span class="sql-kw">AS</span> PCT_ALINEACION
<span class="sql-kw">FROM</span> final
<span class="sql-kw">GROUP BY</span> 1,2,3,4
<span class="sql-kw">ORDER BY</span> PCT_ALINEACION <span class="sql-kw">ASC</span>;
</pre></div>
  </div>

</main>

<footer class="footer" role="contentinfo">
  Generado por Rintyn (Code Puppy) · Análisis de Pricing &amp; Familias · Tienda 4076 · SW 22 · {datetime.now().strftime('%Y-%m-%d %H:%M')} ·
  <strong>Datos:</strong> wmt-k1-cons-data-users.k1_adhoc_tables.prcng_info_cam_a0g0dn_3_insumos_tienda
</footer>

<script>
// ── DATA ──
const detailData   = {detail_json};
const summaryData  = {summary_json};

// ── TABS ──
function showTab(id, btn) {{
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t => {{ t.classList.remove('active'); t.setAttribute('aria-selected','false'); }});
  document.getElementById(id).classList.add('active');
  btn.classList.add('active');
  btn.setAttribute('aria-selected','true');
  updateCounts();
}}

// ── FILTERS ──
function filterSummary() {{
  const q    = (document.getElementById('srch-fam').value || '').toLowerCase();
  const aln  = document.getElementById('sel-aln').value;
  let count  = 0;
  document.querySelectorAll('#summary-body .summary-row').forEach(row => {{
    const txt = row.textContent.toLowerCase();
    const pct = parseFloat(row.querySelector('.bar-wrap')?.getAttribute('aria-valuenow') || 0);
    const skus = parseInt(row.cells[3].textContent) || 0;
    let vis = (!q || txt.includes(q));
    if (vis && aln === '100')     vis = pct === 100;
    if (vis && aln === 'partial') vis = pct > 0 && pct < 100;
    if (vis && aln === 'none')    vis = pct === 0;
    if (vis && aln === 'multi')   vis = skus > 1;
    if (vis && aln === 'single')  vis = skus === 1;
    row.style.display = vis ? '' : 'none';
    if (vis) count++;
  }});
  document.getElementById('summary-count').textContent = `${{count}} familia(s) mostrada(s)`;
}}

function filterDetail() {{
  const q       = (document.getElementById('srch-det').value || '').toLowerCase();
  const agrup   = document.getElementById('sel-agrup').value;
  const estado  = document.getElementById('sel-estado').value;
  let count     = 0;
  document.querySelectorAll('#detail-body .detail-row').forEach(row => {{
    const txt  = row.textContent.toLowerCase();
    const ag   = row.dataset.agrupacion || '';
    const es   = row.dataset.estado || '';
    let vis = (!q || txt.includes(q)) &&
              (!agrup || ag === agrup) &&
              (!estado || es === estado);
    row.style.display = vis ? '' : 'none';
    if (vis) count++;
  }});
  document.getElementById('detail-count').textContent = `${{count}} SKU(s) mostrado(s)`;
}}

function resetFilters() {{
  document.getElementById('srch-fam').value = '';
  document.getElementById('sel-aln').value  = '';
  filterSummary();
}}
function resetDetailFilters() {{
  document.getElementById('srch-det').value    = '';
  document.getElementById('sel-agrup').value   = '';
  document.getElementById('sel-estado').value  = '';
  filterDetail();
}}

// ── SORT ──
let sortDir = {{}};
function sortTable(tblId, col) {{
  const tbl  = document.getElementById(tblId);
  const tbody = tbl.querySelector('tbody');
  const rows = Array.from(tbody.querySelectorAll('tr'));
  const dir  = (sortDir[tblId + col] = !(sortDir[tblId + col]));
  rows.sort((a, b) => {{
    const av = a.cells[col]?.textContent.trim() || '';
    const bv = b.cells[col]?.textContent.trim() || '';
    const an = parseFloat(av.replace(/[^0-9.\-]/g,''));
    const bn = parseFloat(bv.replace(/[^0-9.\-]/g,''));
    if (!isNaN(an) && !isNaN(bn)) return dir ? an - bn : bn - an;
    return dir ? av.localeCompare(bv,'es') : bv.localeCompare(av,'es');
  }});
  rows.forEach(r => tbody.appendChild(r));
}}

// ── EXPORT CSV ──
function exportCSV(type) {{
  const data = type === 'summary' ? summaryData : detailData;
  if (!data || !data.length) return;
  const keys  = Object.keys(data[0]);
  const lines = [keys.join(',')];
  data.forEach(row => {{
    lines.push(keys.map(k => {{
      const v = row[k] == null ? '' : String(row[k]);
      return v.includes(',') || v.includes('"') || v.includes('\\n')
        ? `"${{v.replace(/"/g,'""')}}"` : v;
    }}).join(','));
  }});
  const blob = new Blob([lines.join('\\n')], {{type:'text/csv;charset=utf-8;'}});
  const a    = document.createElement('a');
  a.href     = URL.createObjectURL(blob);
  a.download = `pricing_${{type}}_store4076_sw22.csv`;
  a.click();
}}

// ── COUNTS ON LOAD ──
function updateCounts() {{
  filterSummary();
  filterDetail();
}}
updateCounts();
</script>
</body>
</html>"""

with open('pricing_families_report.html', 'w', encoding='utf-8') as f:
    f.write(HTML)

print(f"\n[DONE] pricing_families_report.html generated successfully!")
print(f"       Open: C:\\Users\\shern22\\Documents\\puppy_workspace\\pricing_families_report.html")

import re, json

with open('reporte_familias_precios.html', encoding='utf-8') as f:
    html = f.read()

print(f'Tamano: {len(html):,} chars')

# 1. Variables de datos definidas
for v in ['W_DET','W_FAM','W_PCK','W_DIR','W_CHL','W_ALI','W_NALI','W_PCTS','W_DONA']:
    found = f'var {v} =' in html
    print(f'  {"OK" if found else "FAIL"}  var {v}')

# 2. Variables usadas en LOGIC (no literal, sino como var JS)
for v in ['W_DET','W_FAM','W_PCK','W_DIR','W_CHL','W_ALI','W_NALI','W_PCTS','W_DONA']:
    count = html.count(v)
    print(f'  Ocurrencias de {v}: {count}')

# 3. IDs criticos
for eid in ['bd_det','bd_fam','bd_pck','pg_det','pg_fam','pg_pck',
            'sr_det','sr_fam','sr_pck','pa_det','pa_fam','pa_pck',
            'ch1','ch2','rc_det','rc_fam','rc_pck']:
    found = f"id='{eid}'" in html or f'id="{eid}"' in html
    print(f'  {"OK" if found else "FAIL"}  id={eid}')

# 4. Funciones JS
for fn in ['function render','function buildPager','function go',
           'function filt','function dlcsv','function tab',
           'window.addEventListener']:
    found = fn in html
    print(f'  {"OK" if found else "FAIL"}  {fn}')

# 5. Placeholders sin reemplazar (ninguno debe quedar)
for p in ['DATA_DET','DATA_FAM','DATA_PCK','LABELS','W_CHL = LABELS']:
    found = p in html
    print(f'  {"FAIL PLACEHOLDER SIN REEMPLAZAR" if found else "OK"}  {p}')

# 6. Parsear JSON de datos
scripts = re.findall(r'var (W_\w+)\s*=\s*(\[.*?\]);', html, re.DOTALL)
for name, data in scripts[:4]:
    try:
        parsed = json.loads(data)
        print(f'  OK  {name} JSON valido: {len(parsed)} filas')
    except Exception as e:
        print(f'  FAIL  {name} JSON error: {str(e)[:60]}')

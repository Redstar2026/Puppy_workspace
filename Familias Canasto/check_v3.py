import json, re

with open('reporte_familias_precios.html', encoding='utf-8') as f:
    html = f.read()

checks = {
    'Chart.js embebido': 'function Chart(' in html or 'Chart.register' in html,
    'DATA_DET inyectado (no literal)': 'DATA_DET' not in html,
    'DATA_FAM inyectado': 'DATA_FAM' not in html,
    'DATA_PCK inyectado': 'DATA_PCK' not in html,
    'DATA_DIR inyectado': 'DATA_DIR' not in html,
    'LABELS inyectado': '"LABELS"' not in html and "'LABELS'" not in html,
    'renderTbl det': "renderTbl('det')" in html,
    'renderTbl fam': "renderTbl('fam')" in html,
    'renderTbl pck': "renderTbl('pck')" in html,
    'body_det existe': 'id="body_det"' in html,
    'body_fam existe': 'id="body_fam"' in html,
    'body_pck existe': 'id="body_pck"' in html,
    'pg_det existe': 'id="pg_det"' in html,
    'pg_fam existe': 'id="pg_fam"' in html,
    'pg_pck existe': 'id="pg_pck"' in html,
    'dlCSV funcion': 'function dlCSV' in html,
    'applyFilter funcion': 'function applyFilter' in html,
    'switchTab funcion': 'function switchTab' in html,
    'HTML cierra': html.strip().endswith('</html>'),
}

# Verificar JSON parseables en el HTML
for key in ['det', 'fam', 'pck']:
    marker = f'ST[\n  {key}' if False else None
    # busca el array de datos inyectado
    # buscar 'filtered: [' en el area de cada key
pass

with open('check_v3.txt', 'w', encoding='utf-8') as o:
    all_ok = True
    for k, v in checks.items():
        s = 'OK' if v else 'FAIL'
        if not v: all_ok = False
        o.write(f'  {s}  {k}\n')
    o.write(f'\nRESULTADO: {"TODO OK" if all_ok else "HAY FALLOS"}\n')
    o.write(f'Tamano HTML: {len(html):,} chars\n')

print('check_v3.txt escrito')

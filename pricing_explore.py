import csv
from collections import defaultdict

rows = []
with open('prcng_info_store4076_sw22_cat894_6987.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

print(f'Total rows: {len(rows)}')

paises = set(r['PAIS'] for r in rows)
formatos = set(r['FORMATO'] for r in rows)
zonas = set(r['NOMB_ZONE'] for r in rows)
cats = set(r['CATEGORY_NBR'] for r in rows)

print(f'PAIS: {paises}')
print(f'FORMATO: {formatos}')
print(f'ZONAS: {zonas}')
print(f'CATEGORIES: {cats}')

ventas_nulls = sum(1 for r in rows if not r['VENTAS'])
rot_nulls = sum(1 for r in rows if not r['ROTACIONES'])
print(f'VENTAS nulls: {ventas_nulls}/{len(rows)}')
print(f'ROTACIONES nulls: {rot_nulls}/{len(rows)}')

families = defaultdict(list)
for r in rows:
    key = (r['PAIS'], r['FORMATO'], r['NOMB_ZONE'], r['COST_UNIT'], r['MARCA_DESC'], r['N_MARCA'], r['N_FINELINE'])
    families[key].append(r['ITEM'])

print(f'Unique families: {len(families)}')
multi = {k: v for k,v in families.items() if len(v) > 1}
print(f'Families with >1 item: {len(multi)}')
for k, v in list(multi.items())[:10]:
    print(f'  KEY={k}')
    print(f'  ITEMS={v}')

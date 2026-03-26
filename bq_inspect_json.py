import json, os
from collections import Counter

with open(r'C:\Users\shern22\Documents\puppy_workspace\query_index.json', encoding='utf-8') as f:
    data = json.load(f)

comps = sorted(set(r['competidor'] for r in data))
print('ALL COMPETIDORES (' + str(len(comps)) + '):')
for c in comps:
    print(' ', c)

size = os.path.getsize(r'C:\Users\shern22\Documents\puppy_workspace\query_index.json')
print(f'\nFile size: {size:,} bytes ({size/1024:.1f} KB)')

print('\nSAMPLE ROWS (first 3):')
for r in data[:3]:
    print(' ', r)

idx = [r['index_normal'] for r in data if r['index_normal'] is not None]
print(f'\nindex_normal stats across {len(idx)} non-null rows:')
print(f'  min={min(idx):.6f}  max={max(idx):.6f}  avg={sum(idx)/len(idx):.6f}')
print(f'  nulls={sum(1 for r in data if r["index_normal"] is None)}')

idx_o = [r['index_oferta'] for r in data if r['index_oferta'] is not None]
print(f'\nindex_oferta: {len(idx_o)} non-null rows out of {len(data)}')
if idx_o:
    print(f'  min={min(idx_o):.6f}  max={max(idx_o):.6f}  avg={sum(idx_o)/len(idx_o):.6f}')
print(f'  nulls={sum(1 for r in data if r["index_oferta"] is None)}')

pais_cnt = Counter(r['pais'] for r in data)
print('\nRows per pais:', dict(sorted(pais_cnt.items())))

comp_pais = {}
for r in data:
    comp_pais.setdefault(r['pais'], set()).add(r['competidor'])
print('\nCompetidores per pais:')
for p, cs in sorted(comp_pais.items()):
    print(f'  {p} ({len(cs)}): {sorted(cs)}')

print('\nDONE')

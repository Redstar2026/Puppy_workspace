"""Inspecciona la estructura de los JSONs de datos."""
import json

q1 = json.load(open('query1_semanal.json', encoding='utf-8'))
q3 = json.load(open('query3_mensual.json', encoding='utf-8'))

result = []

# --- Q1 info ---
r0 = q1[0]
result.append(f'Q1 total_rows={len(q1)}')
result.append(f'Q1 keys={list(r0.keys())}')
result.append(f'Q1 row0={r0}')

# Dias de semana unicos
dias = sorted(set(r.get('dia_semana', '') for r in q1))
result.append(f'Q1 dias_semana={dias}')

# Segmentos unicos
segs = sorted(set(r.get('segmento', '') for r in q1))
result.append(f'Q1 segmentos={segs}')

# Conteo por segmento
from collections import Counter
cnt_seg = Counter(r.get('segmento', '') for r in q1)
result.append(f'Q1 seg_counts={dict(cnt_seg)}')

# Conteo dias
cnt_dia = Counter(r.get('dia_semana', '') for r in q1)
result.append(f'Q1 dia_counts={dict(cnt_dia)}')

# Filas con cnt_precio_normal=0
ceros = sum(1 for r in q1 if not r.get('cnt_precio_normal'))
result.append(f'Q1 rows_cnt_normal_zero={ceros}')

# Meses y semanas
anos = sorted(set(r.get('ano') for r in q1))
result.append(f'Q1 anos={anos}')

# Q3 info
r0q3 = q3[0]
result.append(f'\nQ3 total_rows={len(q3)}')
result.append(f'Q3 keys={list(r0q3.keys())}')
result.append(f'Q3 row0={r0q3}')
cnt_seg3 = Counter(r.get('segmento', '') for r in q3)
result.append(f'Q3 seg_counts={dict(cnt_seg3)}')

out = '\n'.join(str(x) for x in result)
with open('debug_data_out.txt', 'w', encoding='utf-8') as f:
    f.write(out)
print('OK -> debug_data_out.txt')
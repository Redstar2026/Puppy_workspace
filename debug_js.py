"""Detecta errores de sintaxis JS en el reporte generado."""
import re, sys

html = open('reporte_precios_cam.html', encoding='utf-8').read()
m    = re.search(r'<script>(.*?)</script>', html, re.DOTALL)
if not m:
    print('ERROR: no se encontro bloque <script>')
    sys.exit(1)

js    = m.group(1)
lines = js.split('\n')

ob, cb = js.count('{'), js.count('}')
op, cp = js.count('('), js.count(')')

print(f'Lineas JS   : {len(lines)}')
print(f'Braces diff : {ob - cb}  ({ob} abiertas, {cb} cerradas)')
print(f'Parens diff : {op - cp}  ({op} abiertas, {cp} cerradas)')

# Buscar patrones conocidos de corrupcion
print('\n--- Patrones problematicos ---')
for i, l in enumerate(lines, 1):
    stripped = l.strip()
    bad = False
    reason = ''
    if 'ginPath' in l and 'beginPath' not in l:
        bad, reason = True, 'ginPath (ctx.be cortado)'
    if bad:
        print(f'  L{i:4d}: [{reason}] {stripped[:100]}')

# Buscar la seccion donut del archivo final - checar que esta cerrada
idx_donut = next((i for i,l in enumerate(lines,1) if 'donut' in l and 'function' in l.lower()), None)
idx_end   = next((i for i,l in enumerate(lines[idx_donut:],idx_donut+1) if l.strip()=='}();'), None) if idx_donut else None
print(f'\nFuncion donut empieza en L{idx_donut}')
print(f'IIFE cierre en L{idx_end}')

# Mostrar las ultimas 15 lineas del script para verificar cierre
print('\n--- Ultimas 15 lineas del JS ---')
for i, l in enumerate(lines[-15:], len(lines)-14):
    print(f'  L{i:4d}: {l}')
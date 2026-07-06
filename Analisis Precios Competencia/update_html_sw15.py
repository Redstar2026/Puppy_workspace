"""
update_html_sw15.py
Actualiza el HTML competitive_analysis_report.html de SW11-SW14 → SW12-SW15.
Usa placeholders para no hacer double-replace.
"""
import re

IN  = r"C:\Users\shern22\Documents\puppy_workspace\Analisis Precios Competencia\competitive_analysis_report.html"
OUT = r"C:\Users\shern22\Documents\puppy_workspace\Analisis Precios Competencia\competitive_analysis_SW15.html"

with open(IN, encoding="utf-8") as f:
    html = f.read()

# ─── PASO 1: Rolling window con placeholders (SW11→12, SW12→13, SW13→14, SW14→15) ───
# Hacerlo PRIMERO para no corromper los resultados intermedios.
html = html.replace("SW11", "PLAC12")
html = html.replace("SW12", "PLAC13")
html = html.replace("SW13", "PLAC14")
html = html.replace("SW14", "PLAC15")

html = html.replace("PLAC12", "SW12")
html = html.replace("PLAC13", "SW13")
html = html.replace("PLAC14", "SW14")
html = html.replace("PLAC15", "SW15")

# ─── PASO 2: Patrones numéricos sin prefijo SW (deltas, CSV headers) ──────────
# Estos NO son afectados por el rolling window de arriba (no tienen "SW" delante).
html = html.replace("14v13",  "15v14")
html = html.replace("14v12",  "15v13")
html = html.replace("14/13",  "15/14")
html = html.replace("14/12",  "15/13")

# Textos libres con números sueltos (sin prefijo SW)
html = html.replace("Semanas 11-14", "Semanas 12-15")
html = html.replace("11-14 ·",       "12-15 ·")

# ─── PASO 3: Metadatos de fecha ────────────────────────────────────────
html = html.replace(
    "Generado: 2026-05-13 15:51",
    "Generado: 2026-05-15"
)

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

print(f"[OK] Guardado: {OUT}", flush=True)
print(f"     Chars: {len(html):,}", flush=True)

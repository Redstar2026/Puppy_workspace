"""
Script para unir los 5 archivos JSON de drivers (uno por pais) en un solo archivo FULL.
CR + GT + HN + NI + SV -> drivers-categoria-escenario-FULL.json
"""

import json
from pathlib import Path

BASE_DIR = Path(r"C:\Users\shern22\Documents\puppy_workspace\bigquery_results")

PAIS_FILES = {
    "CR": BASE_DIR / "drivers-CR.json",
    "GT": BASE_DIR / "drivers-GT.json",
    "HN": BASE_DIR / "drivers-hn-20260521-204343.json",
    "NI": BASE_DIR / "drivers-NI.json",
    "SV": BASE_DIR / "drivers-SV.json",
}
OUTPUT     = BASE_DIR / "drivers-categoria-escenario-FULL.json"
ITEMS_FILE = BASE_DIR / "items-microdetalle-escenario-20260521-204027.json"

print("Cargando archivos por pais...")
drivers_full = []
for pais, filepath in PAIS_FILES.items():
    with open(filepath, encoding="utf-8-sig") as f:
        data = json.load(f)
    print(f"  {pais}: {len(data):,} filas  <- {filepath.name}")
    wrong = [r for r in data if r.get("PAIS") != pais]
    if wrong:
        print(f"  AVISO: {len(wrong)} filas con PAIS incorrecto en {pais}")
    drivers_full.extend(data)

# Ordenar igual que la query original
drivers_full.sort(key=lambda r: (
    r.get("PAIS", ""),
    r.get("FORMATO", ""),
    r.get("DIVISION", ""),
    r.get("CATEGORIA", ""),
    r.get("ESCENARIO", ""),
))
print(f"\n  TOTAL combinado: {len(drivers_full):,} filas")

# Guardar UTF-8
with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(drivers_full, f, ensure_ascii=False, indent=2)
print(f"\n[OK] Drivers FULL guardado -> {OUTPUT}")

# Verificar items file
with open(ITEMS_FILE, encoding="utf-8") as f:
    items = json.load(f)
print(f"[OK] Items microdetalle  -> {len(items):,} filas  ({ITEMS_FILE.name})")

# Resumen
paises     = sorted(set(r["PAIS"]      for r in drivers_full))
escenarios = sorted(set(r["ESCENARIO"] for r in drivers_full))
divisiones = sorted(set(r["DIVISION"]  for r in drivers_full))
categorias = len(set(r["CATEGORIA"]    for r in drivers_full))

print(f"\n[RESUMEN] Drivers FULL:")
print(f"  Paises:     {paises}")
print(f"  Escenarios: {escenarios}")
print(f"  Divisiones: {divisiones}")
print(f"  Categorias: {categorias} unicas")
print(f"\n[ARCHIVOS LISTOS PARA REPORTE HTML]")
print(f"  QUERY 1 (drivers) -> {OUTPUT}")
print(f"  QUERY 2 (items)   -> {ITEMS_FILE}")

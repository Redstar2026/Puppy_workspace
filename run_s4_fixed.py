# /// script
# requires-python = ">=3.9"
# dependencies = ["google-cloud-bigquery"]
# ///
"""
Query S4 corregida: CATEGORIA agregada a subqueries internas.
"""

import json
from pathlib import Path
from google.cloud import bigquery

PROJECT = "wmt-k1-cons-data-users"
OUT_DIR = Path(r"C:\Users\shern22\Documents\puppy_workspace\bigquery_results")

client = bigquery.Client(project=PROJECT)

T_CON = "`wmt-k1-cons-data-users.k1_adhoc_tables.MEDICION_LOW_A0M1J1N`"
T_SIN = "`wmt-k1-cons-data-users.k1_adhoc_tables.prcng_info_cam_a0m1j1n_medicion_low_v2`"
IDS   = "(228,229,230,231)"

# ── S4 corregida: CATEGORIA incluida en subqueries ─────────────────────────
# Fix: se agregó CATEGORIA al SELECT y GROUP BY de ambas subqueries internas

SQL_S4 = f"""
SELECT ITEM, PAIS,
  MAX(ITEM_DESCRIP) AS ITEM_DESCRIP,
  MAX(CATEGORIA)    AS CATEGORIA,
  COMPETIDOR,
  MAX(CASE WHEN FUENTE = 'CON COD CANASTO' THEN 'SI' ELSE NULL END) AS EN_CON,
  MAX(CASE WHEN FUENTE = 'SIN COD CANASTO' THEN 'SI' ELSE NULL END) AS EN_SIN,
  CASE
    WHEN MAX(CASE WHEN FUENTE = 'CON COD CANASTO' THEN 1 ELSE 0 END) = 1
     AND MAX(CASE WHEN FUENTE = 'SIN COD CANASTO' THEN 1 ELSE 0 END) = 1
     THEN 'AMBAS FUENTES'
    WHEN MAX(CASE WHEN FUENTE = 'CON COD CANASTO' THEN 1 ELSE 0 END) = 1
     THEN 'SOLO CON COD CANASTO'
    ELSE 'SOLO SIN COD CANASTO'
  END AS ESTADO
FROM (
  -- CON COD CANASTO: CATEGORIA incluida para que MAX(CATEGORIA) funcione afuera
  SELECT "CON COD CANASTO" AS FUENTE, ITEM, PAIS, ITEM_DESCRIP, CATEGORIA, COMPETIDOR
  FROM {T_CON}
  WHERE ID_SW IN {IDS}
  GROUP BY FUENTE, ITEM, PAIS, ITEM_DESCRIP, CATEGORIA, COMPETIDOR

  UNION ALL

  -- SIN COD CANASTO: ídem
  SELECT "SIN COD CANASTO" AS FUENTE, ITEM, PAIS, ITEM_DESCRIP, CATEGORIA, COMPETIDOR
  FROM {T_SIN}
  WHERE ID_SW IN {IDS}
  GROUP BY FUENTE, ITEM, PAIS, ITEM_DESCRIP, CATEGORIA, COMPETIDOR
)
GROUP BY ITEM, PAIS, COMPETIDOR
ORDER BY ITEM, PAIS, COMPETIDOR
LIMIT 50000
"""

print("=" * 65)
print("S4 — Competidores por item/fuente (query corregida)")
print(f"ID_SW: {IDS}  |  Proyecto: {PROJECT}")
print("=" * 65)

print("\n[S4] Ejecutando...", flush=True)
job  = client.query(SQL_S4)
rows = list(job.result())
data = [dict(r) for r in rows]

# Resumen rápido de ESTADO antes de guardar
from collections import Counter
estados = Counter(r["ESTADO"] for r in data)
print(f"  -> {len(data):,} filas totales")
for estado, cnt in sorted(estados.items()):
    print(f"     {estado}: {cnt:,}")

path = OUT_DIR / "s4_competidores.json"
with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2, default=str)

mb = path.stat().st_size / 1_048_576
print(f"\n  -> {mb:.2f} MB | guardado: s4_competidores.json")
print(f"     Ruta: {path}")

# ── Verificar archivos generados en sesión ─────────────────────────────────
print("\n" + "=" * 65)
print("TODOS LOS ARCHIVOS GENERADOS EN ESTA SESION:")
print("=" * 65)
for f in ["s1a_pais.json","s1b_div.json","s1c_cat.json","s1d_tier.json",
          "s2_categorias.json","s3_lineas_item.json","s4_competidores.json"]:
    p = OUT_DIR / f
    if p.exists():
        sz = p.stat().st_size / 1_048_576
        data_check = json.loads(p.read_text(encoding="utf-8"))
        print(f"  {f:<30} {len(data_check):>7,} filas  {sz:>6.2f} MB  ✅")
    else:
        print(f"  {f:<30} ❌ NO ENCONTRADO")

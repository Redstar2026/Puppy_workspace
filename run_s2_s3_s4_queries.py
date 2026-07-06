# /// script
# requires-python = ">=3.9"
# dependencies = ["google-cloud-bigquery"]
# ///
"""
Queries S2, S3, S4 del reporte comparativo CON vs SIN COD CANASTO.
ID_SW: 228, 229, 230, 231
"""

import json
from pathlib import Path
from google.cloud import bigquery

PROJECT = "wmt-k1-cons-data-users"
OUT_DIR = Path(r"C:\Users\shern22\Documents\puppy_workspace\bigquery_results")
OUT_DIR.mkdir(exist_ok=True)

client = bigquery.Client(project=PROJECT)

T_CON = "`wmt-k1-cons-data-users.k1_adhoc_tables.MEDICION_LOW_A0M1J1N`"
T_SIN = "`wmt-k1-cons-data-users.k1_adhoc_tables.prcng_info_cam_a0m1j1n_medicion_low_v2`"
IDS   = "(228,229,230,231)"


def run_and_save(label: str, sql: str, out_file: str):
    print(f"\n[{label}] Ejecutando...", flush=True)
    job  = client.query(sql)
    rows = list(job.result())
    data = [dict(r) for r in rows]
    path = OUT_DIR / out_file
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    mb = path.stat().st_size / 1_048_576
    print(f"  -> {len(data):,} filas | {mb:.2f} MB | {out_file}", flush=True)
    return len(data)


# ── S2: PAIS + DIVISION_COMERCIAL + CATEGORIA ──────────────────────────────

SQL_S2 = f"""
SELECT FUENTE, PAIS, DIVISION_COMERCIAL, CATEGORIA,
  SUM(FACTOR_CALC) / NULLIF(SUM(PESO_CALC),    0) AS PG_MB,
  SUM(MB_CALC)     / NULLIF(SUM(PARTICIPA_CALC),0) AS MBMB,
  COUNT(DISTINCT ITEM) AS ITEMS,
  COUNT(*)             AS LINEAS
FROM (
  SELECT "CON COD CANASTO" AS FUENTE, ITEM, PAIS, DIVISION_COMERCIAL, CATEGORIA,
    FACTOR_CALC, PESO_CALC, PARTICIPA_CALC, MB_CALC
  FROM {T_CON} WHERE ID_SW IN {IDS}
  UNION ALL
  SELECT "SIN COD CANASTO" AS FUENTE, ITEM, PAIS, DIVISION_COMERCIAL, CATEGORIA,
    FACTOR_CALC, PESO_CALC, PARTICIPA_CALC, MB_CALC
  FROM {T_SIN} WHERE ID_SW IN {IDS}
)
GROUP BY FUENTE, PAIS, DIVISION_COMERCIAL, CATEGORIA
ORDER BY PAIS, DIVISION_COMERCIAL, CATEGORIA, FUENTE
"""

# ── S3: Items con delta de lineas entre fuentes ────────────────────────────

SQL_S3 = f"""
SELECT ITEM, PAIS, CATEGORIA, DIVISION_COMERCIAL,
  MAX(ITEM_DESCRIP) AS ITEM_DESCRIP,
  SUM(CASE WHEN FUENTE = 'CON COD CANASTO' THEN LINEAS ELSE 0 END) AS LINEAS_CON,
  SUM(CASE WHEN FUENTE = 'SIN COD CANASTO' THEN LINEAS ELSE 0 END) AS LINEAS_SIN,
  SUM(CASE WHEN FUENTE = 'CON COD CANASTO' THEN LINEAS ELSE 0 END)
  - SUM(CASE WHEN FUENTE = 'SIN COD CANASTO' THEN LINEAS ELSE 0 END) AS DELTA_LINEAS
FROM (
  SELECT "CON COD CANASTO" AS FUENTE, ITEM, PAIS, CATEGORIA, DIVISION_COMERCIAL,
    MAX(ITEM_DESCRIP) AS ITEM_DESCRIP, COUNT(*) AS LINEAS
  FROM {T_CON} WHERE ID_SW IN {IDS}
  GROUP BY FUENTE, ITEM, PAIS, CATEGORIA, DIVISION_COMERCIAL
  UNION ALL
  SELECT "SIN COD CANASTO" AS FUENTE, ITEM, PAIS, CATEGORIA, DIVISION_COMERCIAL,
    MAX(ITEM_DESCRIP) AS ITEM_DESCRIP, COUNT(*) AS LINEAS
  FROM {T_SIN} WHERE ID_SW IN {IDS}
  GROUP BY FUENTE, ITEM, PAIS, CATEGORIA, DIVISION_COMERCIAL
)
GROUP BY ITEM, PAIS, CATEGORIA, DIVISION_COMERCIAL
HAVING DELTA_LINEAS != 0
ORDER BY ABS(DELTA_LINEAS) DESC
LIMIT 5000
"""

# ── S4: Competidores por item en cada fuente ───────────────────────────────

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
  SELECT "CON COD CANASTO" AS FUENTE, ITEM, PAIS, ITEM_DESCRIP, COMPETIDOR
  FROM {T_CON} WHERE ID_SW IN {IDS}
  GROUP BY FUENTE, ITEM, PAIS, ITEM_DESCRIP, COMPETIDOR
  UNION ALL
  SELECT "SIN COD CANASTO" AS FUENTE, ITEM, PAIS, ITEM_DESCRIP, COMPETIDOR
  FROM {T_SIN} WHERE ID_SW IN {IDS}
  GROUP BY FUENTE, ITEM, PAIS, ITEM_DESCRIP, COMPETIDOR
)
GROUP BY ITEM, PAIS, COMPETIDOR
ORDER BY ITEM, PAIS, COMPETIDOR
LIMIT 50000
"""

# ── Ejecutar ───────────────────────────────────────────────────────────────

print("=" * 65)
print("QUERIES S2 / S3 / S4 — CON COD CANASTO vs SIN COD CANASTO")
print(f"ID_SW: {IDS}  |  Proyecto: {PROJECT}")
print("=" * 65)

results = {}
results["S2"] = run_and_save("S2 - PAIS+DIV+CAT (todas)",       SQL_S2, "s2_categorias.json")
results["S3"] = run_and_save("S3 - Items con delta de lineas",   SQL_S3, "s3_lineas_item.json")
results["S4"] = run_and_save("S4 - Competidores por item/fuente",SQL_S4, "s4_competidores.json")

print("\n" + "=" * 65)
print("RESUMEN FINAL")
print("=" * 65)
for k, n in results.items():
    print(f"  {k}: {n:,} filas")
print(f"\nArchivos en: {OUT_DIR}")

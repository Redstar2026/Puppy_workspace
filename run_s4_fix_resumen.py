# /// script
# requires-python = ">=3.9"
# dependencies = ["google-cloud-bigquery"]
# ///
"""
S4_FIX  — Solo combinaciones item+competidor que NO estan en ambas fuentes.
S4_RESUMEN — Conteo global de combinaciones por ESTADO.
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
    return data


# ── S4_FIX: solo SOLO CON o SOLO SIN ──────────────────────────────────────

SQL_S4_FIX = f"""
SELECT
  ITEM, PAIS,
  MAX(ITEM_DESCRIP)      AS ITEM_DESCRIP,
  MAX(CATEGORIA)         AS CATEGORIA,
  MAX(DIVISION_COMERCIAL) AS DIVISION,
  COMPETIDOR,
  MAX(CASE WHEN FUENTE = 'CON COD CANASTO' THEN 'SI' ELSE 'NO' END) AS EN_CON,
  MAX(CASE WHEN FUENTE = 'SIN COD CANASTO' THEN 'SI' ELSE 'NO' END) AS EN_SIN,
  CASE
    WHEN MAX(CASE WHEN FUENTE = 'CON COD CANASTO' THEN 1 ELSE 0 END) = 1
     AND MAX(CASE WHEN FUENTE = 'SIN COD CANASTO' THEN 1 ELSE 0 END) = 1
     THEN 'AMBAS FUENTES'
    WHEN MAX(CASE WHEN FUENTE = 'CON COD CANASTO' THEN 1 ELSE 0 END) = 1
     THEN 'SOLO CON COD CANASTO'
    ELSE 'SOLO SIN COD CANASTO'
  END AS ESTADO
FROM (
  SELECT "CON COD CANASTO" AS FUENTE,
    ITEM, PAIS, ITEM_DESCRIP, CATEGORIA, COMPETIDOR, DIVISION_COMERCIAL
  FROM {T_CON} WHERE ID_SW IN {IDS}
  GROUP BY FUENTE, ITEM, PAIS, ITEM_DESCRIP, CATEGORIA, COMPETIDOR, DIVISION_COMERCIAL

  UNION ALL

  SELECT "SIN COD CANASTO" AS FUENTE,
    ITEM, PAIS, ITEM_DESCRIP, CATEGORIA, COMPETIDOR, DIVISION_COMERCIAL
  FROM {T_SIN} WHERE ID_SW IN {IDS}
  GROUP BY FUENTE, ITEM, PAIS, ITEM_DESCRIP, CATEGORIA, COMPETIDOR, DIVISION_COMERCIAL
)
GROUP BY ITEM, PAIS, COMPETIDOR
HAVING ESTADO != 'AMBAS FUENTES'
ORDER BY ESTADO, ITEM, PAIS, COMPETIDOR
LIMIT 10000
"""

# ── S4_RESUMEN: conteo global por ESTADO ──────────────────────────────────

SQL_S4_RESUMEN = f"""
SELECT
  ESTADO,
  COUNT(*)            AS COMBINACIONES,
  COUNT(DISTINCT ITEM) AS ITEMS_UNICOS
FROM (
  SELECT ITEM, PAIS, COMPETIDOR,
    CASE
      WHEN MAX(CASE WHEN FUENTE = 'CON COD CANASTO' THEN 1 ELSE 0 END) = 1
       AND MAX(CASE WHEN FUENTE = 'SIN COD CANASTO' THEN 1 ELSE 0 END) = 1
       THEN 'AMBAS FUENTES'
      WHEN MAX(CASE WHEN FUENTE = 'CON COD CANASTO' THEN 1 ELSE 0 END) = 1
       THEN 'SOLO CON COD CANASTO'
      ELSE 'SOLO SIN COD CANASTO'
    END AS ESTADO
  FROM (
    SELECT "CON COD CANASTO" AS FUENTE, ITEM, PAIS, COMPETIDOR
    FROM {T_CON} WHERE ID_SW IN {IDS}
    UNION ALL
    SELECT "SIN COD CANASTO" AS FUENTE, ITEM, PAIS, COMPETIDOR
    FROM {T_SIN} WHERE ID_SW IN {IDS}
  )
  GROUP BY ITEM, PAIS, COMPETIDOR
)
GROUP BY ESTADO
ORDER BY ESTADO
"""

# ── Ejecutar ───────────────────────────────────────────────────────────────

print("=" * 65)
print("S4_FIX + S4_RESUMEN  |  CON vs SIN COD CANASTO")
print(f"ID_SW: {IDS}  |  Proyecto: {PROJECT}")
print("=" * 65)

data_fix    = run_and_save("S4_FIX    - Solo diferencias",   SQL_S4_FIX,    "s4_diferencias.json")
data_resumen = run_and_save("S4_RESUMEN - Conteo por estado", SQL_S4_RESUMEN, "s4_resumen.json")

# ── Preview inline ─────────────────────────────────────────────────────────

print("\n--- S4_RESUMEN ---")
for r in data_resumen:
    print(f"  {r['ESTADO']:<25}  {r['COMBINACIONES']:>10,} combinaciones  "
          f"{r['ITEMS_UNICOS']:>7,} items unicos")

print("\n--- S4_FIX: primeros 20 ---")
for r in data_fix[:20]:
    print(f"  [{r['ESTADO']}]  ITEM={r['ITEM']}  PAIS={r['PAIS']}  "
          f"COMP={r['COMPETIDOR']}  |  {r.get('ITEM_DESCRIP','')[:40]}")

print("\n--- S4_FIX: distribucion por ESTADO ---")
from collections import Counter
estados = Counter(r["ESTADO"] for r in data_fix)
for estado, cnt in sorted(estados.items()):
    print(f"  {estado}: {cnt:,}")

print("\n--- S4_FIX: distribucion por PAIS ---")
paises = Counter(r["PAIS"] for r in data_fix)
for pais, cnt in sorted(paises.items()):
    print(f"  {pais}: {cnt:,}")

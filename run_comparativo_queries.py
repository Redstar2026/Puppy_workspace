# /// script
# requires-python = ">=3.9"
# dependencies = ["google-cloud-bigquery"]
# ///
"""
Ejecuta las 4 queries del reporte comparativo CON vs SIN COD CANASTO
y guarda los resultados como JSON en bigquery_results/.
"""

import json
from pathlib import Path
from google.cloud import bigquery

PROJECT  = "wmt-k1-cons-data-users"
OUT_DIR  = Path(r"C:\Users\shern22\Documents\puppy_workspace\bigquery_results")
OUT_DIR.mkdir(exist_ok=True)

client = bigquery.Client(project=PROJECT)

# ── helpers ────────────────────────────────────────────────────────────────

def run_and_save(label: str, sql: str, out_file: str):
    print(f"\n[{label}] Ejecutando...", flush=True)
    job = client.query(sql)
    rows = list(job.result())
    data = [dict(r) for r in rows]
    path = OUT_DIR / out_file
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    print(f"  -> {len(data):,} filas  | guardado: {out_file}", flush=True)
    return len(data)

# ── SQL de las tablas fuente ────────────────────────────────────────────────

T_CON = "`wmt-k1-cons-data-users.k1_adhoc_tables.MEDICION_LOW_A0M1J1N`"
T_SIN = "`wmt-k1-cons-data-users.k1_adhoc_tables.prcng_info_cam_a0m1j1n_medicion_low_v2`"
IDS   = "(228,229,230,231)"

# ── S1A: por PAIS ──────────────────────────────────────────────────────────

SQL_S1A = f"""
SELECT FUENTE, PAIS,
  SUM(FACTOR_CALC) / NULLIF(SUM(PESO_CALC),    0) AS PG_MB,
  SUM(MB_CALC)     / NULLIF(SUM(PARTICIPA_CALC),0) AS MBMB,
  COUNT(DISTINCT ITEM) AS ITEMS,
  COUNT(*)             AS LINEAS
FROM (
  SELECT "CON COD CANASTO" AS FUENTE, ITEM, PAIS,
    FACTOR_CALC, PESO_CALC, PARTICIPA_CALC, MB_CALC
  FROM {T_CON} WHERE ID_SW IN {IDS}
  UNION ALL
  SELECT "SIN COD CANASTO" AS FUENTE, ITEM, PAIS,
    FACTOR_CALC, PESO_CALC, PARTICIPA_CALC, MB_CALC
  FROM {T_SIN} WHERE ID_SW IN {IDS}
)
GROUP BY FUENTE, PAIS
ORDER BY PAIS, FUENTE
"""

# ── S1B: por PAIS + DIVISION_COMERCIAL ─────────────────────────────────────

SQL_S1B = f"""
SELECT FUENTE, PAIS, DIVISION_COMERCIAL,
  SUM(FACTOR_CALC) / NULLIF(SUM(PESO_CALC),    0) AS PG_MB,
  SUM(MB_CALC)     / NULLIF(SUM(PARTICIPA_CALC),0) AS MBMB,
  COUNT(DISTINCT ITEM) AS ITEMS,
  COUNT(*)             AS LINEAS
FROM (
  SELECT "CON COD CANASTO" AS FUENTE, ITEM, PAIS, DIVISION_COMERCIAL,
    FACTOR_CALC, PESO_CALC, PARTICIPA_CALC, MB_CALC
  FROM {T_CON} WHERE ID_SW IN {IDS}
  UNION ALL
  SELECT "SIN COD CANASTO" AS FUENTE, ITEM, PAIS, DIVISION_COMERCIAL,
    FACTOR_CALC, PESO_CALC, PARTICIPA_CALC, MB_CALC
  FROM {T_SIN} WHERE ID_SW IN {IDS}
)
GROUP BY FUENTE, PAIS, DIVISION_COMERCIAL
ORDER BY PAIS, DIVISION_COMERCIAL, FUENTE
"""

# ── S1C: por PAIS + DIVISION_COMERCIAL + CATEGORIA ─────────────────────────

SQL_S1C = f"""
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

# ── S1D: por PAIS + TIER (KVI_NBB) ────────────────────────────────────────

SQL_S1D = f"""
SELECT FUENTE, PAIS, KVI_NBB AS TIER,
  SUM(FACTOR_CALC) / NULLIF(SUM(PESO_CALC),    0) AS PG_MB,
  SUM(MB_CALC)     / NULLIF(SUM(PARTICIPA_CALC),0) AS MBMB,
  COUNT(DISTINCT ITEM) AS ITEMS,
  COUNT(*)             AS LINEAS
FROM (
  SELECT "CON COD CANASTO" AS FUENTE, ITEM, PAIS, KVI_NBB,
    FACTOR_CALC, PESO_CALC, PARTICIPA_CALC, MB_CALC
  FROM {T_CON} WHERE ID_SW IN {IDS}
  UNION ALL
  SELECT "SIN COD CANASTO" AS FUENTE, ITEM, PAIS, KVI_NBB,
    FACTOR_CALC, PESO_CALC, PARTICIPA_CALC, MB_CALC
  FROM {T_SIN} WHERE ID_SW IN {IDS}
)
GROUP BY FUENTE, PAIS, KVI_NBB
ORDER BY PAIS, KVI_NBB, FUENTE
"""

# ── Ejecutar todas ──────────────────────────────────────────────────────────

print("=" * 60)
print("REPORTE COMPARATIVO: CON COD CANASTO vs SIN COD CANASTO")
print(f"ID_SW: {IDS}  |  Proyecto: {PROJECT}")
print("=" * 60)

results = {}
results["S1A"] = run_and_save("S1A - por PAIS",               SQL_S1A, "s1a_pais.json")
results["S1B"] = run_and_save("S1B - por PAIS+DIV",           SQL_S1B, "s1b_div.json")
results["S1C"] = run_and_save("S1C - por PAIS+DIV+CAT",       SQL_S1C, "s1c_cat.json")
results["S1D"] = run_and_save("S1D - por PAIS+TIER",          SQL_S1D, "s1d_tier.json")

print("\n" + "=" * 60)
print("RESUMEN FINAL")
print("=" * 60)
for key, n in results.items():
    print(f"  {key}: {n:,} filas")
print(f"\nArchivos guardados en: {OUT_DIR}")

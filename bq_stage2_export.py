"""Exporta el index FdS vs ES desde BigQuery.

Formula correcta del volumen:
  Para cada UPC-PAIS-COMPETIDOR-ANO-SW-SEGMENTO:
    Vol = SUM(precio_dia_i) * rotaciones_upc_semana
  (SUM de precios diarios, no AVG, para reflejar la cobertura real de checkeos)
  Luego se agrega a PAIS-COMPETIDOR-ANO-SW y se aplica:
    Index = (SUM_Vol_FdS - SUM_Vol_ES) / SUM_Vol_ES
"""
import json
import math
from datetime import datetime
from google.cloud import bigquery

client = bigquery.Client(project='wmt-k1-cons-data-users')

QUERY = """
WITH

-- PASO 1: Precios diarios por UPC-PAIS-COMP-ANO-SW-SEGMENTO
-- SUM de precio por segmento = refleja dias reales de checkeo (cobertura)
precios_upc AS (
  SELECT
    CAST(upc AS STRING)  AS upc,
    pais,
    competidor,
    ano,
    sw,
    CASE
      WHEN EXTRACT(DAYOFWEEK FROM fecha) IN (2,3,4,5) THEN 'ES'
      ELSE 'FdS'
    END AS seg,
    -- SUM: cada dia de checkeo aporta su precio al volumen
    SUM(CASE WHEN precio_normal  IS NOT NULL
                  AND NOT IS_INF(precio_normal)  AND NOT IS_NAN(precio_normal)
             THEN precio_normal  END) AS sum_p_normal,
    SUM(CASE WHEN precio_oferta   IS NOT NULL
                  AND NOT IS_INF(precio_oferta)   AND NOT IS_NAN(precio_oferta)
             THEN precio_oferta   END) AS sum_p_oferta,
    SUM(CASE WHEN precio_mayoreo  IS NOT NULL
                  AND NOT IS_INF(precio_mayoreo)  AND NOT IS_NAN(precio_mayoreo)
             THEN precio_mayoreo  END) AS sum_p_mayoreo,
    -- AVG: precio de referencia para mostrar en reporte
    AVG(CASE WHEN precio_normal  IS NOT NULL
                  AND NOT IS_INF(precio_normal)  AND NOT IS_NAN(precio_normal)
             THEN precio_normal  END) AS avg_p_normal,
    AVG(CASE WHEN precio_oferta   IS NOT NULL
                  AND NOT IS_INF(precio_oferta)   AND NOT IS_NAN(precio_oferta)
             THEN precio_oferta   END) AS avg_p_oferta,
    AVG(CASE WHEN precio_mayoreo  IS NOT NULL
                  AND NOT IS_INF(precio_mayoreo)  AND NOT IS_NAN(precio_mayoreo)
             THEN precio_mayoreo  END) AS avg_p_mayoreo,
    -- Conteo de dias con precio (mide cobertura)
    COUNT(CASE WHEN precio_normal  IS NOT NULL THEN 1 END) AS n_dias_normal,
    COUNT(CASE WHEN precio_oferta   IS NOT NULL THEN 1 END) AS n_dias_oferta,
    COUNT(CASE WHEN precio_mayoreo  IS NOT NULL THEN 1 END) AS n_dias_mayoreo
  FROM `wmt-k1-cons-data-users.k1_adhoc_tables.prcng_info_cam_historico_precio_comp`
  WHERE DATE(fecha) BETWEEN '2025-08-01' AND '2026-03-31'
    AND competidor IS NOT NULL
    AND upc        IS NOT NULL
  GROUP BY 1,2,3,4,5,6
),

-- PASO 2: Rotaciones por UPC-PAIS-ANO-SW (sin segmento, son ventas semanales)
rotaciones AS (
  SELECT
    CAST(upc AS STRING) AS upc,
    pais,
    extract_yr          AS ano,
    sw,
    SUM(COALESCE(rotaciones, 0)) AS rot
  FROM `wmt-k1-cons-data-users.k1_adhoc_tables.prcng_info_cam_a0u01jb_historico_insumos`
  WHERE DATE(extract_date) BETWEEN '2025-08-01' AND '2026-03-31'
  GROUP BY 1,2,3,4
),

-- PASO 3: Pivotar ES/FdS y calcular volumen por UPC
-- Volumen = SUM_precio_segmento x rotaciones_upc
-- Clave: la misma llave UPC-PAIS-COMPETIDOR-ANO-SW para ambos segmentos
pivot_upc AS (
  SELECT
    v.upc,
    v.pais,
    v.competidor,
    v.ano,
    v.sw,
    COALESCE(MAX(r.rot), 0)  AS rotaciones,

    -- Precios de referencia (AVG)
    MAX(CASE WHEN v.seg='ES'  THEN v.avg_p_normal  END) AS p_normal_es,
    MAX(CASE WHEN v.seg='FdS' THEN v.avg_p_normal  END) AS p_normal_fds,
    MAX(CASE WHEN v.seg='ES'  THEN v.avg_p_oferta  END) AS p_oferta_es,
    MAX(CASE WHEN v.seg='FdS' THEN v.avg_p_oferta  END) AS p_oferta_fds,
    MAX(CASE WHEN v.seg='ES'  THEN v.avg_p_mayoreo END) AS p_mayoreo_es,
    MAX(CASE WHEN v.seg='FdS' THEN v.avg_p_mayoreo END) AS p_mayoreo_fds,

    -- Dias de cobertura
    MAX(CASE WHEN v.seg='ES'  THEN v.n_dias_normal  END) AS dias_normal_es,
    MAX(CASE WHEN v.seg='FdS' THEN v.n_dias_normal  END) AS dias_normal_fds,
    MAX(CASE WHEN v.seg='ES'  THEN v.n_dias_oferta  END) AS dias_oferta_es,
    MAX(CASE WHEN v.seg='FdS' THEN v.n_dias_oferta  END) AS dias_oferta_fds,
    MAX(CASE WHEN v.seg='ES'  THEN v.n_dias_mayoreo END) AS dias_mayoreo_es,
    MAX(CASE WHEN v.seg='FdS' THEN v.n_dias_mayoreo END) AS dias_mayoreo_fds,

    -- VOLUMEN por UPC-SEGMENTO = SUM_precio_dias x rotaciones_upc
    MAX(CASE WHEN v.seg='ES'  THEN v.sum_p_normal  END) * COALESCE(MAX(r.rot),0) AS vol_normal_es,
    MAX(CASE WHEN v.seg='FdS' THEN v.sum_p_normal  END) * COALESCE(MAX(r.rot),0) AS vol_normal_fds,
    MAX(CASE WHEN v.seg='ES'  THEN v.sum_p_oferta  END) * COALESCE(MAX(r.rot),0) AS vol_oferta_es,
    MAX(CASE WHEN v.seg='FdS' THEN v.sum_p_oferta  END) * COALESCE(MAX(r.rot),0) AS vol_oferta_fds,
    MAX(CASE WHEN v.seg='ES'  THEN v.sum_p_mayoreo END) * COALESCE(MAX(r.rot),0) AS vol_mayoreo_es,
    MAX(CASE WHEN v.seg='FdS' THEN v.sum_p_mayoreo END) * COALESCE(MAX(r.rot),0) AS vol_mayoreo_fds

  FROM precios_upc v
  LEFT JOIN rotaciones r
    ON  v.upc  = r.upc
    AND v.pais = r.pais
    AND v.ano  = r.ano
    AND v.sw   = r.sw
  GROUP BY v.upc, v.pais, v.competidor, v.ano, v.sw
),

-- PASO 4: Solo UPCs con precio Normal en AMBOS segmentos
comparable AS (
  SELECT *
  FROM pivot_upc
  WHERE p_normal_es  IS NOT NULL
    AND p_normal_fds IS NOT NULL
),

-- PASO 5: Agregar a PAIS-COMPETIDOR-ANO-SW
-- El INDEX se calcula sobre la SUMA de volumenes (no el promedio de indices por UPC)
agg AS (
  SELECT
    pais,
    competidor,
    ano,
    sw,
    COUNT(DISTINCT upc)            AS upcs_comparables,
    ROUND(SUM(rotaciones),       2) AS total_rotaciones,

    -- Precios promedio de referencia
    ROUND(AVG(p_normal_es),    4)   AS avg_precio_normal_es,
    ROUND(AVG(p_normal_fds),   4)   AS avg_precio_normal_fds,
    ROUND(AVG(p_oferta_es),    4)   AS avg_precio_oferta_es,
    ROUND(AVG(p_oferta_fds),   4)   AS avg_precio_oferta_fds,
    ROUND(AVG(p_mayoreo_es),   4)   AS avg_precio_mayoreo_es,
    ROUND(AVG(p_mayoreo_fds),  4)   AS avg_precio_mayoreo_fds,

    -- Cobertura promedio de dias de checkeo por segmento
    ROUND(AVG(dias_normal_es),   2) AS avg_dias_normal_es,
    ROUND(AVG(dias_normal_fds),  2) AS avg_dias_normal_fds,
    ROUND(AVG(dias_oferta_es),   2) AS avg_dias_oferta_es,
    ROUND(AVG(dias_oferta_fds),  2) AS avg_dias_oferta_fds,
    ROUND(AVG(dias_mayoreo_es),  2) AS avg_dias_mayoreo_es,
    ROUND(AVG(dias_mayoreo_fds), 2) AS avg_dias_mayoreo_fds,

    -- Volumenes totales (SUM a nivel PAIS-COMP-ANO-SW)
    ROUND(SUM(vol_normal_es),    2) AS vol_normal_es,
    ROUND(SUM(vol_normal_fds),   2) AS vol_normal_fds,
    ROUND(SUM(vol_oferta_es),    2) AS vol_oferta_es,
    ROUND(SUM(vol_oferta_fds),   2) AS vol_oferta_fds,
    ROUND(SUM(vol_mayoreo_es),   2) AS vol_mayoreo_es,
    ROUND(SUM(vol_mayoreo_fds),  2) AS vol_mayoreo_fds,

    -- INDEX = (SUM_Vol_FdS - SUM_Vol_ES) / SUM_Vol_ES
    ROUND(SAFE_DIVIDE(
      SUM(vol_normal_fds)  - SUM(vol_normal_es),
      SUM(vol_normal_es)),  6)      AS index_normal,
    ROUND(SAFE_DIVIDE(
      SUM(vol_oferta_fds)  - SUM(vol_oferta_es),
      SUM(vol_oferta_es)),  6)      AS index_oferta,
    ROUND(SAFE_DIVIDE(
      SUM(vol_mayoreo_fds) - SUM(vol_mayoreo_es),
      SUM(vol_mayoreo_es)), 6)      AS index_mayoreo,

    -- Clasificacion de UPCs por precio relativo FdS vs ES
    COUNT(CASE WHEN p_normal_fds < p_normal_es * 0.99 THEN 1 END) AS upcs_fds_barato_normal,
    COUNT(CASE WHEN p_normal_fds > p_normal_es * 1.01 THEN 1 END) AS upcs_fds_caro_normal,
    COUNT(CASE WHEN p_oferta_fds  IS NOT NULL AND p_oferta_es  IS NOT NULL
               AND p_oferta_fds  < p_oferta_es  * 0.99 THEN 1 END) AS upcs_fds_barato_oferta,
    COUNT(CASE WHEN p_oferta_fds  IS NOT NULL AND p_oferta_es  IS NOT NULL
               AND p_oferta_fds  > p_oferta_es  * 1.01 THEN 1 END) AS upcs_fds_caro_oferta,
    COUNT(CASE WHEN p_mayoreo_fds IS NOT NULL AND p_mayoreo_es IS NOT NULL
               AND p_mayoreo_fds < p_mayoreo_es * 0.99 THEN 1 END) AS upcs_fds_barato_mayoreo,
    COUNT(CASE WHEN p_mayoreo_fds IS NOT NULL AND p_mayoreo_es IS NOT NULL
               AND p_mayoreo_fds > p_mayoreo_es * 1.01 THEN 1 END) AS upcs_fds_caro_mayoreo

  FROM comparable
  GROUP BY pais, competidor, ano, sw
  ORDER BY pais, competidor, ano, sw
)

SELECT * FROM agg
"""

ts = lambda: datetime.now().strftime('%H:%M:%S')
print(f"[{ts()}] Enviando query a BigQuery...", flush=True)
job = client.query(QUERY)
print(f"[{ts()}] Job ID: {job.job_id}", flush=True)
print(f"[{ts()}] Esperando resultados...", flush=True)
rows = list(job.result())
print(f"[{ts()}] Query completa!", flush=True)
print(f"  Bytes procesados : {job.total_bytes_processed:,}", flush=True)
print(f"  Bytes facturados : {job.total_bytes_billed:,}", flush=True)
print(f"  Filas retornadas : {len(rows):,}", flush=True)


def safe(v):
    """Convierte valores no serializables a None."""
    if v is None:
        return None
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None
    return v


records, paises, comps = [], set(), set()
for r in rows:
    d = {k: safe(v) for k, v in dict(r).items()}
    paises.add(d['pais'])
    comps.add(d['competidor'])
    records.append(d)

OUT = r'C:\Users\shern22\Documents\puppy_workspace\query_index.json'
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(records, f, ensure_ascii=False, indent=2)

print(f"\n[{ts()}] JSON guardado en: {OUT}", flush=True)
print(f"  Total filas           : {len(records):,}", flush=True)
print(f"  Paises                : {sorted(paises)}", flush=True)
print(f"  Competidores          : {len(comps)}", flush=True)
print(f"  Lista competidores    : {sorted(comps)}", flush=True)
print("DONE", flush=True)

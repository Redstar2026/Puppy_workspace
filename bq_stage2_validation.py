import sys
from google.cloud import bigquery

client = bigquery.Client(project='wmt-k1-cons-data-users')

CTE_BLOCK = """
WITH precios_base AS (
  SELECT
    upc, pais, competidor, ano, sw,
    CASE
      WHEN EXTRACT(DAYOFWEEK FROM fecha) IN (2,3,4,5) THEN 'Entre Semana'
      ELSE 'Fin de Semana'
    END AS segmento,
    AVG(IF(precio_normal IS NOT NULL AND NOT IS_INF(precio_normal) AND NOT IS_NAN(precio_normal), precio_normal, NULL)) AS avg_precio_normal,
    AVG(IF(precio_oferta  IS NOT NULL AND NOT IS_INF(precio_oferta)  AND NOT IS_NAN(precio_oferta),  precio_oferta,  NULL)) AS avg_precio_oferta
  FROM `wmt-k1-cons-data-users.k1_adhoc_tables.prcng_info_cam_historico_precio_comp`
  WHERE DATE(fecha) BETWEEN '2025-08-01' AND '2026-03-31'
  GROUP BY upc, pais, competidor, ano, sw, segmento
),
rotaciones_base AS (
  SELECT
    CAST(upc AS INT64) AS upc,
    pais,
    extract_yr AS ano,
    sw,
    SUM(COALESCE(rotaciones, 0)) AS suma_rotaciones
  FROM `wmt-k1-cons-data-users.k1_adhoc_tables.prcng_info_cam_a0u01jb_historico_insumos`
  WHERE DATE(extract_date) BETWEEN '2025-08-01' AND '2026-03-31'
  GROUP BY upc, pais, extract_yr, sw
),
joined AS (
  SELECT
    p.upc, p.pais, p.competidor, p.ano, p.sw, p.segmento,
    p.avg_precio_normal,
    p.avg_precio_oferta,
    COALESCE(r.suma_rotaciones, 0) AS suma_rotaciones,
    p.avg_precio_normal * COALESCE(r.suma_rotaciones, 0) AS vol_normal,
    p.avg_precio_oferta  * COALESCE(r.suma_rotaciones, 0) AS vol_oferta
  FROM precios_base p
  LEFT JOIN rotaciones_base r
    ON p.upc = r.upc AND p.pais = r.pais AND p.ano = r.ano AND p.sw = r.sw
),
pivoted AS (
  SELECT
    upc, pais, competidor, ano, sw,
    MAX(CASE WHEN segmento='Entre Semana' THEN avg_precio_normal END) AS precio_normal_es,
    MAX(CASE WHEN segmento='Fin de Semana' THEN avg_precio_normal END) AS precio_normal_fds,
    MAX(CASE WHEN segmento='Entre Semana' THEN avg_precio_oferta  END) AS precio_oferta_es,
    MAX(CASE WHEN segmento='Fin de Semana' THEN avg_precio_oferta  END) AS precio_oferta_fds,
    MAX(suma_rotaciones) AS suma_rotaciones,
    MAX(CASE WHEN segmento='Entre Semana' THEN vol_normal END) AS vol_normal_es,
    MAX(CASE WHEN segmento='Fin de Semana' THEN vol_normal END) AS vol_normal_fds,
    MAX(CASE WHEN segmento='Entre Semana' THEN vol_oferta  END) AS vol_oferta_es,
    MAX(CASE WHEN segmento='Fin de Semana' THEN vol_oferta  END) AS vol_oferta_fds
  FROM joined
  GROUP BY upc, pais, competidor, ano, sw
),
comparable AS (
  SELECT *,
    SAFE_DIVIDE(vol_normal_fds - vol_normal_es, vol_normal_es) AS index_normal,
    SAFE_DIVIDE(vol_oferta_fds  - vol_oferta_es,  vol_oferta_es)  AS index_oferta
  FROM pivoted
  WHERE precio_normal_es  IS NOT NULL
    AND precio_normal_fds IS NOT NULL
)
"""

# ── 1. SAMPLE 20 rows ──────────────────────────────────────────────────────────
print('=' * 70)
print('QUERY 1: SAMPLE 20 ROWS')
print('=' * 70)
q_sample = CTE_BLOCK + "SELECT * FROM comparable LIMIT 20"
job = client.query(q_sample)
rows = list(job.result())
print(f'Bytes processed : {job.total_bytes_processed:,}')
print(f'Bytes billed    : {job.total_bytes_billed:,}')
print(f'Rows returned   : {len(rows)}')
print()

# Collect index stats inline
index_normals = []
index_ofertas = []
for i, r in enumerate(rows):
    d = dict(r)
    print(f'--- ROW {i+1} ---')
    for k, v in d.items():
        print(f'  {k}: {v!r}')
    if d.get('index_normal') is not None:
        index_normals.append(d['index_normal'])
    if d.get('index_oferta') is not None:
        index_ofertas.append(d['index_oferta'])

# ── 2. COUNT(*) ────────────────────────────────────────────────────────────────
print()
print('=' * 70)
print('QUERY 2: COUNT(*) of comparable CTE')
print('=' * 70)
q_count = CTE_BLOCK + "SELECT COUNT(*) AS total_comparable FROM comparable"
job2 = client.query(q_count)
count_rows = list(job2.result())
print(f'Bytes processed : {job2.total_bytes_processed:,}')
print(f'Bytes billed    : {job2.total_bytes_billed:,}')
for r in count_rows:
    print(f'  total_comparable: {r.total_comparable:,}')

# ── 3. INDEX DISTRIBUTION analysis ────────────────────────────────────────────
print()
print('=' * 70)
print('QUERY 3: INDEX DISTRIBUTION STATS (full comparable)')
print('=' * 70)
q_dist = CTE_BLOCK + """
SELECT
  -- index_normal distribution
  COUNTIF(index_normal IS NULL)          AS idx_normal_nulls,
  COUNTIF(index_normal BETWEEN -1 AND 1) AS idx_normal_in_range,
  COUNTIF(index_normal < -1)             AS idx_normal_below_minus1,
  COUNTIF(index_normal > 1)              AS idx_normal_above_1,
  ROUND(MIN(index_normal), 4)            AS idx_normal_min,
  ROUND(MAX(index_normal), 4)            AS idx_normal_max,
  ROUND(AVG(index_normal), 4)            AS idx_normal_avg,
  ROUND(STDDEV(index_normal), 4)         AS idx_normal_stddev,
  -- index_oferta distribution
  COUNTIF(index_oferta IS NULL)          AS idx_oferta_nulls,
  COUNTIF(index_oferta BETWEEN -1 AND 1) AS idx_oferta_in_range,
  COUNTIF(index_oferta < -1)             AS idx_oferta_below_minus1,
  COUNTIF(index_oferta > 1)              AS idx_oferta_above_1,
  ROUND(MIN(index_oferta), 4)            AS idx_oferta_min,
  ROUND(MAX(index_oferta), 4)            AS idx_oferta_max,
  ROUND(AVG(index_oferta), 4)            AS idx_oferta_avg,
  -- rotaciones join quality
  COUNTIF(suma_rotaciones = 0)           AS rows_zero_rotaciones,
  COUNTIF(suma_rotaciones > 0)           AS rows_with_rotaciones,
  COUNT(*) AS total_rows
FROM comparable
"""
job3 = client.query(q_dist)
rows3 = list(job3.result())
print(f'Bytes processed : {job3.total_bytes_processed:,}')
print(f'Bytes billed    : {job3.total_bytes_billed:,}')
for r in rows3:
    for k, v in dict(r).items():
        print(f'  {k}: {v}')

print()
print('DONE')

import sys
from google.cloud import bigquery

client = bigquery.Client(project='wmt-k1-cons-data-users')
TABLE = 'wmt-k1-cons-data-users.k1_adhoc_tables.prcng_info_cam_historico_precio_comp'

print('=== 3 SAMPLE ROWS ===')
rows = list(client.query('SELECT * FROM `' + TABLE + '` LIMIT 3').result())
for i, r in enumerate(rows):
    print(f'--- ROW {i+1} ---')
    for k, v in dict(r).items():
        print(f'  {k}: {v!r}')

print('\n=== PRICE NULL / ZERO ANALYSIS ===')
q_price = '''
SELECT
  COUNT(*) AS total_rows,
  COUNTIF(precio_normal IS NULL)  AS normal_nulls,
  COUNTIF(precio_normal = 0)      AS normal_zeros,
  COUNTIF(precio_normal > 0)      AS normal_positive,
  COUNTIF(precio_oferta IS NULL)  AS oferta_nulls,
  COUNTIF(precio_oferta = 0)      AS oferta_zeros,
  COUNTIF(precio_oferta > 0)      AS oferta_positive,
  MIN(precio_normal)              AS min_normal,
  MAX(precio_normal)              AS max_normal,
  ROUND(AVG(precio_normal),4)     AS avg_normal,
  MIN(precio_oferta)              AS min_oferta,
  MAX(precio_oferta)              AS max_oferta
FROM `wmt-k1-cons-data-users.k1_adhoc_tables.prcng_info_cam_historico_precio_comp`
'''
for k, v in dict(list(client.query(q_price).result())[0]).items():
    print(f'  {k}: {v}')

print('\n=== OVERALL STATS ===')
q_stats = '''
SELECT
  COUNT(*) AS total_rows,
  COUNT(DISTINCT upc)        AS distinct_upcs,
  COUNT(DISTINCT pais)       AS distinct_paises,
  COUNT(DISTINCT competidor) AS distinct_competidores,
  COUNT(DISTINCT cod_comp)   AS distinct_cod_comp,
  MIN(fecha) AS min_fecha,  MAX(fecha) AS max_fecha,
  MIN(ano)   AS min_ano,    MAX(ano)   AS max_ano,
  MIN(sw)    AS min_sw,     MAX(sw)    AS max_sw
FROM `wmt-k1-cons-data-users.k1_adhoc_tables.prcng_info_cam_historico_precio_comp`
'''
for k, v in dict(list(client.query(q_stats).result())[0]).items():
    print(f'  {k}: {v}')

print('\n=== DISTINCT PAIS + COMPETIDOR SAMPLES ===')
q_pais = 'SELECT DISTINCT pais FROM `wmt-k1-cons-data-users.k1_adhoc_tables.prcng_info_cam_historico_precio_comp` ORDER BY pais'
print('  PAIS:', [r.pais for r in client.query(q_pais).result()])

q_comp = 'SELECT DISTINCT competidor FROM `wmt-k1-cons-data-users.k1_adhoc_tables.prcng_info_cam_historico_precio_comp` ORDER BY competidor LIMIT 20'
print('  COMPETIDORES:', [r.competidor for r in client.query(q_comp).result()])

print('\n=== precio_cf / precio_mayoreo CHECK ===')
q_cf = '''
SELECT
  COUNTIF(precio_cf IS NULL)     AS cf_nulls,
  COUNTIF(precio_cf IS NOT NULL) AS cf_not_null,
  COUNTIF(precio_cf_emp IS NULL)     AS cf_emp_nulls,
  COUNTIF(precio_cf_emp IS NOT NULL) AS cf_emp_not_null
FROM `wmt-k1-cons-data-users.k1_adhoc_tables.prcng_info_cam_historico_precio_comp`
'''
for k, v in dict(list(client.query(q_cf).result())[0]).items():
    print(f'  {k}: {v}')

print('DONE')

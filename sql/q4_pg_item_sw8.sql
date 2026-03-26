WITH base AS (
  SELECT
    PAIS,
    DIVISION,
    CATEGORIA,
    ITEM,
    MAX(ITEM_DESCRIP)  AS item_descrip,
    MAX(BRAND_NAME)    AS brand_name,
    COUNT(*)           AS total_rows,
    ROUND(SUM(FACTOR_CALC), 6)                        AS sum_factor_calc,
    ROUND(SUM(PESO_CALC),   6)                        AS sum_peso_calc,
    ROUND(SUM(FACTOR_CALC) / SUM(PESO_CALC), 6)      AS pg,
    ROUND(AVG(PRICE_GAP), 6)                          AS avg_price_gap
  FROM `wmt-k1-cons-data-users.k1_adhoc_tables.PGMB_PREMED_A0M1J1N`
  WHERE ANIO = 2026
    AND SW   = 8
    AND FACTOR_CALC IS NOT NULL
    AND PESO_CALC   IS NOT NULL
    AND PESO_CALC   > 0
  GROUP BY PAIS, DIVISION, CATEGORIA, ITEM
),
stats AS (
  SELECT
    PERCENTILE_CONT(pg, 0.25) OVER () AS q1,
    PERCENTILE_CONT(pg, 0.75) OVER () AS q3
  FROM base
),
bounds AS (
  SELECT
    MIN(q1) - 1.5 * (MIN(q3) - MIN(q1)) AS lower_bound,
    MAX(q3) + 1.5 * (MAX(q3) - MIN(q1)) AS upper_bound
  FROM stats
)
SELECT
  b.PAIS, b.DIVISION, b.CATEGORIA, b.ITEM,
  b.item_descrip, b.brand_name,
  b.total_rows,
  b.sum_factor_calc, b.sum_peso_calc,
  b.pg,
  b.avg_price_gap,
  CASE
    WHEN b.pg < (SELECT lower_bound FROM bounds) THEN 'Outlier Negativo'
    WHEN b.pg > (SELECT upper_bound FROM bounds) THEN 'Outlier Positivo'
    ELSE 'Normal'
  END AS tipo_outlier,
  (SELECT lower_bound FROM bounds) AS lower_bound,
  (SELECT upper_bound FROM bounds) AS upper_bound
FROM base b
ORDER BY b.pg ASC
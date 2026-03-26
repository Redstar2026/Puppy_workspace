SELECT
  PAIS,
  DIVISION,
  CATEGORIA,
  COUNT(*)                                        AS total_items,
  ROUND(SUM(FACTOR_CALC), 6)                      AS sum_factor_calc,
  ROUND(SUM(PESO_CALC), 6)                        AS sum_peso_calc,
  ROUND(SUM(FACTOR_CALC) / SUM(PESO_CALC), 6)    AS pg,
  ROUND(AVG(PRICE_GAP), 6)                        AS avg_price_gap
FROM `wmt-k1-cons-data-users.k1_adhoc_tables.PGMB_PREMED_A0M1J1N`
WHERE ANIO = 2026
  AND SW = 8
  AND FACTOR_CALC IS NOT NULL
  AND PESO_CALC IS NOT NULL
  AND PESO_CALC > 0
GROUP BY PAIS, DIVISION, CATEGORIA
ORDER BY pg ASC
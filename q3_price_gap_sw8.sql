SELECT 
  PAIS,
  DIVISION,
  CATEGORIA,
  COUNT(*) as total_items,
  ROUND(AVG(FACTOR_CALC), 4) as avg_factor_calc,
  ROUND(SUM(PESO_CALC), 4) as total_peso_calc,
  ROUND(SUM(FACTOR_CALC * PESO_CALC), 4) as weighted_factor,
  ROUND(AVG(PRICE_GAP), 4) as avg_price_gap,
  ROUND(MIN(FACTOR_CALC), 4) as min_factor_calc,
  ROUND(MAX(FACTOR_CALC), 4) as max_factor_calc
FROM `wmt-k1-cons-data-users.k1_adhoc_tables.PGMB_PREMED_A0M1J1N`
WHERE SW = 8 AND ANIO = 2026
AND FACTOR_CALC IS NOT NULL
AND PESO_CALC IS NOT NULL
GROUP BY PAIS, DIVISION, CATEGORIA
ORDER BY PAIS, DIVISION, avg_factor_calc ASC
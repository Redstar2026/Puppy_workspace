WITH sw7 AS (
  SELECT ITEM, PAIS, DIVISION, CATEGORIA, PRECIO_WM_LOW as precio_sw7
  FROM `wmt-k1-cons-data-users.k1_adhoc_tables.PGMB_PREMED_A0M1J1N`
  WHERE SW = 7 AND ANIO = 2026
  AND PRECIO_WM_LOW IS NOT NULL
),
sw8 AS (
  SELECT ITEM, PAIS, DIVISION, CATEGORIA, PRECIO_WM_LOW as precio_sw8
  FROM `wmt-k1-cons-data-users.k1_adhoc_tables.PGMB_PREMED_A0M1J1N`
  WHERE SW = 8 AND ANIO = 2026
  AND PRECIO_WM_LOW IS NOT NULL
),
comparacion AS (
  SELECT 
    sw8.PAIS, sw8.DIVISION, sw8.CATEGORIA,
    CASE 
      WHEN sw7.ITEM IS NULL THEN 'Nuevo'
      WHEN sw8.precio_sw8 < sw7.precio_sw7 THEN 'Bajo'
      WHEN sw8.precio_sw8 > sw7.precio_sw7 THEN 'Subio'
      ELSE 'Mantiene'
    END as segmento
  FROM sw8
  LEFT JOIN sw7 ON sw8.ITEM = sw7.ITEM AND sw8.PAIS = sw7.PAIS
)
SELECT PAIS, DIVISION, CATEGORIA, segmento, COUNT(*) as cantidad
FROM comparacion
GROUP BY PAIS, DIVISION, CATEGORIA, segmento
ORDER BY PAIS, DIVISION, CATEGORIA, segmento
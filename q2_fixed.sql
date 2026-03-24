WITH sw7 AS (
  SELECT 
    ITEM, PAIS, DIVISION, CATEGORIA,
    IFNULL(COMPETIDOR,'') AS COMPETIDOR,
    IFNULL(FORMATO,'')    AS FORMATO,
    IFNULL(CODIGO_ZONA,0) AS CODIGO_ZONA,
    PRECIO_WM_LOW
  FROM `wmt-k1-cons-data-users.k1_adhoc_tables.PGMB_PREMED_A0M1J1N`
  WHERE ANIO = 2026 AND SW = 7
),
sw8 AS (
  SELECT 
    ITEM, PAIS, DIVISION, CATEGORIA,
    IFNULL(COMPETIDOR,'') AS COMPETIDOR,
    IFNULL(FORMATO,'')    AS FORMATO,
    IFNULL(CODIGO_ZONA,0) AS CODIGO_ZONA,
    PRECIO_WM_LOW
  FROM `wmt-k1-cons-data-users.k1_adhoc_tables.PGMB_PREMED_A0M1J1N`
  WHERE ANIO = 2026 AND SW = 8
),
comparacion AS (
  SELECT
    sw8.PAIS, sw8.DIVISION, sw8.CATEGORIA,
    CASE
      WHEN sw7.ITEM IS NULL                                         THEN 'Nuevo'
      WHEN sw7.PRECIO_WM_LOW IS NULL AND sw8.PRECIO_WM_LOW IS NOT NULL THEN 'Nuevo'
      WHEN sw8.PRECIO_WM_LOW IS NULL                                THEN 'Sin precio'
      WHEN sw8.PRECIO_WM_LOW < sw7.PRECIO_WM_LOW                   THEN 'Bajo'
      WHEN sw8.PRECIO_WM_LOW > sw7.PRECIO_WM_LOW                   THEN 'Subio'
      ELSE 'Mantiene'
    END AS segmento,
    COUNT(*) AS cantidad
  FROM sw8
  LEFT JOIN sw7
    ON  sw8.ITEM        = sw7.ITEM
    AND sw8.PAIS        = sw7.PAIS
    AND sw8.COMPETIDOR  = sw7.COMPETIDOR
    AND sw8.FORMATO     = sw7.FORMATO
    AND sw8.CODIGO_ZONA = sw7.CODIGO_ZONA
  GROUP BY sw8.PAIS, sw8.DIVISION, sw8.CATEGORIA, segmento
)
SELECT PAIS, DIVISION, CATEGORIA, segmento, cantidad
FROM comparacion
WHERE segmento != 'Sin precio'
ORDER BY PAIS, DIVISION, CATEGORIA, segmento
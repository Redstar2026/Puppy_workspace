SELECT
  'SW' AS campo, CAST(SW AS STRING) AS valor, COUNT(*) AS frecuencia
FROM `wmt-k1-cons-data-users.k1_adhoc_tables.PGMB_PREMED_A0M1J1N`
GROUP BY SW
ORDER BY SW
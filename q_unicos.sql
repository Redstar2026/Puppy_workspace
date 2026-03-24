SELECT
  (SELECT STRING_AGG(DISTINCT PAIS ORDER BY PAIS) FROM `wmt-k1-cons-data-users.k1_adhoc_tables.PGMB_PREMED_A0M1J1N`) AS paises_unicos,
  (SELECT STRING_AGG(DISTINCT DIVISION ORDER BY DIVISION) FROM `wmt-k1-cons-data-users.k1_adhoc_tables.PGMB_PREMED_A0M1J1N`) AS divisiones_unicas,
  (SELECT STRING_AGG(DISTINCT CATEGORIA ORDER BY CATEGORIA LIMIT 50) FROM `wmt-k1-cons-data-users.k1_adhoc_tables.PGMB_PREMED_A0M1J1N`) AS categorias_unicas
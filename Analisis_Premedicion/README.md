# 📊 Análisis Premedición — 2026

## Dashboards disponibles

| Dashboard | Semanas | Archivo |
|-----------|---------|---------|
| SW10 vs SW9 | Comparación SW9 → SW10 | `pricing_dashboard_sw10.html` |
| SW11 vs SW10 | Comparación SW10 → SW11 | `pricing_dashboard_sw11.html` |

---

## SW11 vs SW10 · 2026 (más reciente)

### Descripción
Dashboard interactivo de competitividad de precios para la **Semana 11 vs Semana 10 del año 2026**.
Cubre los 5 países de Centroamérica: **CR, GT, HN, NI, SV**.

### Hallazgos clave SW11
| País | Δ PG MB (BPS) | Tendencia |
|------|--------------|-----------|
| CR   | −43 bps      | 🔴 Baja   |
| GT   | +74 bps      | 🟢 Sube   |
| HN   | −11 bps      | ➡️ Estable |
| NI   | −90 bps      | 🔴 Baja   |
| SV   | +2 bps       | ➡️ Estable |

⚠️ **SV FARMACIA** registra caída crítica de **−635 bps**.
⚠️ **NI** lidera caídas: −90 bps en PG MB y −646 bps en %MB MB.
🟢 **GT** es el único país con mejora sólida (+74 bps).

---

## Cómo usarlo
Abre el HTML directamente en el navegador. No requiere servidor.

## Segmentos del Dashboard
| Tab | Contenido |
|-----|-----------| 
| 📊 General | KPIs + PG MB y MB MB por país, tendencia BPS |
| 🌎 País | Drill-down por país, divisiones vs meta |
| 🏪 División | Semáforo divisiones × países, heatmap |
| 🎯 Meta | % PG MB vs META, heatmap de desviación |
| ⚠️ Outliers Top 30 | Negativos + positivos en Price Gap, filtrable |
| ⬇️ Descargables | Exporta CSV por país/división |
| 📐 Base 100 | Contribución normalizada por ítem |
| 🔍 Desviación Meta | Ítems más desviados con semáforo |

## Fórmulas utilizadas
| Métrica | Fórmula |
|---------|---------| 
| % PG MB | `FACTOR / PESO` |
| % MB MB | `MB_CALC / PARTICIPA_CALC` |
| % PG    | `FACTOR_CALC / PESO_CALC` |
| % MB    | `MB / PARTICIPA` |
| META    | `FACTOR_META_BASE / PESO_META_BASE` |

## Fuente de datos
- Tabla base: `wmt-k1-cons-data-users.k1_adhoc_tables.PGMB_PREMED_A0M1J1N`
- Filtro SW11 vs SW10: `ANIO = 2026`, `SW IN (10, 11)`
- Filtro SW10 vs SW9: `ANIO = 2026`, `SW IN (9, 10)`

## Generado
- SW11 Dashboard — Fecha: 2026-04-14
- SW10 Dashboard — Fecha: 2026-04-07
- Generado con: Code Puppy 🐶 (`code-puppy-7e6adc`)

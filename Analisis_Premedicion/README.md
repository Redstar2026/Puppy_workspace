# 📊 Análisis Premedición — SW10 vs SW9 · 2026

## Descripción
Dashboard interactivo de competitividad de precios para la **Semana 10 vs Semana 9 del año 2026**.
Cubre los 5 países de Centroamérica: **CR, GT, HN, NI, SV**.

## Archivos
| Archivo | Descripción |
|---------|-------------|
| `pricing_dashboard_sw10.html` | Dashboard HTML interactivo — abrir en navegador |

## Cómo usarlo
Abre `pricing_dashboard_sw10.html` directamente en el navegador. No requiere servidor.

## Link compartible (Walmart VPN/Eagle WiFi requerido)
🔗 https://puppy.walmart.com/sharing/shern22/pricing-dashboard-sw10

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
| % PG | `FACTOR / PESO_CAM` |
| % MB | `MB / PARTICIPA_MB` |
| % PG MB | `FACTOR_MB / PESO_MB` |
| % MB MB | `MB_MB_CALC / PARTICIPA_MB_CALC` |
| META | `FACTOR_META / PESO_META` |

## Fuente de datos
- Tabla base: `wmt-k1-cons-data-users.k1_adhoc_tables.PGMB_PREMED_A0M1J1N`
- Filtro: `ANIO = 2026`, `SW IN (9, 10)`

## Generado
- Fecha: 2026-04-07
- Generado con: Code Puppy 🐶 (`code-puppy-948529`)

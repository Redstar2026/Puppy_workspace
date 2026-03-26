# 📡 Radar de Precios CAM

> Dashboard interactivo para el análisis de precios de competidores en Centroamérica y México.  
> Compara precios **Entre Semana (Lun–Jue)** vs **Fin de Semana (Vie–Dom)** por competidor, país y semana.

---

## 🎯 Objetivo

Entender qué está sucediendo con los precios de competidores los **fines de semana**, detectar:
- Ausencia de checkeos de precios FdS por competidor
- Diferencias de precio entre segmentos ES y FdS
- Tendencias de precio normal, oferta y mayoreo
- Índice de variación ES vs FdS ponderado por volumen de ventas

---

## 🗂️ Estructura del proyecto

```
radar-de-precios/
│
├── build_report.py          # 🚀 Entry point — genera el HTML final
├── html_assembler.py        # Ensambla el HTML con todos los módulos
├── report_app.py            # JavaScript: filtros, tabs, renders Tabs 1–6
├── report_index.py          # JavaScript: Tab Index (Índice FdS vs ES bipolar)
├── report_template.py       # CSS + librería VC (canvas charts con tooltips)
├── chart_gen.py             # Gráficas matplotlib (legacy, no en uso activo)
│
├── bq_stage2_export.py      # Query BQ → query_index.json (índice ES vs FdS)
├── bq_stage2_validation.py  # Validaciones de calidad del índice
├── bq_comp_sample.py        # Muestreo de precios por competidor
├── bq_inspect_json.py       # Inspección de esquema BQ
│
├── sql/                     # Queries SQL de exploración y validación
│   ├── q1_*.sql
│   ├── q2_*.sql
│   └── ...
│
├── .gitignore               # Excluye JSONs de datos, HTMLs, venv, PII
├── GUIA_GIT_GITHUB.md       # Guía de trabajo con Git para el equipo
└── README.md                # Este archivo
```

---

## 📊 Tabs del Dashboard

| Tab | Contenido |
|---|---|
| **1 – Conteos Semanal** | Barras ES vs FdS por semana (normal, oferta, mayoreo) |
| **2 – Tendencia Diaria** | Barras Lun–Dom coloreadas por segmento |
| **3 – Mes / País / Comp** | Líneas de tendencia mensual por competidor |
| **4 – Caída FdS** | Detección de semanas sin precios de fin de semana |
| **5 – Deltas MoM** | Variación mes a mes con deltas +/– |
| **6 – Tendencias Competidor** | Curvas de comportamiento por competidor y segmento |
| **📊 INDEX FdS vs ES** | Índice bipolar volumen-ponderado con crosshair interactivo |

---

## 🧮 Fórmula del Índice (Tab INDEX)

El índice mide **cuánto difieren los precios FdS vs ES**, ponderado por ventas reales:

```
Vol_ES  = Σ_UPC [ SUM(precio_dia_ES_i)  × rotaciones_UPC ]
Vol_FdS = Σ_UPC [ SUM(precio_dia_FdS_i) × rotaciones_UPC ]

Índice = (Vol_FdS - Vol_ES) / Vol_ES
```

- **`-` (negativo)** → FdS más barato que entre semana  
- **`+` (positivo)** → FdS más caro que entre semana  
- **`≈ 0`** → Precios similares en ambos segmentos  

> ⚠️ El `SUM` de precios diarios (no `AVG`) es crítico: captura la cobertura real de checkeos.  
> Si un competidor tiene 4 días de datos ES pero solo 1 de FdS, eso se refleja en el índice.

---

## 🗄️ Fuentes de Datos (BigQuery)

| Tabla | Contenido |
|---|---|
| `wmt-k1-cons-data-users.k1_adhoc_tables.prcng_info_cam_historico_precio_comp` | Precios diarios por UPC-Competidor-País |
| `wmt-k1-cons-data-users.k1_adhoc_tables.prcng_info_cam_a0u01jb_historico_insumos` | Rotaciones semanales por UPC-País |

**Periodo analizado:** Agosto 2025 – Marzo 2026  
**Segmentación:** `DAYOFWEEK IN (2,3,4,5)` = Entre Semana · resto = Fin de Semana

---

## ⚙️ Cómo ejecutar

### Pre-requisitos

```bash
# Crear entorno virtual
uv venv
.venv\Scripts\activate   # Windows

# Instalar dependencias
uv pip install google-cloud-bigquery --index-url https://pypi.ci.artifacts.walmart.com/...
```

### 1. Exportar datos desde BigQuery

```bash
# Genera query_index.json (índice ES vs FdS por competidor/semana)
python bq_stage2_export.py
```

> Los JSONs de Q1, Q3 (semanal y mensual) se generan via el sub-agente `bigquery-explorer`  
> y se guardan como `query1_semanal.json`, `query3_mensual.json`.

### 2. Generar el reporte HTML

```bash
python build_report.py
# → reporte_precios_cam.html  (~1.8 MB, auto-suficiente, sin servidor)
```

### 3. Abrir en el navegador

```bash
start reporte_precios_cam.html   # Windows
open reporte_precios_cam.html    # Mac
```

---

## 🎨 Interactividad de las Gráficas

Todas las gráficas canvas soportan:

| Acción | Resultado |
|---|---|
| Hover sobre línea | **Crosshair vertical** + tooltip con TODOS los competidores en ese periodo |
| Hover sobre barra | **Hover-band** azul + tooltip multi-serie con valores de todos los datasets |
| Hover sobre donut | Segmento resaltado con valor y % |
| Cambiar de Tab | Re-render automático para dimensiones correctas |

> Las gráficas de línea muestran **data labels automáticos** cuando hay ≤ 10 periodos y ≤ 4 series.

---

## 🔍 Hallazgos Clave del Análisis

- **Cobertura FdS es 5x menor que ES**: 876 registros FdS vs 4,485 ES en Q1
- **Domingo es el día menos cubierto**: solo 119 checkeos vs 1,481 de Miércoles
- **Viernes tiene mejor cobertura FdS**: 512 checkeos
- El índice normal varía entre **-15% y +10%** según competidor y semana
- Precio **oferta FdS** tiende a ser más barato (-15% promedio en algunos competidores)

---

## 👥 Equipo

Proyecto desarrollado con **Code Puppy** 🐶 (Walmart Internal AI Agent)  
Para actualizaciones de datos, re-ejecutar las queries BQ y reconstruir el HTML.

---

## 📋 Dependencias Python

```
google-cloud-bigquery
pandas
matplotlib
numpy
```

---

*Última actualización: Marzo 2026 · Radar de Precios CAM v12*

# ============================================================
#  WALMART PRICING PLATFORM — CÓMO EJECUTAR
# ============================================================

## ¿Qué es esto?
Una plataforma web para el equipo de Pricing de Walmart que permite:
- Registrar y dar seguimiento a solicitudes de cambio
- Ver un dashboard ejecutivo con KPIs y gráficas
- Gestionar estados, prioridades y avances
- Agregar comentarios e historial de cambios

## PASOS PARA EJECUTAR (solo 3 pasos)

### Paso 1 — Abrir una terminal en esta carpeta
```
pricing-simple/
```

### Paso 2 — Instalar dependencias
```bash
pip install fastapi uvicorn sqlalchemy jinja2 python-multipart
```

### Paso 3 — Ejecutar la app
```bash
python main.py
```

---
### EN TU MÁQUINA ACTUAL (atajo directo)
Ya tienes el venv del proyecto anterior con todo instalado.
Desde la carpeta puppy_workspace ejecuta:
```
cd pricing-simple
..\..\.venv\Scripts\uvicorn.exe main:app --port 8000 --reload
```
O más simple, doble clic en este comando:
```
..\pricing-platform\.venv\Scripts\uvicorn.exe main:app --host 0.0.0.0 --port 8000
```

Luego abre tu navegador en:
👉  http://localhost:8000

============================================================

## CREDENCIALES DE ACCESO

| Rol      | Email                  | Password |
|----------|------------------------|----------|
| Admin    | admin@walmart.com      | admin123 |
| Manager  | ana@walmart.com        | pass123  |
| Dev      | carlos@walmart.com     | pass123  |
| QA       | maria@walmart.com      | pass123  |
| Analista | roberto@walmart.com    | pass123  |

============================================================

## QUÉ INCLUYE EL DEMO

Dashboard  →  http://localhost:8000/
  - KPIs: Total, Activas, Implementadas, Críticas
  - Gráfica de dona por estado
  - Gráfica de barras por prioridad
  - Tabla de solicitudes recientes

Solicitudes →  http://localhost:8000/solicitudes
  - Lista con filtros por estado y prioridad
  - Búsqueda por folio o título
  - Vista en tabla con avance visual

Nueva Solicitud →  http://localhost:8000/solicitudes/nueva
  - Formulario de 3 pasos
  - Tipo, prioridad, área, encargado, riesgo, KPI

Detalle de Solicitud
  - Actualizar estado y porcentaje de avance
  - Agregar comentarios
  - Ver historial de cambios

============================================================

## ARCHIVOS DEL PROYECTO

pricing-simple/
├── main.py              ← TODO el backend (un solo archivo)
├── pricing.db           ← Se crea automático al iniciar
├── COMO_EJECUTAR.md     ← Este archivo
└── templates/
    ├── login.html       ← Pantalla de login
    ├── dashboard.html   ← Dashboard con gráficas
    ← solicitudes.html  ← Lista con filtros
    ├── form.html        ← Crear nueva solicitud
    └── detalle.html     ← Detalle + comentarios + historial

============================================================

## SI ALGO FALLA

Error: "No module named fastapi"
→ Solución: pip install fastapi uvicorn sqlalchemy jinja2 python-multipart

Error: "Port already in use"
→ Solución: Cambiar el puerto en la última línea de main.py (port=8001)

Error de permisos en Windows
→ Ejecutar la terminal como Administrador

============================================================

## TECNOLOGÍAS USADAS

- Python 3.11+
- FastAPI (backend)
- SQLite (base de datos, sin instalar nada extra)
- Jinja2 (templates HTML)
- Tailwind CSS (estilos, via CDN)
- Chart.js (gráficas, via CDN)

============================================================

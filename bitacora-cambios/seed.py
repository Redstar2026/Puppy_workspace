"""Pobla la base de datos con usuarios y tareas de ejemplo."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timedelta
from app.database import engine, SessionLocal
from app import models
from app.auth import hash_password

models.Base.metadata.create_all(bind=engine)
db = SessionLocal()

# ── Usuarios ─────────────────────────────────────────────────────────────────
users_data = [
    ("Admin Sistema",     "admin@walmart.com",   "admin123",  "IT",               "Administrador"),
    ("María García",      "maria@walmart.com",   "pass123",   "Pricing",          "Analista Senior"),
    ("Carlos Rodríguez",  "carlos@walmart.com",  "pass123",   "Pricing",          "Desarrollador"),
    ("Ana López",         "ana@walmart.com",     "pass123",   "QA",               "Analista de Calidad"),
    ("Luis Martínez",     "luis@walmart.com",    "pass123",   "Operaciones",      "Gerente de Área"),
    ("Sofia Herrera",     "sofia@walmart.com",   "pass123",   "Data Analytics",   "Data Engineer"),
]

created_users = []
for nombre, email, pwd, depto, cargo in users_data:
    existing = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if not existing:
        u = models.Usuario(nombre=nombre, email=email,
                           password_hash=hash_password(pwd),
                           departamento=depto, cargo=cargo)
        db.add(u)
        db.flush()
        created_users.append(u)
        print(f"  [OK] Usuario: {nombre} ({email})")
    else:
        created_users.append(existing)
        print(f"  [--] Ya existe: {nombre}")

db.commit()

admin, maria, carlos, ana, luis, sofia = [
    db.query(models.Usuario).filter(models.Usuario.email == e).first()
    for _, e, *_ in users_data
]

# ── Tareas de ejemplo ─────────────────────────────────────────────────────────
tareas_data = [
    {
        "titulo": "Implementación de nueva lógica de precios competitivos",
        "tipo": models.TipoTarea.cambio,
        "descripcion": "Actualizar el algoritmo de precios para considerar datos de competencia en tiempo real. Afecta todas las categorías de electrónicos.",
        "prioridad": models.Prioridad.alta,
        "estado": models.EstadoTarea.en_progreso,
        "encargado_id": carlos.id,
        "fecha_inicio": datetime.now() - timedelta(days=5),
        "fecha_fin": datetime.now() + timedelta(days=10),
        "fecha_implementacion": datetime.now() + timedelta(days=12),
        "requiere_autorizacion": True,
        "dependencias": "Sistema de ingesta de precios (v2.3), API de competencia",
        "beneficio_afectacion": "Mejora estimada del 3% en margen. Riesgo de afectación a ventas si hay errores en algoritmo.",
        "ambiente": "produccion",
        "categoria": "Precios",
        "riesgo": "alto",
        "plan_rollback": "Restaurar configuración anterior desde backup del 01/05/2026",
        "creado_por_id": maria.id,
        "roles": {
            "desarrollo": carlos.id,
            "validacion": ana.id,
            "implementacion": carlos.id,
            "verificacion_vivo": luis.id,
            "presentacion": maria.id,
        }
    },
    {
        "titulo": "Migración de base de datos de inventario a nuevo servidor",
        "tipo": models.TipoTarea.tarea,
        "descripcion": "Migrar la BD de inventario del servidor legacy DB-01 al nuevo clúster PostgreSQL en la nube.",
        "prioridad": models.Prioridad.critica,
        "estado": models.EstadoTarea.pendiente_aprobacion,
        "encargado_id": sofia.id,
        "fecha_inicio": datetime.now() + timedelta(days=2),
        "fecha_fin": datetime.now() + timedelta(days=7),
        "fecha_implementacion": datetime.now() + timedelta(days=8),
        "requiere_autorizacion": True,
        "dependencias": "Ventana de mantenimiento, Backup completo confirmado",
        "beneficio_afectacion": "Mejora de rendimiento 40%, reducción de costos de infraestructura.",
        "ambiente": "produccion",
        "categoria": "Infraestructura",
        "riesgo": "alto",
        "plan_rollback": "Mantener DB-01 activa 72h post-migración para rollback inmediato",
        "creado_por_id": admin.id,
        "roles": {
            "desarrollo": sofia.id,
            "validacion": ana.id,
            "implementacion": sofia.id,
            "verificacion_vivo": carlos.id,
            "presentacion": luis.id,
        }
    },
    {
        "titulo": "Dashboard ejecutivo de indicadores de pricing Q2",
        "tipo": models.TipoTarea.mejora,
        "descripcion": "Crear dashboard en Power BI con KPIs de pricing: competitividad, índice de precios, elasticidad por categoría.",
        "prioridad": models.Prioridad.media,
        "estado": models.EstadoTarea.completada,
        "encargado_id": maria.id,
        "fecha_inicio": datetime.now() - timedelta(days=20),
        "fecha_fin": datetime.now() - timedelta(days=3),
        "fecha_implementacion": datetime.now() - timedelta(days=2),
        "requiere_autorizacion": False,
        "dependencias": "Acceso a BQ: pricing_prod, ventas_consolidado",
        "beneficio_afectacion": "Visibilidad ejecutiva mejorada, toma de decisiones más rápida.",
        "ambiente": "todos",
        "categoria": "Analytics",
        "riesgo": "bajo",
        "plan_rollback": "N/A - Dashboard de solo lectura",
        "creado_por_id": maria.id,
        "roles": {
            "desarrollo": sofia.id,
            "validacion": maria.id,
            "implementacion": sofia.id,
            "verificacion_vivo": luis.id,
            "presentacion": maria.id,
        }
    },
    {
        "titulo": "Incidente: Error en cálculo de descuentos especiales",
        "tipo": models.TipoTarea.incidente,
        "descripcion": "Se detectó error en el módulo de descuentos que aplicaba porcentaje incorrecto en promociones de 2x1.",
        "prioridad": models.Prioridad.critica,
        "estado": models.EstadoTarea.completada,
        "encargado_id": carlos.id,
        "fecha_inicio": datetime.now() - timedelta(days=3),
        "fecha_fin": datetime.now() - timedelta(days=2),
        "fecha_implementacion": datetime.now() - timedelta(days=2),
        "requiere_autorizacion": False,
        "dependencias": "Módulo promociones v1.8",
        "beneficio_afectacion": "Corrección evitó pérdida estimada de $45,000 en descuentos mal aplicados.",
        "ambiente": "produccion",
        "categoria": "Corrección de Bug",
        "riesgo": "alto",
        "plan_rollback": "Hotfix aplicado — rollback a v1.7 disponible",
        "creado_por_id": carlos.id,
        "roles": {
            "desarrollo": carlos.id,
            "validacion": ana.id,
            "implementacion": carlos.id,
            "verificacion_vivo": ana.id,
            "presentacion": luis.id,
        }
    },
    {
        "titulo": "Automatización de reportes semanales de competencia",
        "tipo": models.TipoTarea.mejora,
        "descripcion": "Script Python que genera y envía automáticamente cada lunes el reporte de análisis de precios vs competencia.",
        "prioridad": models.Prioridad.media,
        "estado": models.EstadoTarea.borrador,
        "encargado_id": sofia.id,
        "fecha_inicio": datetime.now() + timedelta(days=5),
        "fecha_fin": datetime.now() + timedelta(days=20),
        "requiere_autorizacion": False,
        "dependencias": "API Competencia, Servicio de correo corporativo",
        "beneficio_afectacion": "Ahorro de 8h/semana en generación manual de reportes.",
        "ambiente": "produccion",
        "categoria": "Automatización",
        "riesgo": "bajo",
        "creado_por_id": sofia.id,
        "roles": {
            "desarrollo": sofia.id,
            "validacion": maria.id,
            "implementacion": sofia.id,
        }
    },
]

for td in tareas_data:
    roles = td.pop("roles", {})
    tarea = models.Tarea(**td)
    db.add(tarea)
    db.flush()

    for rol_key, uid in roles.items():
        try:
            rol_enum = models.RolAsignacion(rol_key)
            db.add(models.AsignacionRol(
                tarea_id=tarea.id,
                rol=rol_enum,
                usuario_id=uid,
                completado=(tarea.estado == models.EstadoTarea.completada)
            ))
        except ValueError:
            pass

    # Historial inicial
    db.add(models.HistorialCambio(
        tarea_id=tarea.id,
        usuario_id=tarea.creado_por_id,
        accion="Tarea creada",
        detalle=f"Creada por seed inicial",
    ))

    # Aprobaciones para las que requieren
    if tarea.requiere_autorizacion and tarea.estado == models.EstadoTarea.pendiente_aprobacion:
        db.add(models.Aprobacion(
            tarea_id=tarea.id,
            aprobador_id=luis.id,
            estado=models.EstadoAprobacion.pendiente,
        ))
    elif tarea.requiere_autorizacion and tarea.estado == models.EstadoTarea.en_progreso:
        db.add(models.Aprobacion(
            tarea_id=tarea.id,
            aprobador_id=luis.id,
            estado=models.EstadoAprobacion.aprobada,
        ))

    # Comentario de ejemplo
    db.add(models.Comentario(
        tarea_id=tarea.id,
        autor_id=maria.id,
        contenido="Tarea registrada en la bitácora. Se coordinará con el equipo en el stand-up del lunes.",
    ))

    print(f"  [OK] Tarea: {tarea.titulo[:60]}...")

db.commit()
db.close()
print("\n[DONE] Seed completado exitosamente!")
print("\n[INFO] Credenciales de acceso:")
for nombre, email, pwd, *_ in users_data:
    print(f"   {email:30s} -> {pwd}")

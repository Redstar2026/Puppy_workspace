"""
Seed de datos realistas para Walmart Pricing Platform.
Ejecutar: uv run python seed.py
"""
from datetime import datetime, timedelta
import random
from app.database import SessionLocal, engine, Base
from app.models import (
    Usuario, Solicitud, Desarrollo, Aprobacion, Comentario,
    HistorialCambio, AuditoriaLog, Etiqueta,
    RolUsuario, TipoSolicitud, Prioridad, EstadoSolicitud,
    NivelRiesgo, ResultadoQA, EstadoAprobacion, TipoAccionAudit,
)
from app.auth import hash_password

Base.metadata.create_all(bind=engine)

def _val(v):
    """Get string value from enum or string."""
    return v.value if hasattr(v, 'value') else str(v)


def main():
    db = SessionLocal()
    # Guard — no re-seed si ya hay usuarios
    if db.query(Usuario).count() > 0:
        print("[OK] Base de datos ya tiene datos. Skipping seed.")
        db.close()
        return

    print("[Seed] Creando datos semilla...")

    # ── Usuarios ──────────────────────────────────────────────────────────
    usuarios_data = [
        ("Admin Sistema",       "admin@walmart.com",       "admin123",  "admin",     "TI",                "Administrador",        True,  True),
        ("Ana García",          "ana.garcia@walmart.com",  "pass123",   "manager",   "Pricing",           "Directora Pricing",    True,  True),
        ("Carlos Mendoza",      "carlos.m@walmart.com",    "pass123",   "developer", "Tech Pricing",      "Desarrollador Senior", False, True),
        ("María López",         "maria.l@walmart.com",     "pass123",   "qa",        "QA",                "QA Engineer",          False, True),
        ("Roberto Jiménez",     "roberto.j@walmart.com",   "pass123",   "analista",  "Pricing",           "Analista de Precios",  False, False),
        ("Laura Sánchez",       "laura.s@walmart.com",     "pass123",   "analista",  "Pricing",           "Analista Senior",      False, False),
        ("Diego Ramírez",       "diego.r@walmart.com",     "pass123",   "developer", "Tech Pricing",      "Backend Engineer",     False, False),
        ("Isabel Torres",       "isabel.t@walmart.com",    "pass123",   "manager",   "Dirección Comercial","Gerente Comercial",   True,  True),
    ]
    usuarios = []
    for nombre, email, pwd, rol, dept, cargo, es_apr, activo in usuarios_data:
        u = Usuario(
            nombre=nombre, email=email,
            password_hash=hash_password(pwd),
            rol=rol, departamento=dept, cargo=cargo,
            es_aprobador=es_apr, activo=activo,
            ultimo_acceso=datetime.utcnow() - timedelta(hours=random.randint(1, 48)),
        )
        db.add(u)
        usuarios.append(u)
    db.flush()

    # ── Etiquetas ─────────────────────────────────────────────────────────
    etiquetas_data = [
        ("Precios", "#0053e2"), ("Automático", "#2a8703"), ("Urgente", "#ea1100"),
        ("ETL", "#7c3aed"), ("BigQuery", "#0891b2"), ("Regla Negocio", "#d97706"),
        ("Integración", "#db2777"), ("Performance", "#059669"),
    ]
    etiquetas = []
    for nombre, color in etiquetas_data:
        e = Etiqueta(nombre=nombre, color=color)
        db.add(e)
        etiquetas.append(e)
    db.flush()

    # ── Solicitudes ───────────────────────────────────────────────────────
    solicitudes_data = [
        # (titulo, tipo, prioridad, estado, avance, area_imp, encargado_idx, riesgo, desc)
        ("Implementación de algoritmo de precios dinámicos por zona geográfica",
         "nuevo_desarrollo", "critica", "en_desarrollo", 45,
         "Pricing / Comercial", 2, "alto",
         "Desarrollar lógica para ajustar precios automáticamente según la zona geográfica del cliente. Implica cambios en motor de precios y reglas de negocio."),
        ("Corrección de redondeo en cálculo de descuentos promocionales",
         "correccion", "alta", "qa", 90,
         "Pricing", 6, "medio",
         "Se detectó error en redondeo al calcular descuentos del 10% y 15%. El sistema aplica centavos incorrectos en ~3% de las transacciones."),
        ("Automatización de reporte semanal de índice de precios vs competencia",
         "automatizacion", "media", "implementado", 100,
         "Pricing / BI", 2, "bajo",
         "Automatizar el proceso de generación del reporte semanal de precios vs competencia. Actualmente toma 4 horas manuales."),
        ("Mejora en tiempo de respuesta del API de precios (SLA <200ms)",
         "mejora", "alta", "en_analisis", 15,
         "Tech Pricing", 2, "alto",
         "El API de precios tiene tiempos de respuesta de 800ms en horas pico. Meta: <200ms. Se requiere optimización de queries y caching."),
        ("Incidencia: Precios incorrectos en categoría Electrónica 14 Nov",
         "incidencia", "critica", "implementado", 100,
         "Pricing / Electrónica", 2, "critico",
         "A las 14:30 se detectaron precios incorrectos en ~200 SKUs de electrónica. Causa: fallo en ETL de actualización nocturna."),
        ("Ajuste de reglas de precio mínimo para productos frescos",
         "ajuste", "media", "pendiente", 0,
         "Pricing / Frescos", 4, "medio",
         "Actualizar las reglas de precio mínimo para la categoría de frescos acorde a nueva política comercial Q1 2026."),
        ("Nuevo módulo de simulación de impacto de cambios de precio",
         "nuevo_desarrollo", "alta", "en_desarrollo", 35,
         "Pricing / Analytics", 6, "medio",
         "Crear herramienta de simulación que permita al equipo de Pricing visualizar el impacto financiero de un cambio de precio antes de implementarlo."),
        ("Integración con sistema de proveedores para precios de costo en tiempo real",
         "nuevo_desarrollo", "alta", "aprobacion", 75,
         "Pricing / Compras", 2, "alto",
         "Conectar el motor de precios con el sistema de proveedores para recibir actualizaciones de precios de costo en tiempo real vía API REST."),
        ("Corrección de cálculo de IVA en productos exentos",
         "correccion", "alta", "implementado", 100,
         "Pricing / Fiscal", 2, "alto",
         "Algunos productos exentos de IVA estaban aplicando la tasa del 16%. Corrección urgente requerida para cumplimiento fiscal."),
        ("Dashboard de monitoreo de precios en tiempo real",
         "nuevo_desarrollo", "media", "en_analisis", 20,
         "Pricing / BI", 4, "bajo",
         "Crear dashboard ejecutivo con métricas de precios en tiempo real: variaciones, alertas, comparativo vs competencia."),
        ("Automatización de alertas de precio por debajo del costo",
         "automatizacion", "alta", "en_desarrollo", 60,
         "Pricing", 6, "medio",
         "Sistema de alertas automáticas cuando un precio de venta queda por debajo del costo de adquisición + margen mínimo."),
        ("Mejora en validaciones del formulario de captura de precios",
         "mejora", "baja", "pendiente", 0,
         "Pricing UX", 4, "bajo",
         "El formulario de captura de precios carece de validaciones básicas. Se requiere agregar validaciones de rango, formato y duplicados."),
    ]

    solicitudes = []
    anio = datetime.utcnow().year
    for i, (titulo, tipo, prio, estado, avance, area, enc_idx, riesgo, desc) in enumerate(solicitudes_data, 1):
        sol = Solicitud(
            folio=f"SOL-{anio}-{i:04d}",
            titulo=titulo, tipo=tipo, prioridad=prio, estado=estado,
            porcentaje_avance=float(avance),
            area_impactada=area,
            area_solicitante="Equipo de Pricing",
            descripcion=desc,
            encargado_id=usuarios[enc_idx].id,
            creado_por_id=usuarios[0].id,
            riesgo_operativo=riesgo,
            equipo_responsable="Squad Pricing Tech",
            requiere_aprobacion=(prio in ["alta", "critica"]),
            kpi_asociado="Reducir error de precios <0.5%",
            beneficios_esperados="Reducción de incidencias operativas",
            impacto_esperado="Mejora en eficiencia y precisión de precios",
            fecha_ingreso=datetime.utcnow() - timedelta(days=random.randint(5, 90)),
            fecha_estimada_fin=datetime.utcnow() + timedelta(days=random.randint(7, 60)),
            fecha_implementacion=datetime.utcnow() - timedelta(days=random.randint(1, 10)) if estado == "implementado" else None,
        )
        if etiquetas:
            sol.etiquetas.append(random.choice(etiquetas))
        db.add(sol)
        solicitudes.append(sol)

    db.flush()

    # ── Historial para cada solicitud ────────────────────────────────────
    for sol in solicitudes:
        db.add(HistorialCambio(
            solicitud_id=sol.id,
            usuario_id=usuarios[0].id,
            accion="Solicitud creada",
            detalle=f"Solicitud {sol.folio} registrada en el sistema",
        ))
        if _val(sol.estado) != "pendiente":
            db.add(HistorialCambio(
                solicitud_id=sol.id,
                usuario_id=usuarios[2].id,
                accion="Cambio de estado",
                campo_modificado="estado",
                valor_anterior="pendiente",
                valor_nuevo=_val(sol.estado),
            ))

    # ── Aprobaciones ─────────────────────────────────────────────────────
    aprobaciones_soles = [s for s in solicitudes if s.requiere_aprobacion]
    for sol in aprobaciones_soles[:5]:
        es_impl = _val(sol.estado) == "implementado"
        ap = Aprobacion(
            solicitud_id=sol.id,
            aprobador_id=usuarios[1].id,
            orden=1,
            estado="aprobado" if es_impl else "pendiente",
            comentario="Revisado y aprobado. Proceder con implementación." if es_impl else "",
            respondida_en=datetime.utcnow() - timedelta(days=2) if es_impl else None,
        )
        db.add(ap)
        ap2 = Aprobacion(
            solicitud_id=sol.id,
            aprobador_id=usuarios[7].id,
            orden=2,
            estado="aprobado" if es_impl else "pendiente",
            comentario="OK desde área comercial." if es_impl else "",
            respondida_en=datetime.utcnow() - timedelta(days=1) if es_impl else None,
        )
        db.add(ap2)

    # ── Comentarios ──────────────────────────────────────────────────────
    comentarios_ejemplo = [
        "Confirmado, esto es prioritario para Q4. Asignar máxima prioridad.",
        "Se requiere análisis de impacto en sistemas downstream antes de proceder.",
        "El equipo de QA estará disponible a partir del lunes para las pruebas.",
        "Coordinado con el área de TI para los ambientes de prueba.",
        "Revisando dependencias técnicas con el equipo de arquitectura.",
        "Actualización: ya se completó la fase de análisis. Pasamos a desarrollo.",
    ]
    for i, sol in enumerate(solicitudes[:8]):
        com = Comentario(
            solicitud_id=sol.id,
            autor_id=random.choice([u.id for u in usuarios[:5]]),
            contenido=comentarios_ejemplo[i % len(comentarios_ejemplo)],
            tipo="interno",
        )
        db.add(com)

    # ── Desarrollos ──────────────────────────────────────────────────────
    desarrollos_data = [
        ("Motor de Precios Dinámicos v2.0",
         solicitudes[0],
         "Refactorización completa del motor de precios para soportar reglas geográficas y temporales dinámicas.",
         "implementado", 100, "aprobado",
         "walmart-pricing/pricing-engine", "feat/dynamic-pricing-v2", "a1b2c3d", "https://github.com/walmart-pricing/pricing-engine/pull/42"),
        ("Fix Redondeo Descuentos - Hotfix",
         solicitudes[1],
         "Corrección de bug en función de redondeo que afectaba cálculo de descuentos del 10% y 15%.",
         "qa", 85, "con_observaciones",
         "walmart-pricing/pricing-core", "hotfix/discount-rounding", "e5f6g7h", ""),
        ("ETL Automatización Reporte Semanal",
         solicitudes[2],
         "Pipeline de datos automatizado en BigQuery para generar el reporte semanal de precios.",
         "implementado", 100, "aprobado",
         "walmart-pricing/data-pipelines", "main", "i9j0k1l", "https://github.com/walmart-pricing/data-pipelines/pull/15"),
        ("Optimización API Precios - Cache Redis",
         solicitudes[3],
         "Implementación de capa de caché con Redis para mejorar SLA del API de precios a <200ms.",
         "en_desarrollo", 40, "pendiente",
         "walmart-pricing/pricing-api", "feat/redis-cache", "", ""),
        ("Módulo Simulación Impacto Precios",
         solicitudes[6],
         "Herramienta de simulación con cálculo de elasticidad y proyección de ventas.",
         "en_desarrollo", 35, "pendiente",
         "walmart-pricing/pricing-tools", "feat/simulation-module", "", ""),
    ]

    for i, (nombre, sol, desc_tec, estado, avance, qa_res, repo, branch, commit, pr) in enumerate(desarrollos_data, 1):
        dev = Desarrollo(
            folio=f"DEV-{anio}-{i:04d}",
            solicitud_id=sol.id if sol else None,
            nombre=nombre,
            descripcion_tecnica=desc_tec,
            objetivo_cambio=sol.descripcion[:200] if sol else "",
            estado=estado,
            porcentaje_avance=float(avance),
            responsable_dev_id=usuarios[2].id,
            responsable_qa_id=usuarios[3].id,
            responsable_negocio_id=usuarios[1].id,
            resultado_qa=qa_res,
            riesgo_cambio="medio",
            github_repo=repo,
            github_branch=branch,
            github_commit=commit,
            github_pr=pr,
            tipo_implementacion="Backend Python" if i % 2 == 0 else "SQL / BigQuery",
            ambiente="produccion" if estado == "implementado" else "qa",
            rollback_plan="Revertir al tag anterior y ejecutar migration rollback script.",
            resultado_esperado="Cumplimiento de SLA y reducción de incidencias en un 80%.",
            fecha_ingreso=datetime.utcnow() - timedelta(days=random.randint(10, 60)),
            fecha_estimada=datetime.utcnow() + timedelta(days=random.randint(5, 30)),
            fecha_implementacion=datetime.utcnow() - timedelta(days=3) if estado == "implementado" else None,
        )
        db.add(dev)
        db.flush()
        db.add(HistorialCambio(
            desarrollo_id=dev.id,
            usuario_id=usuarios[2].id,
            accion="Desarrollo creado",
            detalle=f"{dev.folio} registrado por {usuarios[2].nombre}",
        ))

    # ── Auditoría ────────────────────────────────────────────────────────
    acciones_audit = [TipoAccionAudit.login, TipoAccionAudit.creacion,
                      TipoAccionAudit.actualizacion, TipoAccionAudit.estado_cambio]
    for j in range(20):
        u = random.choice(usuarios[:6])
        db.add(AuditoriaLog(
            usuario_id=u.id,
            accion=random.choice(acciones_audit),
            tabla_afectada=random.choice(["solicitudes", "desarrollos", "aprobaciones"]),
            registro_id=random.randint(1, 10),
            descripcion=f"Acción de sistema registrada automáticamente",
            ip_address=f"10.0.{random.randint(1,5)}.{random.randint(10,200)}",
            creado_en=datetime.utcnow() - timedelta(hours=random.randint(1, 720)),
        ))

    db.commit()
    db.close()
    print("[OK] Seed completado exitosamente!")
    print("\nCredenciales de acceso:")
    print("  Admin:    admin@walmart.com / admin123")
    print("  Manager:  ana.garcia@walmart.com / pass123")
    print("  Dev:      carlos.m@walmart.com / pass123")
    print("  QA:       maria.l@walmart.com / pass123")
    print("  Analista: roberto.j@walmart.com / pass123")


if __name__ == "__main__":
    main()

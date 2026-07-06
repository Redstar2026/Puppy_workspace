"""
Walmart Pricing Platform — Modelos de Base de Datos
Arquitectura enterprise con auditoría completa y trazabilidad total.
"""
import secrets
from datetime import datetime
import enum
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime,
    Float, ForeignKey, Enum as SAEnum, Table, Index
)
from sqlalchemy.orm import relationship
from app.database import Base


# ── Enumeraciones ──────────────────────────────────────────────────────────────

class RolUsuario(str, enum.Enum):
    admin = "admin"
    manager = "manager"
    developer = "developer"
    qa = "qa"
    analista = "analista"
    viewer = "viewer"


class TipoSolicitud(str, enum.Enum):
    nuevo_desarrollo = "nuevo_desarrollo"
    ajuste = "ajuste"
    correccion = "correccion"
    mejora = "mejora"
    incidencia = "incidencia"
    automatizacion = "automatizacion"


class Prioridad(str, enum.Enum):
    baja = "baja"
    media = "media"
    alta = "alta"
    critica = "critica"


class EstadoSolicitud(str, enum.Enum):
    pendiente = "pendiente"
    en_analisis = "en_analisis"
    en_desarrollo = "en_desarrollo"
    qa = "qa"
    aprobacion = "aprobacion"
    implementado = "implementado"
    rechazado = "rechazado"
    cancelado = "cancelado"


class NivelRiesgo(str, enum.Enum):
    bajo = "bajo"
    medio = "medio"
    alto = "alto"
    critico = "critico"


class EstadoAprobacion(str, enum.Enum):
    pendiente = "pendiente"
    aprobado = "aprobado"
    rechazado = "rechazado"
    omitido = "omitido"


class TipoAccionAudit(str, enum.Enum):
    creacion = "creacion"
    actualizacion = "actualizacion"
    eliminacion = "eliminacion"
    aprobacion = "aprobacion"
    rechazo = "rechazo"
    comentario = "comentario"
    archivo = "archivo"
    estado_cambio = "estado_cambio"
    login = "login"


class ResultadoQA(str, enum.Enum):
    pendiente = "pendiente"
    aprobado = "aprobado"
    rechazado = "rechazado"
    con_observaciones = "con_observaciones"


# ── Tabla de asociación solicitud–etiquetas ────────────────────────────────────

solicitud_etiquetas = Table(
    "solicitud_etiquetas",
    Base.metadata,
    Column("solicitud_id", Integer, ForeignKey("solicitudes.id"), primary_key=True),
    Column("etiqueta_id", Integer, ForeignKey("etiquetas.id"), primary_key=True),
)

desarrollo_etiquetas = Table(
    "desarrollo_etiquetas",
    Base.metadata,
    Column("desarrollo_id", Integer, ForeignKey("desarrollos.id"), primary_key=True),
    Column("etiqueta_id", Integer, ForeignKey("etiquetas.id"), primary_key=True),
)


# ── Modelos ────────────────────────────────────────────────────────────────────

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(120), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(200), nullable=False)
    rol = Column(SAEnum(RolUsuario), default=RolUsuario.analista)
    departamento = Column(String(100), default="Pricing")
    cargo = Column(String(100), default="")
    avatar_url = Column(String(300), default="")
    activo = Column(Boolean, default=True)
    es_aprobador = Column(Boolean, default=False)
    creado_en = Column(DateTime, default=datetime.utcnow)
    ultimo_acceso = Column(DateTime, nullable=True)

    # Relaciones
    solicitudes_creadas = relationship("Solicitud", back_populates="creado_por",
                                       foreign_keys="Solicitud.creado_por_id")
    solicitudes_asignadas = relationship("Solicitud", back_populates="encargado",
                                         foreign_keys="Solicitud.encargado_id")
    desarrollos_responsable = relationship("Desarrollo", back_populates="responsable_dev",
                                           foreign_keys="Desarrollo.responsable_dev_id")
    desarrollos_qa = relationship("Desarrollo", back_populates="responsable_qa",
                                  foreign_keys="Desarrollo.responsable_qa_id")
    aprobaciones = relationship("Aprobacion", back_populates="aprobador")
    comentarios = relationship("Comentario", back_populates="autor")
    auditoria = relationship("AuditoriaLog", back_populates="usuario")


class Etiqueta(Base):
    __tablename__ = "etiquetas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)
    color = Column(String(7), default="#0053e2")  # Walmart Blue por defecto
    descripcion = Column(String(200), default="")


class Solicitud(Base):
    __tablename__ = "solicitudes"
    __table_args__ = (
        Index("ix_solicitudes_estado", "estado"),
        Index("ix_solicitudes_prioridad", "prioridad"),
        Index("ix_solicitudes_fecha_ingreso", "fecha_ingreso"),
    )

    id = Column(Integer, primary_key=True, index=True)
    folio = Column(String(20), unique=True, index=True)  # SOL-2025-0001
    tipo = Column(SAEnum(TipoSolicitud), nullable=False)
    titulo = Column(String(300), nullable=False)
    descripcion = Column(Text, default="")
    area_impactada = Column(String(150), default="")
    prioridad = Column(SAEnum(Prioridad), default=Prioridad.media)
    estado = Column(SAEnum(EstadoSolicitud), default=EstadoSolicitud.pendiente)
    porcentaje_avance = Column(Float, default=0.0)

    # Fechas
    fecha_ingreso = Column(DateTime, default=datetime.utcnow)
    fecha_estimada_fin = Column(DateTime, nullable=True)
    fecha_real_fin = Column(DateTime, nullable=True)
    fecha_implementacion = Column(DateTime, nullable=True)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Personas
    creado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    area_solicitante = Column(String(150), default="")
    encargado_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    equipo_responsable = Column(String(200), default="")

    # Detalles operativos
    dependencias = Column(Text, default="")
    requiere_aprobacion = Column(Boolean, default=False)
    riesgo_operativo = Column(SAEnum(NivelRiesgo), default=NivelRiesgo.bajo)
    impacto_esperado = Column(Text, default="")
    beneficios_esperados = Column(Text, default="")
    kpi_asociado = Column(String(200), default="")
    comentarios_internos = Column(Text, default="")

    # Relaciones
    creado_por = relationship("Usuario", back_populates="solicitudes_creadas",
                              foreign_keys=[creado_por_id])
    encargado = relationship("Usuario", back_populates="solicitudes_asignadas",
                             foreign_keys=[encargado_id])
    aprobaciones = relationship("Aprobacion", back_populates="solicitud",
                                cascade="all, delete-orphan",
                                foreign_keys="Aprobacion.solicitud_id")
    comentarios = relationship("Comentario", back_populates="solicitud",
                               cascade="all, delete-orphan",
                               foreign_keys="Comentario.solicitud_id")
    historial = relationship("HistorialCambio", back_populates="solicitud",
                             cascade="all, delete-orphan",
                             foreign_keys="HistorialCambio.solicitud_id")
    adjuntos = relationship("Adjunto", back_populates="solicitud",
                            cascade="all, delete-orphan",
                            foreign_keys="Adjunto.solicitud_id")
    etiquetas = relationship("Etiqueta", secondary=solicitud_etiquetas)
    desarrollo = relationship("Desarrollo", back_populates="solicitud",
                              uselist=False, foreign_keys="Desarrollo.solicitud_id")


class Desarrollo(Base):
    __tablename__ = "desarrollos"
    __table_args__ = (
        Index("ix_desarrollos_estado", "estado"),
        Index("ix_desarrollos_fecha_ingreso", "fecha_ingreso"),
    )

    id = Column(Integer, primary_key=True, index=True)
    folio = Column(String(20), unique=True, index=True)  # DEV-2025-0001
    solicitud_id = Column(Integer, ForeignKey("solicitudes.id"), nullable=True)
    nombre = Column(String(300), nullable=False)
    descripcion_tecnica = Column(Text, default="")
    objetivo_cambio = Column(Text, default="")

    # Fechas
    fecha_ingreso = Column(DateTime, default=datetime.utcnow)
    fecha_estimada = Column(DateTime, nullable=True)
    fecha_finalizacion = Column(DateTime, nullable=True)
    fecha_implementacion = Column(DateTime, nullable=True)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Estados y avance
    estado = Column(SAEnum(EstadoSolicitud), default=EstadoSolicitud.pendiente)
    porcentaje_avance = Column(Float, default=0.0)

    # Responsables
    responsable_dev_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    responsable_qa_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    responsable_negocio_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    # QA y validación
    validacion_qa = Column(Boolean, default=False)
    resultado_qa = Column(SAEnum(ResultadoQA), default=ResultadoQA.pendiente)
    checklist_validacion = Column(Text, default="")  # JSON serialized
    evidencia_pruebas = Column(Text, default="")
    aprobacion_implementacion = Column(Boolean, default=False)
    presentacion_resultados = Column(Text, default="")

    # Riesgo e impacto
    riesgo_cambio = Column(SAEnum(NivelRiesgo), default=NivelRiesgo.bajo)
    impacto_operativo = Column(Text, default="")
    beneficios_esperados = Column(Text, default="")
    resultado_esperado = Column(Text, default="")
    resultado_real = Column(Text, default="")
    rollback_plan = Column(Text, default="")
    dependencias_tecnicas = Column(Text, default="")

    # GitHub integration
    github_repo = Column(String(300), default="")
    github_commit = Column(String(100), default="")
    github_pr = Column(String(300), default="")
    github_branch = Column(String(100), default="")
    logs_implementacion = Column(Text, default="")

    # Tipo implementación
    tipo_implementacion = Column(String(100), default="")
    ambiente = Column(String(50), default="produccion")

    # Relaciones
    solicitud = relationship("Solicitud", back_populates="desarrollo",
                             foreign_keys=[solicitud_id])
    responsable_dev = relationship("Usuario", back_populates="desarrollos_responsable",
                                   foreign_keys=[responsable_dev_id])
    responsable_qa = relationship("Usuario", back_populates="desarrollos_qa",
                                  foreign_keys=[responsable_qa_id])
    responsable_negocio = relationship("Usuario", foreign_keys=[responsable_negocio_id])
    aprobaciones = relationship("Aprobacion", back_populates="desarrollo",
                                cascade="all, delete-orphan",
                                foreign_keys="Aprobacion.desarrollo_id")
    comentarios = relationship("Comentario", back_populates="desarrollo",
                               cascade="all, delete-orphan",
                               foreign_keys="Comentario.desarrollo_id")
    historial = relationship("HistorialCambio", back_populates="desarrollo",
                             cascade="all, delete-orphan",
                             foreign_keys="HistorialCambio.desarrollo_id")
    adjuntos = relationship("Adjunto", back_populates="desarrollo",
                            cascade="all, delete-orphan",
                            foreign_keys="Adjunto.desarrollo_id")
    etiquetas = relationship("Etiqueta", secondary=desarrollo_etiquetas)


class Aprobacion(Base):
    __tablename__ = "aprobaciones"

    id = Column(Integer, primary_key=True, index=True)
    solicitud_id = Column(Integer, ForeignKey("solicitudes.id"), nullable=True)
    desarrollo_id = Column(Integer, ForeignKey("desarrollos.id"), nullable=True)
    aprobador_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    orden = Column(Integer, default=1)
    estado = Column(SAEnum(EstadoAprobacion), default=EstadoAprobacion.pendiente)
    comentario = Column(Text, default="")
    token = Column(String(64), unique=True, default=lambda: secrets.token_urlsafe(32))
    solicitada_en = Column(DateTime, default=datetime.utcnow)
    respondida_en = Column(DateTime, nullable=True)
    notificado = Column(Boolean, default=False)

    # Relaciones
    solicitud = relationship("Solicitud", back_populates="aprobaciones",
                             foreign_keys=[solicitud_id])
    desarrollo = relationship("Desarrollo", back_populates="aprobaciones",
                              foreign_keys=[desarrollo_id])
    aprobador = relationship("Usuario", back_populates="aprobaciones")


class Comentario(Base):
    __tablename__ = "comentarios"

    id = Column(Integer, primary_key=True, index=True)
    solicitud_id = Column(Integer, ForeignKey("solicitudes.id"), nullable=True)
    desarrollo_id = Column(Integer, ForeignKey("desarrollos.id"), nullable=True)
    autor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    contenido = Column(Text, nullable=False)
    tipo = Column(String(30), default="interno")  # interno, aprobador, sistema
    creado_en = Column(DateTime, default=datetime.utcnow)
    editado = Column(Boolean, default=False)

    # Relaciones
    solicitud = relationship("Solicitud", back_populates="comentarios",
                             foreign_keys=[solicitud_id])
    desarrollo = relationship("Desarrollo", back_populates="comentarios",
                              foreign_keys=[desarrollo_id])
    autor = relationship("Usuario", back_populates="comentarios")


class HistorialCambio(Base):
    """Versionado automático de todos los cambios de campos."""
    __tablename__ = "historial_cambios"

    id = Column(Integer, primary_key=True, index=True)
    solicitud_id = Column(Integer, ForeignKey("solicitudes.id"), nullable=True)
    desarrollo_id = Column(Integer, ForeignKey("desarrollos.id"), nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    accion = Column(String(100), nullable=False)
    campo_modificado = Column(String(100), default="")
    valor_anterior = Column(Text, default="")
    valor_nuevo = Column(Text, default="")
    detalle = Column(Text, default="")
    creado_en = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    solicitud = relationship("Solicitud", back_populates="historial",
                             foreign_keys=[solicitud_id])
    desarrollo = relationship("Desarrollo", back_populates="historial",
                              foreign_keys=[desarrollo_id])
    usuario = relationship("Usuario")


class AuditoriaLog(Base):
    """Auditoría de seguridad — registro de TODAS las acciones de usuarios."""
    __tablename__ = "auditoria_logs"
    __table_args__ = (
        Index("ix_audit_usuario_id", "usuario_id"),
        Index("ix_audit_creado_en", "creado_en"),
        Index("ix_audit_tabla", "tabla_afectada"),
    )

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    accion = Column(SAEnum(TipoAccionAudit), nullable=False)
    tabla_afectada = Column(String(50), default="")
    registro_id = Column(Integer, nullable=True)
    descripcion = Column(Text, default="")
    ip_address = Column(String(45), default="")
    user_agent = Column(String(500), default="")
    creado_en = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    usuario = relationship("Usuario", back_populates="auditoria")


class Adjunto(Base):
    __tablename__ = "adjuntos"

    id = Column(Integer, primary_key=True, index=True)
    solicitud_id = Column(Integer, ForeignKey("solicitudes.id"), nullable=True)
    desarrollo_id = Column(Integer, ForeignKey("desarrollos.id"), nullable=True)
    subido_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    nombre_original = Column(String(300), nullable=False)
    nombre_almacenado = Column(String(300), nullable=False)
    ruta = Column(String(500), nullable=False)
    tipo_mime = Column(String(100), default="")
    tamano_bytes = Column(Integer, default=0)
    creado_en = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    solicitud = relationship("Solicitud", back_populates="adjuntos",
                             foreign_keys=[solicitud_id])
    desarrollo = relationship("Desarrollo", back_populates="adjuntos",
                              foreign_keys=[desarrollo_id])
    subido_por = relationship("Usuario")

import secrets
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime,
    ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class TipoTarea(str, enum.Enum):
    cambio = "cambio"
    tarea = "tarea"
    incidente = "incidente"
    mejora = "mejora"


class Prioridad(str, enum.Enum):
    critica = "critica"
    alta = "alta"
    media = "media"
    baja = "baja"


class EstadoTarea(str, enum.Enum):
    borrador = "borrador"
    pendiente_aprobacion = "pendiente_aprobacion"
    aprobada = "aprobada"
    rechazada = "rechazada"
    en_progreso = "en_progreso"
    en_revision = "en_revision"
    completada = "completada"
    cancelada = "cancelada"


class EstadoAprobacion(str, enum.Enum):
    pendiente = "pendiente"
    aprobada = "aprobada"
    rechazada = "rechazada"


class RolAsignacion(str, enum.Enum):
    desarrollo = "desarrollo"
    validacion = "validacion"
    implementacion = "implementacion"
    verificacion_vivo = "verificacion_vivo"
    presentacion = "presentacion"


class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(200), nullable=False)
    departamento = Column(String(100), default="")
    cargo = Column(String(100), default="")
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime, default=datetime.utcnow)

    tareas_encargado = relationship("Tarea", back_populates="encargado", foreign_keys="Tarea.encargado_id")
    asignaciones = relationship("AsignacionRol", back_populates="usuario")
    aprobaciones = relationship("Aprobacion", back_populates="aprobador")
    comentarios = relationship("Comentario", back_populates="autor")
    historial = relationship("HistorialCambio", back_populates="usuario")


class Tarea(Base):
    __tablename__ = "tareas"
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(SAEnum(TipoTarea), nullable=False, default=TipoTarea.tarea)
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text, default="")
    prioridad = Column(SAEnum(Prioridad), default=Prioridad.media)
    estado = Column(SAEnum(EstadoTarea), default=EstadoTarea.borrador)
    encargado_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    fecha_inicio = Column(DateTime, nullable=True)
    fecha_fin = Column(DateTime, nullable=True)
    fecha_implementacion = Column(DateTime, nullable=True)
    requiere_autorizacion = Column(Boolean, default=False)
    dependencias = Column(Text, default="")
    beneficio_afectacion = Column(Text, default="")
    ambiente = Column(String(50), default="produccion")
    categoria = Column(String(100), default="")
    riesgo = Column(String(50), default="bajo")
    plan_rollback = Column(Text, default="")
    creado_en = Column(DateTime, default=datetime.utcnow)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    creado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    encargado = relationship("Usuario", back_populates="tareas_encargado", foreign_keys=[encargado_id])
    creado_por = relationship("Usuario", foreign_keys=[creado_por_id])
    asignaciones = relationship("AsignacionRol", back_populates="tarea", cascade="all, delete-orphan")
    aprobaciones = relationship("Aprobacion", back_populates="tarea", cascade="all, delete-orphan")
    historial = relationship("HistorialCambio", back_populates="tarea", cascade="all, delete-orphan")
    comentarios = relationship("Comentario", back_populates="tarea", cascade="all, delete-orphan")


class AsignacionRol(Base):
    __tablename__ = "asignaciones_rol"
    id = Column(Integer, primary_key=True, index=True)
    tarea_id = Column(Integer, ForeignKey("tareas.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    rol = Column(SAEnum(RolAsignacion), nullable=False)
    notas = Column(Text, default="")
    completado = Column(Boolean, default=False)

    tarea = relationship("Tarea", back_populates="asignaciones")
    usuario = relationship("Usuario", back_populates="asignaciones")


class Aprobacion(Base):
    __tablename__ = "aprobaciones"
    id = Column(Integer, primary_key=True, index=True)
    tarea_id = Column(Integer, ForeignKey("tareas.id"), nullable=False)
    aprobador_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    estado = Column(SAEnum(EstadoAprobacion), default=EstadoAprobacion.pendiente)
    comentario = Column(Text, default="")
    token = Column(String(64), unique=True, default=lambda: secrets.token_urlsafe(32))
    solicitada_en = Column(DateTime, default=datetime.utcnow)
    respondida_en = Column(DateTime, nullable=True)

    tarea = relationship("Tarea", back_populates="aprobaciones")
    aprobador = relationship("Usuario", back_populates="aprobaciones")


class HistorialCambio(Base):
    __tablename__ = "historial_cambios"
    id = Column(Integer, primary_key=True, index=True)
    tarea_id = Column(Integer, ForeignKey("tareas.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    accion = Column(String(100), nullable=False)
    detalle = Column(Text, default="")
    campo_modificado = Column(String(100), default="")
    valor_anterior = Column(Text, default="")
    valor_nuevo = Column(Text, default="")
    creado_en = Column(DateTime, default=datetime.utcnow)

    tarea = relationship("Tarea", back_populates="historial")
    usuario = relationship("Usuario", back_populates="historial")


class Comentario(Base):
    __tablename__ = "comentarios"
    id = Column(Integer, primary_key=True, index=True)
    tarea_id = Column(Integer, ForeignKey("tareas.id"), nullable=False)
    autor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    contenido = Column(Text, nullable=False)
    creado_en = Column(DateTime, default=datetime.utcnow)

    tarea = relationship("Tarea", back_populates="comentarios")
    autor = relationship("Usuario", back_populates="comentarios")

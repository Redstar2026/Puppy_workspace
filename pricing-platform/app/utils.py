"""Helpers de utilidad — generación de folios, paginación, etc."""
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Solicitud, Desarrollo


def generar_folio_solicitud(db: Session) -> str:
    anio = datetime.utcnow().year
    ultimo = (
        db.query(Solicitud)
        .filter(Solicitud.folio.like(f"SOL-{anio}-%"))
        .order_by(Solicitud.id.desc())
        .first()
    )
    if ultimo and ultimo.folio:
        num = int(ultimo.folio.split("-")[-1]) + 1
    else:
        num = 1
    return f"SOL-{anio}-{num:04d}"


def generar_folio_desarrollo(db: Session) -> str:
    anio = datetime.utcnow().year
    ultimo = (
        db.query(Desarrollo)
        .filter(Desarrollo.folio.like(f"DEV-{anio}-%"))
        .order_by(Desarrollo.id.desc())
        .first()
    )
    if ultimo and ultimo.folio:
        num = int(ultimo.folio.split("-")[-1]) + 1
    else:
        num = 1
    return f"DEV-{anio}-{num:04d}"


def label_estado(estado: str) -> dict:
    """Devuelve texto y color CSS para cada estado."""
    MAP = {
        "pendiente":      {"label": "Pendiente",       "css": "badge-gray"},
        "en_analisis":    {"label": "En Análisis",     "css": "badge-blue"},
        "en_desarrollo":  {"label": "En Desarrollo",   "css": "badge-indigo"},
        "qa":             {"label": "QA",               "css": "badge-purple"},
        "aprobacion":     {"label": "Aprobación",      "css": "badge-yellow"},
        "implementado":   {"label": "Implementado",    "css": "badge-green"},
        "rechazado":      {"label": "Rechazado",       "css": "badge-red"},
        "cancelado":      {"label": "Cancelado",       "css": "badge-dark"},
    }
    return MAP.get(estado, {"label": estado, "css": "badge-gray"})


def label_prioridad(prioridad: str) -> dict:
    MAP = {
        "baja":    {"label": "Baja",    "css": "badge-green",  "icon": "▼"},
        "media":   {"label": "Media",   "css": "badge-blue",   "icon": "◆"},
        "alta":    {"label": "Alta",    "css": "badge-yellow", "icon": "▲"},
        "critica": {"label": "Crítica", "css": "badge-red",    "icon": "⚠"},
    }
    return MAP.get(prioridad, {"label": prioridad, "css": "badge-gray", "icon": "◆"})


def label_riesgo(riesgo: str) -> dict:
    MAP = {
        "bajo":    {"label": "Bajo",    "css": "text-green-600"},
        "medio":   {"label": "Medio",   "css": "text-yellow-600"},
        "alto":    {"label": "Alto",    "css": "text-orange-600"},
        "critico": {"label": "Crítico", "css": "text-red-600"},
    }
    return MAP.get(riesgo, {"label": riesgo, "css": "text-gray-600"})


ESTADOS_KANBAN = [
    "pendiente", "en_analisis", "en_desarrollo",
    "qa", "aprobacion", "implementado"
]

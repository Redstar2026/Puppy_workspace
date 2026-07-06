"""Dashboard ejecutivo con KPIs y gráficas."""
from datetime import datetime, timedelta
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.auth import get_current_user
from app.models import Solicitud, Desarrollo, Aprobacion, EstadoSolicitud, Prioridad
from app.templates import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=302)

    total_solicitudes = db.query(Solicitud).count()
    abiertas = db.query(Solicitud).filter(
        Solicitud.estado.notin_(["implementado", "rechazado", "cancelado"])
    ).count()
    implementadas_mes = db.query(Solicitud).filter(
        Solicitud.estado == EstadoSolicitud.implementado,
        Solicitud.fecha_implementacion >= datetime.utcnow() - timedelta(days=30),
    ).count()
    pendientes_aprobacion = db.query(Aprobacion).filter(
        Aprobacion.estado == "pendiente"
    ).count()
    criticas = db.query(Solicitud).filter(
        Solicitud.prioridad == Prioridad.critica,
        Solicitud.estado.notin_(["implementado", "rechazado", "cancelado"]),
    ).count()
    en_riesgo = db.query(Solicitud).filter(
        Solicitud.riesgo_operativo.in_(["alto", "critico"]),
        Solicitud.estado.notin_(["implementado", "rechazado", "cancelado"]),
    ).count()

    por_estado_raw = db.query(
        Solicitud.estado, func.count(Solicitud.id)
    ).group_by(Solicitud.estado).all()
    por_estado = {
        (r[0].value if hasattr(r[0], "value") else r[0]): r[1]
        for r in por_estado_raw
    }

    por_prioridad_raw = db.query(
        Solicitud.prioridad, func.count(Solicitud.id)
    ).group_by(Solicitud.prioridad).all()
    por_prioridad = {
        (r[0].value if hasattr(r[0], "value") else r[0]): r[1]
        for r in por_prioridad_raw
    }

    meses, impl_mes, sol_mes = [], [], []
    for i in range(5, -1, -1):
        inicio = (datetime.utcnow() - timedelta(days=30 * i)).replace(
            day=1, hour=0, minute=0, second=0, microsecond=0)
        fin_mes = (inicio + timedelta(days=32)).replace(day=1)
        meses.append(inicio.strftime("%b %Y"))
        impl_mes.append(db.query(Solicitud).filter(
            Solicitud.estado == EstadoSolicitud.implementado,
            Solicitud.fecha_implementacion >= inicio,
            Solicitud.fecha_implementacion < fin_mes,
        ).count())
        sol_mes.append(db.query(Solicitud).filter(
            Solicitud.fecha_ingreso >= inicio,
            Solicitud.fecha_ingreso < fin_mes,
        ).count())

    recientes = db.query(Solicitud).order_by(
        Solicitud.fecha_ingreso.desc()).limit(8).all()

    total_dev = db.query(Desarrollo).count()
    dev_qa_ok = db.query(Desarrollo).filter(
        Desarrollo.resultado_qa == "aprobado").count()
    dev_en_qa = db.query(Desarrollo).filter(
        Desarrollo.estado == EstadoSolicitud.qa).count()

    return templates.TemplateResponse(request, "dashboard/index.html", {
        "user": user, "page": "dashboard",
        "total_solicitudes": total_solicitudes,
        "abiertas": abiertas,
        "implementadas_mes": implementadas_mes,
        "pendientes_aprobacion": pendientes_aprobacion,
        "criticas": criticas,
        "en_riesgo": en_riesgo,
        "total_dev": total_dev,
        "dev_qa_ok": dev_qa_ok,
        "dev_en_qa": dev_en_qa,
        "por_estado": por_estado,
        "por_prioridad": por_prioridad,
        "meses": meses,
        "implementaciones_mes": impl_mes,
        "solicitudes_mes": sol_mes,
        "recientes": recientes,
    })

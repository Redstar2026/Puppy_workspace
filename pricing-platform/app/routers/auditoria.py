"""Router de Auditoría — Módulo 5."""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from app.database import get_db
from app.auth import get_current_user
from app.models import AuditoriaLog, HistorialCambio, Usuario
from app.templates import templates

router = APIRouter(prefix="/auditoria", tags=["auditoria"])
_RL = lambda: RedirectResponse("/login", status_code=302)


@router.get("", response_class=HTMLResponse)
async def lista_auditoria(
    request: Request, db: Session = Depends(get_db),
    usuario_id: str = "", accion: str = "", tabla: str = "",
    buscar: str = "", pagina: int = 1,
):
    user = get_current_user(request, db)
    if not user:
        return _RL()

    q = db.query(AuditoriaLog).options(joinedload(AuditoriaLog.usuario))
    if usuario_id and usuario_id.isdigit():
        q = q.filter(AuditoriaLog.usuario_id == int(usuario_id))
    if accion:
        q = q.filter(AuditoriaLog.accion == accion)
    if tabla:
        q = q.filter(AuditoriaLog.tabla_afectada == tabla)
    if buscar:
        q = q.filter(AuditoriaLog.descripcion.ilike(f"%{buscar}%"))

    total = q.count()
    per_page = 50
    logs = q.order_by(AuditoriaLog.creado_en.desc()).offset(
        (pagina - 1) * per_page).limit(per_page).all()

    usuarios = db.query(Usuario).filter(Usuario.activo == True).all()
    return templates.TemplateResponse(request, "auditoria/lista.html", {
        "user": user, "page": "auditoria",
        "logs": logs, "total": total, "pagina": pagina, "per_page": per_page,
        "usuarios": usuarios,
        "filtros": {"usuario_id": usuario_id, "accion": accion,
                    "tabla": tabla, "buscar": buscar},
        "acciones": ["creacion", "actualizacion", "eliminacion",
                     "aprobacion", "rechazo", "comentario", "estado_cambio", "login"],
        "tablas": ["solicitudes", "desarrollos", "aprobaciones", "usuarios"],
    })


@router.get("/historial", response_class=HTMLResponse)
async def historial_cambios(
    request: Request, db: Session = Depends(get_db),
    buscar: str = "", pagina: int = 1,
):
    user = get_current_user(request, db)
    if not user:
        return _RL()

    q = db.query(HistorialCambio).options(
        joinedload(HistorialCambio.usuario),
        joinedload(HistorialCambio.solicitud),
        joinedload(HistorialCambio.desarrollo),
    )
    if buscar:
        q = q.filter(or_(
            HistorialCambio.accion.ilike(f"%{buscar}%"),
            HistorialCambio.detalle.ilike(f"%{buscar}%"),
        ))

    total = q.count()
    per_page = 50
    cambios = q.order_by(HistorialCambio.creado_en.desc()).offset(
        (pagina - 1) * per_page).limit(per_page).all()

    return templates.TemplateResponse(request, "auditoria/historial.html", {
        "user": user, "page": "auditoria",
        "cambios": cambios, "total": total,
        "pagina": pagina, "per_page": per_page,
        "filtros": {"buscar": buscar},
    })

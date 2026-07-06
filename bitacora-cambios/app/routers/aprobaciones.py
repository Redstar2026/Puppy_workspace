"""Router de aprobaciones: lista, respuesta autenticada y página pública por token."""
import json
from datetime import datetime
from fastapi import APIRouter, Request, Form, Depends, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import Aprobacion, Tarea, Usuario, HistorialCambio, EstadoAprobacion, EstadoTarea
from app.auth import get_current_user
from app.email_service import notify_status_change

router = APIRouter(prefix="/aprobaciones")
templates = Jinja2Templates(directory="templates")


def _ctx(request, db, **extra):
    user = get_current_user(request, db)
    pendientes = db.query(Aprobacion).filter(
        Aprobacion.aprobador_id == user.id,
        Aprobacion.estado == EstadoAprobacion.pendiente,
    ).count() if user else 0
    flash_raw = request.cookies.get("flash")
    flash = json.loads(flash_raw) if flash_raw else None
    return {"request": request, "current_user": user, "pendientes": pendientes, "flash": flash, **extra}


def _log(db, tarea_id, user_id, accion, detalle=""):
    db.add(HistorialCambio(tarea_id=tarea_id, usuario_id=user_id, accion=accion, detalle=detalle))


def _sync_tarea_estado(tarea: Tarea, db: Session):
    """Actualiza estado de tarea según resultado de aprobaciones."""
    todas = tarea.aprobaciones
    if not todas:
        return
    if any(a.estado == EstadoAprobacion.rechazada for a in todas):
        tarea.estado = EstadoTarea.rechazada
    elif all(a.estado == EstadoAprobacion.aprobada for a in todas):
        tarea.estado = EstadoTarea.aprobada


# ── Lista de aprobaciones del usuario actual ──────────────────────────────────

@router.get("", response_class=HTMLResponse)
def lista(request: Request, response: Response, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=302)
    aprobaciones = (
        db.query(Aprobacion)
        .filter(Aprobacion.aprobador_id == user.id)
        .options(joinedload(Aprobacion.tarea))
        .order_by(Aprobacion.solicitada_en.desc())
        .all()
    )
    ctx = _ctx(request, db, aprobaciones=aprobaciones)
    resp = templates.TemplateResponse("aprobaciones/lista.html", ctx)
    resp.delete_cookie("flash")
    return resp


# ── Página pública por token (sin login) ─────────────────────────────────────

@router.get("/publica/{token}", response_class=HTMLResponse)
def publica(token: str, request: Request, db: Session = Depends(get_db)):
    aprobacion = (
        db.query(Aprobacion)
        .filter(Aprobacion.token == token)
        .options(joinedload(Aprobacion.tarea), joinedload(Aprobacion.aprobador))
        .first()
    )
    if not aprobacion:
        return HTMLResponse("<h1>Enlace inválido o expirado.</h1>", status_code=404)
    return templates.TemplateResponse(
        "aprobaciones/publica.html",
        {"request": request, "aprobacion": aprobacion},
    )


# ── Responder via token (link de email) ───────────────────────────────────────

@router.get("/responder/{token}")
def responder_token(
    token: str, accion: str, request: Request, db: Session = Depends(get_db)
):
    aprobacion = (
        db.query(Aprobacion)
        .filter(Aprobacion.token == token)
        .options(joinedload(Aprobacion.tarea))
        .first()
    )
    if not aprobacion or aprobacion.estado != EstadoAprobacion.pendiente:
        return RedirectResponse("/login", status_code=302)
    if accion not in ("aprobada", "rechazada"):
        return RedirectResponse("/login", status_code=302)

    aprobacion.estado = accion
    aprobacion.respondida_en = datetime.utcnow()
    _sync_tarea_estado(aprobacion.tarea, db)
    _log(db, aprobacion.tarea_id, aprobacion.aprobador_id,
         f"Aprobación {accion}", f"Respondida vía email")
    db.commit()
    return RedirectResponse(f"/aprobaciones/publica/{token}", status_code=302)


# ── Responder desde el panel (usuario logueado) ───────────────────────────────

@router.post("/{aprobacion_id}/responder")
def responder_panel(
    aprobacion_id: int, request: Request,
    accion: str = Form(...),
    comentario: str = Form(""),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=302)
    aprobacion = db.query(Aprobacion).options(
        joinedload(Aprobacion.tarea)
    ).filter(Aprobacion.id == aprobacion_id).first()
    if not aprobacion or aprobacion.aprobador_id != user.id:
        return RedirectResponse("/aprobaciones", status_code=302)

    aprobacion.estado = accion
    aprobacion.comentario = comentario
    aprobacion.respondida_en = datetime.utcnow()
    _sync_tarea_estado(aprobacion.tarea, db)
    _log(db, aprobacion.tarea_id, user.id, f"Aprobación {accion}", comentario)
    db.commit()

    resp = RedirectResponse("/aprobaciones", status_code=302)
    resp.set_cookie("flash", json.dumps(
        {"msg": f"✅ Respondiste: {accion}.", "tipo": "ok"}), max_age=10)
    return resp

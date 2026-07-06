"""Router de Aprobaciones — Módulo 3."""
from datetime import datetime
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.auth import get_current_user, log_audit
from app.models import (
    Aprobacion, Solicitud, HistorialCambio,
    TipoAccionAudit, EstadoAprobacion,
)
from app.templates import templates

router = APIRouter(prefix="/aprobaciones", tags=["aprobaciones"])
_RL = lambda: RedirectResponse("/login", status_code=302)


@router.get("", response_class=HTMLResponse)
async def lista_aprobaciones(
    request: Request, db: Session = Depends(get_db),
    estado: str = "", filtro: str = "todas",
):
    user = get_current_user(request, db)
    if not user:
        return _RL()

    q = db.query(Aprobacion).options(
        joinedload(Aprobacion.aprobador),
        joinedload(Aprobacion.solicitud),
        joinedload(Aprobacion.desarrollo),
    )
    if filtro == "mias":
        q = q.filter(Aprobacion.aprobador_id == user.id)
    if estado:
        q = q.filter(Aprobacion.estado == estado)

    aprobaciones = q.order_by(Aprobacion.solicitada_en.desc()).all()
    pendientes_mias = db.query(Aprobacion).filter(
        Aprobacion.aprobador_id == user.id,
        Aprobacion.estado == EstadoAprobacion.pendiente,
    ).count()

    return templates.TemplateResponse(request, "aprobaciones/lista.html", {
        "user": user, "page": "aprobaciones",
        "aprobaciones": aprobaciones, "pendientes_mias": pendientes_mias,
        "filtros": {"estado": estado, "filtro": filtro},
    })


@router.post("/{ap_id}/aprobar", response_class=HTMLResponse)
async def aprobar(
    ap_id: int, request: Request, db: Session = Depends(get_db),
    comentario: str = Form(""),
):
    user = get_current_user(request, db)
    if not user:
        return _RL()
    ap = db.query(Aprobacion).filter(Aprobacion.id == ap_id).first()
    if not ap or ap.aprobador_id != user.id:
        return RedirectResponse("/aprobaciones", status_code=302)

    ap.estado = EstadoAprobacion.aprobado
    ap.comentario = comentario
    ap.respondida_en = datetime.utcnow()

    if ap.solicitud_id:
        db.add(HistorialCambio(
            solicitud_id=ap.solicitud_id, usuario_id=user.id,
            accion="Aprobado", detalle=f"Por {user.nombre}. {comentario}",
        ))
        sol = db.query(Solicitud).filter(Solicitud.id == ap.solicitud_id).first()
        if sol:
            todas = all(
                a.estado == EstadoAprobacion.aprobado
                for a in sol.aprobaciones if a.id != ap.id
            )
            if todas and sol.estado.value == "aprobacion":
                sol.estado = "implementado"

    db.commit()
    log_audit(db, TipoAccionAudit.aprobacion, user.id, "aprobaciones", ap_id,
              f"Aprobado por {user.nombre}", request)
    return RedirectResponse("/aprobaciones", status_code=302)


@router.post("/{ap_id}/rechazar", response_class=HTMLResponse)
async def rechazar(
    ap_id: int, request: Request, db: Session = Depends(get_db),
    comentario: str = Form(...),
):
    user = get_current_user(request, db)
    if not user:
        return _RL()
    ap = db.query(Aprobacion).filter(Aprobacion.id == ap_id).first()
    if not ap or ap.aprobador_id != user.id:
        return RedirectResponse("/aprobaciones", status_code=302)

    ap.estado = EstadoAprobacion.rechazado
    ap.comentario = comentario
    ap.respondida_en = datetime.utcnow()

    if ap.solicitud_id:
        sol = db.query(Solicitud).filter(Solicitud.id == ap.solicitud_id).first()
        if sol:
            sol.estado = "rechazado"
        db.add(HistorialCambio(
            solicitud_id=ap.solicitud_id, usuario_id=user.id,
            accion="Rechazado", detalle=f"Por {user.nombre}: {comentario}",
        ))
    db.commit()
    log_audit(db, TipoAccionAudit.rechazo, user.id, "aprobaciones", ap_id,
              f"Rechazado: {comentario[:80]}", request)
    return RedirectResponse("/aprobaciones", status_code=302)


@router.get("/publica/{token}", response_class=HTMLResponse)
async def aprobacion_publica(token: str, request: Request, db: Session = Depends(get_db)):
    ap = db.query(Aprobacion).options(
        joinedload(Aprobacion.aprobador),
        joinedload(Aprobacion.solicitud),
        joinedload(Aprobacion.desarrollo),
    ).filter(Aprobacion.token == token).first()
    if not ap:
        return HTMLResponse("<h2>Token invalido o expirado.</h2>", status_code=404)
    return templates.TemplateResponse(request, "aprobaciones/publica.html",
                                      {"ap": ap, "user": None})


@router.post("/publica/{token}/responder", response_class=HTMLResponse)
async def aprobacion_publica_responder(
    token: str, request: Request, db: Session = Depends(get_db),
    decision: str = Form(...), comentario: str = Form(""),
):
    ap = db.query(Aprobacion).filter(Aprobacion.token == token).first()
    if not ap or ap.estado != EstadoAprobacion.pendiente:
        return HTMLResponse("<h2>Esta aprobacion ya fue procesada.</h2>", status_code=400)
    ap.estado = EstadoAprobacion.aprobado if decision == "aprobar" else EstadoAprobacion.rechazado
    ap.comentario = comentario
    ap.respondida_en = datetime.utcnow()
    db.commit()
    accion = "Aprobado" if decision == "aprobar" else "Rechazado"
    return HTMLResponse(f"""<html><body style="font-family:sans-serif;text-align:center;padding:3rem">
    <h2>{accion} exitosamente</h2>
    <p>Gracias por su respuesta. Puede cerrar esta ventana.</p>
    </body></html>""")

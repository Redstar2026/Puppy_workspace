"""Router de Solicitudes — Módulo 1 (Bitácora Central)."""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from app.database import get_db
from app.auth import get_current_user, log_audit
from app.models import (
    Solicitud, Usuario, Aprobacion, Comentario, HistorialCambio,
    Adjunto, Etiqueta, TipoAccionAudit, EstadoSolicitud,
    TipoSolicitud, Prioridad, NivelRiesgo, EstadoAprobacion,
)
from app.utils import generar_folio_solicitud, label_estado, label_prioridad, ESTADOS_KANBAN
from app.templates import templates

router = APIRouter(prefix="/solicitudes", tags=["solicitudes"])
_RL = lambda: RedirectResponse("/login", status_code=302)


def _historial(db, sol_id, uid, accion, campo="", ant="", nuevo="", detalle=""):
    db.add(HistorialCambio(
        solicitud_id=sol_id, usuario_id=uid, accion=accion,
        campo_modificado=campo, valor_anterior=str(ant),
        valor_nuevo=str(nuevo), detalle=detalle,
    ))


def _ctx_form(db):
    return {
        "usuarios": db.query(Usuario).filter(Usuario.activo == True).all(),
        "aprobadores": db.query(Usuario).filter(Usuario.es_aprobador == True, Usuario.activo == True).all(),
        "etiquetas": db.query(Etiqueta).all(),
        "tipos": [e.value for e in TipoSolicitud],
        "prioridades": [e.value for e in Prioridad],
        "estados": [e.value for e in EstadoSolicitud],
        "riesgos": [e.value for e in NivelRiesgo],
    }


@router.get("", response_class=HTMLResponse)
async def lista_solicitudes(
    request: Request, db: Session = Depends(get_db),
    vista: str = "tabla", estado: str = "", prioridad: str = "",
    tipo: str = "", buscar: str = "", responsable: str = "",
    riesgo: str = "", pagina: int = 1,
):
    user = get_current_user(request, db)
    if not user:
        return _RL()

    q = db.query(Solicitud).options(
        joinedload(Solicitud.encargado),
        joinedload(Solicitud.creado_por),
    )
    if estado:
        q = q.filter(Solicitud.estado == estado)
    if prioridad:
        q = q.filter(Solicitud.prioridad == prioridad)
    if tipo:
        q = q.filter(Solicitud.tipo == tipo)
    if riesgo:
        q = q.filter(Solicitud.riesgo_operativo == riesgo)
    if responsable:
        q = q.filter(Solicitud.encargado_id == int(responsable))
    if buscar:
        q = q.filter(or_(
            Solicitud.titulo.ilike(f"%{buscar}%"),
            Solicitud.folio.ilike(f"%{buscar}%"),
            Solicitud.descripcion.ilike(f"%{buscar}%"),
        ))

    total = q.count()
    per_page = 20
    solicitudes = q.order_by(Solicitud.fecha_ingreso.desc()).offset(
        (pagina - 1) * per_page).limit(per_page).all()

    kanban_data = {}
    if vista == "kanban":
        all_sols = q.order_by(Solicitud.prioridad.desc()).all()
        for est in ESTADOS_KANBAN:
            kanban_data[est] = [s for s in all_sols if s.estado.value == est]

    usuarios = db.query(Usuario).filter(Usuario.activo == True).all()
    return templates.TemplateResponse(request, "solicitudes/lista.html", {
        "user": user, "page": "solicitudes",
        "solicitudes": solicitudes, "kanban_data": kanban_data,
        "estados_kanban": ESTADOS_KANBAN, "total": total,
        "pagina": pagina, "per_page": per_page, "vista": vista,
        "filtros": {"estado": estado, "prioridad": prioridad, "tipo": tipo,
                    "buscar": buscar, "responsable": responsable, "riesgo": riesgo},
        "usuarios": usuarios,
    })


@router.get("/nueva", response_class=HTMLResponse)
async def nueva_form(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return _RL()
    return templates.TemplateResponse(request, "solicitudes/form.html",
                                      {"user": user, "page": "solicitudes",
                                       "solicitud": None, **_ctx_form(db)})


@router.post("/nueva", response_class=HTMLResponse)
async def crear_solicitud(
    request: Request, db: Session = Depends(get_db),
    titulo: str = Form(...), tipo: str = Form(...),
    descripcion: str = Form(""), area_impactada: str = Form(""),
    prioridad: str = Form("media"), estado: str = Form("pendiente"),
    area_solicitante: str = Form(""), encargado_id: Optional[str] = Form(None),
    equipo_responsable: str = Form(""), dependencias: str = Form(""),
    requiere_aprobacion: str = Form("no"), riesgo_operativo: str = Form("bajo"),
    impacto_esperado: str = Form(""), beneficios_esperados: str = Form(""),
    kpi_asociado: str = Form(""), comentarios_internos: str = Form(""),
    fecha_estimada_fin: Optional[str] = Form(None),
    aprobadores_ids: list[str] = Form(default=[]),
    etiquetas_ids: list[str] = Form(default=[]),
):
    user = get_current_user(request, db)
    if not user:
        return _RL()

    folio = generar_folio_solicitud(db)
    enc_id = int(encargado_id) if encargado_id and encargado_id.isdigit() else None
    fecha_est = datetime.strptime(fecha_estimada_fin, "%Y-%m-%d") if fecha_estimada_fin else None

    sol = Solicitud(
        folio=folio, titulo=titulo, tipo=tipo, descripcion=descripcion,
        area_impactada=area_impactada, prioridad=prioridad, estado=estado,
        area_solicitante=area_solicitante, encargado_id=enc_id,
        equipo_responsable=equipo_responsable, dependencias=dependencias,
        requiere_aprobacion=(requiere_aprobacion == "si"),
        riesgo_operativo=riesgo_operativo, impacto_esperado=impacto_esperado,
        beneficios_esperados=beneficios_esperados, kpi_asociado=kpi_asociado,
        comentarios_internos=comentarios_internos, fecha_estimada_fin=fecha_est,
        creado_por_id=user.id,
    )
    db.add(sol)
    db.flush()

    for eid in etiquetas_ids:
        etq = db.query(Etiqueta).filter(Etiqueta.id == int(eid)).first()
        if etq:
            sol.etiquetas.append(etq)

    for orden, apid in enumerate(aprobadores_ids, start=1):
        if apid.isdigit():
            db.add(Aprobacion(solicitud_id=sol.id, aprobador_id=int(apid), orden=orden))

    _historial(db, sol.id, user.id, "Solicitud creada",
               detalle=f"{folio} creada por {user.nombre}")
    db.commit()
    log_audit(db, TipoAccionAudit.creacion, user.id, "solicitudes", sol.id,
              f"Solicitud {folio} creada", request)
    return RedirectResponse(f"/solicitudes/{sol.id}", status_code=302)


@router.get("/{sol_id}", response_class=HTMLResponse)
async def detalle_solicitud(sol_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return _RL()
    sol = db.query(Solicitud).options(
        joinedload(Solicitud.creado_por),
        joinedload(Solicitud.encargado),
        joinedload(Solicitud.aprobaciones).joinedload(Aprobacion.aprobador),
        joinedload(Solicitud.comentarios).joinedload(Comentario.autor),
        joinedload(Solicitud.historial).joinedload(HistorialCambio.usuario),
        joinedload(Solicitud.adjuntos),
        joinedload(Solicitud.etiquetas),
    ).filter(Solicitud.id == sol_id).first()
    if not sol:
        return RedirectResponse("/solicitudes", status_code=302)

    return templates.TemplateResponse(request, "solicitudes/detalle.html", {
        "user": user, "page": "solicitudes", "sol": sol,
        "estados": [e.value for e in EstadoSolicitud],
        **_ctx_form(db),
    })


@router.post("/{sol_id}/estado", response_class=HTMLResponse)
async def cambiar_estado(
    sol_id: int, request: Request, db: Session = Depends(get_db),
    estado: str = Form(...), porcentaje_avance: float = Form(0.0),
):
    user = get_current_user(request, db)
    if not user:
        return _RL()
    sol = db.query(Solicitud).filter(Solicitud.id == sol_id).first()
    if sol:
        anterior = sol.estado.value if sol.estado else ""
        sol.estado = estado
        sol.porcentaje_avance = porcentaje_avance
        if estado == "implementado" and not sol.fecha_implementacion:
            sol.fecha_implementacion = datetime.utcnow()
        _historial(db, sol_id, user.id, "Cambio de estado", "estado", anterior, estado)
        db.commit()
        log_audit(db, TipoAccionAudit.estado_cambio, user.id, "solicitudes", sol_id,
                  f"Estado: {anterior} → {estado}", request)
    return RedirectResponse(f"/solicitudes/{sol_id}", status_code=302)


@router.post("/{sol_id}/comentario", response_class=HTMLResponse)
async def agregar_comentario(
    sol_id: int, request: Request, db: Session = Depends(get_db),
    contenido: str = Form(...), tipo: str = Form("interno"),
):
    user = get_current_user(request, db)
    if not user:
        return _RL()
    db.add(Comentario(solicitud_id=sol_id, autor_id=user.id,
                      contenido=contenido, tipo=tipo))
    _historial(db, sol_id, user.id, "Comentario agregado", detalle=contenido[:100])
    db.commit()
    log_audit(db, TipoAccionAudit.comentario, user.id, "solicitudes", sol_id,
              "Comentario agregado", request)
    return RedirectResponse(f"/solicitudes/{sol_id}#comentarios", status_code=302)


@router.get("/{sol_id}/editar", response_class=HTMLResponse)
async def editar_form(sol_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return _RL()
    sol = db.query(Solicitud).filter(Solicitud.id == sol_id).first()
    if not sol:
        return RedirectResponse("/solicitudes", status_code=302)
    return templates.TemplateResponse(request, "solicitudes/form.html",
                                      {"user": user, "page": "solicitudes",
                                       "solicitud": sol, **_ctx_form(db)})


@router.post("/{sol_id}/editar", response_class=HTMLResponse)
async def actualizar_solicitud(
    sol_id: int, request: Request, db: Session = Depends(get_db),
    titulo: str = Form(...), tipo: str = Form(...),
    descripcion: str = Form(""), area_impactada: str = Form(""),
    prioridad: str = Form("media"), estado: str = Form("pendiente"),
    area_solicitante: str = Form(""), encargado_id: Optional[str] = Form(None),
    equipo_responsable: str = Form(""), dependencias: str = Form(""),
    requiere_aprobacion: str = Form("no"), riesgo_operativo: str = Form("bajo"),
    impacto_esperado: str = Form(""), beneficios_esperados: str = Form(""),
    kpi_asociado: str = Form(""), comentarios_internos: str = Form(""),
    fecha_estimada_fin: Optional[str] = Form(None),
    porcentaje_avance: float = Form(0.0),
):
    user = get_current_user(request, db)
    if not user:
        return _RL()
    sol = db.query(Solicitud).filter(Solicitud.id == sol_id).first()
    if not sol:
        return RedirectResponse("/solicitudes", status_code=302)

    campos = {
        "titulo": titulo, "tipo": tipo, "descripcion": descripcion,
        "area_impactada": area_impactada, "prioridad": prioridad,
        "estado": estado, "area_solicitante": area_solicitante,
        "equipo_responsable": equipo_responsable, "dependencias": dependencias,
        "riesgo_operativo": riesgo_operativo, "impacto_esperado": impacto_esperado,
        "beneficios_esperados": beneficios_esperados, "kpi_asociado": kpi_asociado,
        "comentarios_internos": comentarios_internos,
        "porcentaje_avance": porcentaje_avance,
    }
    for campo, nuevo_val in campos.items():
        if str(getattr(sol, campo)) != str(nuevo_val):
            _historial(db, sol_id, user.id, "Actualización",
                       campo, getattr(sol, campo), nuevo_val)
            setattr(sol, campo, nuevo_val)

    sol.encargado_id = int(encargado_id) if encargado_id and encargado_id.isdigit() else None
    sol.requiere_aprobacion = (requiere_aprobacion == "si")
    if fecha_estimada_fin:
        sol.fecha_estimada_fin = datetime.strptime(fecha_estimada_fin, "%Y-%m-%d")
    if estado == "implementado" and not sol.fecha_implementacion:
        sol.fecha_implementacion = datetime.utcnow()
    sol.actualizado_en = datetime.utcnow()
    db.commit()
    log_audit(db, TipoAccionAudit.actualizacion, user.id, "solicitudes", sol_id,
              f"Solicitud {sol.folio} actualizada", request)
    return RedirectResponse(f"/solicitudes/{sol_id}", status_code=302)

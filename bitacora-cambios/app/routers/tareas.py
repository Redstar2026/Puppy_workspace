"""Router de tareas: CRUD completo + historial de auditoría."""
import json
from datetime import datetime
from fastapi import APIRouter, Request, Form, Depends, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import (
    Tarea, Usuario, AsignacionRol, Aprobacion, HistorialCambio,
    Comentario, TipoTarea, Prioridad, EstadoTarea, RolAsignacion, EstadoAprobacion
)
from app.auth import get_current_user, SESSION_COOKIE
from app.email_service import notify_approval_request, notify_status_change

router = APIRouter(prefix="/tareas")
templates = Jinja2Templates(directory="templates")

ROLES_ORDEN = [
    RolAsignacion.desarrollo,
    RolAsignacion.validacion,
    RolAsignacion.implementacion,
    RolAsignacion.verificacion_vivo,
    RolAsignacion.presentacion,
]


def _ctx(request: Request, db: Session, **extra):
    user = get_current_user(request, db)
    pendientes = db.query(Aprobacion).filter(
        Aprobacion.aprobador_id == user.id,
        Aprobacion.estado == EstadoAprobacion.pendiente,
    ).count() if user else 0
    flash_raw = request.cookies.get("flash")
    flash = json.loads(flash_raw) if flash_raw else None
    return {"request": request, "current_user": user, "pendientes": pendientes, "flash": flash, **extra}


def _render(name: str, request: Request, db: Session, response: Response, **kw):
    ctx = _ctx(request, db, **kw)
    resp = templates.TemplateResponse(name, ctx)
    resp.delete_cookie("flash")
    return resp


def _set_flash(msg: str, tipo: str = "ok") -> Response:
    resp = RedirectResponse("/tareas", status_code=302)
    resp.set_cookie("flash", json.dumps({"msg": msg, "tipo": tipo}), max_age=10)
    return resp


def _log(db: Session, tarea_id: int, user_id: int | None, accion: str, detalle: str = "",
         campo: str = "", anterior: str = "", nuevo: str = ""):
    db.add(HistorialCambio(
        tarea_id=tarea_id, usuario_id=user_id, accion=accion,
        detalle=detalle, campo_modificado=campo,
        valor_anterior=anterior, valor_nuevo=nuevo,
    ))


# ── Lista ────────────────────────────────────────────────────────────────────

@router.get("", response_class=HTMLResponse)
def lista(
    request: Request, response: Response,
    estado: str = "", tipo: str = "", prioridad: str = "", q: str = "",
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=302)

    query = db.query(Tarea).options(joinedload(Tarea.encargado))
    if estado:
        query = query.filter(Tarea.estado == estado)
    if tipo:
        query = query.filter(Tarea.tipo == tipo)
    if prioridad:
        query = query.filter(Tarea.prioridad == prioridad)
    if q:
        query = query.filter(Tarea.titulo.ilike(f"%{q}%"))
    tareas = query.order_by(Tarea.creado_en.desc()).all()
    usuarios = db.query(Usuario).filter(Usuario.activo == True).all()

    return _render("tareas/lista.html", request, db, response,
                   tareas=tareas, usuarios=usuarios,
                   filtro_estado=estado, filtro_tipo=tipo,
                   filtro_prioridad=prioridad, filtro_q=q)


# ── Nueva ────────────────────────────────────────────────────────────────────

@router.get("/nueva", response_class=HTMLResponse)
def nueva_form(request: Request, response: Response, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=302)
    usuarios = db.query(Usuario).filter(Usuario.activo == True).all()
    return _render("tareas/form.html", request, db, response,
                   tarea=None, usuarios=usuarios, accion="Crear")


@router.post("/nueva")
def nueva_submit(
    request: Request,
    titulo: str = Form(...),
    tipo: str = Form(...),
    descripcion: str = Form(""),
    prioridad: str = Form("media"),
    encargado_id: str = Form(""),
    fecha_inicio: str = Form(""),
    fecha_fin: str = Form(""),
    fecha_implementacion: str = Form(""),
    requiere_autorizacion: str = Form("off"),
    dependencias: str = Form(""),
    beneficio_afectacion: str = Form(""),
    ambiente: str = Form("produccion"),
    categoria: str = Form(""),
    riesgo: str = Form("bajo"),
    plan_rollback: str = Form(""),
    rol_desarrollo: str = Form(""),
    rol_validacion: str = Form(""),
    rol_implementacion: str = Form(""),
    rol_verificacion_vivo: str = Form(""),
    rol_presentacion: str = Form(""),
    aprobadores: list[str] = Form(default=[]),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=302)

    def parse_dt(s: str):
        return datetime.fromisoformat(s) if s else None

    tarea = Tarea(
        titulo=titulo, tipo=tipo, descripcion=descripcion,
        prioridad=prioridad, estado=EstadoTarea.borrador,
        encargado_id=int(encargado_id) if encargado_id else None,
        fecha_inicio=parse_dt(fecha_inicio), fecha_fin=parse_dt(fecha_fin),
        fecha_implementacion=parse_dt(fecha_implementacion),
        requiere_autorizacion=(requiere_autorizacion == "on"),
        dependencias=dependencias, beneficio_afectacion=beneficio_afectacion,
        ambiente=ambiente, categoria=categoria, riesgo=riesgo,
        plan_rollback=plan_rollback, creado_por_id=user.id,
    )
    db.add(tarea)
    db.flush()

    # Asignaciones de rol
    roles_map = {
        RolAsignacion.desarrollo: rol_desarrollo,
        RolAsignacion.validacion: rol_validacion,
        RolAsignacion.implementacion: rol_implementacion,
        RolAsignacion.verificacion_vivo: rol_verificacion_vivo,
        RolAsignacion.presentacion: rol_presentacion,
    }
    for rol, uid_str in roles_map.items():
        db.add(AsignacionRol(tarea_id=tarea.id, rol=rol,
                             usuario_id=int(uid_str) if uid_str else None))

    # Aprobaciones
    if tarea.requiere_autorizacion and aprobadores:
        tarea.estado = EstadoTarea.pendiente_aprobacion
        for uid_str in aprobadores:
            if not uid_str:
                continue
            aprobacion = Aprobacion(tarea_id=tarea.id, aprobador_id=int(uid_str))
            db.add(aprobacion)
            db.flush()
            aprobador = db.query(Usuario).get(int(uid_str))
            if aprobador:
                notify_approval_request(aprobador.email, tarea.titulo, aprobacion.token, user.nombre)

    _log(db, tarea.id, user.id, "Tarea creada", f"Creada por {user.nombre}")
    db.commit()

    resp = RedirectResponse(f"/tareas/{tarea.id}", status_code=302)
    resp.set_cookie("flash", json.dumps({"msg": "✅ Tarea creada exitosamente.", "tipo": "ok"}), max_age=10)
    return resp


# ── Detalle ──────────────────────────────────────────────────────────────────

@router.get("/{tarea_id}", response_class=HTMLResponse)
def detalle(tarea_id: int, request: Request, response: Response, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=302)
    tarea = db.query(Tarea).options(
        joinedload(Tarea.encargado),
        joinedload(Tarea.asignaciones).joinedload(AsignacionRol.usuario),
        joinedload(Tarea.aprobaciones).joinedload(Aprobacion.aprobador),
        joinedload(Tarea.historial).joinedload(HistorialCambio.usuario),
        joinedload(Tarea.comentarios).joinedload(Comentario.autor),
    ).filter(Tarea.id == tarea_id).first()
    if not tarea:
        return RedirectResponse("/tareas", status_code=302)
    roles_dict = {a.rol: a for a in tarea.asignaciones}
    usuarios = db.query(Usuario).filter(Usuario.activo == True).all()
    return _render("tareas/detalle.html", request, db, response,
                   tarea=tarea, roles_dict=roles_dict,
                   roles_orden=ROLES_ORDEN, usuarios=usuarios)


# ── Editar ───────────────────────────────────────────────────────────────────

@router.get("/{tarea_id}/editar", response_class=HTMLResponse)
def editar_form(tarea_id: int, request: Request, response: Response, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=302)
    tarea = db.query(Tarea).options(
        joinedload(Tarea.asignaciones),
        joinedload(Tarea.aprobaciones),
    ).filter(Tarea.id == tarea_id).first()
    if not tarea:
        return RedirectResponse("/tareas", status_code=302)
    usuarios = db.query(Usuario).filter(Usuario.activo == True).all()
    roles_dict = {a.rol: a for a in tarea.asignaciones}
    return _render("tareas/form.html", request, db, response,
                   tarea=tarea, usuarios=usuarios,
                   roles_dict=roles_dict, accion="Editar")


@router.post("/{tarea_id}/editar")
def editar_submit(
    tarea_id: int, request: Request,
    titulo: str = Form(...),
    tipo: str = Form(...),
    descripcion: str = Form(""),
    prioridad: str = Form("media"),
    estado: str = Form("borrador"),
    encargado_id: str = Form(""),
    fecha_inicio: str = Form(""),
    fecha_fin: str = Form(""),
    fecha_implementacion: str = Form(""),
    requiere_autorizacion: str = Form("off"),
    dependencias: str = Form(""),
    beneficio_afectacion: str = Form(""),
    ambiente: str = Form("produccion"),
    categoria: str = Form(""),
    riesgo: str = Form("bajo"),
    plan_rollback: str = Form(""),
    rol_desarrollo: str = Form(""),
    rol_validacion: str = Form(""),
    rol_implementacion: str = Form(""),
    rol_verificacion_vivo: str = Form(""),
    rol_presentacion: str = Form(""),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=302)
    tarea = db.query(Tarea).filter(Tarea.id == tarea_id).first()
    if not tarea:
        return RedirectResponse("/tareas", status_code=302)

    def parse_dt(s: str):
        return datetime.fromisoformat(s) if s else None

    cambios = []
    for campo, nuevo in [("titulo", titulo), ("descripcion", descripcion),
                          ("tipo", tipo), ("prioridad", prioridad), ("estado", estado)]:
        viejo = str(getattr(tarea, campo) or "")
        if viejo != nuevo:
            cambios.append((campo, viejo, nuevo))

    tarea.titulo = titulo
    tarea.tipo = tipo
    tarea.descripcion = descripcion
    tarea.prioridad = prioridad
    tarea.estado = estado
    tarea.encargado_id = int(encargado_id) if encargado_id else None
    tarea.fecha_inicio = parse_dt(fecha_inicio)
    tarea.fecha_fin = parse_dt(fecha_fin)
    tarea.fecha_implementacion = parse_dt(fecha_implementacion)
    tarea.requiere_autorizacion = (requiere_autorizacion == "on")
    tarea.dependencias = dependencias
    tarea.beneficio_afectacion = beneficio_afectacion
    tarea.ambiente = ambiente
    tarea.categoria = categoria
    tarea.riesgo = riesgo
    tarea.plan_rollback = plan_rollback
    tarea.actualizado_en = datetime.utcnow()

    # Actualizar roles
    roles_map = {
        RolAsignacion.desarrollo: rol_desarrollo,
        RolAsignacion.validacion: rol_validacion,
        RolAsignacion.implementacion: rol_implementacion,
        RolAsignacion.verificacion_vivo: rol_verificacion_vivo,
        RolAsignacion.presentacion: rol_presentacion,
    }
    for asig in tarea.asignaciones:
        uid_str = roles_map.get(asig.rol, "")
        asig.usuario_id = int(uid_str) if uid_str else None

    for campo, ant, nvo in cambios:
        _log(db, tarea.id, user.id, "Campo modificado", campo=campo, anterior=ant, nuevo=nvo)
    if not cambios:
        _log(db, tarea.id, user.id, "Tarea actualizada")

    db.commit()
    resp = RedirectResponse(f"/tareas/{tarea_id}", status_code=302)
    resp.set_cookie("flash", json.dumps({"msg": "✏️ Tarea actualizada.", "tipo": "ok"}), max_age=10)
    return resp


# ── Comentarios ───────────────────────────────────────────────────────────────

@router.post("/{tarea_id}/comentar")
def comentar(
    tarea_id: int, request: Request,
    contenido: str = Form(...),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=302)
    db.add(Comentario(tarea_id=tarea_id, autor_id=user.id, contenido=contenido))
    _log(db, tarea_id, user.id, "Comentario añadido")
    db.commit()
    return RedirectResponse(f"/tareas/{tarea_id}#comentarios", status_code=302)


# ── Eliminar ──────────────────────────────────────────────────────────────────

@router.post("/{tarea_id}/eliminar")
def eliminar(tarea_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=302)
    tarea = db.query(Tarea).filter(Tarea.id == tarea_id).first()
    if tarea:
        db.delete(tarea)
        db.commit()
    resp = RedirectResponse("/tareas", status_code=302)
    resp.set_cookie("flash", json.dumps({"msg": "🗑️ Tarea eliminada.", "tipo": "warn"}), max_age=10)
    return resp

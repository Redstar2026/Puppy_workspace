"""Router de usuarios + dashboard raíz + historial global + kanban."""
import json
from fastapi import APIRouter, Request, Form, Depends, Response
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func
from app.database import get_db
from app.models import (
    Usuario, Tarea, HistorialCambio, Aprobacion,
    EstadoAprobacion, EstadoTarea, TipoTarea, Prioridad
)
from app.auth import get_current_user, hash_password

router = APIRouter()
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


# ── Dashboard ─────────────────────────────────────────────────────────────────

@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, response: Response, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=302)

    total = db.query(Tarea).count()
    en_progreso = db.query(Tarea).filter(Tarea.estado == EstadoTarea.en_progreso).count()
    completadas = db.query(Tarea).filter(Tarea.estado == EstadoTarea.completada).count()
    pendientes_apr = db.query(Aprobacion).filter(
        Aprobacion.estado == EstadoAprobacion.pendiente).count()
    recientes = db.query(Tarea).options(joinedload(Tarea.encargado)).order_by(
        desc(Tarea.creado_en)).limit(8).all()
    mis_pendientes = db.query(Aprobacion).filter(
        Aprobacion.aprobador_id == user.id,
        Aprobacion.estado == EstadoAprobacion.pendiente,
    ).options(joinedload(Aprobacion.tarea)).all()
    actividad = db.query(HistorialCambio).options(
        joinedload(HistorialCambio.usuario)
    ).order_by(desc(HistorialCambio.creado_en)).limit(10).all()

    # Datos para graficas Chart.js
    estados_raw = db.query(Tarea.estado, func.count(Tarea.id)).group_by(Tarea.estado).all()
    tipos_raw = db.query(Tarea.tipo, func.count(Tarea.id)).group_by(Tarea.tipo).all()
    prio_raw = db.query(Tarea.prioridad, func.count(Tarea.id)).group_by(Tarea.prioridad).all()

    estados_chart = json.dumps({r[0].value: r[1] for r in estados_raw})
    tipos_chart = json.dumps({r[0].value: r[1] for r in tipos_raw})
    prio_chart = json.dumps({r[0].value: r[1] for r in prio_raw})

    ctx = _ctx(request, db,
               total=total, en_progreso=en_progreso, completadas=completadas,
               pendientes_apr=pendientes_apr, recientes=recientes,
               mis_pendientes=mis_pendientes, actividad=actividad,
               estados_chart=estados_chart, tipos_chart=tipos_chart,
               prio_chart=prio_chart)
    resp = templates.TemplateResponse("dashboard.html", ctx)
    resp.delete_cookie("flash")
    return resp


# ── Kanban ────────────────────────────────────────────────────────────────────

@router.get("/kanban", response_class=HTMLResponse)
def kanban(request: Request, response: Response, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=302)
    tareas = db.query(Tarea).options(
        joinedload(Tarea.encargado)
    ).order_by(desc(Tarea.creado_en)).all()
    columnas = [
        ("borrador",             "Borrador",          "draft",        "gray"),
        ("pendiente_aprobacion", "Pend. Aprobacion",  "pending",      "yellow"),
        ("aprobada",             "Aprobada",          "check_circle", "green"),
        ("en_progreso",          "En Progreso",       "sync",         "blue"),
        ("en_revision",          "En Revision",       "rate_review",  "purple"),
        ("completada",           "Completada",        "task_alt",     "emerald"),
    ]
    kanban_data = {
        col[0]: [t for t in tareas if t.estado.value == col[0]]
        for col in columnas
    }
    ctx = _ctx(request, db, columnas=columnas, kanban_data=kanban_data)
    resp = templates.TemplateResponse("kanban.html", ctx)
    resp.delete_cookie("flash")
    return resp


# ── Historial global ──────────────────────────────────────────────────────────

@router.get("/historial", response_class=HTMLResponse)
def historial(request: Request, response: Response, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=302)
    registros = db.query(HistorialCambio).order_by(
        desc(HistorialCambio.creado_en)).limit(200).all()
    ctx = _ctx(request, db, registros=registros)
    resp = templates.TemplateResponse("historial/lista.html", ctx)
    resp.delete_cookie("flash")
    return resp


# ── Usuarios ──────────────────────────────────────────────────────────────────

@router.get("/usuarios", response_class=HTMLResponse)
def usuarios_lista(request: Request, response: Response, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=302)
    usuarios = db.query(Usuario).order_by(Usuario.nombre).all()
    ctx = _ctx(request, db, usuarios=usuarios)
    resp = templates.TemplateResponse("usuarios/lista.html", ctx)
    resp.delete_cookie("flash")
    return resp


@router.post("/usuarios/nuevo")
def usuario_nuevo(
    request: Request,
    nombre: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    departamento: str = Form(""),
    cargo: str = Form(""),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=302)
    existe = db.query(Usuario).filter(Usuario.email == email).first()
    if existe:
        resp = RedirectResponse("/usuarios", status_code=302)
        resp.set_cookie("flash", json.dumps(
            {"msg": "⚠️ El email ya está registrado.", "tipo": "warn"}), max_age=10)
        return resp
    db.add(Usuario(nombre=nombre, email=email, password_hash=hash_password(password),
                   departamento=departamento, cargo=cargo))
    db.commit()
    resp = RedirectResponse("/usuarios", status_code=302)
    resp.set_cookie("flash", json.dumps(
        {"msg": f"✅ Usuario {nombre} creado.", "tipo": "ok"}), max_age=10)
    return resp


@router.get("/usuarios/api", response_class=JSONResponse)
def usuarios_api(db: Session = Depends(get_db)):
    """Endpoint JSON para dropdowns dinámicos."""
    usuarios = db.query(Usuario).filter(Usuario.activo == True).order_by(Usuario.nombre).all()
    return [{"id": u.id, "nombre": u.nombre, "email": u.email} for u in usuarios]

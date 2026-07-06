"""Router de Usuarios."""
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user, hash_password, log_audit
from app.models import Usuario, RolUsuario, TipoAccionAudit
from app.templates import templates

router = APIRouter(prefix="/usuarios", tags=["usuarios"])
_RL = lambda: RedirectResponse("/login", status_code=302)


@router.get("", response_class=HTMLResponse)
async def lista_usuarios(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return _RL()
    if user.rol.value != "admin":
        return RedirectResponse("/", status_code=302)
    usuarios = db.query(Usuario).order_by(Usuario.nombre).all()
    return templates.TemplateResponse(request, "usuarios/lista.html", {
        "user": user, "page": "usuarios",
        "usuarios": usuarios,
        "roles": [e.value for e in RolUsuario],
    })


@router.post("/nuevo", response_class=HTMLResponse)
async def crear_usuario(
    request: Request, db: Session = Depends(get_db),
    nombre: str = Form(...), email: str = Form(...),
    password: str = Form(...), rol: str = Form("analista"),
    departamento: str = Form("Pricing"), cargo: str = Form(""),
    es_aprobador: str = Form("no"),
):
    user = get_current_user(request, db)
    if not user or user.rol.value != "admin":
        return _RL()
    nuevo = Usuario(
        nombre=nombre, email=email.lower().strip(),
        password_hash=hash_password(password),
        rol=rol, departamento=departamento, cargo=cargo,
        es_aprobador=(es_aprobador == "si"),
    )
    db.add(nuevo)
    db.commit()
    log_audit(db, TipoAccionAudit.creacion, user.id, "usuarios", nuevo.id,
              f"Usuario {email} creado", request)
    return RedirectResponse("/usuarios", status_code=302)


@router.post("/{uid}/toggle", response_class=HTMLResponse)
async def toggle_usuario(uid: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user or user.rol.value != "admin":
        return _RL()
    target = db.query(Usuario).filter(Usuario.id == uid).first()
    if target and target.id != user.id:
        target.activo = not target.activo
        db.commit()
    return RedirectResponse("/usuarios", status_code=302)

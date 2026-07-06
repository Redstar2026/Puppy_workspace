"""Router de autenticación."""
from datetime import datetime
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Usuario, TipoAccionAudit
from app.auth import (
    verify_password, create_session_token,
    get_current_user, SESSION_COOKIE, log_audit,
)
from app.templates import templates

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, db: Session = Depends(get_db)):
    if get_current_user(request, db):
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse(request, "login.html", {"error": None})


@router.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(Usuario).filter(
        Usuario.email == email.lower().strip(),
        Usuario.activo == True,
    ).first()

    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            request, "login.html",
            {"error": "Credenciales incorrectas. Intente de nuevo."},
            status_code=401,
        )

    user.ultimo_acceso = datetime.utcnow()
    db.commit()

    log_audit(db, TipoAccionAudit.login, user.id,
              tabla="usuarios", registro_id=user.id,
              descripcion=f"Login exitoso: {user.email}", request=request)

    token = create_session_token(user.id)
    response = RedirectResponse("/", status_code=302)
    response.set_cookie(SESSION_COOKIE, token, httponly=True,
                        samesite="lax", max_age=60 * 60 * 8)
    return response


@router.get("/logout")
async def logout():
    response = RedirectResponse("/login", status_code=302)
    response.delete_cookie(SESSION_COOKIE)
    return response

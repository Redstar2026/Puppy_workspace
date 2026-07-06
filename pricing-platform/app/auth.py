"""Auth helpers — sesiones firmadas con itsdangerous."""
from datetime import datetime
from fastapi import Request, HTTPException
from itsdangerous import URLSafeTimedSerializer
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.config import get_settings
from app.models import Usuario, AuditoriaLog, TipoAccionAudit

settings = get_settings()
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
_serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
SESSION_COOKIE = "wp_session"
MAX_AGE = 60 * 60 * 8  # 8 horas


def hash_password(raw: str) -> str:
    return pwd_ctx.hash(raw)


def verify_password(raw: str, hashed: str) -> bool:
    return pwd_ctx.verify(raw, hashed)


def create_session_token(user_id: int) -> str:
    return _serializer.dumps({"uid": user_id})


def decode_session_token(token: str) -> int | None:
    try:
        data = _serializer.loads(token, max_age=MAX_AGE)
        return data["uid"]
    except Exception:
        return None


def get_current_user(request: Request, db: Session) -> Usuario | None:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return None
    uid = decode_session_token(token)
    if not uid:
        return None
    return db.query(Usuario).filter(Usuario.id == uid, Usuario.activo == True).first()


def require_user(request: Request, db: Session) -> Usuario:
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=302, headers={"Location": "/login"})
    return user


def require_role(request: Request, db: Session, roles: list[str]) -> Usuario:
    user = require_user(request, db)
    if user.rol.value not in roles:
        raise HTTPException(status_code=403, detail="Sin permisos suficientes")
    return user


def log_audit(
    db: Session,
    accion: TipoAccionAudit,
    usuario_id: int | None,
    tabla: str = "",
    registro_id: int | None = None,
    descripcion: str = "",
    request: Request | None = None,
):
    ip = ""
    ua = ""
    if request:
        ip = request.client.host if request.client else ""
        ua = request.headers.get("user-agent", "")[:500]
    entry = AuditoriaLog(
        usuario_id=usuario_id,
        accion=accion,
        tabla_afectada=tabla,
        registro_id=registro_id,
        descripcion=descripcion,
        ip_address=ip,
        user_agent=ua,
    )
    db.add(entry)
    db.commit()

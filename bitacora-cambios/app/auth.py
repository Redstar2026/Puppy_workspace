from passlib.context import CryptContext
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from fastapi import Request, HTTPException
from sqlalchemy.orm import Session
from app.config import SECRET_KEY
from app.models import Usuario

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
serializer = URLSafeTimedSerializer(SECRET_KEY)
SESSION_COOKIE = "bitacora_session"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_session_token(user_id: int) -> str:
    return serializer.dumps(user_id, salt="session")


def decode_session_token(token: str) -> int | None:
    try:
        return serializer.loads(token, salt="session", max_age=86400 * 7)
    except (BadSignature, SignatureExpired):
        return None


def get_current_user(request: Request, db: Session) -> Usuario | None:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return None
    user_id = decode_session_token(token)
    if not user_id:
        return None
    return db.query(Usuario).filter(Usuario.id == user_id, Usuario.activo == True).first()


def require_user(request: Request, db: Session) -> Usuario:
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=302, headers={"Location": "/login"})
    return user

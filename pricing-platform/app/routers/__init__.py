from app.routers.auth import router as auth_router
from app.routers.dashboard import router as dashboard_router
from app.routers.solicitudes import router as solicitudes_router
from app.routers.desarrollos import router as desarrollos_router
from app.routers.aprobaciones import router as aprobaciones_router
from app.routers.auditoria import router as auditoria_router
from app.routers.usuarios import router as usuarios_router

__all__ = [
    "auth_router", "dashboard_router", "solicitudes_router",
    "desarrollos_router", "aprobaciones_router",
    "auditoria_router", "usuarios_router",
]

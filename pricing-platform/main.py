"""
Walmart Pricing Platform — Entry Point
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
from app.routers import (
    auth_router, dashboard_router, solicitudes_router,
    desarrollos_router, aprobaciones_router,
    auditoria_router, usuarios_router,
)
from app.config import get_settings

settings = get_settings()
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="Plataforma enterprise de gestión de solicitudes — Walmart Pricing",
    version="1.0.0",
    docs_url="/api/docs" if settings.DEBUG else None,
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(solicitudes_router)
app.include_router(desarrollos_router)
app.include_router(aprobaciones_router)
app.include_router(auditoria_router)
app.include_router(usuarios_router)

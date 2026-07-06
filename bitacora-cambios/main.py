"""Punto de entrada principal de la aplicación FastAPI."""
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from app.database import engine
from app import models
from app.routers import auth, tareas, aprobaciones, pages

# Crea todas las tablas al iniciar
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bitácora de Cambios", version="1.0.0")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(pages.router)
app.include_router(tareas.router)
app.include_router(aprobaciones.router)


@app.exception_handler(302)
async def redirect_handler(request: Request, exc):
    return RedirectResponse(exc.headers["Location"])

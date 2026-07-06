"""
Walmart Pricing Platform — Demo Simple y Funcional
Un solo archivo. Sin drama. Funciona.
"""
import os, hashlib, secrets
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship

# ── Base de datos ────────────────────────────────────────────────────────────
engine = create_engine("sqlite:///./pricing.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Usuario(Base):
    __tablename__ = "usuarios"
    id       = Column(Integer, primary_key=True)
    nombre   = Column(String(120))
    email    = Column(String(150), unique=True)
    password = Column(String(200))
    rol      = Column(String(30), default="analista")
    activo   = Column(Boolean, default=True)


class Solicitud(Base):
    __tablename__ = "solicitudes"
    id                  = Column(Integer, primary_key=True)
    folio               = Column(String(20), unique=True)
    titulo              = Column(String(300))
    descripcion         = Column(Text, default="")
    tipo                = Column(String(50), default="nuevo_desarrollo")
    prioridad           = Column(String(20), default="media")
    estado              = Column(String(30), default="pendiente")
    area_impactada      = Column(String(150), default="")
    encargado           = Column(String(120), default="")
    porcentaje_avance   = Column(Float, default=0.0)
    riesgo              = Column(String(20), default="bajo")
    fecha_ingreso       = Column(DateTime, default=datetime.utcnow)
    fecha_estimada      = Column(String(20), default="")
    kpi                 = Column(String(200), default="")
    impacto             = Column(Text, default="")
    creado_por          = Column(String(120), default="")
    comentarios         = relationship("Comentario", back_populates="solicitud", cascade="all, delete-orphan")
    historial           = relationship("Historial", back_populates="solicitud", cascade="all, delete-orphan")


class Comentario(Base):
    __tablename__ = "comentarios"
    id           = Column(Integer, primary_key=True)
    solicitud_id = Column(Integer, ForeignKey("solicitudes.id"))
    autor        = Column(String(120))
    contenido    = Column(Text)
    creado_en    = Column(DateTime, default=datetime.utcnow)
    solicitud    = relationship("Solicitud", back_populates="comentarios")


class Historial(Base):
    __tablename__ = "historial"
    id           = Column(Integer, primary_key=True)
    solicitud_id = Column(Integer, ForeignKey("solicitudes.id"))
    accion       = Column(String(200))
    usuario      = Column(String(120))
    creado_en    = Column(DateTime, default=datetime.utcnow)
    solicitud    = relationship("Solicitud", back_populates="historial")


Base.metadata.create_all(bind=engine)

# ── Helpers ──────────────────────────────────────────────────────────────────
def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def check_pw(pw: str, hashed: str) -> bool:
    return hash_pw(pw) == hashed

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user(request: Request, db: Session) -> Optional[Usuario]:
    uid = request.cookies.get("uid")
    if uid and uid.isdigit():
        return db.query(Usuario).filter(Usuario.id == int(uid), Usuario.activo == True).first()
    return None

def folio_siguiente(db: Session) -> str:
    year = datetime.utcnow().year
    count = db.query(Solicitud).count() + 1
    return f"SOL-{year}-{count:04d}"

# ── Datos iniciales ──────────────────────────────────────────────────────────
def seed(db: Session):
    if db.query(Usuario).count() > 0:
        return
    users = [
        ("Admin Sistema",   "admin@walmart.com",    "admin123",  "admin"),
        ("Ana Garcia",      "ana@walmart.com",       "pass123",   "manager"),
        ("Carlos Mendoza",  "carlos@walmart.com",    "pass123",   "developer"),
        ("Maria Lopez",     "maria@walmart.com",     "pass123",   "qa"),
        ("Roberto Jimenez", "roberto@walmart.com",   "pass123",   "analista"),
    ]
    for nombre, email, pw, rol in users:
        db.add(Usuario(nombre=nombre, email=email, password=hash_pw(pw), rol=rol))
    solicitudes = [
        ("Algoritmo de precios dinamicos por zona",   "nuevo_desarrollo", "critica",  "en_desarrollo", 45, "Pricing / Comercial",   "Carlos Mendoza", "alto"),
        ("Correccion redondeo en descuentos",          "correccion",       "alta",     "qa",            90, "Pricing",               "Carlos Mendoza", "medio"),
        ("Automatizacion reporte semanal de precios",  "automatizacion",   "media",    "implementado",  100,"Pricing / BI",          "Carlos Mendoza", "bajo"),
        ("Mejora tiempo de respuesta API precios",     "mejora",           "alta",     "en_analisis",   15, "Tech Pricing",          "Carlos Mendoza", "alto"),
        ("Incidencia: Precios incorrectos Electronica","incidencia",       "critica",  "implementado",  100,"Pricing / Electronica", "Carlos Mendoza", "critico"),
        ("Ajuste reglas precio minimo frescos",        "ajuste",           "media",    "pendiente",     0,  "Pricing / Frescos",     "Maria Lopez",    "medio"),
        ("Modulo simulacion impacto de precios",       "nuevo_desarrollo", "alta",     "en_desarrollo", 35, "Pricing / Analytics",   "Roberto Jimenez","medio"),
        ("Integracion proveedores tiempo real",        "nuevo_desarrollo", "alta",     "aprobacion",    75, "Pricing / Compras",     "Carlos Mendoza", "alto"),
    ]
    year = datetime.utcnow().year
    for i, (titulo, tipo, prio, estado, avance, area, enc, riesgo) in enumerate(solicitudes, 1):
        sol = Solicitud(
            folio=f"SOL-{year}-{i:04d}", titulo=titulo, tipo=tipo,
            prioridad=prio, estado=estado, porcentaje_avance=float(avance),
            area_impactada=area, encargado=enc, riesgo=riesgo,
            creado_por="Admin Sistema",
            descripcion=f"Descripcion detallada de: {titulo}",
            kpi="Reducir error de precios < 0.5%",
            impacto="Mejora en eficiencia y precision de precios",
        )
        db.add(sol)
        db.flush()
        db.add(Historial(solicitud_id=sol.id, accion="Solicitud creada", usuario="Admin Sistema"))
    db.commit()

with SessionLocal() as _s:
    seed(_s)

# ── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(title="Walmart Pricing Platform")
templates = Jinja2Templates(directory="templates")

ESTADO_CSS = {
    "pendiente":     "bg-gray-100 text-gray-700",
    "en_analisis":   "bg-blue-100 text-blue-700",
    "en_desarrollo": "bg-indigo-100 text-indigo-700",
    "qa":            "bg-purple-100 text-purple-700",
    "aprobacion":    "bg-yellow-100 text-yellow-800",
    "implementado":  "bg-green-100 text-green-700",
    "rechazado":     "bg-red-100 text-red-700",
    "cancelado":     "bg-gray-200 text-gray-600",
}
ESTADO_LABEL = {
    "pendiente": "Pendiente", "en_analisis": "En Analisis",
    "en_desarrollo": "En Desarrollo", "qa": "QA",
    "aprobacion": "Aprobacion", "implementado": "Implementado",
    "rechazado": "Rechazado", "cancelado": "Cancelado",
}
PRIO_CSS = {
    "baja": "bg-green-100 text-green-700",
    "media": "bg-blue-100 text-blue-700",
    "alta": "bg-yellow-100 text-yellow-800",
    "critica": "bg-red-100 text-red-700",
}
templates.env.globals["estado_css"]   = lambda e: ESTADO_CSS.get(e, "bg-gray-100 text-gray-700")
templates.env.globals["estado_label"] = lambda e: ESTADO_LABEL.get(e, e)
templates.env.globals["prio_css"]     = lambda e: PRIO_CSS.get(e, "bg-gray-100 text-gray-700")

# ── Rutas ────────────────────────────────────────────────────────────────────

@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request, db: Session = Depends(get_db)):
    if get_user(request, db):
        return RedirectResponse("/", 302)
    return templates.TemplateResponse(request, "login.html", {"error": ""})

@app.post("/login", response_class=HTMLResponse)
async def login_post(request: Request, db: Session = Depends(get_db),
                     email: str = Form(...), password: str = Form(...)):
    user = db.query(Usuario).filter(Usuario.email == email.strip().lower()).first()
    if not user or not check_pw(password, user.password):
        return templates.TemplateResponse(request, "login.html",
                                          {"error": "Email o contrasena incorrectos"})
    resp = RedirectResponse("/", 302)
    resp.set_cookie("uid", str(user.id), httponly=True, max_age=28800)
    resp.set_cookie("uname", user.nombre, max_age=28800)
    return resp

@app.get("/logout")
async def logout():
    resp = RedirectResponse("/login", 302)
    resp.delete_cookie("uid")
    resp.delete_cookie("uname")
    return resp

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_user(request, db)
    if not user:
        return RedirectResponse("/login", 302)
    total     = db.query(Solicitud).count()
    activas   = db.query(Solicitud).filter(Solicitud.estado.notin_(["implementado","rechazado","cancelado"])).count()
    impl      = db.query(Solicitud).filter(Solicitud.estado == "implementado").count()
    criticas  = db.query(Solicitud).filter(Solicitud.prioridad == "critica", Solicitud.estado.notin_(["implementado","rechazado","cancelado"])).count()
    recientes = db.query(Solicitud).order_by(Solicitud.fecha_ingreso.desc()).limit(6).all()
    by_estado = {}
    for s in db.query(Solicitud).all():
        by_estado[s.estado] = by_estado.get(s.estado, 0) + 1
    by_prio = {}
    for s in db.query(Solicitud).all():
        by_prio[s.prioridad] = by_prio.get(s.prioridad, 0) + 1
    return templates.TemplateResponse(request, "dashboard.html", {
        "user": user, "total": total, "activas": activas,
        "impl": impl, "criticas": criticas,
        "recientes": recientes, "by_estado": by_estado, "by_prio": by_prio,
    })

@app.get("/solicitudes", response_class=HTMLResponse)
async def solicitudes_list(
    request: Request, db: Session = Depends(get_db),
    buscar: str = "", estado: str = "", prioridad: str = "",
):
    user = get_user(request, db)
    if not user:
        return RedirectResponse("/login", 302)
    q = db.query(Solicitud)
    if buscar:
        q = q.filter(Solicitud.titulo.ilike(f"%{buscar}%") | Solicitud.folio.ilike(f"%{buscar}%"))
    if estado:
        q = q.filter(Solicitud.estado == estado)
    if prioridad:
        q = q.filter(Solicitud.prioridad == prioridad)
    items = q.order_by(Solicitud.fecha_ingreso.desc()).all()
    return templates.TemplateResponse(request, "solicitudes.html", {
        "user": user, "items": items, "total": len(items),
        "filtros": {"buscar": buscar, "estado": estado, "prioridad": prioridad},
        "estados": list(ESTADO_LABEL.keys()),
        "prioridades": ["baja", "media", "alta", "critica"],
    })

@app.get("/solicitudes/nueva", response_class=HTMLResponse)
async def solicitud_nueva_get(request: Request, db: Session = Depends(get_db)):
    user = get_user(request, db)
    if not user:
        return RedirectResponse("/login", 302)
    return templates.TemplateResponse(request, "form.html", {"user": user, "sol": None})

@app.post("/solicitudes/nueva", response_class=HTMLResponse)
async def solicitud_nueva_post(
    request: Request, db: Session = Depends(get_db),
    titulo: str = Form(...), tipo: str = Form("nuevo_desarrollo"),
    descripcion: str = Form(""), area_impactada: str = Form(""),
    prioridad: str = Form("media"), encargado: str = Form(""),
    riesgo: str = Form("bajo"), kpi: str = Form(""),
    impacto: str = Form(""), fecha_estimada: str = Form(""),
):
    user = get_user(request, db)
    if not user:
        return RedirectResponse("/login", 302)
    folio = folio_siguiente(db)
    sol = Solicitud(
        folio=folio, titulo=titulo, tipo=tipo, descripcion=descripcion,
        area_impactada=area_impactada, prioridad=prioridad,
        encargado=encargado, riesgo=riesgo, kpi=kpi, impacto=impacto,
        fecha_estimada=fecha_estimada, creado_por=user.nombre,
    )
    db.add(sol)
    db.flush()
    db.add(Historial(solicitud_id=sol.id, accion="Solicitud creada", usuario=user.nombre))
    db.commit()
    return RedirectResponse(f"/solicitudes/{sol.id}", 302)

@app.get("/solicitudes/{sol_id}", response_class=HTMLResponse)
async def solicitud_detalle(sol_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_user(request, db)
    if not user:
        return RedirectResponse("/login", 302)
    sol = db.query(Solicitud).filter(Solicitud.id == sol_id).first()
    if not sol:
        return RedirectResponse("/solicitudes", 302)
    return templates.TemplateResponse(request, "detalle.html", {
        "user": user, "sol": sol,
        "estados": list(ESTADO_LABEL.keys()),
        "prioridades": ["baja", "media", "alta", "critica"],
    })

@app.post("/solicitudes/{sol_id}/estado")
async def cambiar_estado(sol_id: int, request: Request, db: Session = Depends(get_db),
                         estado: str = Form(...), porcentaje_avance: float = Form(0.0)):
    user = get_user(request, db)
    if not user:
        return RedirectResponse("/login", 302)
    sol = db.query(Solicitud).filter(Solicitud.id == sol_id).first()
    if sol:
        anterior = sol.estado
        sol.estado = estado
        sol.porcentaje_avance = porcentaje_avance
        db.add(Historial(solicitud_id=sol_id,
                         accion=f"Estado: {anterior} → {estado}", usuario=user.nombre))
        db.commit()
    return RedirectResponse(f"/solicitudes/{sol_id}", 302)

@app.post("/solicitudes/{sol_id}/comentar")
async def comentar(sol_id: int, request: Request, db: Session = Depends(get_db),
                   contenido: str = Form(...)):
    user = get_user(request, db)
    if not user:
        return RedirectResponse("/login", 302)
    db.add(Comentario(solicitud_id=sol_id, autor=user.nombre, contenido=contenido))
    db.commit()
    return RedirectResponse(f"/solicitudes/{sol_id}#comentarios", 302)

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*55)
    print("  WALMART PRICING PLATFORM - DEMO")
    print("="*55)
    print("  URL:  http://localhost:8000")
    print("  Admin:   admin@walmart.com  /  admin123")
    print("  Manager: ana@walmart.com    /  pass123")
    print("  Dev:     carlos@walmart.com /  pass123")
    print("="*55 + "\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

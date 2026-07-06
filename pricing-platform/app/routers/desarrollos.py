"""Router de Desarrollos — Módulo 2."""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from app.database import get_db
from app.auth import get_current_user, log_audit
from app.models import (
    Desarrollo, Solicitud, Usuario, Aprobacion, Comentario,
    HistorialCambio, TipoAccionAudit, EstadoSolicitud,
    NivelRiesgo, ResultadoQA,
)
from app.utils import generar_folio_desarrollo, label_estado
from app.templates import templates

router = APIRouter(prefix="/desarrollos", tags=["desarrollos"])
_RL = lambda: RedirectResponse("/login", status_code=302)


def _hist(db, dev_id, uid, accion, campo="", ant="", nuevo="", detalle=""):
    db.add(HistorialCambio(
        desarrollo_id=dev_id, usuario_id=uid, accion=accion,
        campo_modificado=campo, valor_anterior=str(ant),
        valor_nuevo=str(nuevo), detalle=detalle,
    ))


@router.get("", response_class=HTMLResponse)
async def lista_desarrollos(
    request: Request, db: Session = Depends(get_db),
    estado: str = "", riesgo: str = "", buscar: str = "",
    responsable: str = "", qa: str = "", pagina: int = 1,
):
    user = get_current_user(request, db)
    if not user:
        return _RL()

    q = db.query(Desarrollo).options(
        joinedload(Desarrollo.responsable_dev),
        joinedload(Desarrollo.solicitud),
    )
    if estado:
        q = q.filter(Desarrollo.estado == estado)
    if riesgo:
        q = q.filter(Desarrollo.riesgo_cambio == riesgo)
    if responsable:
        q = q.filter(Desarrollo.responsable_dev_id == int(responsable))
    if qa:
        q = q.filter(Desarrollo.resultado_qa == qa)
    if buscar:
        q = q.filter(or_(
            Desarrollo.nombre.ilike(f"%{buscar}%"),
            Desarrollo.folio.ilike(f"%{buscar}%"),
        ))

    total = q.count()
    per_page = 20
    desarrollos = q.order_by(Desarrollo.fecha_ingreso.desc()).offset(
        (pagina - 1) * per_page).limit(per_page).all()

    usuarios = db.query(Usuario).filter(Usuario.activo == True).all()
    return templates.TemplateResponse(request, "desarrollos/lista.html", {
        "user": user, "page": "desarrollos",
        "desarrollos": desarrollos, "total": total,
        "pagina": pagina, "per_page": per_page,
        "filtros": {"estado": estado, "riesgo": riesgo,
                    "buscar": buscar, "responsable": responsable, "qa": qa},
        "usuarios": usuarios, "label_estado": label_estado,
    })


@router.get("/nuevo", response_class=HTMLResponse)
async def nuevo_form(request: Request, db: Session = Depends(get_db),
                     solicitud_id: Optional[int] = None):
    user = get_current_user(request, db)
    if not user:
        return _RL()
    usuarios = db.query(Usuario).filter(Usuario.activo == True).all()
    solicitudes = db.query(Solicitud).order_by(Solicitud.folio.desc()).limit(100).all()
    return templates.TemplateResponse(request, "desarrollos/form.html", {
        "user": user, "page": "desarrollos",
        "desarrollo": None, "usuarios": usuarios, "solicitudes": solicitudes,
        "solicitud_id_pre": solicitud_id,
        "estados": [e.value for e in EstadoSolicitud],
        "riesgos": [e.value for e in NivelRiesgo],
        "resultados_qa": [e.value for e in ResultadoQA],
    })


@router.post("/nuevo", response_class=HTMLResponse)
async def crear_desarrollo(
    request: Request, db: Session = Depends(get_db),
    nombre: str = Form(...), descripcion_tecnica: str = Form(""),
    objetivo_cambio: str = Form(""),
    solicitud_id: Optional[str] = Form(None),
    responsable_dev_id: Optional[str] = Form(None),
    responsable_qa_id: Optional[str] = Form(None),
    responsable_negocio_id: Optional[str] = Form(None),
    estado: str = Form("pendiente"), porcentaje_avance: float = Form(0.0),
    riesgo_cambio: str = Form("bajo"), impacto_operativo: str = Form(""),
    beneficios_esperados: str = Form(""), resultado_esperado: str = Form(""),
    rollback_plan: str = Form(""), dependencias_tecnicas: str = Form(""),
    tipo_implementacion: str = Form(""), ambiente: str = Form("produccion"),
    github_repo: str = Form(""), github_branch: str = Form(""),
    github_commit: str = Form(""), github_pr: str = Form(""),
    fecha_estimada: Optional[str] = Form(None),
):
    user = get_current_user(request, db)
    if not user:
        return _RL()

    def _int(v):
        return int(v) if v and str(v).isdigit() else None

    folio = generar_folio_desarrollo(db)
    dev = Desarrollo(
        folio=folio, nombre=nombre, descripcion_tecnica=descripcion_tecnica,
        objetivo_cambio=objetivo_cambio, solicitud_id=_int(solicitud_id),
        responsable_dev_id=_int(responsable_dev_id),
        responsable_qa_id=_int(responsable_qa_id),
        responsable_negocio_id=_int(responsable_negocio_id),
        estado=estado, porcentaje_avance=porcentaje_avance,
        riesgo_cambio=riesgo_cambio, impacto_operativo=impacto_operativo,
        beneficios_esperados=beneficios_esperados,
        resultado_esperado=resultado_esperado, rollback_plan=rollback_plan,
        dependencias_tecnicas=dependencias_tecnicas,
        tipo_implementacion=tipo_implementacion, ambiente=ambiente,
        github_repo=github_repo, github_branch=github_branch,
        github_commit=github_commit, github_pr=github_pr,
        fecha_estimada=datetime.strptime(fecha_estimada, "%Y-%m-%d") if fecha_estimada else None,
    )
    db.add(dev)
    db.flush()
    _hist(db, dev.id, user.id, "Desarrollo creado",
          detalle=f"{folio} creado por {user.nombre}")
    db.commit()
    log_audit(db, TipoAccionAudit.creacion, user.id, "desarrollos", dev.id,
              f"Desarrollo {folio} creado", request)
    return RedirectResponse(f"/desarrollos/{dev.id}", status_code=302)


@router.get("/{dev_id}", response_class=HTMLResponse)
async def detalle_desarrollo(dev_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return _RL()
    dev = db.query(Desarrollo).options(
        joinedload(Desarrollo.responsable_dev),
        joinedload(Desarrollo.responsable_qa),
        joinedload(Desarrollo.responsable_negocio),
        joinedload(Desarrollo.solicitud),
        joinedload(Desarrollo.aprobaciones).joinedload(Aprobacion.aprobador),
        joinedload(Desarrollo.comentarios).joinedload(Comentario.autor),
        joinedload(Desarrollo.historial).joinedload(HistorialCambio.usuario),
        joinedload(Desarrollo.adjuntos),
    ).filter(Desarrollo.id == dev_id).first()
    if not dev:
        return RedirectResponse("/desarrollos", status_code=302)

    usuarios = db.query(Usuario).filter(Usuario.activo == True).all()
    return templates.TemplateResponse(request, "desarrollos/detalle.html", {
        "user": user, "page": "desarrollos", "dev": dev, "usuarios": usuarios,
        "estados": [e.value for e in EstadoSolicitud],
        "resultados_qa": [e.value for e in ResultadoQA],
        "label_estado": label_estado,
    })


@router.post("/{dev_id}/estado", response_class=HTMLResponse)
async def cambiar_estado_dev(
    dev_id: int, request: Request, db: Session = Depends(get_db),
    estado: str = Form(...), porcentaje_avance: float = Form(0.0),
    resultado_qa: str = Form("pendiente"),
):
    user = get_current_user(request, db)
    if not user:
        return _RL()
    dev = db.query(Desarrollo).filter(Desarrollo.id == dev_id).first()
    if dev:
        anterior = dev.estado.value if dev.estado else ""
        _hist(db, dev_id, user.id, "Cambio de estado", "estado", anterior, estado)
        dev.estado = estado
        dev.porcentaje_avance = porcentaje_avance
        dev.resultado_qa = resultado_qa
        if estado == "implementado" and not dev.fecha_implementacion:
            dev.fecha_implementacion = datetime.utcnow()
        db.commit()
    return RedirectResponse(f"/desarrollos/{dev_id}", status_code=302)


@router.post("/{dev_id}/comentario", response_class=HTMLResponse)
async def comentar_desarrollo(
    dev_id: int, request: Request, db: Session = Depends(get_db),
    contenido: str = Form(...), tipo: str = Form("interno"),
):
    user = get_current_user(request, db)
    if not user:
        return _RL()
    db.add(Comentario(desarrollo_id=dev_id, autor_id=user.id,
                      contenido=contenido, tipo=tipo))
    db.commit()
    return RedirectResponse(f"/desarrollos/{dev_id}#comentarios", status_code=302)


@router.post("/{dev_id}/github", response_class=HTMLResponse)
async def actualizar_github(
    dev_id: int, request: Request, db: Session = Depends(get_db),
    github_repo: str = Form(""), github_branch: str = Form(""),
    github_commit: str = Form(""), github_pr: str = Form(""),
    logs_implementacion: str = Form(""),
):
    user = get_current_user(request, db)
    if not user:
        return _RL()
    dev = db.query(Desarrollo).filter(Desarrollo.id == dev_id).first()
    if dev:
        dev.github_repo = github_repo
        dev.github_branch = github_branch
        dev.github_commit = github_commit
        dev.github_pr = github_pr
        dev.logs_implementacion = logs_implementacion
        _hist(db, dev_id, user.id, "GitHub actualizado",
              detalle=f"Repo:{github_repo} Commit:{github_commit}")
        db.commit()
    return RedirectResponse(f"/desarrollos/{dev_id}", status_code=302)

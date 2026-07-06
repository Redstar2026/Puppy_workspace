"""Instancia compartida de Jinja2Templates con globals de utilidad."""
from fastapi.templating import Jinja2Templates
from app.utils import label_estado, label_prioridad, label_riesgo
from app.config import get_settings

settings = get_settings()

templates = Jinja2Templates(directory="templates")
templates.env.globals.update({
    "label_estado": label_estado,
    "label_prioridad": label_prioridad,
    "label_riesgo": label_riesgo,
    "app_name": settings.APP_NAME,
})

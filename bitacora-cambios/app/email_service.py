import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from app.config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_FROM, APP_URL


def _build_approval_email(tarea_titulo: str, token: str, solicitante: str) -> tuple[str, str]:
    url_aprobar = f"{APP_URL}/aprobaciones/responder/{token}?accion=aprobada"
    url_rechazar = f"{APP_URL}/aprobaciones/responder/{token}?accion=rechazada"
    url_detalle = f"{APP_URL}/aprobaciones/publica/{token}"

    subject = f"[Bitácora] Aprobación requerida: {tarea_titulo}"
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f9fafb;padding:20px;">
      <div style="background:#0053e2;padding:20px;border-radius:8px 8px 0 0;">
        <h1 style="color:#fff;margin:0;font-size:20px;">📋 Bitácora de Cambios</h1>
        <p style="color:#93c5fd;margin:4px 0 0;">Walmart — Solicitud de Aprobación</p>
      </div>
      <div style="background:#fff;padding:24px;border-radius:0 0 8px 8px;border:1px solid #e5e7eb;">
        <p style="color:#374151;">Hola,</p>
        <p style="color:#374151;"><strong>{solicitante}</strong> solicita tu aprobación para:</p>
        <div style="background:#eff6ff;border-left:4px solid #0053e2;padding:12px 16px;margin:16px 0;border-radius:4px;">
          <p style="margin:0;font-size:18px;font-weight:bold;color:#1e3a8a;">{tarea_titulo}</p>
        </div>
        <p style="color:#374151;">Revisa los detalles y responde:</p>
        <div style="text-align:center;margin:24px 0;">
          <a href="{url_aprobar}" style="background:#2a8703;color:#fff;padding:12px 28px;border-radius:6px;text-decoration:none;font-weight:bold;margin-right:12px;">✅ Aprobar</a>
          <a href="{url_rechazar}" style="background:#ea1100;color:#fff;padding:12px 28px;border-radius:6px;text-decoration:none;font-weight:bold;">❌ Rechazar</a>
        </div>
        <p style="text-align:center;margin-top:8px;">
          <a href="{url_detalle}" style="color:#0053e2;font-size:14px;">Ver detalles completos</a>
        </p>
        <hr style="border:none;border-top:1px solid #e5e7eb;margin:20px 0;">
        <p style="color:#6b7280;font-size:12px;text-align:center;">
          Bitácora de Cambios · Walmart · {datetime.now().strftime('%d/%m/%Y %H:%M')}
        </p>
      </div>
    </div>
    """
    return subject, html


def _build_status_email(tarea_titulo: str, tarea_id: int, estado: str, usuario_nombre: str) -> tuple[str, str]:
    labels = {
        "aprobada": ("✅ Aprobada", "#2a8703"),
        "rechazada": ("❌ Rechazada", "#ea1100"),
        "en_progreso": ("🔄 En Progreso", "#0053e2"),
        "completada": ("🏁 Completada", "#2a8703"),
        "cancelada": ("🚫 Cancelada", "#6b7280"),
    }
    label, color = labels.get(estado, (estado, "#374151"))
    url = f"{APP_URL}/tareas/{tarea_id}"
    subject = f"[Bitácora] Actualización: {tarea_titulo} → {label}"
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f9fafb;padding:20px;">
      <div style="background:#0053e2;padding:20px;border-radius:8px 8px 0 0;">
        <h1 style="color:#fff;margin:0;font-size:20px;">📋 Bitácora de Cambios</h1>
      </div>
      <div style="background:#fff;padding:24px;border-radius:0 0 8px 8px;border:1px solid #e5e7eb;">
        <p>La tarea <strong>{tarea_titulo}</strong> fue actualizada por <strong>{usuario_nombre}</strong>.</p>
        <p style="font-size:20px;font-weight:bold;color:{color};">{label}</p>
        <a href="{url}" style="background:#0053e2;color:#fff;padding:10px 24px;border-radius:6px;text-decoration:none;">Ver Tarea</a>
      </div>
    </div>
    """
    return subject, html


def send_email(to: str, subject: str, html: str) -> bool:
    """Envía email. Si SMTP no está configurado, imprime en consola."""
    if not SMTP_HOST or not SMTP_USER:
        print(f"\n{'='*60}")
        print(f"📧 [EMAIL SIMULADO — configura SMTP en .env para envíos reales]")
        print(f"Para: {to}")
        print(f"Asunto: {subject}")
        print(f"{'='*60}\n")
        return True
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = SMTP_FROM
        msg["To"] = to
        msg.attach(MIMEText(html, "html"))
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, to, msg.as_string())
        return True
    except Exception as e:
        print(f"❌ Error al enviar email: {e}")
        return False


def notify_approval_request(aprobador_email: str, tarea_titulo: str, token: str, solicitante: str):
    subject, html = _build_approval_email(tarea_titulo, token, solicitante)
    send_email(aprobador_email, subject, html)


def notify_status_change(to_email: str, tarea_titulo: str, tarea_id: int, estado: str, usuario_nombre: str):
    subject, html = _build_status_email(tarea_titulo, tarea_id, estado, usuario_nombre)
    send_email(to_email, subject, html)

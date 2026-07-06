import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./bitacora.db")
APP_URL: str = os.getenv("APP_URL", "http://localhost:8000")
SMTP_HOST: str = os.getenv("SMTP_HOST", "")
SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER: str = os.getenv("SMTP_USER", "")
SMTP_PASS: str = os.getenv("SMTP_PASS", "")
SMTP_FROM: str = os.getenv("SMTP_FROM", "Bitácora <noreply@walmart.com>")

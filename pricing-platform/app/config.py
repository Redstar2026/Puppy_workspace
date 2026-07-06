from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    SECRET_KEY: str = "walmart-pricing-platform-secret-key-change-me"
    DATABASE_URL: str = "sqlite:///./pricing.db"
    APP_NAME: str = "Walmart Pricing Platform"
    DEBUG: bool = True
    UPLOAD_DIR: str = "static/uploads"
    MAX_UPLOAD_MB: int = 10
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    SMTP_FROM: str = "pricing-platform@walmart.com"
    GITHUB_TOKEN: str = ""
    GITHUB_REPO: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

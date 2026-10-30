import os
import logging
import secrets
from typing import List

app_environment = os.getenv("APP_ENV", "development").lower()
secret_key = os.getenv("SECRET_KEY")
if not secret_key:
    if app_environment == "production":
        raise RuntimeError("SECRET_KEY must be configured when APP_ENV=production.")
    secret_key = secrets.token_urlsafe(32)
    logging.getLogger(__name__).warning(
        "SECRET_KEY is unset; using a temporary development key. "
        "Set SECRET_KEY to keep sessions valid across restarts."
    )


class Settings:
    APP_ENV: str = app_environment
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Multi-Feature AI-Powered CRM")
    API_V1_STR: str = os.getenv("API_V1_STR", "/api")
    SECRET_KEY: str = secret_key
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24 * 7)))
    COOKIE_SECURE: bool = os.getenv(
        "COOKIE_SECURE", "true" if app_environment == "production" else "false"
    ).lower() in {"1", "true", "yes"}
    SEED_DEMO_DATA: bool = os.getenv(
        "SEED_DEMO_DATA", "false" if app_environment == "production" else "true"
    ).lower() in {"1", "true", "yes"}
    
    # Database: Supports SQLite for zero-config dev and PostgreSQL for production
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./crm.db")
    
    # CORS Origins
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    
    # AI / LLM Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "mock")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")

settings = Settings()

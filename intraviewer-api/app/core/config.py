from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Intraviewer API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"  # development | production

    DATABASE_URL: str = "sqlite:///./intraviewer.db"
    GROQ_API_KEY: Optional[str] = None

    # --- Auth tokens -------------------------------------------------------
    # MUST be overridden in production via .env (min 32 random chars).
    SECRET_KEY: str = "dev-only-insecure-secret-change-me-0123456789abcdef"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 10

    # --- Cookies -------------------------------------------------------------
    ACCESS_COOKIE_NAME: str = "iv_access"
    REFRESH_COOKIE_NAME: str = "iv_refresh"
    COOKIE_SECURE: bool = False  # set True in production (HTTPS)
    COOKIE_SAMESITE: str = "lax"
    COOKIE_DOMAIN: Optional[str] = None

    # --- CORS (only needed if frontend calls API directly, not via proxy) ----
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Trust X-Forwarded-For (Next.js rewrite proxy sits in front of the API).
    TRUST_PROXY_HEADERS: bool = True

    # --- OTP -----------------------------------------------------------------
    OTP_LENGTH: int = 6
    OTP_EXPIRE_MINUTES: int = 10
    OTP_MAX_ATTEMPTS: int = 5
    OTP_RESEND_COOLDOWN_SECONDS: int = 60
    OTP_MAX_SENDS_PER_HOUR: int = 5

    # --- Login rate limiting -------------------------------------------------
    LOGIN_MAX_FAILURES_PER_EMAIL: int = 5
    LOGIN_FAILURE_WINDOW_SECONDS: int = 900
    LOGIN_MAX_ATTEMPTS_PER_IP: int = 30
    LOGIN_IP_WINDOW_SECONDS: int = 300

    # --- Email (SMTP). If SMTP_HOST is empty, emails are logged to console. --
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True
    EMAIL_FROM: str = "Intraviewer <no-reply@intraviewer.ai>"

    # --- Uploads -------------------------------------------------------------
    UPLOAD_DIR: str = "app/static/uploads"
    MAX_IMAGE_UPLOAD_BYTES: int = 2 * 1024 * 1024

    # Extra consumer domains to block for company signup (comma separated in .env)
    EXTRA_CONSUMER_EMAIL_DOMAINS: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"


settings = Settings()

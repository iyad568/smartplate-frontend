from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from functools import lru_cache


class Settings(BaseSettings):
    """
    All settings are read from environment variables first, then from a
    local .env file (development only).  On Render / Railway simply set the
    env vars in the dashboard — no .env file needed.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ─── Database ─────────────────────────────────────────────────────────────
    DATABASE_URL: str = ""

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def fix_async_db_url(cls, v: str) -> str:
        """
        Render (and most PaaS) provide  postgresql://  URLs.
        SQLAlchemy's asyncpg driver requires  postgresql+asyncpg://
        """
        if v and v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    # ─── JWT ──────────────────────────────────────────────────────────────────
    SECRET_KEY: str = "changeme-set-a-real-secret-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PRE_AUTH_TOKEN_EXPIRE_MINUTES: int = 10

    # ─── OTP ──────────────────────────────────────────────────────────────────
    OTP_LENGTH: int = 6
    OTP_EXPIRE_MINUTES: int = 10
    OTP_RESEND_COOLDOWN_SECONDS: int = 60
    OTP_MAX_ATTEMPTS: int = 5
    MAX_LOGIN_ATTEMPTS_PER_MINUTE: int = 5

    # ─── SMTP ─────────────────────────────────────────────────────────────────
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_NAME: str = "SmartPlate"
    EMAILS_FROM_EMAIL: str = ""

    # ─── App ──────────────────────────────────────────────────────────────────
    FRONTEND_URL: str = "http://localhost:5173"
    BACKEND_URL: str = "http://localhost:8002"
    APP_ENV: str = "development"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

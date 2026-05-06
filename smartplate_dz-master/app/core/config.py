from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import dotenv

dotenv.load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    # ─── Database ─────────────────────────────────────────────────────────────
    DATABASE_URL: str = dotenv.dotenv_values().get("DATABASE_URL", "")

    # ─── JWT ──────────────────────────────────────────────────────────────────
    SECRET_KEY: str = dotenv.dotenv_values().get("SECRET_KEY", "changeme")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    # Pre-auth (otp_pending) token issued after step-1 of login, used for /verify-login-otp
    PRE_AUTH_TOKEN_EXPIRE_MINUTES: int = 10

    # ─── OTP ──────────────────────────────────────────────────────────────────
    OTP_LENGTH: int = 6
    OTP_EXPIRE_MINUTES: int = 10           # 5–10 min per spec
    OTP_RESEND_COOLDOWN_SECONDS: int = 60  # seconds between successive OTP sends
    OTP_MAX_ATTEMPTS: int = 5              # max wrong-code attempts before forced regenerate
    MAX_LOGIN_ATTEMPTS_PER_MINUTE: int = 5 # used by slowapi limiter on /auth/login

    # ─── SMTP ─────────────────────────────────────────────────────────────────
    SMTP_HOST: str = dotenv.dotenv_values().get("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(dotenv.dotenv_values().get("SMTP_PORT", "587"))
    SMTP_USERNAME: str = dotenv.dotenv_values().get("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = dotenv.dotenv_values().get("SMTP_PASSWORD", "")
    EMAILS_FROM_NAME: str = dotenv.dotenv_values().get("EMAILS_FROM_NAME", "SmartPlate")
    EMAILS_FROM_EMAIL: str = dotenv.dotenv_values().get("EMAILS_FROM_EMAIL", "")

    # ─── App ──────────────────────────────────────────────────────────────────
    FRONTEND_URL: str = dotenv.dotenv_values().get("FRONTEND_URL", "http://localhost:3000")
    BACKEND_URL: str = dotenv.dotenv_values().get("BACKEND_URL", "http://localhost:8002")
    APP_ENV: str = dotenv.dotenv_values().get("APP_ENV", "development")

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

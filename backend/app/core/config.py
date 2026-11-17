"""Application settings, loaded from environment variables (see /.env.example)."""

from functools import lru_cache
from typing import Literal

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEV_PEPPER = "dev-only-change-me"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: Literal["development", "test", "staging", "production"] = "development"
    app_name: str = "Offerlight"
    public_app_url: str = "http://localhost:5173"
    api_cors_origins: list[str] = ["http://localhost:5173"]
    log_level: str = "INFO"

    database_url: str = "postgresql+asyncpg://offerlight:offerlight@localhost:5432/offerlight"
    redis_url: str = "redis://localhost:6379/0"

    # Auth
    auth_code_pepper: SecretStr = SecretStr(_DEV_PEPPER)
    auth_code_ttl_seconds: int = 600
    auth_code_max_attempts: int = 5
    webauthn_rp_id: str = "localhost"
    webauthn_rp_name: str = "Offerlight"
    webauthn_origins: list[str] = ["http://localhost:5173"]

    # Bot protection
    turnstile_enabled: bool = False
    turnstile_secret_key: SecretStr | None = None
    turnstile_expected_hostname: str | None = None
    min_form_seconds: float = 2.0

    # Rate limiting
    rate_limit_backend: Literal["redis", "memory"] = "redis"

    # Email
    email_provider: Literal["smtp", "postmark", "ses", "memory"] = "smtp"
    email_from: str = "Offerlight <hello@offerlight.localhost>"
    smtp_host: str = "localhost"
    smtp_port: int = 1025

    # Privacy (docs/13-privacy-and-compliance.md)
    privacy_pseudonym_key: SecretStr = SecretStr(_DEV_PEPPER)
    privacy_contact_email: str = "privacy@offerlight.localhost"

    # Observability
    sentry_dsn: str | None = None

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def docs_enabled(self) -> bool:
        return self.environment in ("development", "test")

    @model_validator(mode="after")
    def _production_safety(self) -> "Settings":
        if self.environment in ("staging", "production"):
            if self.auth_code_pepper.get_secret_value() == _DEV_PEPPER:
                raise ValueError("AUTH_CODE_PEPPER must be set outside development")
            key = self.privacy_pseudonym_key.get_secret_value()
            if key == _DEV_PEPPER or key == self.auth_code_pepper.get_secret_value():
                raise ValueError(
                    "PRIVACY_PSEUDONYM_KEY must be set outside development "
                    "and differ from the pepper"
                )
            if not self.turnstile_enabled or self.turnstile_secret_key is None:
                raise ValueError("Turnstile must be enabled with a secret key outside development")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()

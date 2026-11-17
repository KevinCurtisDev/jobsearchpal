import pytest
from pydantic import SecretStr, ValidationError

from app.core.config import Settings


def test_production_requires_real_pepper_and_turnstile() -> None:
    with pytest.raises(ValidationError):
        Settings(environment="production")
    with pytest.raises(ValidationError):
        Settings(environment="production", auth_code_pepper=SecretStr("real-secret"))
    base = {
        "environment": "production",
        "auth_code_pepper": SecretStr("real-secret"),
        "turnstile_enabled": True,
        "turnstile_secret_key": SecretStr("ts"),
    }
    with pytest.raises(ValidationError, match="PRIVACY_PSEUDONYM_KEY"):
        Settings(**base)  # type: ignore[arg-type]
    with pytest.raises(ValidationError, match="PRIVACY_PSEUDONYM_KEY"):
        Settings(**base, privacy_pseudonym_key=SecretStr("real-secret"))  # type: ignore[arg-type]
    ok = Settings(**base, privacy_pseudonym_key=SecretStr("another-secret"))  # type: ignore[arg-type]
    assert ok.is_production and not ok.docs_enabled

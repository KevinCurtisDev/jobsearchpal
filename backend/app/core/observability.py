"""Error monitoring with personal data stripped (see app/privacy/redaction.py)."""

from app.core.config import Settings
from app.privacy.redaction import sentry_before_send


def init_sentry(settings: Settings, component: str) -> bool:
    """Initialise Sentry if a DSN is set. Returns True when enabled."""
    if not settings.sentry_dsn:
        return False
    import sentry_sdk

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        send_default_pii=False,  # never send IPs, cookies or user details
        before_send=sentry_before_send,  # type: ignore[arg-type]
        max_request_body_size="never",
        traces_sample_rate=0.0,
        server_name=component,  # avoid the host name
    )
    return True

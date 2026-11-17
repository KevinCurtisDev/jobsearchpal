"""Import every model here so Alembic autogenerate can see it.

Stage 1 adds: User, PasskeyCredential, UserSession, Consent, AuditLog, FeatureFlag
(see docs/04-data-model.md). Example convention:

    class User(IdTimestampMixin, Base):
        __tablename__ = "users"
        email: Mapped[str] = mapped_column(CITEXT, unique=True)
        ...
"""

from app.db.base import Base

__all__ = ["Base"]

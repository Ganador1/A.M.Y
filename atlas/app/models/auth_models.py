"""
User Authentication Models for AXIOM ATLAS
Database models for user management and authentication.
"""

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func

from app.models.database_models import Base
from app.core.rbac import Role


class User(Base):
    """User model for authentication"""

    __tablename__ = "users"

    id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)

    # Role and status - stored as string for SQLite compatibility
    role = Column(String, nullable=False, default=Role.VIEWER.value)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Additional metadata
    organization = Column(String, nullable=True)
    department = Column(String, nullable=True)

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.role})>"


class RefreshToken(Base):
    """Refresh token model for token rotation"""

    __tablename__ = "refresh_tokens"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    token_hash = Column(String, nullable=False, unique=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_revoked = Column(Boolean, default=False, nullable=False)

    # Device/session tracking
    user_agent = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)

    def __repr__(self) -> str:
        return f"<RefreshToken {self.id} for user {self.user_id}>"


class LoginAttempt(Base):
    """Track login attempts for security monitoring"""

    __tablename__ = "login_attempts"

    id = Column(String, primary_key=True)
    username = Column(String, nullable=False, index=True)
    success = Column(Boolean, nullable=False)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    attempted_at = Column(DateTime(timezone=True), server_default=func.now())
    failure_reason = Column(String, nullable=True)

    def __repr__(self) -> str:
        status = "SUCCESS" if self.success else "FAILED"
        return f"<LoginAttempt {self.username} {status} at {self.attempted_at}>"

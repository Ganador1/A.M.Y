"""
Authentication Service for AXIOM ATLAS
Business logic for user authentication and authorization.
"""

from typing import Optional
from datetime import datetime, timedelta
from uuid import uuid4
import hashlib

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.auth_models import User, RefreshToken, LoginAttempt
from app.core.jwt_handler import JWTHandler
from app.core.rbac import Role
from app.schemas.auth_schemas import UserRegister


class AuthService:
    """Service for authentication operations"""

    def __init__(self):
        self.jwt_handler = JWTHandler()

    async def register_user(
        self,
        user_data: UserRegister,
        db: AsyncSession,
        role: Role = Role.VIEWER
    ) -> User:
        """Register a new user"""
        # Check if user exists
        result = await db.execute(
            select(User).where(User.username == user_data.username)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

        # Check if email exists
        result = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create user
        hashed_password = self.jwt_handler.get_password_hash(user_data.password)
        user = User(
            id=str(uuid4()),
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role=role,
            organization=user_data.organization,
            department=user_data.department
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user

    async def authenticate_user(
        self,
        username: str,
        password: str,
        db: AsyncSession,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Optional[User]:
        """Authenticate user and log attempt"""
        # Get user
        result = await db.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()

        # Log attempt
        attempt = LoginAttempt(
            id=str(uuid4()),
            username=username,
            success=False,
            ip_address=ip_address,
            user_agent=user_agent
        )

        if not user:
            attempt.failure_reason = "User not found"
            db.add(attempt)
            await db.commit()
            return None

        if not user.is_active:
            attempt.failure_reason = "Account disabled"
            db.add(attempt)
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled"
            )

        # Verify password
        if not self.jwt_handler.verify_password(password, user.hashed_password):
            attempt.failure_reason = "Invalid password"
            db.add(attempt)
            await db.commit()
            return None

        # Success
        attempt.success = True
        user.last_login = datetime.utcnow()
        db.add(attempt)
        await db.commit()
        await db.refresh(user)

        return user

    async def create_tokens(
        self,
        user: User,
        db: AsyncSession,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> tuple[str, str]:
        """Create access and refresh tokens"""
        # Create access token
        access_token = self.jwt_handler.create_access_token(
            data={
                "user_id": user.id,
                "sub": user.username,
                "role": user.role.value,
                "email": user.email
            }
        )

        # Create refresh token
        refresh_token = self.jwt_handler.create_refresh_token(
            data={"user_id": user.id}
        )

        # Store refresh token
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        refresh_token_record = RefreshToken(
            id=str(uuid4()),
            user_id=user.id,
            token_hash=token_hash,
            expires_at=datetime.utcnow() + timedelta(days=7),
            ip_address=ip_address,
            user_agent=user_agent
        )

        db.add(refresh_token_record)
        await db.commit()

        return access_token, refresh_token

    async def refresh_access_token(
        self,
        refresh_token: str,
        db: AsyncSession
    ) -> str:
        """Refresh access token using refresh token"""
        # Verify refresh token
        payload = self.jwt_handler.verify_token(refresh_token)

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        # Check if token is revoked
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        token_record = result.scalar_one_or_none()

        if not token_record or token_record.is_revoked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token revoked or invalid"
            )

        if token_record.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )

        # Get user
        user_id = payload.get("user_id")
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        # Create new access token
        access_token = self.jwt_handler.create_access_token(
            data={
                "user_id": user.id,
                "sub": user.username,
                "role": user.role.value,
                "email": user.email
            }
        )

        return access_token

    async def revoke_refresh_token(
        self,
        refresh_token: str,
        db: AsyncSession
    ) -> None:
        """Revoke a refresh token"""
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        token_record = result.scalar_one_or_none()

        if token_record:
            token_record.is_revoked = True
            await db.commit()

    async def revoke_all_user_tokens(
        self,
        user_id: str,
        db: AsyncSession
    ) -> None:
        """Revoke all refresh tokens for a user"""
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.user_id == user_id)
        )
        tokens = result.scalars().all()

        for token in tokens:
            token.is_revoked = True

        await db.commit()

    async def change_password(
        self,
        user_id: str,
        old_password: str,
        new_password: str,
        db: AsyncSession
    ) -> None:
        """Change user password"""
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Verify old password
        if not self.jwt_handler.verify_password(old_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid current password"
            )

        # Update password
        user.hashed_password = self.jwt_handler.get_password_hash(new_password)
        await db.commit()

        # Revoke all existing tokens for security
        await self.revoke_all_user_tokens(user_id, db)

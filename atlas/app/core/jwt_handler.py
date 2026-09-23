"""
JWT Token Handler for AXIOM ATLAS
Provides JWT token generation, validation, and management.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour
REFRESH_TOKEN_EXPIRE_DAYS = 7  # 7 days


class JWTHandler:
    """Handle JWT token operations"""

    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = ALGORITHM
        self.access_token_expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        self.refresh_token_expire = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token.

        Args:
            data: Payload data (user_id, username, role, etc.)
            expires_delta: Optional custom expiration time

        Returns:
            Encoded JWT token string
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + self.access_token_expire

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })

        encoded_jwt = jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm
        )

        logger.info("Access token created for user: %s", data.get('sub'))
        return encoded_jwt

    def create_refresh_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT refresh token.

        Args:
            data: Payload data (user_id, username)
            expires_delta: Optional custom expiration time

        Returns:
            Encoded JWT refresh token string
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + self.refresh_token_expire

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })

        encoded_jwt = jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm
        )

        logger.info("Refresh token created for user: %s", data.get('sub'))
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode JWT token.

        Args:
            token: JWT token string

        Returns:
            Decoded token payload or None if invalid

        Raises:
            JWTError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )

            # Validate token type
            token_type = payload.get("type")
            if token_type not in ["access", "refresh"]:
                logger.warning("Invalid token type: %s", token_type)
                return None

            return payload

        except JWTError as e:
            logger.error("Token verification failed: %s", str(e))
            raise

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against hash.

        Args:
            plain_password: Plain text password
            hashed_password: Hashed password

        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        Hash password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        return pwd_context.hash(password)


# Global JWT handler instance
jwt_handler = JWTHandler()


# Utility functions
def create_access_token(data: Dict[str, Any]) -> str:
    """Create access token - convenience wrapper"""
    return jwt_handler.create_access_token(data)


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create refresh token - convenience wrapper"""
    return jwt_handler.create_refresh_token(data)


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify token - convenience wrapper"""
    return jwt_handler.verify_token(token)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password - convenience wrapper"""
    return jwt_handler.verify_password(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password - convenience wrapper"""
    return jwt_handler.get_password_hash(password)

"""
Integration tests for Authentication Flow
Tests the complete auth flow: login → access → refresh → logout
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.database_models import Base
from app.models.auth_models import RefreshToken
from app.core.rbac import Role
from app.services.auth_service import AuthService
from app.schemas.auth_schemas import UserRegister


# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def auth_service():
    """Create AuthService instance"""
    return AuthService()


@pytest.fixture
async def test_user(db_session, auth_service):
    """Create a test user"""
    user_data = UserRegister(
        username="testuser",
        email="test@example.com",
        password="TestPassword123!"
    )

    user = await auth_service.register_user(user_data, db_session, role=Role.RESEARCHER)
    return user


class TestUserRegistration:
    """Test suite for user registration"""

    @pytest.mark.asyncio
    async def test_register_new_user(self, db_session, auth_service):
        """Test successful user registration"""
        user_data = UserRegister(
            username="newuser",
            email="newuser@example.com",
            password="SecurePass123!",
            full_name="New User"
        )

        user = await auth_service.register_user(user_data, db_session)

        assert user.id is not None
        assert user.username == "newuser"
        assert user.email == "newuser@example.com"
        assert user.full_name == "New User"
        assert user.role == Role.VIEWER.value  # Default role
        assert user.is_active is True
        assert user.is_verified is False
        assert user.hashed_password != "SecurePass123!"  # Should be hashed

    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, db_session, auth_service, test_user):
        """Test registration with duplicate username"""
        user_data = UserRegister(
            username="testuser",  # Same as test_user
            email="different@example.com",
            password="Password123!"
        )

        with pytest.raises(Exception) as exc_info:
            await auth_service.register_user(user_data, db_session)

        assert "already exists" in str(exc_info.value).lower() or \
               "username" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, db_session, auth_service, test_user):
        """Test registration with duplicate email"""
        user_data = UserRegister(
            username="differentuser",
            email="test@example.com",  # Same as test_user
            password="Password123!"
        )

        with pytest.raises(Exception) as exc_info:
            await auth_service.register_user(user_data, db_session)

        assert "already" in str(exc_info.value).lower() or \
               "email" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_register_with_role(self, db_session, auth_service):
        """Test registration with specific role"""
        user_data = UserRegister(
            username="adminuser",
            email="admin@example.com",
            password="AdminPass123!"
        )

        user = await auth_service.register_user(user_data, db_session, role=Role.ADMIN)

        assert user.role == Role.ADMIN.value


class TestUserAuthentication:
    """Test suite for user authentication"""

    @pytest.mark.asyncio
    async def test_authenticate_valid_credentials(self, db_session, auth_service, test_user):
        """Test authentication with valid credentials"""
        user = await auth_service.authenticate_user(
            username="testuser",
            password="TestPassword123!",
            db=db_session
        )

        assert user is not None
        assert user.username == "testuser"
        assert user.last_login is not None

    @pytest.mark.asyncio
    async def test_authenticate_wrong_password(self, db_session, auth_service, test_user):
        """Test authentication with wrong password"""
        user = await auth_service.authenticate_user(
            username="testuser",
            password="WrongPassword123!",
            db=db_session
        )

        assert user is None

    @pytest.mark.asyncio
    async def test_authenticate_nonexistent_user(self, db_session, auth_service):
        """Test authentication with non-existent user"""
        user = await auth_service.authenticate_user(
            username="nonexistent",
            password="AnyPassword123!",
            db=db_session
        )

        assert user is None

    @pytest.mark.asyncio
    async def test_authenticate_inactive_user(self, db_session, auth_service, test_user):
        """Test authentication with inactive user"""
        # Deactivate user
        test_user.is_active = False
        db_session.commit()

        with pytest.raises(Exception) as exc_info:
            await auth_service.authenticate_user(
                username="testuser",
                password="TestPassword123!",
                db=db_session
            )

        assert "disabled" in str(exc_info.value).lower() or \
               "inactive" in str(exc_info.value).lower()


class TestTokenGeneration:
    """Test suite for token generation"""

    @pytest.mark.asyncio
    async def test_create_tokens(self, db_session, auth_service, test_user):
        """Test creation of access and refresh tokens"""
        access_token, refresh_token = await auth_service.create_tokens(
            user=test_user,
            db=db_session,
            ip_address="192.168.1.1",
            user_agent="Test Client"
        )

        assert isinstance(access_token, str)
        assert isinstance(refresh_token, str)
        assert len(access_token) > 0
        assert len(refresh_token) > 0
        assert access_token != refresh_token

    @pytest.mark.asyncio
    async def test_refresh_token_stored(self, db_session, auth_service, test_user):
        """Test that refresh token is stored in database"""
        _access_token, _refresh_token = await auth_service.create_tokens(
            user=test_user,
            db=db_session
        )

        # Check refresh token is in database
        from sqlalchemy import select
        result = await db_session.execute(
            select(RefreshToken).where(RefreshToken.user_id == test_user.id)
        )
        stored_token = result.scalar_one_or_none()

        assert stored_token is not None
        assert stored_token.user_id == test_user.id
        assert stored_token.is_revoked is False


class TestTokenRefresh:
    """Test suite for token refresh flow"""

    @pytest.mark.asyncio
    async def test_refresh_access_token(self, db_session, auth_service, test_user):
        """Test refreshing access token with valid refresh token"""
        # Create initial tokens
        old_access_token, refresh_token = await auth_service.create_tokens(
            user=test_user,
            db=db_session
        )

        # Refresh access token
        new_access_token = await auth_service.refresh_access_token(
            refresh_token=refresh_token,
            db=db_session
        )

        assert isinstance(new_access_token, str)
        assert new_access_token != old_access_token

    @pytest.mark.asyncio
    async def test_refresh_with_invalid_token(self, db_session, auth_service):
        """Test refresh with invalid token"""
        with pytest.raises(Exception):
            await auth_service.refresh_access_token(
                refresh_token="invalid.token.here",
                db=db_session
            )

    @pytest.mark.asyncio
    async def test_refresh_with_revoked_token(self, db_session, auth_service, test_user):
        """Test refresh with revoked token"""
        # Create and revoke token
        _access_token, refresh_token = await auth_service.create_tokens(
            user=test_user,
            db=db_session
        )

        await auth_service.revoke_refresh_token(refresh_token, db_session)

        # Try to refresh
        with pytest.raises(Exception) as exc_info:
            await auth_service.refresh_access_token(refresh_token, db_session)

        assert "revoked" in str(exc_info.value).lower() or \
               "invalid" in str(exc_info.value).lower()


class TestTokenRevocation:
    """Test suite for token revocation"""

    @pytest.mark.asyncio
    async def test_revoke_single_token(self, db_session, auth_service, test_user):
        """Test revoking a single refresh token"""
        _access_token, refresh_token = await auth_service.create_tokens(
            user=test_user,
            db=db_session
        )

        await auth_service.revoke_refresh_token(refresh_token, db_session)

        # Verify token is revoked
        from sqlalchemy import select
        import hashlib
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        result = await db_session.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        stored_token = result.scalar_one_or_none()

        assert stored_token.is_revoked is True

    @pytest.mark.asyncio
    async def test_revoke_all_user_tokens(self, db_session, auth_service, test_user):
        """Test revoking all tokens for a user"""
        # Create multiple tokens
        tokens = []
        for _ in range(3):
            _access_token, refresh_token = await auth_service.create_tokens(
                user=test_user,
                db=db_session
            )
            tokens.append(refresh_token)

        # Revoke all
        await auth_service.revoke_all_user_tokens(test_user.id, db_session)

        # Verify all are revoked
        from sqlalchemy import select
        result = await db_session.execute(
            select(RefreshToken).where(RefreshToken.user_id == test_user.id)
        )
        all_tokens = result.scalars().all()

        assert all(token.is_revoked for token in all_tokens)


class TestPasswordChange:
    """Test suite for password change"""

    @pytest.mark.asyncio
    async def test_change_password_success(self, db_session, auth_service, test_user):
        """Test successful password change"""
        old_password = "TestPassword123!"
        new_password = "NewPassword456!"

        await auth_service.change_password(
            user_id=test_user.id,
            old_password=old_password,
            new_password=new_password,
            db=db_session
        )

        # Verify old password no longer works
        user = await auth_service.authenticate_user(
            username="testuser",
            password=old_password,
            db=db_session
        )
        assert user is None

        # Verify new password works
        user = await auth_service.authenticate_user(
            username="testuser",
            password=new_password,
            db=db_session
        )
        assert user is not None

    @pytest.mark.asyncio
    async def test_change_password_wrong_old_password(self, db_session, auth_service, test_user):
        """Test password change with wrong old password"""
        with pytest.raises(Exception) as exc_info:
            await auth_service.change_password(
                user_id=test_user.id,
                old_password="WrongOldPassword!",
                new_password="NewPassword456!",
                db=db_session
            )

        assert "invalid" in str(exc_info.value).lower() or \
               "incorrect" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_password_change_revokes_tokens(self, db_session, auth_service, test_user):
        """Test that password change revokes all refresh tokens"""
        # Create token
        _access_token, _refresh_token = await auth_service.create_tokens(
            user=test_user,
            db=db_session
        )

        # Change password
        await auth_service.change_password(
            user_id=test_user.id,
            old_password="TestPassword123!",
            new_password="NewPassword456!",
            db=db_session
        )

        # Verify token is revoked
        from sqlalchemy import select
        result = await db_session.execute(
            select(RefreshToken).where(RefreshToken.user_id == test_user.id)
        )
        all_tokens = result.scalars().all()

        assert all(token.is_revoked for token in all_tokens)


class TestCompleteAuthFlow:
    """Test suite for complete authentication flow"""

    @pytest.mark.asyncio
    async def test_full_auth_flow(self, db_session, auth_service):
        """Test complete flow: register → login → refresh → logout"""
        # 1. Register
        user_data = UserRegister(
            username="flowuser",
            email="flow@example.com",
            password="FlowPassword123!"
        )
        user = await auth_service.register_user(user_data, db_session)
        assert user.username == "flowuser"

        # 2. Authenticate
        auth_user = await auth_service.authenticate_user(
            username="flowuser",
            password="FlowPassword123!",
            db=db_session
        )
        assert auth_user is not None

        # 3. Create tokens
        access_token, refresh_token = await auth_service.create_tokens(
            user=auth_user,
            db=db_session
        )
        assert access_token is not None
        assert refresh_token is not None

        # 4. Refresh access token
        new_access_token = await auth_service.refresh_access_token(
            refresh_token=refresh_token,
            db=db_session
        )
        assert new_access_token != access_token

        # 5. Logout (revoke token)
        await auth_service.revoke_refresh_token(refresh_token, db_session)

        # 6. Verify cannot refresh with revoked token
        with pytest.raises(Exception):
            await auth_service.refresh_access_token(refresh_token, db_session)

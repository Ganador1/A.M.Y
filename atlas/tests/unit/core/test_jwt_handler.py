"""
Unit tests for JWT Handler
Tests token generation, validation, and password hashing.
"""

import pytest
from datetime import datetime, timedelta
from jose import jwt

from app.core.jwt_handler import (
    JWTHandler,
    create_access_token,
    create_refresh_token,
    verify_token,
    verify_password,
    get_password_hash,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
)
from app.core.config import settings


class TestJWTHandler:
    """Test suite for JWTHandler class"""

    def setup_method(self):
        """Setup for each test"""
        self.jwt_handler = JWTHandler()
        self.test_user_data = {
            "user_id": "test-user-123",
            "sub": "testuser",
            "role": "RESEARCHER",
            "email": "test@example.com"
        }

    def test_jwt_handler_initialization(self):
        """Test JWTHandler initializes correctly"""
        assert self.jwt_handler.secret_key == settings.secret_key
        assert self.jwt_handler.algorithm == ALGORITHM
        assert self.jwt_handler.access_token_expire.total_seconds() == ACCESS_TOKEN_EXPIRE_MINUTES * 60
        assert self.jwt_handler.refresh_token_expire.total_seconds() == REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600

    def test_create_access_token_with_defaults(self):
        """Test access token creation with default expiration"""
        token = self.jwt_handler.create_access_token(data=self.test_user_data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode and verify payload
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        assert payload["user_id"] == self.test_user_data["user_id"]
        assert payload["sub"] == self.test_user_data["sub"]
        assert payload["role"] == self.test_user_data["role"]
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload

    def test_create_access_token_with_custom_expiration(self):
        """Test access token creation with custom expiration"""
        custom_expire = timedelta(minutes=5)
        token = self.jwt_handler.create_access_token(
            data=self.test_user_data,
            expires_delta=custom_expire
        )
        
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        
        # Check expiration is approximately 5 minutes from now
        exp_time = datetime.fromtimestamp(payload["exp"])
        now = datetime.utcnow()
        time_diff = (exp_time - now).total_seconds()
        
        assert 290 < time_diff < 310  # Allow 10 seconds tolerance

    def test_create_refresh_token(self):
        """Test refresh token creation"""
        data = {"user_id": "test-user-123"}
        token = self.jwt_handler.create_refresh_token(data=data)
        
        assert isinstance(token, str)
        
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        assert payload["user_id"] == data["user_id"]
        assert payload["type"] == "refresh"
        
        # Check expiration is approximately 7 days from now
        exp_time = datetime.fromtimestamp(payload["exp"])
        now = datetime.utcnow()
        time_diff = (exp_time - now).total_seconds()
        
        expected_seconds = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600
        assert expected_seconds - 60 < time_diff < expected_seconds + 60

    def test_verify_token_valid(self):
        """Test verification of valid token"""
        token = self.jwt_handler.create_access_token(data=self.test_user_data)
        payload = self.jwt_handler.verify_token(token)
        
        assert payload is not None
        assert payload["user_id"] == self.test_user_data["user_id"]
        assert payload["sub"] == self.test_user_data["sub"]

    def test_verify_token_expired(self):
        """Test verification of expired token"""
        # Create token that expired 1 hour ago
        expired_delta = timedelta(hours=-1)
        token = self.jwt_handler.create_access_token(
            data=self.test_user_data,
            expires_delta=expired_delta
        )
        
        payload = self.jwt_handler.verify_token(token)
        assert payload is None

    def test_verify_token_invalid_signature(self):
        """Test verification of token with invalid signature"""
        token = self.jwt_handler.create_access_token(data=self.test_user_data)
        
        # Tamper with token
        tampered_token = token[:-10] + "invalidxx"
        
        payload = self.jwt_handler.verify_token(tampered_token)
        assert payload is None

    def test_verify_token_malformed(self):
        """Test verification of malformed token"""
        malformed_token = "not.a.valid.jwt.token"
        payload = self.jwt_handler.verify_token(malformed_token)
        assert payload is None

    def test_password_hashing(self):
        """Test password hashing"""
        password = "SuperSecretPassword123!"
        hashed = self.jwt_handler.get_password_hash(password)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password  # Should be hashed, not plain
        assert hashed.startswith("$2b$")  # Bcrypt prefix

    def test_password_verification_correct(self):
        """Test password verification with correct password"""
        password = "MyPassword123"
        hashed = self.jwt_handler.get_password_hash(password)
        
        is_valid = self.jwt_handler.verify_password(password, hashed)
        assert is_valid is True

    def test_password_verification_incorrect(self):
        """Test password verification with incorrect password"""
        correct_password = "CorrectPassword123"
        wrong_password = "WrongPassword456"
        hashed = self.jwt_handler.get_password_hash(correct_password)
        
        is_valid = self.jwt_handler.verify_password(wrong_password, hashed)
        assert is_valid is False

    def test_password_hashing_different_hashes(self):
        """Test that same password produces different hashes (salt)"""
        password = "SamePassword123"
        hash1 = self.jwt_handler.get_password_hash(password)
        hash2 = self.jwt_handler.get_password_hash(password)
        
        assert hash1 != hash2  # Different due to salt
        assert self.jwt_handler.verify_password(password, hash1)
        assert self.jwt_handler.verify_password(password, hash2)


class TestUtilityFunctions:
    """Test suite for utility wrapper functions"""

    def test_create_access_token_wrapper(self):
        """Test create_access_token utility function"""
        data = {"user_id": "123", "sub": "user"}
        token = create_access_token(data=data)
        
        assert isinstance(token, str)
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        assert payload["user_id"] == "123"

    def test_create_refresh_token_wrapper(self):
        """Test create_refresh_token utility function"""
        data = {"user_id": "456"}
        token = create_refresh_token(data=data)
        
        assert isinstance(token, str)
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        assert payload["type"] == "refresh"

    def test_verify_token_wrapper(self):
        """Test verify_token utility function"""
        data = {"user_id": "789", "sub": "test"}
        token = create_access_token(data=data)
        
        payload = verify_token(token)
        assert payload is not None
        assert payload["user_id"] == "789"

    def test_get_password_hash_wrapper(self):
        """Test get_password_hash utility function"""
        password = "TestPassword123"
        hashed = get_password_hash(password)
        
        assert isinstance(hashed, str)
        assert hashed.startswith("$2b$")

    def test_verify_password_wrapper(self):
        """Test verify_password utility function"""
        password = "MyTestPassword"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
        assert verify_password("WrongPassword", hashed) is False


class TestSecurityScenarios:
    """Test suite for security-specific scenarios"""

    def setup_method(self):
        """Setup for each test"""
        self.jwt_handler = JWTHandler()

    def test_token_type_enforcement(self):
        """Test that token types are correctly set"""
        access_token = self.jwt_handler.create_access_token(data={"user_id": "1"})
        refresh_token = self.jwt_handler.create_refresh_token(data={"user_id": "1"})
        
        access_payload = jwt.decode(access_token, settings.secret_key, algorithms=[ALGORITHM])
        refresh_payload = jwt.decode(refresh_token, settings.secret_key, algorithms=[ALGORITHM])
        
        assert access_payload["type"] == "access"
        assert refresh_payload["type"] == "refresh"

    def test_empty_password_handling(self):
        """Test handling of empty password"""
        empty_password = ""
        hashed = self.jwt_handler.get_password_hash(empty_password)
        
        # Should still hash it (not reject)
        assert isinstance(hashed, str)
        assert self.jwt_handler.verify_password(empty_password, hashed)

    def test_long_password_handling(self):
        """Test handling of very long password"""
        long_password = "a" * 1000
        hashed = self.jwt_handler.get_password_hash(long_password)
        
        assert isinstance(hashed, str)
        assert self.jwt_handler.verify_password(long_password, hashed)

    def test_special_characters_in_password(self):
        """Test password with special characters"""
        special_password = "P@ssw0rd!#$%^&*()_+-=[]{}|;:',.<>?/~`"
        hashed = self.jwt_handler.get_password_hash(special_password)
        
        assert self.jwt_handler.verify_password(special_password, hashed)

    def test_unicode_password(self):
        """Test password with unicode characters"""
        unicode_password = "密码123🔐"
        hashed = self.jwt_handler.get_password_hash(unicode_password)
        
        assert self.jwt_handler.verify_password(unicode_password, hashed)

    def test_token_with_special_payload(self):
        """Test token creation with special characters in payload"""
        special_data = {
            "user_id": "user@example.com",
            "sub": "user with spaces",
            "role": "ADMIN",
            "metadata": {"key": "value with 特殊 chars"}
        }
        
        token = self.jwt_handler.create_access_token(data=special_data)
        payload = self.jwt_handler.verify_token(token)
        
        assert payload is not None
        assert payload["user_id"] == special_data["user_id"]

    def test_verify_none_token(self):
        """Test verification of None token"""
        payload = self.jwt_handler.verify_token(None)  # type: ignore
        assert payload is None

    def test_verify_empty_string_token(self):
        """Test verification of empty string token"""
        payload = self.jwt_handler.verify_token("")
        assert payload is None


@pytest.mark.parametrize("password,should_be_strong", [
    ("weak", False),
    ("StrongP@ss123", True),
    ("12345678", False),
    ("", False),
    ("aaaaaaaa", False),
])
def test_password_strength_examples(password, should_be_strong):
    """Test various password examples (documentation purposes)"""
    # This is more of a documentation test
    # Actual password strength validation should be in registration logic
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)

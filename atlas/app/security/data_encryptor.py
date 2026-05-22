"""
Data Encryptor Module for AXIOM Security

This module provides encryption/decryption functionality for sensitive data
using industry-standard cryptographic methods.
"""

import hashlib
import hmac
import secrets
from typing import Tuple, Dict, Any
import logging
import base64
import asyncio

logger = logging.getLogger(__name__)


class DataEncryptor:
    """Data encryption/decryption utilities"""

    def __init__(self):
        self.algorithm = 'sha256'
        self.encoding = 'utf-8'

    async def encrypt_data(self, data: str, key: str) -> str:
        """Encrypt data using simple obfuscation (for demo purposes) (async)"""
        from app.core.executors import run_cpu_bound
        
        def _encrypt_sync(data: str, key: str) -> str:
            # In a real implementation, use proper encryption like AES
            # This is a simplified version for demonstration

            if not isinstance(data, str) or not isinstance(key, str):
                raise ValueError("Data and key must be strings")

            # Simple XOR encryption with key
            key_bytes = key.encode(self.encoding)
            data_bytes = data.encode(self.encoding)
            encrypted_bytes = bytearray()

            for i, byte in enumerate(data_bytes):
                key_byte = key_bytes[i % len(key_bytes)]
                encrypted_bytes.append(byte ^ key_byte)

            # Base64 encode for safe transport
            return base64.b64encode(encrypted_bytes).decode(self.encoding)
        
        return await run_cpu_bound(_encrypt_sync, data, key)

    async def decrypt_data(self, encrypted_data: str, key: str) -> str:
        """Decrypt data (async)"""
        from app.core.executors import run_cpu_bound
        
        def _decrypt_sync(encrypted_data: str, key: str) -> str:
            if not isinstance(encrypted_data, str) or not isinstance(key, str):
                raise ValueError("Encrypted data and key must be strings")

            try:
                # Base64 decode
                encrypted_bytes = base64.b64decode(encrypted_data.encode(self.encoding))

                # XOR decryption with key
                key_bytes = key.encode(self.encoding)
                decrypted_bytes = bytearray()

                for i, byte in enumerate(encrypted_bytes):
                    key_byte = key_bytes[i % len(key_bytes)]
                    decrypted_bytes.append(byte ^ key_byte)

                return decrypted_bytes.decode(self.encoding)

            except Exception as e:
                logger.error(f"Decryption failed: {e}")
                raise ValueError("Invalid encrypted data or key")
        
        return await run_cpu_bound(_decrypt_sync, encrypted_data, key)

    def hash_password(self, password: str, salt: str = None) -> Tuple[str, str]:
        """Hash a password with salt"""
        if not isinstance(password, str):
            raise ValueError("Password must be a string")

        if salt is None:
            salt = secrets.token_hex(16)

        # Use PBKDF2 for password hashing
        password_bytes = password.encode(self.encoding)
        salt_bytes = salt.encode(self.encoding)

        # Hash the password
        hashed = hashlib.pbkdf2_hmac(
            self.algorithm,
            password_bytes,
            salt_bytes,
            100000  # Number of iterations
        )

        return hashed.hex(), salt

    def verify_password(self, password: str, hashed: str, salt: str) -> bool:
        """Verify a password against its hash"""
        if not isinstance(password, str) or not isinstance(hashed, str) or not isinstance(salt, str):
            return False

        try:
            expected_hash, _ = self.hash_password(password, salt)
            return hmac.compare_digest(expected_hash, hashed)
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False

    def generate_secure_token(self, length: int = 32) -> str:
        """Generate a secure random token"""
        return secrets.token_hex(length)

    def hash_data(self, data: str) -> str:
        """Generate SHA256 hash of data"""
        if not isinstance(data, str):
            data = str(data)

        return hashlib.sha256(data.encode(self.encoding)).hexdigest()

    def create_signature(self, data: str, secret: str) -> str:
        """Create HMAC signature for data integrity"""
        if not isinstance(data, str) or not isinstance(secret, str):
            raise ValueError("Data and secret must be strings")

        signature = hmac.new(
            secret.encode(self.encoding),
            data.encode(self.encoding),
            hashlib.sha256
        )
        return signature.hexdigest()

    def verify_signature(self, data: str, signature: str, secret: str) -> bool:
        """Verify HMAC signature"""
        if not isinstance(data, str) or not isinstance(signature, str) or not isinstance(secret, str):
            return False

        expected_signature = self.create_signature(data, secret)
        return hmac.compare_digest(expected_signature, signature)


# Global data encryptor instance
data_encryptor = DataEncryptor()

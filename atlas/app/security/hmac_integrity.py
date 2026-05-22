"""HMAC Integrity Module

Añade firmas HMAC opcionales para artefactos usando clave de entorno.
Si INTEGRITY_HMAC_KEY está definida, los artefactos se firman automáticamente
y la verificación incluye validación HMAC.
"""
import hmac
import hashlib
import os
from typing import Optional
from app.config import settings

def get_hmac_key() -> Optional[str]:
    """Get HMAC key from environment"""
    return settings.INTEGRITY_HMAC_KEY

def compute_hmac(data_hash: str, metadata_hash: str, key: str) -> str:
    """Compute HMAC signature for artifact"""
    payload = f"{data_hash}:{metadata_hash}"
    return hmac.new(key.encode(), payload.encode(), hashlib.sha256).hexdigest()

def verify_hmac(data_hash: str, metadata_hash: str, signature: str, key: str) -> bool:
    """Verify HMAC signature"""
    expected = compute_hmac(data_hash, metadata_hash, key)
    return hmac.compare_digest(expected, signature)
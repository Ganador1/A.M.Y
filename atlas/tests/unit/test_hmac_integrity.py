import os
from app.hmac_integrity import verify_hmac
from app.integrity_core import integrity_core


def test_hmac_integration_without_key():
    """Test that HMAC is optional when no key is set"""
    # Ensure no key
    if "INTEGRITY_HMAC_KEY" in os.environ:
        del os.environ["INTEGRITY_HMAC_KEY"]
    
    record = integrity_core.register_artifact({"test": "data"})
    assert record.hmac_signature is None


def test_hmac_integration_with_key(monkeypatch):
    """Test HMAC signature and verification with key"""
    test_key = "test-hmac-key-12345"
    monkeypatch.setenv("INTEGRITY_HMAC_KEY", test_key)
    
    # Register artifact with HMAC
    record = integrity_core.register_artifact({"test": "data"}, artifact_type="test")
    assert record.hmac_signature is not None
    
    # Verify HMAC
    assert verify_hmac(record.data_hash, record.metadata_hash, record.hmac_signature, test_key)
    
    # Test verification through integrity_core
    import asyncio
    status = asyncio.run(integrity_core.verify_artifact(record.artifact_id))
    assert status["hmac_valid"] is True
    assert status["integrity_ok"] is True


def test_hmac_tamper_detection(monkeypatch):
    """Test that HMAC detects tampering"""
    test_key = "test-hmac-key-tamper"
    monkeypatch.setenv("INTEGRITY_HMAC_KEY", test_key)
    
    record = integrity_core.register_artifact({"test": "data"})
    
    # Tamper with signature
    record.hmac_signature = "invalid_signature"
    
    import asyncio
    status = asyncio.run(integrity_core.verify_artifact(record.artifact_id))
    assert status["hmac_valid"] is False
    assert status["integrity_ok"] is False

#!/usr/bin/env python3
"""
Unit tests for AXIOM Advanced Security System
"""

import pytest
from datetime import datetime
from app.security import (
    DataEncryption, InputValidation, SecurityAuditor,
    AdvancedRateLimiter, SecurityEvent
)


class TestDataEncryption:
    """Test data encryption utilities"""

    def test_generate_key(self):
        """Test key generation"""
        key = DataEncryption.generate_key()
        assert len(key) == 64  # 32 bytes hex encoded
        assert key.isalnum()

    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "test_password_123"

        # Hash password
        hashed, salt = DataEncryption.hash_password(password)
        assert len(hashed) == 64  # SHA-256 hex
        assert len(salt) == 32   # 16 bytes hex

        # Verify password
        assert DataEncryption.verify_password(password, hashed, salt)
        assert not DataEncryption.verify_password("wrong_password", hashed, salt)

    def test_data_encryption(self):
        """Test data encryption/decryption"""
        key = DataEncryption.generate_key()
        data = "sensitive_data_123"

        # Encrypt
        encrypted = DataEncryption.encrypt_data(data, key)
        assert encrypted != data

        # Decrypt
        decrypted = DataEncryption.decrypt_data(encrypted, key)
        assert decrypted == data

        # Wrong key should fail
        wrong_key = DataEncryption.generate_key()
        with pytest.raises(Exception):
            DataEncryption.decrypt_data(encrypted, wrong_key)


class TestInputValidation:
    """Test input validation and sanitization"""

    def test_sanitize_input(self):
        """Test input sanitization"""
        # XSS test
        malicious = "<script>alert('xss')</script><img src=x onerror=alert(1)>"
        sanitized = InputValidation.sanitize_input(malicious)
        assert "<script>" not in sanitized
        assert "javascript:" not in sanitized
        assert "onerror" not in sanitized

    def test_sql_injection_detection(self):
        """Test SQL injection detection"""
        safe_query = "SELECT * FROM users WHERE id = 1"
        assert InputValidation.validate_sql_input(safe_query)

        malicious_queries = [
            "SELECT * FROM users WHERE id = 1; DROP TABLE users;",
            "SELECT * FROM users -- comment",
            "SELECT * FROM users UNION SELECT password FROM admin"
        ]

        for query in malicious_queries:
            assert not InputValidation.validate_sql_input(query)

    def test_math_expression_validation(self):
        """Test mathematical expression validation"""
        safe_expr = "2*x + 3*sin(y) - sqrt(z)"
        assert InputValidation.validate_math_expression(safe_expr)

        dangerous_expr = "2*x + __import__('os').system('rm -rf /')"
        assert not InputValidation.validate_math_expression(dangerous_expr)

        invalid_chars = "2*x + y@z"  # @ is not allowed
        assert not InputValidation.validate_math_expression(invalid_chars)


class TestSecurityAuditor:
    """Test security auditing system"""

    def test_log_security_event(self):
        """Test security event logging"""
        auditor = SecurityAuditor()

        event = SecurityEvent(
            event_type="test_event",
            severity="INFO",
            source_ip="192.168.1.1",
            user_agent="test_agent",
            endpoint="/api/test",
            user_id="user123",
            details={"test": "data"},
            timestamp=datetime.now()
        )

        auditor.log_security_event(event)
        assert len(auditor.events) == 1
        assert auditor.events[0].event_type == "test_event"

    def test_security_report(self):
        """Test security report generation"""
        auditor = SecurityAuditor()

        # Add some test events
        for i in range(3):
            event = SecurityEvent(
                event_type="test_event",
                severity="INFO",
                source_ip=f"192.168.1.{i}",
                user_agent="test_agent",
                endpoint="/api/test",
                user_id=f"user{i}",
                details={},
                timestamp=datetime.now()
            )
            auditor.log_security_event(event)

        report = auditor.get_security_report()
        assert report["total_events"] == 3
        assert len(report["recent_events"]) == 3


class TestAdvancedRateLimiter:
    """Test advanced rate limiting"""

    def test_rate_limit_rules(self):
        """Test rate limiting rules"""
        limiter = AdvancedRateLimiter()

        # Test rule matching
        rule = limiter._find_matching_rule("/api/arithmetic/calculate")
        assert rule is not None
        assert rule.max_requests == 100

        # Test pattern matching
        assert limiter._matches_pattern("/api/arithmetic/calculate", "/api/arithmetic/*")
        assert not limiter._matches_pattern("/api/other/endpoint", "/api/arithmetic/*")

    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        limiter = AdvancedRateLimiter()

        client_ip = "192.168.1.100"
        endpoint = "/api/arithmetic/calculate"

        # Should allow initial requests
        for i in range(10):
            assert limiter.is_allowed(endpoint, client_ip)

        # Check status
        status = limiter.get_rate_limit_status(client_ip)
        assert not status["blocked"]
        assert status["request_count"] == 10


if __name__ == "__main__":
    pytest.main([__file__])

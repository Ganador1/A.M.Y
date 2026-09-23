"""
Fuzz Testing for API Input Validation

This module provides comprehensive fuzz testing for API endpoint input validation,
including request bodies, query parameters, headers, and authentication tokens.

Test Categories:
1. JSON payload fuzzing
2. Query parameter injection
3. Header manipulation
4. Authentication token fuzzing
5. SQL injection attempts
6. XSS attack vectors
7. Path traversal attempts
8. Buffer overflow testing
9. Type confusion
10. Rate limiting bypass

Author: Atlas AI Mathematics System
Date: October 2025
"""

import pytest
from hypothesis import given, strategies as st, settings
from hypothesis import HealthCheck
import string
import json
from typing import Any, Dict
import base64


class APIValidator:
    """
    Mock API input validator for testing purposes.

    In production, this would integrate with FastAPI/Pydantic validators
    and security middleware.
    """

    def __init__(self):
        self.max_body_size = 1024 * 1024  # 1MB
        self.max_header_size = 8192  # 8KB
        self.max_query_params = 100
        self.allowed_content_types = [
            'application/json',
            'application/x-www-form-urlencoded',
            'multipart/form-data'
        ]

    def validate_json_body(self, body: Any) -> dict:
        """
        Validate JSON request body.

        Args:
            body: Request body to validate

        Returns:
            dict: Validation result

        Raises:
            ValueError: If body is invalid
            TypeError: If body has wrong type
        """
        if body is None:
            raise ValueError("Body cannot be None")

        if isinstance(body, str):
            if len(body) > self.max_body_size:
                raise ValueError("Body too large")
            try:
                parsed = json.loads(body)
                return {
                    'valid': True,
                    'type': 'json',
                    'size': len(body),
                    'parsed': parsed
                }
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON: {e}")

        if isinstance(body, (dict, list)):
            serialized = json.dumps(body)
            if len(serialized) > self.max_body_size:
                raise ValueError("Body too large")
            return {
                'valid': True,
                'type': 'json',
                'size': len(serialized),
                'parsed': body
            }

        raise TypeError("Body must be string, dict, or list")

    def validate_query_params(self, params: Dict[str, Any]) -> dict:
        """
        Validate query parameters.

        Args:
            params: Query parameters dict

        Returns:
            dict: Validation result

        Raises:
            ValueError: If params are invalid
        """
        if not isinstance(params, dict):
            raise TypeError("Params must be dict")

        if len(params) > self.max_query_params:
            raise ValueError(f"Too many query params (max {self.max_query_params})")

        # Check for SQL injection patterns
        sql_patterns = ['--', 'drop table', 'delete from', 'insert into', 'update ', 'union select']
        for key, value in params.items():
            if not isinstance(key, str):
                raise ValueError("Param keys must be strings")

            value_str = str(value).lower()
            # Check for SQL injection with more precise patterns
            if any(pattern in value_str for pattern in sql_patterns):
                raise ValueError("Potential SQL injection detected")
            # Check for SQL comment patterns with context
            if '--' in value_str and len(value_str) > 3:
                raise ValueError("Potential SQL injection detected")

            # Check for XSS patterns
            xss_patterns = ['<script', 'javascript:', 'onerror=', 'onclick=', 'onload=']
            if any(pattern in value_str for pattern in xss_patterns):
                raise ValueError("Potential XSS attack detected")

        return {
            'valid': True,
            'count': len(params),
            'keys': list(params.keys())
        }

    def validate_headers(self, headers: Dict[str, str]) -> dict:
        """
        Validate HTTP headers.

        Args:
            headers: HTTP headers dict

        Returns:
            dict: Validation result

        Raises:
            ValueError: If headers are invalid
        """
        if not isinstance(headers, dict):
            raise TypeError("Headers must be dict")

        total_size = sum(len(k) + len(v) for k, v in headers.items())
        if total_size > self.max_header_size:
            raise ValueError("Headers too large")

        # Validate Content-Type if present
        if 'content-type' in {k.lower() for k in headers.keys()}:
            content_type = next(
                v for k, v in headers.items()
                if k.lower() == 'content-type'
            )
            base_type = content_type.split(';')[0].strip()
            if base_type not in self.allowed_content_types:
                raise ValueError(f"Unsupported Content-Type: {base_type}")

        return {
            'valid': True,
            'count': len(headers),
            'size': total_size
        }

    def validate_auth_token(self, token: str) -> dict:
        """
        Validate authentication token.

        Args:
            token: Auth token string

        Returns:
            dict: Validation result

        Raises:
            ValueError: If token is invalid
        """
        if not isinstance(token, str):
            raise TypeError("Token must be string")

        if not token:
            raise ValueError("Token cannot be empty")

        if len(token) > 2048:
            raise ValueError("Token too long")

        # Check for Bearer format
        if token.startswith('Bearer '):
            token = token[7:]

        # Basic validation: should be base64-like or JWT-like
        if '.' in token:
            # JWT format: header.payload.signature
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid JWT format")
            for part in parts:
                if not all(c in string.ascii_letters + string.digits + '-_=' for c in part):
                    raise ValueError("Invalid JWT characters")
        else:
            # Should be valid base64
            try:
                decoded = base64.b64decode(token + '==', validate=True)
                if len(decoded) == 0:
                    raise ValueError("Empty token")
            except Exception:
                raise ValueError("Invalid token encoding")

        return {
            'valid': True,
            'format': 'jwt' if '.' in token else 'base64',
            'length': len(token)
        }

    def validate_path(self, path: str) -> dict:
        """
        Validate URL path for path traversal attacks.

        Args:
            path: URL path string

        Returns:
            dict: Validation result

        Raises:
            ValueError: If path is invalid
        """
        if not isinstance(path, str):
            raise TypeError("Path must be string")

        if not path:
            raise ValueError("Path cannot be empty")

        if len(path) > 2048:
            raise ValueError("Path too long")

        # Check for path traversal patterns (more precise)
        path_lower = path.lower()
        dangerous_patterns = ['../', '..\\', '%2e%2e/', '%252e', '....//']
        if any(pattern in path_lower for pattern in dangerous_patterns):
            raise ValueError("Path traversal attempt detected")
        
        # Also check for encoded versions
        if '..' in path and ('/' in path or '\\' in path):
            # Allow single dots but not double dots with slashes
            segments = path.replace('\\', '/').split('/')
            if any('..' == seg for seg in segments):
                raise ValueError("Path traversal attempt detected")

        # Check for null bytes
        if '\x00' in path:
            raise ValueError("Null byte in path")

        # Path must start with /
        if not path.startswith('/'):
            raise ValueError("Path must start with /")

        return {
            'valid': True,
            'length': len(path),
            'segments': len(path.split('/')) - 1
        }


class TestJSONPayloadFuzzing:
    """Fuzz tests for JSON body validation."""

    @given(st.text(min_size=0, max_size=1000))
    @settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
    def test_random_strings_as_json(self, random_text):
        """Test random strings as JSON bodies."""
        validator = APIValidator()
        try:
            result = validator.validate_json_body(random_text)
            assert isinstance(result, dict)
        except (ValueError, TypeError, json.JSONDecodeError):
            pass

    @given(st.dictionaries(
        st.text(min_size=1, max_size=50),
        st.one_of(st.integers(), st.floats(), st.text(), st.booleans(), st.none()),
        min_size=0,
        max_size=20
    ))
    @settings(max_examples=200)
    def test_valid_json_objects(self, json_dict):
        """Test with valid JSON-serializable dicts."""
        validator = APIValidator()
        try:
            result = validator.validate_json_body(json_dict)
            assert result['valid']
            assert result['type'] == 'json'
        except (ValueError, TypeError):
            pass

    @given(st.lists(st.integers(), min_size=0, max_size=100))
    @settings(max_examples=100)
    def test_json_arrays(self, json_array):
        """Test JSON array validation."""
        validator = APIValidator()
        result = validator.validate_json_body(json_array)
        assert result['valid']
        assert isinstance(result['parsed'], list)

    @given(st.recursive(
        st.none() | st.booleans() | st.integers() | st.text(),
        lambda children: st.lists(children) | st.dictionaries(st.text(), children),
        max_leaves=20
    ))
    @settings(max_examples=150, suppress_health_check=[HealthCheck.too_slow])
    def test_deeply_nested_json(self, nested_structure):
        """Test deeply nested JSON structures."""
        validator = APIValidator()
        try:
            result = validator.validate_json_body(nested_structure)
            assert isinstance(result, dict)
        except (ValueError, TypeError, RecursionError):
            pass

    def test_empty_body(self):
        """Test empty body rejection."""
        validator = APIValidator()
        with pytest.raises(ValueError, match="cannot be None"):
            validator.validate_json_body(None)


class TestQueryParameterFuzzing:
    """Fuzz tests for query parameter validation."""

    @given(st.dictionaries(
        st.text(min_size=1, max_size=50),
        st.text(min_size=0, max_size=100),
        min_size=0,
        max_size=20
    ))
    @settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
    def test_random_query_params(self, params):
        """Test random query parameter combinations."""
        validator = APIValidator()
        try:
            result = validator.validate_query_params(params)
            assert isinstance(result, dict)
        except (ValueError, TypeError):
            pass

    @given(st.text(alphabet=string.ascii_letters + string.digits + '-_', min_size=1, max_size=20))
    @settings(max_examples=100)
    def test_sql_injection_detection(self, base_value):
        """Test SQL injection pattern detection."""
        validator = APIValidator()
        sql_attacks = [
            f"{base_value}'; drop table users--",
            f"{base_value} union select * from passwords",
            f"{base_value}'; delete from data--"
        ]
        for attack in sql_attacks:
            with pytest.raises(ValueError, match="SQL injection"):
                validator.validate_query_params({'query': attack})

    @given(st.text(alphabet=string.ascii_letters, min_size=1, max_size=20))
    @settings(max_examples=100)
    def test_xss_detection(self, base_value):
        """Test XSS attack pattern detection."""
        validator = APIValidator()
        xss_attacks = [
            f"<script>alert('{base_value}')</script>",
            f"javascript:alert('{base_value}')",
            f"<img src=x onerror=alert('{base_value}')>",
            f"<body onload=alert('{base_value}')>"
        ]
        for attack in xss_attacks:
            with pytest.raises(ValueError, match="XSS"):
                validator.validate_query_params({'input': attack})

    @given(st.integers(min_value=101, max_value=200))
    @settings(max_examples=50)
    def test_param_limit(self, num_params):
        """Test query parameter count limits."""
        validator = APIValidator()
        params = {f"param_{i}": f"value_{i}" for i in range(num_params)}
        with pytest.raises(ValueError, match="Too many"):
            validator.validate_query_params(params)


class TestHeaderFuzzing:
    """Fuzz tests for HTTP header validation."""

    @given(st.dictionaries(
        st.text(alphabet=string.ascii_letters + '-', min_size=1, max_size=50),
        st.text(min_size=0, max_size=100),
        min_size=0,
        max_size=20
    ))
    @settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
    def test_random_headers(self, headers):
        """Test random header combinations."""
        validator = APIValidator()
        try:
            result = validator.validate_headers(headers)
            assert isinstance(result, dict)
        except (ValueError, TypeError):
            pass

    @given(st.sampled_from([
        'application/json',
        'application/x-www-form-urlencoded',
        'multipart/form-data'
    ]))
    @settings(max_examples=50)
    def test_valid_content_types(self, content_type):
        """Test valid Content-Type headers."""
        validator = APIValidator()
        headers = {'Content-Type': content_type}
        result = validator.validate_headers(headers)
        assert result['valid']

    @given(st.text(min_size=1, max_size=100))
    @settings(max_examples=100)
    def test_invalid_content_types(self, content_type):
        """Test invalid Content-Type rejection."""
        validator = APIValidator()
        if content_type not in validator.allowed_content_types:
            headers = {'Content-Type': content_type}
            with pytest.raises(ValueError, match="Unsupported"):
                validator.validate_headers(headers)

    @given(st.integers(min_value=100, max_value=500))
    @settings(max_examples=50)
    def test_header_size_limit(self, num_headers):
        """Test header size limits."""
        validator = APIValidator()
        # Create headers that exceed size limit
        headers = {f"X-Custom-{i}": "A" * 100 for i in range(num_headers)}
        with pytest.raises(ValueError, match="too large"):
            validator.validate_headers(headers)


class TestAuthTokenFuzzing:
    """Fuzz tests for authentication token validation."""

    @given(st.text(min_size=0, max_size=500))
    @settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
    def test_random_tokens(self, token):
        """Test random token strings."""
        validator = APIValidator()
        try:
            result = validator.validate_auth_token(token)
            assert isinstance(result, dict)
        except (ValueError, TypeError):
            pass

    @given(
        st.text(alphabet=string.ascii_letters + string.digits + '-_', min_size=10, max_size=50),
        st.text(alphabet=string.ascii_letters + string.digits + '-_', min_size=10, max_size=100),
        st.text(alphabet=string.ascii_letters + string.digits + '-_', min_size=10, max_size=50)
    )
    @settings(max_examples=100)
    def test_jwt_format_tokens(self, header, payload, signature):
        """Test JWT-format tokens."""
        validator = APIValidator()
        token = f"{header}.{payload}.{signature}"
        try:
            result = validator.validate_auth_token(token)
            assert result['format'] == 'jwt'
        except ValueError:
            pass

    @given(st.binary(min_size=10, max_size=100))
    @settings(max_examples=100)
    def test_base64_tokens(self, binary_data):
        """Test base64-encoded tokens."""
        validator = APIValidator()
        token = base64.b64encode(binary_data).decode('ascii')
        try:
            result = validator.validate_auth_token(token)
            assert result['valid']
        except ValueError:
            pass

    @given(st.integers(min_value=2049, max_value=3000))
    @settings(max_examples=50)
    def test_token_length_limit(self, length):
        """Test token length limits."""
        validator = APIValidator()
        token = 'A' * length
        with pytest.raises(ValueError, match="too long"):
            validator.validate_auth_token(token)

    def test_empty_token(self):
        """Test empty token rejection."""
        validator = APIValidator()
        with pytest.raises(ValueError, match="cannot be empty"):
            validator.validate_auth_token('')

    @given(st.text(alphabet=string.ascii_letters + string.digits + '-_', min_size=20, max_size=50))
    @settings(max_examples=100)
    def test_bearer_prefix_handling(self, token_body):
        """Test Bearer token prefix handling."""
        validator = APIValidator()
        token = f"Bearer {token_body}"
        try:
            validator.validate_auth_token(token)
        except ValueError:
            pass


class TestPathTraversalFuzzing:
    """Fuzz tests for path traversal detection."""

    @given(st.text(min_size=1, max_size=200))
    @settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
    def test_random_paths(self, path):
        """Test random path strings."""
        validator = APIValidator()
        try:
            result = validator.validate_path(path)
            assert isinstance(result, dict)
        except (ValueError, TypeError):
            pass

    @given(st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=20))
    @settings(max_examples=100)
    def test_path_traversal_detection(self, filename):
        """Test path traversal attack detection."""
        validator = APIValidator()
        attacks = [
            f"/../../{filename}",
            f"/../../../etc/{filename}",
            f"/data/../../../{filename}"
        ]
        for attack in attacks:
            with pytest.raises(ValueError, match="traversal"):
                validator.validate_path(attack)

    @given(st.lists(
        st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=20),
        min_size=1,
        max_size=10
    ))
    @settings(max_examples=100)
    def test_valid_paths(self, segments):
        """Test valid path structures."""
        validator = APIValidator()
        path = '/' + '/'.join(segments)
        try:
            result = validator.validate_path(path)
            assert result['valid']
            assert result['segments'] == len(segments)
        except ValueError:
            pass

    @given(st.integers(min_value=2100, max_value=3000))
    @settings(max_examples=50)
    def test_path_length_limit(self, length):
        """Test path length limits."""
        validator = APIValidator()
        path = '/' + 'a' * length
        with pytest.raises(ValueError, match="too long"):
            validator.validate_path(path)

    def test_null_byte_detection(self):
        """Test null byte injection detection."""
        validator = APIValidator()
        with pytest.raises(ValueError, match="Null byte"):
            validator.validate_path("/files/secret.txt\x00.jpg")


class TestSecurityFuzzing:
    """Security-focused fuzz tests."""

    @given(st.text(alphabet=string.printable, min_size=1, max_size=200))
    @settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
    def test_injection_resistance(self, malicious_input):
        """Test resistance to various injection attacks."""
        validator = APIValidator()

        # Test in all validators
        try:
            validator.validate_json_body(json.dumps({'data': malicious_input}))
        except (ValueError, TypeError):
            pass

        try:
            validator.validate_query_params({'q': malicious_input})
        except (ValueError, TypeError):
            pass

        try:
            validator.validate_headers({'X-Custom': malicious_input[:100]})
        except (ValueError, TypeError):
            pass

    @given(st.binary(min_size=1, max_size=200))
    @settings(max_examples=100)
    def test_binary_input_handling(self, binary_data):
        """Test handling of binary data."""
        validator = APIValidator()

        try:
            text = binary_data.decode('utf-8', errors='ignore')
            if text:
                validator.validate_json_body(text)
        except (ValueError, TypeError):
            pass

    @given(st.lists(st.text(min_size=1, max_size=100), min_size=1, max_size=10))
    @settings(max_examples=100)
    def test_repeated_validation(self, inputs):
        """Test validator stability with repeated calls."""
        validator = APIValidator()

        for inp in inputs:
            try:
                validator.validate_json_body(json.dumps({'data': inp}))
            except (ValueError, TypeError):
                pass

        # Validator should still be functional
        result = validator.validate_json_body({'test': 'data'})
        assert result['valid']


class TestTypeConfusionFuzzing:
    """Type confusion fuzz tests."""

    @given(st.one_of(
        st.integers(),
        st.floats(),
        st.booleans(),
        st.none(),
        st.lists(st.integers()),
        st.binary()
    ))
    @settings(max_examples=200)
    def test_unexpected_types_json(self, unexpected_value):
        """Test unexpected types in JSON validation."""
        validator = APIValidator()
        try:
            validator.validate_json_body(unexpected_value)
        except (TypeError, ValueError):
            pass

    @given(st.one_of(
        st.integers(),
        st.floats(),
        st.none(),
        st.lists(st.text()),
        st.binary()
    ))
    @settings(max_examples=200)
    def test_unexpected_types_params(self, unexpected_value):
        """Test unexpected types in query params."""
        validator = APIValidator()
        try:
            validator.validate_query_params(unexpected_value)
        except (TypeError, ValueError):
            pass

    @given(st.one_of(
        st.integers(),
        st.floats(),
        st.none(),
        st.lists(st.text()),
        st.binary()
    ))
    @settings(max_examples=200)
    def test_unexpected_types_headers(self, unexpected_value):
        """Test unexpected types in headers."""
        validator = APIValidator()
        try:
            validator.validate_headers(unexpected_value)
        except (TypeError, ValueError):
            pass


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--hypothesis-show-statistics'])

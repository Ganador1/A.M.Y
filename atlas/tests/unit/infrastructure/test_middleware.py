#!/usr/bin/env python3
"""
Unit tests for middleware components
"""

import pytest
from unittest.mock import Mock, AsyncMock
from starlette.responses import Response
from starlette.requests import Request
from starlette.testclient import TestClient

from app.middleware import (
    CompressionMiddleware,
    CircuitBreakerMiddleware,
    CacheMiddleware,
    ErrorHandlingMiddleware,
    SecurityHeadersMiddleware
)


class TestCompressionMiddleware:
    """Test cases for CompressionMiddleware"""

    @pytest.mark.asyncio
    async def test_compression_large_response(self):
        """Test compression of large JSON responses"""
        middleware = CompressionMiddleware(Mock())

        # Create mock request with gzip support
        request = Mock()
        request.headers = {"Accept-Encoding": "gzip"}

        # Create mock response with large body
        response = Response(content='{"data": "' + "x" * 2000 + '"}')
        response.headers["content-type"] = "application/json"

        # Mock call_next
        call_next = AsyncMock(return_value=response)

        result = await middleware.dispatch(request, call_next)

        # Should be compressed
        assert result.headers.get("Content-Encoding") == "gzip"
        assert "Content-Length" in result.headers

    @pytest.mark.asyncio
    async def test_no_compression_small_response(self):
        """Test no compression for small responses"""
        middleware = CompressionMiddleware(Mock())

        request = Mock()
        request.headers = {"Accept-Encoding": "gzip"}

        # Small response
        response = Response(content='{"small": "data"}')
        response.headers["content-type"] = "application/json"

        call_next = AsyncMock(return_value=response)

        result = await middleware.dispatch(request, call_next)

        # Should not be compressed
        assert "Content-Encoding" not in result.headers

    @pytest.mark.asyncio
    async def test_no_compression_non_json(self):
        """Test no compression for non-JSON responses"""
        middleware = CompressionMiddleware(Mock())

        request = Mock()
        request.headers = {"Accept-Encoding": "gzip"}

        response = Response(content="<html></html>")
        response.headers["content-type"] = "text/html"

        call_next = AsyncMock(return_value=response)

        result = await middleware.dispatch(request, call_next)

        # Should not be compressed
        assert "Content-Encoding" not in result.headers


class TestCircuitBreakerMiddleware:
    """Test cases for CircuitBreakerMiddleware"""

    @pytest.mark.asyncio
    async def test_circuit_closed_success(self):
        """Test circuit breaker allows requests when closed and successful"""
        middleware = CircuitBreakerMiddleware(Mock())

        request = Mock()
        response = Response(content="success")

        call_next = AsyncMock(return_value=response)

        result = await middleware.dispatch(request, call_next)

        assert result == response
        assert middleware.state == "CLOSED"
        assert middleware.failure_count == 0

    @pytest.mark.asyncio
    async def test_circuit_opens_after_failures(self):
        """Test circuit breaker opens after consecutive failures"""
        middleware = CircuitBreakerMiddleware(Mock(), failure_threshold=2)

        request = Mock()
        call_next = AsyncMock(side_effect=Exception("Service error"))

        # First failure
        with pytest.raises(Exception):
            await middleware.dispatch(request, call_next)

        # Second failure - should open circuit
        with pytest.raises(Exception):
            await middleware.dispatch(request, call_next)

        assert middleware.state == "OPEN"
        assert middleware.failure_count == 2

    @pytest.mark.asyncio
    async def test_circuit_half_open_recovery(self):
        """Test circuit breaker recovery in half-open state"""
        middleware = CircuitBreakerMiddleware(Mock(), failure_threshold=1, recovery_timeout=1)

        # Force circuit open
        middleware.state = "OPEN"
        middleware.failure_count = 1

        request = Mock()
        response = Response(content="recovered")
        call_next = AsyncMock(return_value=response)

        # Should allow request and close circuit on success
        result = await middleware.dispatch(request, call_next)

        assert result == response
        assert middleware.state == "CLOSED"
        assert middleware.failure_count == 0


class TestCacheMiddleware:
    """Test cases for CacheMiddleware"""

    @pytest.mark.asyncio
    async def test_cache_hit(self):
        """Test cache returns cached response"""
        middleware = CacheMiddleware(Mock())

        request = Mock()
        request.method = "GET"
        request.url.path = "/test"
        request.url.query = ""

        # First request - should cache
        response = Response(content='{"cached": true}')
        call_next = AsyncMock(return_value=response)

        result1 = await middleware.dispatch(request, call_next)
        assert result1.status_code == 200  # Basic validation

        # Second request - should return cached
        result2 = await middleware.dispatch(request, call_next)

        # Should have same content (cached)
        assert result2 is not None  # Ensure result2 is assigned
        assert result2.status_code == response.status_code
        assert result2.body == response.body
        # call_next should only be called once
        assert call_next.call_count == 1

    @pytest.mark.asyncio
    async def test_no_cache_post_requests(self):
        """Test POST requests are not cached"""
        middleware = CacheMiddleware(Mock())

        request = Mock()
        request.method = "POST"
        request.url.path = "/test"

        response = Response(content='{"data": "test"}')
        call_next = AsyncMock(return_value=response)

        result1 = await middleware.dispatch(request, call_next)
        result2 = await middleware.dispatch(request, call_next)

        # Both should call next middleware
        assert call_next.call_count == 2

    @pytest.mark.asyncio
    async def test_cache_expiration(self):
        """Test cache expiration"""
        middleware = CacheMiddleware(Mock(), cache_ttl=0)  # Immediate expiration

        request = Mock()
        request.method = "GET"
        request.url.path = "/test"

        response = Response(content='{"data": "test"}')
        call_next = AsyncMock(return_value=response)

        # First request
        await middleware.dispatch(request, call_next)

        # Second request - should not be cached due to TTL=0
        await middleware.dispatch(request, call_next)

        assert call_next.call_count == 2


class TestSecurityHeadersMiddleware:
    """Test cases for SecurityHeadersMiddleware"""

    @pytest.mark.asyncio
    async def test_security_headers_added(self):
        """Test security headers are added to response"""
        middleware = SecurityHeadersMiddleware(Mock())

        request = Mock()
        response = Response(content="test")

        call_next = AsyncMock(return_value=response)

        result = await middleware.dispatch(request, call_next)

        # Check security headers are present
        assert result.headers["X-Content-Type-Options"] == "nosniff"
        assert result.headers["X-Frame-Options"] == "DENY"
        assert result.headers["X-XSS-Protection"] == "1; mode=block"
        assert "Strict-Transport-Security" in result.headers
        assert result.headers["Content-Security-Policy"] == "default-src 'self'"


class TestErrorHandlingMiddleware:
    """Test cases for ErrorHandlingMiddleware"""

    @pytest.mark.asyncio
    async def test_http_exception_handling(self):
        """Test HTTP exceptions are handled properly"""
        from fastapi import HTTPException
        middleware = ErrorHandlingMiddleware(Mock())

        request = Mock()
        call_next = AsyncMock(side_effect=HTTPException(status_code=404, detail="Not found"))

        result = await middleware.dispatch(request, call_next)

        assert result.status_code == 404
        response_data = result.body.decode()
        assert "Not found" in response_data

    @pytest.mark.asyncio
    async def test_value_error_handling(self):
        """Test ValueError exceptions are handled properly"""
        middleware = ErrorHandlingMiddleware(Mock())

        request = Mock()
        call_next = AsyncMock(side_effect=ValueError("Invalid input"))

        result = await middleware.dispatch(request, call_next)

        assert result.status_code == 400
        response_data = result.body.decode()
        assert "Invalid input" in response_data

    @pytest.mark.asyncio
    async def test_generic_exception_handling(self):
        """Test generic exceptions are handled properly"""
        middleware = ErrorHandlingMiddleware(Mock())

        request = Mock()
        call_next = AsyncMock(side_effect=Exception("Unexpected error"))

        result = await middleware.dispatch(request, call_next)

        assert result.status_code == 500
        response_data = result.body.decode()
        assert "Internal Server Error" in response_data

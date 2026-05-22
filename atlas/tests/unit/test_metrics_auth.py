"""
Tests for Metrics Router Authentication

Validates that metrics endpoints are properly protected and require authentication.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import os


# Set test environment before importing app
os.environ['ENABLE_AUTH'] = 'true'  # Enable auth for these tests


@pytest.fixture
def client():
    """Create test client"""
    # Import after setting env var
    from app.main import app
    return TestClient(app)


@pytest.fixture
def mock_token_validation():
    """Mock token validation"""
    with patch('app.security.auth.validate_token') as mock:
        # Return valid admin user
        mock.return_value = {
            'sub': 'test_admin',
            'username': 'test_admin',
            'scopes': ['system:admin', 'metrics:read'],
            'exp': 9999999999  # Far future
        }
        yield mock


@pytest.fixture
def mock_token_validation_no_scope():
    """Mock token validation without metrics scope"""
    with patch('app.security.auth.validate_token') as mock:
        # Return user without metrics scope
        mock.return_value = {
            'sub': 'test_user',
            'username': 'test_user',
            'scopes': ['research:execute'],  # No metrics:read
            'exp': 9999999999
        }
        yield mock


class TestMetricsAuthentication:
    """Test metrics endpoint authentication"""
    
    def test_metrics_requires_auth(self, client):
        """Metrics endpoint should require authentication"""
        response = client.get("/metrics/")
        assert response.status_code == 401
    
    def test_metrics_allows_valid_token(self, client, mock_token_validation):
        """Metrics endpoint should allow valid token with admin scope"""
        headers = {"Authorization": "Bearer valid-token"}
        response = client.get("/metrics/", headers=headers)
        # May be 200 or 503 depending on actual metrics availability
        assert response.status_code in [200, 503]
    
    def test_metrics_rejects_insufficient_scopes(self, client, mock_token_validation_no_scope):
        """Metrics endpoint should reject token without required scopes"""
        headers = {"Authorization": "Bearer valid-token"}
        response = client.get("/metrics/", headers=headers)
        assert response.status_code == 403
        assert "Insufficient permissions" in response.json()['detail']
    
    def test_prometheus_endpoint_requires_auth(self, client):
        """Prometheus endpoint should require authentication"""
        response = client.get("/metrics/prometheus")
        assert response.status_code == 401
    
    def test_system_metrics_requires_auth(self, client):
        """System metrics endpoint should require authentication"""
        response = client.get("/metrics/system")
        assert response.status_code == 401
    
    def test_reset_metrics_requires_auth(self, client):
        """Reset metrics endpoint should require authentication"""
        response = client.post("/metrics/reset")
        assert response.status_code == 401


class TestHealthEndpointPublic:
    """Test that health endpoint remains public"""
    
    def test_health_endpoint_public(self, client):
        """Health endpoint should be accessible without auth"""
        response = client.get("/health")
        # Should succeed without authentication
        assert response.status_code == 200
        assert response.json()['status'] == 'healthy'


class TestDevelopmentMode:
    """Test authentication in development mode"""
    
    @pytest.fixture(autouse=True)
    def set_dev_mode(self):
        """Set development mode"""
        os.environ['ENABLE_AUTH'] = 'false'
        yield
        os.environ['ENABLE_AUTH'] = 'true'
    
    def test_metrics_accessible_in_dev_mode(self, client):
        """Metrics should be accessible in development mode"""
        # Re-import to pick up env change
        import importlib
        import app.security.auth
        importlib.reload(app.security.auth)
        
        response = client.get("/metrics/")
        # Should work without auth in dev mode
        assert response.status_code in [200, 503]

"""
Tests for SSRF Protection Module

Validates that SSRF guard correctly blocks dangerous URLs
and allows safe ones.
"""

import pytest
from app.security.ssrf_guard import (
    validate_url_safety,
    SSRFError,
    is_private_ip,
    is_metadata_ip,
    safe_httpx_client,
)


class TestPrivateIPDetection:
    """Test private IP detection"""
    
    def test_detects_private_ipv4(self):
        """Should detect private IPv4 ranges"""
        assert is_private_ip("10.0.0.1")
        assert is_private_ip("172.16.0.1")
        assert is_private_ip("192.168.1.1")
        assert is_private_ip("127.0.0.1")
        assert is_private_ip("169.254.169.254")
    
    def test_detects_public_ipv4(self):
        """Should allow public IPv4"""
        assert not is_private_ip("8.8.8.8")
        assert not is_private_ip("1.1.1.1")
        assert not is_private_ip("93.184.216.34")  # example.com
    
    def test_detects_metadata_ip(self):
        """Should detect cloud metadata IPs"""
        assert is_metadata_ip("169.254.169.254")


class TestURLValidation:
    """Test URL safety validation"""
    
    def test_allows_safe_https_url(self):
        """Should allow safe HTTPS URLs"""
        validate_url_safety("https://example.com/api")
        validate_url_safety("https://api.github.com/repos")
        # Should not raise
    
    def test_allows_safe_http_url(self):
        """Should allow safe HTTP URLs"""
        validate_url_safety("http://example.com/api")
        # Should not raise
    
    def test_blocks_private_ip_addresses(self):
        """Should block private IP addresses"""
        with pytest.raises(SSRFError, match="private IP"):
            validate_url_safety("http://192.168.1.1/admin")
        
        with pytest.raises(SSRFError, match="private IP"):
            validate_url_safety("http://10.0.0.1/secrets")
        
        with pytest.raises(SSRFError, match="private IP"):
            validate_url_safety("http://172.16.0.1/internal")
    
    def test_blocks_localhost(self):
        """Should block localhost"""
        with pytest.raises(SSRFError, match="private IP"):
            validate_url_safety("http://127.0.0.1/admin")
        
        with pytest.raises(SSRFError, match="private IP"):
            validate_url_safety("http://localhost:8000/metrics")
    
    def test_blocks_metadata_service(self):
        """Should block cloud metadata service"""
        with pytest.raises(SSRFError, match="metadata"):
            validate_url_safety("http://169.254.169.254/latest/meta-data")
    
    def test_blocks_file_scheme(self):
        """Should block file:// URLs"""
        with pytest.raises(SSRFError, match="scheme.*not allowed"):
            validate_url_safety("file:///etc/passwd")
    
    def test_blocks_ftp_scheme(self):
        """Should block ftp:// URLs"""
        with pytest.raises(SSRFError, match="scheme.*not allowed"):
            validate_url_safety("ftp://example.com/files")
    
    def test_blocks_dangerous_ports(self):
        """Should block dangerous ports"""
        with pytest.raises(SSRFError, match="Port.*blocked"):
            validate_url_safety("http://example.com:22/ssh")
        
        with pytest.raises(SSRFError, match="Port.*blocked"):
            validate_url_safety("http://example.com:3306/mysql")
    
    def test_allows_private_ips_when_enabled(self):
        """Should allow private IPs when explicitly enabled"""
        validate_url_safety("http://192.168.1.1/api", allow_private_ips=True)
        # Should not raise
    
    def test_requires_hostname(self):
        """Should require hostname"""
        with pytest.raises(SSRFError, match="hostname"):
            validate_url_safety("http:///api")
    
    def test_blocks_invalid_url_format(self):
        """Should block malformed URLs"""
        with pytest.raises(SSRFError, match="Invalid URL"):
            validate_url_safety("not a url")


class TestSafeHTTPXClient:
    """Test safe httpx client factory"""
    
    def test_creates_client_with_timeout(self):
        """Should create client with timeout"""
        client = safe_httpx_client(timeout=10.0)
        assert client.timeout.read == 10.0
    
    def test_disables_redirects(self):
        """Should disable redirects by default"""
        client = safe_httpx_client()
        assert client.follow_redirects is False


class TestEdgeCases:
    """Test edge cases and special scenarios"""
    
    def test_handles_ipv6_loopback(self):
        """Should block IPv6 loopback"""
        assert is_private_ip("::1")
    
    def test_handles_uppercase_scheme(self):
        """Should normalize scheme case"""
        # Should not raise - scheme should be normalized
        validate_url_safety("HTTPS://example.com/api")

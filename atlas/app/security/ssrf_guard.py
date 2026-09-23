"""
SSRF (Server-Side Request Forgery) Protection Module

Provides utilities to prevent SSRF attacks by validating URLs before
making HTTP requests to external resources.

Features:
- IP address validation (blocks private/internal ranges)
- Scheme allowlist enforcement (http/https only)
- DNS resolution checks
- Metadata endpoint blocking (cloud provider metadata services)
- Port restrictions

Usage:
    from app.security.ssrf_guard import validate_url_safety, safe_httpx_client
    
    # Validate before making request
    validate_url_safety("https://example.com/api")
    
    # Or use the safe client wrapper
    async with safe_httpx_client() as client:
        response = await client.get(url)
"""

import ipaddress
import socket
from typing import Optional, Set
from urllib.parse import urlparse
import httpx
from fastapi import HTTPException

# Private IP ranges that should be blocked
PRIVATE_IP_RANGES = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),  # Loopback
    ipaddress.ip_network("169.254.0.0/16"),  # Link-local
    ipaddress.ip_network("::1/128"),  # IPv6 loopback
    ipaddress.ip_network("fe80::/10"),  # IPv6 link-local
    ipaddress.ip_network("fc00::/7"),  # IPv6 private
]

# Metadata service IPs (cloud providers)
METADATA_IPS = [
    "169.254.169.254",  # AWS, Azure, GCP
    "fd00:ec2::254",  # AWS IPv6
]

# Allowed URL schemes
ALLOWED_SCHEMES: Set[str] = {"http", "https"}

# Blocked ports (well-known dangerous ports)
BLOCKED_PORTS: Set[int] = {
    22,    # SSH
    23,    # Telnet
    25,    # SMTP
    3306,  # MySQL
    5432,  # PostgreSQL
    6379,  # Redis
    27017, # MongoDB
}


class SSRFError(Exception):
    """Raised when a URL fails SSRF validation"""
    pass


def is_private_ip(ip_str: str) -> bool:
    """
    Check if an IP address is in a private range.
    
    Args:
        ip_str: IP address as string
        
    Returns:
        True if IP is private/internal
    """
    try:
        ip = ipaddress.ip_address(ip_str)
        return any(ip in network for network in PRIVATE_IP_RANGES)
    except ValueError:
        # Invalid IP format
        return False


def is_metadata_ip(ip_str: str) -> bool:
    """
    Check if an IP is a cloud metadata service.
    
    Args:
        ip_str: IP address as string
        
    Returns:
        True if IP is a metadata service
    """
    return ip_str in METADATA_IPS


def resolve_hostname(hostname: str) -> str:
    """
    Resolve a hostname to an IP address.
    
    Args:
        hostname: Hostname to resolve
        
    Returns:
        Resolved IP address
        
    Raises:
        SSRFError: If resolution fails or resolves to blocked IP
    """
    try:
        ip = socket.gethostbyname(hostname)
        return ip
    except socket.gaierror as e:
        raise SSRFError(f"Failed to resolve hostname '{hostname}': {e}")


def validate_url_safety(
    url: str,
    allow_private_ips: bool = False,
    allowed_schemes: Optional[Set[str]] = None,
    blocked_ports: Optional[Set[int]] = None,
) -> None:
    """
    Validate that a URL is safe from SSRF attacks.
    
    Args:
        url: URL to validate
        allow_private_ips: If True, allow private IP ranges (default: False)
        allowed_schemes: Set of allowed URL schemes (default: http, https)
        blocked_ports: Set of blocked ports (default: common dangerous ports)
        
    Raises:
        SSRFError: If URL fails validation
        
    Example:
        >>> validate_url_safety("https://example.com/api")  # OK
        >>> validate_url_safety("http://192.168.1.1")  # Raises SSRFError
        >>> validate_url_safety("file:///etc/passwd")  # Raises SSRFError
    """
    if allowed_schemes is None:
        allowed_schemes = ALLOWED_SCHEMES
    if blocked_ports is None:
        blocked_ports = BLOCKED_PORTS
    
    # Parse URL
    try:
        parsed = urlparse(url)
    except Exception as e:
        raise SSRFError(f"Invalid URL format: {e}")
    
    # Validate scheme
    if parsed.scheme not in allowed_schemes:
        raise SSRFError(
            f"URL scheme '{parsed.scheme}' not allowed. "
            f"Allowed schemes: {', '.join(allowed_schemes)}"
        )
    
    # Extract hostname
    hostname = parsed.hostname
    if not hostname:
        raise SSRFError("URL must have a hostname")
    
    # Check port
    port = parsed.port
    if port and port in blocked_ports:
        raise SSRFError(f"Port {port} is blocked for security reasons")
    
    # Check if hostname is already an IP
    try:
        ip = ipaddress.ip_address(hostname)
        ip_str = str(ip)
    except ValueError:
        # It's a hostname, need to resolve
        ip_str = resolve_hostname(hostname)
    
    # Check for metadata IPs
    if is_metadata_ip(ip_str):
        raise SSRFError(
            f"Access to cloud metadata service ({ip_str}) is blocked"
        )
    
    # Check for private IPs
    if not allow_private_ips and is_private_ip(ip_str):
        raise SSRFError(
            f"Access to private IP address ({ip_str}) is blocked"
        )


def safe_httpx_client(
    timeout: float = 30.0,
    allow_private_ips: bool = False,
    **kwargs
) -> httpx.AsyncClient:
    """
    Create an httpx AsyncClient with safe defaults and SSRF protection.
    
    Note: This client still requires manual URL validation before use.
    The timeout and limits are applied automatically.
    
    Args:
        timeout: Request timeout in seconds (default: 30.0)
        allow_private_ips: Allow requests to private IPs
        **kwargs: Additional httpx.AsyncClient arguments
        
    Returns:
        Configured httpx.AsyncClient instance
        
    Example:
        async with safe_httpx_client() as client:
            validate_url_safety(url)  # Validate first
            response = await client.get(url)
    """
    # Set safe defaults
    limits = httpx.Limits(
        max_connections=100,
        max_keepalive_connections=20,
    )
    
    return httpx.AsyncClient(
        timeout=timeout,
        limits=limits,
        follow_redirects=False,  # Prevent redirect-based SSRF
        **kwargs
    )


def validate_and_raise_http_exception(
    url: str,
    allow_private_ips: bool = False,
) -> None:
    """
    Validate URL and raise FastAPI HTTPException if invalid.
    
    Convenience wrapper for use in FastAPI endpoints.
    
    Args:
        url: URL to validate
        allow_private_ips: Allow private IP ranges
        
    Raises:
        HTTPException: 400 Bad Request if validation fails
    """
    try:
        validate_url_safety(url, allow_private_ips=allow_private_ips)
    except SSRFError as e:
        raise HTTPException(
            status_code=400,
            detail=f"URL validation failed: {str(e)}"
        )


__all__ = [
    "SSRFError",
    "validate_url_safety",
    "safe_httpx_client",
    "validate_and_raise_http_exception",
    "is_private_ip",
    "is_metadata_ip",
]

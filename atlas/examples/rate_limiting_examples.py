"""
Rate Limiting Examples for AXIOM ATLAS
Demonstrates how to apply rate limiting to FastAPI endpoints.
"""

from fastapi import APIRouter, Depends
from typing import Annotated

from app.core.rate_limiter import (
    limiter,
    ip_limiter,
    strict_limit,
    anonymous_limit,
    AUTH_RATE_LIMIT,
    PUBLIC_API_LIMIT,
    AUTHENTICATED_API_LIMIT,
    COMPUTE_RATE_LIMIT
)
from app.middleware.auth_middleware import get_current_user

router = APIRouter()


# Example 1: Using default rate limit (1000/hour, 100/minute per user)
@router.get("/api/default-rate-limit")
@limiter.limit("default")
async def default_rate_limit_endpoint():
    """
    Endpoint with default rate limiting.
    Uses global limiter defaults: 1000 req/hour, 100 req/minute.
    """
    return {"message": "Default rate limit applies"}


# Example 2: Custom rate limit for specific endpoint
@router.post("/api/expensive-operation")
@limiter.limit("10/minute")
async def expensive_operation():
    """
    Computationally expensive endpoint with strict rate limit.
    Limited to 10 requests per minute per user.
    """
    return {"message": "Expensive operation completed"}


# Example 3: IP-based rate limiting (regardless of authentication)
@router.post("/api/public/register")
@ip_limiter.limit("5/minute")
async def register_user():
    """
    Public registration endpoint with IP-based rate limiting.
    Prevents automated bot registrations.
    """
    return {"message": "User registered"}


# Example 4: Multiple rate limits (both user and IP)
@router.post("/api/login")
@ip_limiter.limit("10/minute")  # IP limit
@limiter.limit("20/hour")        # User limit
async def login():
    """
    Login endpoint with dual rate limiting.
    - IP: 10 attempts per minute (prevent brute force)
    - User: 20 attempts per hour (prevent credential stuffing)
    """
    return {"access_token": "dummy_token"}


# Example 5: Using pre-defined rate limit constants
@router.post("/auth/login")
@anonymous_limit(AUTH_RATE_LIMIT)  # 5/minute
async def auth_login():
    """
    Authentication endpoint using pre-defined rate limit.
    Uses AUTH_RATE_LIMIT constant (5/minute).
    """
    return {"message": "Logged in"}


# Example 6: Different limits for authenticated vs unauthenticated users
@router.get("/api/data")
async def get_data(current_user: Annotated[dict, Depends(get_current_user)] = None):
    """
    Endpoint with different rate limits based on authentication.
    
    Note: This example shows the concept, but slowapi applies limits
    at decoration time. For dynamic limits, you'd need custom logic.
    """
    if current_user:
        # Authenticated users get higher limits via default limiter
        return {"message": "Data for authenticated user"}
    else:
        # Unauthenticated users hit IP limiter limits
        return {"message": "Limited data for anonymous user"}


# Example 7: Strict rate limiting for sensitive operations
@router.post("/api/admin/sensitive")
@strict_limit("3/hour")  # Very restrictive
async def sensitive_admin_operation(
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """
    Highly sensitive administrative operation.
    Severely rate-limited to 3 requests per hour.
    """
    return {"message": "Sensitive operation completed"}


# Example 8: Rate limiting on file uploads
@router.post("/api/upload")
@limiter.limit("20/hour")
async def upload_file():
    """
    File upload endpoint with hourly rate limit.
    Prevents storage abuse.
    """
    return {"message": "File uploaded"}


# Example 9: Computational endpoints (hypothesis generation, simulations)
@router.post("/api/hypothesis/generate")
@limiter.limit(COMPUTE_RATE_LIMIT)  # 10/minute
async def generate_hypothesis():
    """
    Computationally intensive hypothesis generation.
    Uses COMPUTE_RATE_LIMIT (10/minute) to manage resources.
    """
    return {"hypothesis": "Example hypothesis"}


# Example 10: Search/query endpoints
@router.get("/api/search")
@limiter.limit("100/minute")
async def search():
    """
    Search endpoint with moderate rate limiting.
    Allows frequent queries while preventing abuse.
    """
    return {"results": []}


# Example 11: Exempt an endpoint from rate limiting
@router.get("/health")
# No rate limiter decorator - endpoint is not rate limited
async def health_check():
    """
    Health check endpoint without rate limiting.
    Should always be accessible for monitoring.
    """
    return {"status": "healthy"}


# Example 12: Rate limiting with custom key function (advanced)
# Note: This requires modifying the limiter initialization
# See app/core/rate_limiter.py for key_func parameter

# Example 13: Integration with existing authentication
@router.get("/api/protected")
@limiter.limit(AUTHENTICATED_API_LIMIT)  # 1000/hour
async def protected_endpoint(
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """
    Protected endpoint combining authentication and rate limiting.
    Rate limit is applied per authenticated user.
    """
    return {
        "message": "Protected data",
        "user": current_user.get("sub")
    }


# Notes on Rate Limiting Strategy:
"""
1. **Public Endpoints**: Use IP-based rate limiting with strict limits
   - Registration: 3-5/minute
   - Login attempts: 10/minute
   - Password reset: 3/hour

2. **Authenticated Endpoints**: Use user-based rate limiting
   - Standard API calls: 1000/hour
   - Search/queries: 100/minute
   - Data retrieval: 200/hour

3. **Computational Endpoints**: Strict limits to manage resources
   - Hypothesis generation: 10/minute
   - Simulations: 5/minute
   - Model inference: 20/hour

4. **Administrative Endpoints**: Very restrictive
   - Sensitive operations: 3/hour
   - Configuration changes: 10/hour
   - User management: 50/hour

5. **Health/Monitoring**: No rate limiting
   - Health checks: unrestricted
   - Metrics: unrestricted (or very high limit)

6. **File Operations**:
   - Uploads: 20/hour
   - Downloads: 100/hour
   - Deletions: 50/hour
"""

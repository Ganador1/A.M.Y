# Security Overview - AXIOM ATLAS

This document provides an overview of the security measures implemented in AXIOM ATLAS.

## Table of Contents

- [Authentication & Authorization](#authentication--authorization)
- [SSRF Protection](#ssrf-protection)
- [Rate Limiting](#rate-limiting)
- [Request Size Limits](#request-size-limits)
- [Security Headers](#security-headers)
- [Secret Management](#secret-management)
- [Input Validation](#input-validation)
- [Security Testing](#security-testing)

## Authentication & Authorization

### JWT-Based Authentication

AXIOM uses JWT (JSON Web Tokens) for stateless authentication.

**Location**: `app/security/auth.py`

**Features**:
- Token-based authentication with expiration
- Scope-based authorization (RBAC)
- Development mode toggle via `ENABLE_AUTH` environment variable
- Secure password hashing with bcrypt

**Usage**:

```python
from app.security.auth import require_scopes

@router.get("/admin", dependencies=[Depends(require_scopes(["system:admin"]))])
async def admin_endpoint():
    # Only users with 'system:admin' scope can access
    return {"status": "admin access granted"}
```

**Environment Variables**:
- `ENABLE_AUTH`: Set to `true` for production (validates JWT), `false` for development (mock user)
- `SECRET_KEY`: JWT signing key (use strong random value)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 30 minutes)

### User Roles & Scopes

Predefined user roles:
- `system_admin`: Full system access
- `researcher`: Research and experiment execution
- `lab_operator`: Laboratory equipment operation

Available scopes:
- `system:admin`, `system:read`
- `research:execute`
- `lab:equipment`, `lab:schedule`
- `experimental:run`
- `sandbox:execute`
- `metrics:read`
- And more...

## SSRF Protection

Server-Side Request Forgery (SSRF) protection prevents the application from making requests to internal/private resources.

**Location**: `app/security/ssrf_guard.py`

**Protections**:
- ✅ Blocks private IP ranges (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
- ✅ Blocks loopback addresses (127.0.0.0/8, ::1)
- ✅ Blocks link-local addresses (169.254.0.0/16)
- ✅ Blocks cloud metadata services (169.254.169.254)
- ✅ Scheme allowlist (http/https only, blocks file://, ftp://, etc.)
- ✅ Port blocklist (SSH, MySQL, PostgreSQL, Redis, etc.)
- ✅ DNS resolution validation

**Usage**:

```python
from app.security.ssrf_guard import validate_url_safety, SSRFError

# Validate before making request
url = "https://external-api.example.com/data"
try:
    validate_url_safety(url)
    response = await httpx.get(url)
except SSRFError as e:
    raise HTTPException(400, detail=f"URL validation failed: {e}")
```

**Applied To**:
- All external API calls in `app/services/extended_hypothesis_bridges.py`
- Additional services should validate URLs before HTTP requests

## Rate Limiting

Rate limiting prevents abuse and ensures fair resource usage.

**Location**: `app/middleware/main.py` (RateLimitMiddleware)

**Implementation**: Uses slowapi with Redis backend (falls back to in-memory)

**Default Limits**:
- Anonymous users: 10 requests/minute
- Authenticated users: 100 requests/minute
- Premium users: 1000 requests/minute
- Internal services: 10000 requests/minute

**Endpoint-Specific Limits**:
- `/api/auth/login`: 5 requests/minute
- `/api/auth/register`: 3 requests/minute
- `/api/models/train`: 5 requests/hour
- And more...

**Configuration**: Set `REDIS_URL` environment variable for distributed rate limiting

**Exemptions**: Health checks, static files, docs are exempt from rate limiting

## Request Size Limits

Prevents large payload attacks and resource exhaustion.

**Location**: `app/middleware/main.py` (RequestSizeMiddleware)

**Default Limit**: 10 MB (configurable via `MAX_REQUEST_SIZE_MB` env var)

**Behavior**: Returns `413 Payload Too Large` if Content-Length exceeds limit

**Configuration**:
```bash
# In .env file
MAX_REQUEST_SIZE_MB=10
```

## Security Headers

Comprehensive HTTP security headers protect against common web vulnerabilities.

**Location**: `app/middleware/security_headers.py`

**Headers Applied**:
- `X-Content-Type-Options: nosniff` - Prevents MIME sniffing
- `X-Frame-Options: DENY` - Prevents clickjacking
- `Strict-Transport-Security` - Forces HTTPS
- `Content-Security-Policy` - Prevents XSS attacks
- `Permissions-Policy` - Restricts browser features
- `Cross-Origin-*` headers - CORS controls

**CSP Policies**:
- **Production**: Strict CSP with no unsafe-inline/eval
- **Development**: Relaxed CSP for debugging

## Secret Management

Secure handling of sensitive configuration and credentials.

**Documentation**: See `docs/security/SECRETS.md` for detailed guide

**Key Points**:
- ✅ Never commit `.env` files (except `.env.example`)
- ✅ Use encrypted storage (`.api_keys.enc`) with external decryption key
- ✅ Use environment variables or secret managers in production
- ✅ Rotate secrets regularly (JWT keys every 90 days)
- ✅ `.gitignore` patterns prevent accidental commits

**Production Recommendations**:
- AWS Secrets Manager / Parameter Store
- Google Cloud Secret Manager
- Azure Key Vault
- HashiCorp Vault
- Kubernetes Secrets

## Input Validation

Input validation prevents injection attacks and ensures data integrity.

**Validation Layers**:

1. **Pydantic Models** (all endpoints):
   ```python
   class DataInput(BaseModel):
       name: str = Field(..., min_length=1, max_length=100)
       value: float = Field(..., gt=0)
   ```

2. **SSRF Validation** (external URLs):
   - See SSRF Protection section above

3. **Sandbox Validation** (code execution):
   - Blocks dangerous imports (os, subprocess, etc.)
   - Blocks dangerous functions (eval, exec, open, etc.)
   - Character and line limits
   - **Location**: `app/services/infrastructure/sandbox_executor_service.py`

4. **SQL Injection Prevention**:
   - SQLAlchemy ORM (parameterized queries)
   - No raw SQL strings

## Security Testing

Comprehensive security tests validate protections.

**Test Suites**:

1. **SSRF Guard Tests** (`tests/unit/test_ssrf_guard.py`):
   - Validates blocking of private IPs
   - Validates blocking of dangerous schemes
   - Validates blocking of metadata services
   - Validates allowing of public URLs

2. **Authentication Tests** (`tests/unit/test_metrics_auth.py`):
   - Validates token validation
   - Validates scope checking
   - Validates protected endpoints
   - Validates development mode toggle

3. **Gitignore Tests** (`tests/unit/test_gitignore_patterns.py`):
   - Validates secrets are ignored
   - Validates `.env.example` is not ignored
   - Validates backup files are ignored

**Running Tests**:
```bash
pytest tests/unit/test_ssrf_guard.py -v
pytest tests/unit/test_metrics_auth.py -v
pytest tests/unit/test_gitignore_patterns.py -v
```

## Security Best Practices

### For Developers

**DO**:
- ✅ Use `require_scopes()` for all sensitive endpoints
- ✅ Validate all external URLs with `validate_url_safety()`
- ✅ Use Pydantic models for input validation
- ✅ Use environment variables for configuration
- ✅ Log security events (auth failures, blocked requests)
- ✅ Use `safe_httpx_client()` for external requests
- ✅ Set timeouts on all HTTP requests

**DON'T**:
- ❌ Don't commit secrets to git
- ❌ Don't use `shell=True` in subprocess calls
- ❌ Don't use `eval()` or `exec()` on user input
- ❌ Don't expose `/metrics` without authentication
- ❌ Don't make HTTP requests without SSRF validation
- ❌ Don't hardcode credentials in code
- ❌ Don't log sensitive data (tokens, passwords)

### For Deployment

**DO**:
- ✅ Set `ENABLE_AUTH=true` in production
- ✅ Use HTTPS/TLS for all connections
- ✅ Use strong, unique `SECRET_KEY`
- ✅ Use managed secret stores (not `.env` files)
- ✅ Enable Redis for distributed rate limiting
- ✅ Monitor security logs and alerts
- ✅ Keep dependencies updated
- ✅ Run security scans regularly

**DON'T**:
- ❌ Don't use default passwords
- ❌ Don't expose internal ports
- ❌ Don't disable security middleware
- ❌ Don't ignore security warnings
- ❌ Don't use HTTP in production

## Security Incident Response

If you discover a security vulnerability:

1. **Do NOT** create a public GitHub issue
2. **Do NOT** discuss publicly until patched
3. Email security team: security@axiom-atlas.example
4. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## Security Audit Checklist

Periodic security audits should verify:

- [ ] All secrets are externalized (no hardcoded credentials)
- [ ] `.gitignore` patterns block sensitive files
- [ ] Authentication is enabled (`ENABLE_AUTH=true`)
- [ ] All sensitive endpoints require authentication
- [ ] SSRF protection applied to external HTTP calls
- [ ] Rate limiting is active
- [ ] Request size limits are configured
- [ ] Security headers are present
- [ ] Sandbox executions are restricted
- [ ] Dependencies are up-to-date (no known vulnerabilities)
- [ ] Logs are monitored for suspicious activity
- [ ] Access tokens are rotated regularly

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE/SANS Top 25](https://www.sans.org/top25-software-errors/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Pydantic Security](https://docs.pydantic.dev/latest/concepts/validation/)

## Security Contact

For security concerns:
- Email: security@axiom-atlas.example
- PGP Key: [Link to public key]

---

**Last Updated**: 2025-12-30  
**Review Frequency**: Quarterly  
**Next Review**: 2025-03-30

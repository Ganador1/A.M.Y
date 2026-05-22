# Secret Management in AXIOM ATLAS

This document describes how secrets and sensitive configuration are handled in the AXIOM ATLAS platform.

## Overview

AXIOM ATLAS uses multiple layers of secret management to protect sensitive data:

1. **Environment Variables** (`.env` files)
2. **Encrypted Secret Storage** (`.api_keys.enc`)
3. **Git Ignore Patterns** (prevent accidental commits)
4. **Production Secret Managers** (recommended for deployment)

## Environment Variables

### Development

For local development, copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Then edit `.env` with your local values. **NEVER commit `.env` files to git.**

### Required Secrets

The following secrets must be configured:

- `SECRET_KEY`: JWT signing key (generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- `DATABASE_URL`: PostgreSQL connection string
- API keys for external services (Materials Project, etc.)

### Optional Secrets

- `REDIS_URL`: Redis connection string (if caching enabled)
- `OPENAI_API_KEY`: If using OpenAI models
- User passwords: `SYSTEM_ADMIN_PASSWORD`, `RESEARCHER_PASSWORD`, `LAB_OPERATOR_PASSWORD`

## Encrypted API Keys

The file `.api_keys.enc` contains encrypted API keys for external services. 

**Important Security Notes:**

1. **Encryption Key Location**: The decryption key is **NOT** stored in this repository
2. **Key Management**: In production, use a secure key management service (AWS KMS, HashiCorp Vault, etc.)
3. **Access Control**: Only authorized deployment systems should have access to the decryption key

### How It Works

1. API keys are encrypted using symmetric encryption (AES-256)
2. The encrypted file `.api_keys.enc` is committed to the repository
3. The decryption key is provided via:
   - Environment variable `API_KEYS_ENCRYPTION_KEY` (production)
   - Secure secret manager (recommended)
   - Manual configuration (development only)

### Decryption Process

```python
from app.config.secrets_manager import SecretsManager

# Initialize with encryption key from environment
secrets = SecretsManager()

# Load and decrypt API keys
api_keys = secrets.load_encrypted_keys()

# Access specific keys
materials_project_key = api_keys.get('MATERIALS_PROJECT_API_KEY')
```

## Git Ignore Patterns

The `.gitignore` file is configured to prevent accidental secret commits:

```gitignore
# Environment files
.env
.env.*
!.env.example

# Backup files
*.backup
*.backup.*
backups/

# Cryptographic keys
keys/
*.key
*.pem
.secrets.*
```

### What Gets Ignored

- All `.env` files except `.env.example`
- Any file with `.backup` extension
- Private keys (`.key`, `.pem` files)
- The `keys/` directory
- Any file starting with `.secrets.`

## Production Deployment

### Recommended Approach

**DO NOT** use `.env` files in production. Instead, use:

1. **Cloud Provider Secret Managers**:
   - AWS Secrets Manager / Parameter Store
   - Google Cloud Secret Manager
   - Azure Key Vault

2. **Container Orchestration Secrets**:
   - Kubernetes Secrets
   - Docker Swarm Secrets
   - HashiCorp Vault

3. **Environment Variables** (from secure source):
   - Injected by CI/CD pipeline
   - Set by container orchestrator
   - Provided by platform (Heroku, etc.)

### Example: Kubernetes Deployment

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: axiom-secrets
type: Opaque
data:
  SECRET_KEY: <base64-encoded-value>
  DATABASE_URL: <base64-encoded-value>
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: axiom-api
spec:
  template:
    spec:
      containers:
      - name: api
        envFrom:
        - secretRef:
            name: axiom-secrets
```

### Example: Docker Compose (Production)

```yaml
version: '3.8'
services:
  axiom-api:
    image: axiom-atlas:latest
    environment:
      - SECRET_KEY=${SECRET_KEY}  # From host environment
      - DATABASE_URL=${DATABASE_URL}
    secrets:
      - api_keys_encryption_key

secrets:
  api_keys_encryption_key:
    external: true
```

## Secret Rotation

### JWT Secret Key

Rotate the `SECRET_KEY` periodically (recommended: every 90 days):

1. Generate new key: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
2. Update in secret manager
3. Deploy with new key
4. Old tokens will be invalidated (users must re-authenticate)

### API Keys

When rotating external API keys:

1. Obtain new key from provider
2. Update encrypted file or secret manager
3. Deploy changes
4. Verify connectivity
5. Revoke old key

## Security Best Practices

### DO

✅ Use `.env.example` as a template with placeholder values  
✅ Generate strong random keys using `secrets` module  
✅ Use secret managers in production  
✅ Rotate secrets regularly  
✅ Audit secret access logs  
✅ Use different secrets for each environment (dev/staging/prod)  
✅ Encrypt secrets at rest  
✅ Use HTTPS/TLS for secrets in transit  

### DON'T

❌ **NEVER** commit `.env` files to git  
❌ **NEVER** commit unencrypted API keys  
❌ **NEVER** log secret values  
❌ **NEVER** store decryption keys in the same repo as encrypted data  
❌ **NEVER** use default/example secrets in production  
❌ **NEVER** share secrets via email, Slack, or unencrypted channels  
❌ **NEVER** hardcode secrets in source code  

## Incident Response

If a secret is accidentally committed:

1. **Immediately rotate the compromised secret**
2. Remove the secret from git history:
   ```bash
   # Use BFG Repo Cleaner or git filter-branch
   git filter-branch --force --index-filter \
     'git rm --cached --ignore-unmatch .env' \
     --prune-empty --tag-name-filter cat -- --all
   ```
3. Force push (if repository allows)
4. Notify team members to re-clone
5. Review access logs for suspicious activity
6. Document the incident

## Additional Resources

- [OWASP Secret Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [12 Factor App: Config](https://12factor.net/config)
- [Git Secret Scanner Tools](https://github.com/trufflesecurity/truffleHog)

## Contact

For security concerns related to secret management, contact:
- Security Team: security@axiom-atlas.example
- On-call: PagerDuty rotation

Last Updated: 2025-01-30

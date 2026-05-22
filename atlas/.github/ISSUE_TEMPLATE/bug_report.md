---
name: Bug Report
about: Report a bug or unexpected behavior
title: '[BUG] '
labels: bug
assignees: ''
---

## Bug Description

**Brief description:**
<!-- A clear and concise description of what the bug is -->

**Expected behavior:**
<!-- What you expected to happen -->

**Actual behavior:**
<!-- What actually happened -->

## Steps to Reproduce

1.
2.
3.
4.

**Minimal reproducible example:**
```python
# Code that reproduces the issue

```

## Environment

**AXIOM ATLAS version:**
<!-- e.g., 2.0.0, commit hash, or latest from main -->

**Python version:**
<!-- Output of: python --version -->

**Operating System:**
<!-- e.g., macOS 14.0, Ubuntu 22.04, Windows 11 -->

**Installation method:**
- [ ] pip install
- [ ] from source (git clone)
- [ ] Docker

**Dependencies:**
<!-- Output of: pip freeze | grep -E "(fastapi|pydantic|sqlalchemy)" -->

## Database

**Database type:** PostgreSQL
**Database version:**
<!-- Output of: psql --version -->

**Alembic migration status:**
<!-- Output of: alembic current -->

## Logs and Error Messages

**Error traceback:**
```
# Paste full error traceback here

```

**Relevant logs:**
```
# Paste relevant log output here (set LOG_LEVEL=DEBUG if needed)

```

## Additional Context

**Related components:**
- [ ] Biology domain
- [ ] Chemistry domain
- [ ] Physics/Quantum domain
- [ ] Mathematics domain
- [ ] Autonomous agents
- [ ] Database/ORM
- [ ] API endpoints
- [ ] Configuration
- [ ] Other: ___________

**Screenshots:**
<!-- If applicable, add screenshots to help explain the problem -->

**Is this a regression?**
- [ ] Yes, this worked in version: ___________
- [ ] No
- [ ] Not sure

**Workaround:**
<!-- If you found a temporary workaround, describe it here -->

## Checklist

- [ ] I have searched existing issues to ensure this is not a duplicate
- [ ] I have included a minimal reproducible example
- [ ] I have included error logs and tracebacks
- [ ] I have specified my environment details
- [ ] I have checked that this issue occurs on the latest version

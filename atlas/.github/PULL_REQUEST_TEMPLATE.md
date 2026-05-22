## Description

<!-- Provide a clear and concise description of what this PR does -->

**Type of change:**
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Refactoring (no functional changes, just code improvement)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Test coverage improvement
- [ ] Scientific validation/correction

**Related issues:**
<!-- Link to related issues, e.g., "Fixes #123", "Closes #456" -->
- Fixes #
- Related to #

## Changes Made

<!-- Detailed list of changes -->

**Core changes:**
-
-
-

**Files affected:**
<!-- List key files modified -->
-
-

**Domain(s) affected:**
- [ ] Biology
- [ ] Chemistry
- [ ] Physics/Quantum
- [ ] Mathematics
- [ ] Medicine
- [ ] Neuroscience
- [ ] Engineering
- [ ] Infrastructure/Core
- [ ] Documentation

## Scientific Validation

<!-- If this PR affects scientific functionality, provide validation -->

**Algorithm/method used:**
<!-- e.g., "Grover's algorithm", "BLAST sequence alignment" -->

**References:**
<!-- Scientific papers or authoritative sources -->
1.
2.

**Validation approach:**
- [ ] Verified against reference implementation
- [ ] Compared with published results
- [ ] Validated with synthetic/test data
- [ ] Peer reviewed by domain expert
- [ ] N/A (not scientific change)

**Test results:**
<!-- Summarize test results, benchmark comparisons, etc. -->

## Testing

**Tests added/updated:**
- [ ] Unit tests
- [ ] Integration tests
- [ ] End-to-end tests
- [ ] No tests needed (explain why):

**Test coverage:**
<!-- Output of: pytest --cov=app --cov-report=term-missing -->
- Current coverage: ___%
- Coverage change: +/- ___%

**Manual testing:**
<!-- Describe manual testing performed -->
1.
2.

**Test commands run:**
```bash
# Commands used to test this PR
pytest tests/unit/...
pytest tests/integration/...
```

## Code Quality

**Pre-commit checks:**
- [ ] Black formatting (`black app tests`)
- [ ] Import sorting (`isort app tests --profile black`)
- [ ] Linting (`ruff check .`)
- [ ] Type checking (`mypy app`)
- [ ] Pre-commit hooks pass (`pre-commit run --all-files`)

**Exception handling:**
- [ ] Uses custom exception hierarchy (not generic `Exception`)
- [ ] Proper exception chaining with `from e`
- [ ] No bare `except:` clauses
- [ ] N/A (no exception handling changes)

**Async patterns:**
- [ ] Uses `async def` for I/O operations
- [ ] No blocking `time.sleep()` in async code
- [ ] Proper `await` usage
- [ ] N/A (no async changes)

## Documentation

**Documentation updated:**
- [ ] README.md
- [ ] CONTRIBUTING.md
- [ ] API documentation (docstrings)
- [ ] Domain-specific README
- [ ] EXAMPLES.md
- [ ] No documentation needed

**Docstrings added:**
- [ ] All new public functions have docstrings
- [ ] Docstrings follow Google style
- [ ] Includes examples and usage
- [ ] N/A (no new public functions)

## Database

**Database changes:**
- [ ] Alembic migration created (`alembic revision --autogenerate`)
- [ ] Migration tested (up and down)
- [ ] Backward compatible
- [ ] No database changes

**Migration file:**
<!-- If applicable, name of migration file -->

## Breaking Changes

**Are there breaking changes?**
- [ ] Yes (explain below)
- [ ] No

**If yes, describe:**
<!-- What breaks? How to migrate? -->

**Migration guide:**
<!-- Provide upgrade instructions for users -->

## Performance Impact

**Performance considerations:**
- [ ] Benchmarked performance (attach results)
- [ ] No performance regression
- [ ] Improves performance by: ___%
- [ ] N/A

**Complexity:**
- Computational: <!-- e.g., O(n log n) -->
- Memory: <!-- e.g., O(n) -->

## Security and Ethics

**Security review:**
- [ ] No new security vulnerabilities introduced
- [ ] Input validation added for user-facing inputs
- [ ] No secrets or API keys committed
- [ ] Dependencies audited (`pip-audit`)
- [ ] N/A

**Ethics validation:**
- [ ] Passes ethics gate checks
- [ ] No bypass of safety systems
- [ ] Responsible use considered
- [ ] N/A

## Deployment

**Environment variables:**
- [ ] New environment variables documented in `.env.example`
- [ ] No new environment variables

**Dependencies:**
- [ ] `requirements.txt` updated
- [ ] `requirements-*.txt` updated (specify which domain)
- [ ] No new dependencies

**Configuration:**
- [ ] Config files updated (YAML, etc.)
- [ ] No config changes

## Checklist

### Before Submitting
- [ ] I have read [CONTRIBUTING.md](../CONTRIBUTING.md)
- [ ] I have followed the code style guide (Black, Ruff, type hints)
- [ ] My code follows the custom exception hierarchy
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have updated the documentation accordingly
- [ ] My changes generate no new warnings or errors
- [ ] All tests pass locally (`pytest`)
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing tests pass with my changes
- [ ] Pre-commit hooks pass

### For Maintainers (post-merge)
- [ ] Update CHANGELOG.md
- [ ] Tag release (if applicable)
- [ ] Update documentation site
- [ ] Announce in community channels

## Screenshots (if applicable)

<!-- Add screenshots for UI changes or visual improvements -->

## Additional Context

<!-- Any other context about the PR -->

**Reviewer guidance:**
<!-- What should reviewers focus on? -->

**Questions for reviewers:**
<!-- Specific questions or concerns -->

---

**By submitting this PR, I confirm that:**
- [ ] My contribution is made under the same license as the project
- [ ] I have the right to submit this work
- [ ] I understand and agree to the [Code of Conduct](../CODE_OF_CONDUCT.md)

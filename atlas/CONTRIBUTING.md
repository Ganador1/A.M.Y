# Contributing to AXIOM ATLAS

Thank you for your interest in contributing to AXIOM ATLAS! This document provides guidelines and instructions for contributing to this autonomous scientific research platform.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Code Standards](#code-standards)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Exception Handling](#exception-handling)
- [Documentation](#documentation)

---

## 🤝 Code of Conduct

Be respectful, inclusive, and constructive in all interactions. We're building tools for scientific advancement—let's maintain professional and collaborative standards.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis (optional, for caching)
- Git

### Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR-USERNAME/axiom-atlas.git
cd axiom-atlas

# Add upstream remote
git remote add upstream https://github.com/original-org/axiom-atlas.git
```

---

## 💻 Development Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Core dependencies
pip install -r requirements.txt

# Development dependencies
pip install -r requirements-dev.txt

# Domain-specific (optional)
pip install -r requirements-biology.txt
pip install -r requirements-physics.txt
# etc.
```

### 3. Setup Database

```bash
# Create database
createdb axiom_meta4

# Run migrations
alembic upgrade head
```

### 4. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings
nano .env
```

### 5. Install Pre-commit Hooks

```bash
pre-commit install
```

### 6. Run Application

```bash
# Modular architecture (standard)
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Legacy (for compatibility)
uvicorn main:app --reload
```

### 7. Verify Setup

```bash
# Run tests
pytest -q

# Check code quality
ruff check .

# Format code
black app tests
```

---

## 🛠️ How to Contribute

### Types of Contributions

1. **Bug Fixes** - Fix identified issues
2. **New Features** - Add functionality (discuss first in an issue)
3. **Documentation** - Improve docs, examples, guides
4. **Tests** - Add missing test coverage
5. **Performance** - Optimize slow operations
6. **Refactoring** - Improve code structure

### Finding Work

- Check [Issues](https://github.com/org/axiom-atlas/issues)
- Look for `good first issue` labels
- Check [Roadmaps](docs/roadmaps/) for planned work
- Ask in Discussions

### Before You Start

1. **Check existing issues** - Someone might already be working on it
2. **Create an issue** - Describe what you want to do
3. **Get feedback** - Wait for maintainer response
4. **Create a branch** - Use descriptive names

```bash
# Branch naming
git checkout -b feature/add-quantum-algorithm
git checkout -b fix/database-connection-leak
git checkout -b docs/improve-biology-readme
```

---

## 📐 Code Standards

### Exception Handling (IMPORTANT!)

We use a **custom exception hierarchy**. Never use generic `Exception`:

```python
# ❌ DON'T
try:
    result = process_data()
except Exception as e:
    logger.error(f"Error: {e}")

# ✅ DO - Use specific exceptions
from app.exceptions.domain.biology import ProteinAnalysisError
from app.exceptions.infrastructure.database import QueryTimeoutError

try:
    result = process_protein(protein_id)
except ProteinAnalysisError as e:
    logger.error(f"Protein analysis failed: {e}")
    raise
except QueryTimeoutError as e:
    logger.warning(f"Database timeout: {e}")
    # Handle retry logic
```

**Exception Hierarchy:**

```
app/exceptions/
├── base.py                   # AtlasException (base class)
├── domain/                   # Domain-specific errors
│   ├── biology.py           # BiologyError, ProteinAnalysisError, etc.
│   ├── chemistry.py
│   ├── physics.py
│   └── ...
├── infrastructure/           # Infrastructure errors
│   ├── database.py          # DatabaseError, QueryTimeoutError, etc.
│   ├── cache.py
│   └── api.py
├── external/                 # External service errors
│   ├── llm.py               # LLMError, OllamaUnavailableError, etc.
│   └── scientific_api.py
└── validation/               # Validation errors
    ├── input.py
    ├── ethics.py
    └── output.py
```

**When to Use Which Exception:**

- `BiologyError` → Protein analysis, genomics, biodiversity
- `ChemistryError` → Molecular dynamics, reactions
- `DatabaseError` → DB queries, connections
- `LLMError` → Ollama, OpenAI API calls
- `InputValidationError` → Invalid user input

See `docs/exceptions/README.md` for full guide.

### Code Style

- **Format:** Black (line length 88)
- **Import sorting:** isort (profile: black)
- **Linting:** Ruff
- **Type hints:** Required for all public functions

```python
# Example function
from typing import Optional
from app.exceptions.domain.biology import ProteinAnalysisError

async def analyze_protein(
    uniprot_id: str,
    predict_structure: bool = True
) -> dict:
    """
    Analyze protein structure and function.

    Args:
        uniprot_id: UniProt identifier (e.g., 'P04637')
        predict_structure: Whether to run AlphaFold prediction

    Returns:
        Dict with protein data, structure, and annotations

    Raises:
        ProteinAnalysisError: If analysis fails
        InputValidationError: If uniprot_id is invalid

    Example:
        >>> result = await analyze_protein("P04637")
        >>> print(result['gene_name'])
        'TP53'
    """
    if not uniprot_id:
        raise InputValidationError("UniProt ID required")

    # Implementation...
    return {"uniprot_id": uniprot_id, ...}
```

### Async by Default

Most operations should be async:

```python
# ✅ Prefer async
async def fetch_data():
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# ❌ Avoid sync (unless CPU-bound)
def fetch_data_sync():
    response = requests.get(url)
    return response.json()
```

### No Bare Excepts

```python
# ❌ NEVER
try:
    operation()
except:
    pass

# ✅ ALWAYS specify exception type
try:
    operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise
```

---

## 🧪 Testing Requirements

### Coverage Requirements

- **New features:** 80%+ coverage
- **Bug fixes:** Add test that reproduces bug
- **Refactoring:** Maintain existing coverage

### Test Structure

```
tests/
├── unit/                    # Fast, isolated tests
│   ├── biology/
│   ├── exceptions/         # Test exception hierarchy
│   └── services/
├── integration/            # Test multiple components
├── smoke/                  # Quick sanity checks
└── e2e/                    # Full workflows
```

### Writing Tests

```python
import pytest
from app.services.computational_biology_service import ComputationalBiologyService
from app.exceptions.domain.biology import ProteinAnalysisError

class TestProteinAnalysis:
    @pytest.mark.asyncio
    async def test_valid_protein(self):
        service = ComputationalBiologyService()
        result = await service.analyze_protein("P04637")

        assert result['uniprot_id'] == "P04637"
        assert result['gene_name'] == "TP53"

    @pytest.mark.asyncio
    async def test_invalid_protein_raises_error(self):
        service = ComputationalBiologyService()

        with pytest.raises(ProteinAnalysisError) as exc:
            await service.analyze_protein("INVALID_ID")

        assert "not found" in str(exc.value).lower()
```

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/unit/biology/test_protein_analysis.py -v

# With coverage
pytest --cov=app --cov-report=term-missing

# Fast smoke tests
pytest tests/smoke/ -q

# Mark specific tests
pytest -m asyncio  # Only async tests
pytest -m "not slow"  # Exclude slow tests
```

---

## 🔄 Pull Request Process

### 1. Update Your Branch

```bash
git fetch upstream
git rebase upstream/main
```

### 2. Make Your Changes

- Follow code standards
- Add tests
- Update documentation
- Run pre-commit hooks

### 3. Commit Messages

Use conventional commits:

```bash
# Format: <type>(<scope>): <description>

git commit -m "feat(biology): add protein-ligand docking service"
git commit -m "fix(database): resolve connection pool exhaustion"
git commit -m "docs(contributing): add exception handling guide"
git commit -m "test(biology): add coverage for BiologyLoop"
git commit -m "refactor(async): migrate services to async/await"
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code restructuring
- `perf`: Performance improvement
- `chore`: Maintenance

### 4. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create PR on GitHub with:

- **Title:** Clear, descriptive
- **Description:** What, why, how
- **Related Issues:** Fixes #123
- **Checklist:** Complete the PR template

### 5. PR Checklist

Before submitting, ensure:

- [ ] Code follows style guide (black, ruff pass)
- [ ] All tests pass (`pytest`)
- [ ] Coverage maintained/improved
- [ ] Documentation updated
- [ ] No merge conflicts
- [ ] Commits are clean and atomic
- [ ] PR description is complete
- [ ] Related issue linked
- [ ] Pre-commit hooks pass
- [ ] **Exception handling uses custom hierarchy**

### 6. Review Process

- Maintainers will review within 2-3 days
- Address feedback promptly
- Be respectful and collaborative
- CI must pass (tests, linting, security)

### 7. After Merge

```bash
# Update your fork
git checkout main
git pull upstream main
git push origin main

# Delete feature branch
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name
```

---

## 📚 Documentation

### Docstrings

Use Google style:

```python
def calculate_diversity(species_data: dict) -> dict:
    """
    Calculate biodiversity metrics for species abundance data.

    Computes Shannon index, Simpson index, species richness, and
    evenness metrics for ecological diversity assessment.

    Args:
        species_data: Dict mapping species names to abundance counts
            Example: {"species_A": 50, "species_B": 30}

    Returns:
        Dict containing:
            - shannon: Shannon diversity index (float)
            - simpson: Simpson diversity index (float)
            - richness: Number of species (int)
            - evenness: Pielou's evenness (float)

    Raises:
        InputValidationError: If species_data is empty or invalid

    Example:
        >>> data = {"oak": 100, "pine": 50, "birch": 25}
        >>> metrics = calculate_diversity(data)
        >>> print(f"Shannon: {metrics['shannon']:.3f}")
        Shannon: 1.459

    References:
        Shannon, C.E. (1948). A Mathematical Theory of Communication.
        Bell System Technical Journal, 27, 379-423.
    """
```

### Updating Docs

When adding features, update:

- Domain README (`app/domains/{domain}/README.md`)
- EXAMPLES.md (if applicable)
- API_GUIDE.md (for new endpoints)
- Main README.md (if major feature)

---

## 🐛 Bug Reports

### Good Bug Report Includes:

1. **Description:** What happened vs what you expected
2. **Steps to reproduce:** Minimal reproducible example
3. **Environment:** OS, Python version, dependencies
4. **Logs:** Error messages, stack traces
5. **Screenshots:** If UI-related

### Example:

```markdown
**Bug:** Database connection pool exhaustion after 100 requests

**Steps to Reproduce:**
1. Start app: `uvicorn main_refactored:app`
2. Run load test: `ab -n 1000 -c 50 http://localhost:8000/api/biology/protein/P04637`
3. Observe error after ~100 requests

**Expected:** Should handle 1000 requests
**Actual:** Crashes with "connection pool exhausted"

**Environment:**
- OS: macOS 14.0
- Python: 3.11.5
- PostgreSQL: 14.9
- Dependencies: requirements.txt (commit abc123)

**Logs:**
```
ERROR: QueryTimeoutError: No connections available in pool
...
```

**Suggested Fix:**
Increase pool_size in app/core/database.py
```

---

## 💡 Feature Requests

1. **Check existing issues** - May already be planned
2. **Describe use case** - Why is this needed?
3. **Propose solution** - How might it work?
4. **Consider alternatives** - What else could solve this?

---

## 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic V2 Guide](https://docs.pydantic.dev/latest/)
- [pytest Documentation](https://docs.pytest.org/)
- [Async Python Guide](https://realpython.com/async-io-python/)
- [AXIOM Architecture](docs/architecture.md)
- [Router Registry](docs/router_registry.md)
- [Exception Hierarchy](docs/exceptions/README.md)

---

## 📞 Getting Help

- **Discord:** #axiom-atlas-dev
- **Discussions:** [GitHub Discussions](https://github.com/org/axiom-atlas/discussions)
- **Email:** dev@axiom-atlas.org

---

## 🏆 Recognition

Contributors are recognized in:
- [CONTRIBUTORS.md](CONTRIBUTORS.md)
- Release notes
- Hall of Fame (for significant contributions)

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the same license as the project (see [LICENSE](LICENSE)).

---

**Thank you for contributing to AXIOM ATLAS!** 🚀

Your work helps advance autonomous scientific research and makes science more accessible to everyone.

---

**Last Updated:** 2025-09-30
**Maintainers:** @core-team

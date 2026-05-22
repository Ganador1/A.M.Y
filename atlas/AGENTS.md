# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Project Overview

AXIOM ATLAS is an autonomous scientific research platform that combines multi-agent AI systems with scientific computing across mathematics, physics, chemistry, biology, medicine, and engineering domains. The system generates hypotheses, designs experiments, executes workflows, and validates results with reproducibility guarantees.

## Development Commands

### Running the Application

**Preferred (Modular Architecture):**
```bash
uvicorn main_refactored:app --host 0.0.0.0 --port 8000 --reload
```

**Legacy (Compatibility):**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The refactored entry point provides 60-80% faster startup and 40-60% lower memory usage through lazy loading and router registry.

### Testing

**Run all tests:**
```bash
pytest -q
```

**Run specific test suite:**
```bash
pytest tests/unit/                    # Unit tests
pytest tests/integration/             # Integration tests
pytest tests/smoke/                   # Smoke tests
```

**Run single test file:**
```bash
pytest tests/unit/test_arithmetic.py -v
```

**With coverage:**
```bash
pytest --cov=app --cov-report=term-missing
```

### Linting and Formatting

```bash
# Format with black
black app tests

# Sort imports
isort app tests --profile black

# Lint with ruff
ruff check . --fix

# Type checking (optional, excludes tests/scripts)
mypy app
```

### Pre-commit Hooks

```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Check migration status
python scripts/tools/migration_status.sh

# Rollback one revision
alembic downgrade -1
```

## Architecture Overview

### Dual Entry Points

The codebase maintains two FastAPI applications:

1. **`main_refactored.py`** (PREFERRED) - Modular architecture with:
   - Automatic router registration via `app.routers.router_registry`
   - Lazy loading for 100+ routers
   - Centralized middleware configuration
   - Async lifespan management with health checks
   - Service initialization (orchestration, database, logging)

2. **`main.py`** (LEGACY) - Manual router imports for backwards compatibility

Always use `main_refactored.py` for new development. See `docs/app_entrypoints.md` for migration guidance.

### Domain-Driven Structure

```
app/
├── domains/              # Scientific domain implementations
│   ├── biology/         # Genomics (DNABERT2), protein analysis
│   ├── chemistry/       # Computational chemistry, molecular analysis
│   ├── engineering/     # Materials science, manufacturing
│   ├── mathematics/     # Core mathematical algorithms
│   ├── medicine/        # Medical imaging (DICOM/NIfTI), clinical validation
│   ├── physics/         # Quantum computing (VQE, QAOA), simulations
│   └── neuroscience/    # Brain imaging, neural network analysis
├── routers/             # 130+ FastAPI routers (automatically registered)
├── services/            # 160+ business logic services
├── core/                # Database, config, logging, telemetry
├── autonomous/          # Multi-agent research system
├── models/              # Pydantic v2 data models
└── infrastructure/      # Cache, monitoring, distributed systems
```

### Router Registry System

Routers are automatically discovered and registered by domain. Configuration is in `app/routers/router_registry.py`:

```python
ROUTER_CONFIG = {
    'mathematics': [...],
    'scientific': [...],
    'infrastructure': [...],
    # Each router specifies: name, module, router_var, prefix, tags, lazy_load
}
```

To add a new router:
1. Create router file in `app/routers/` with a router variable (e.g., `my_feature_router`)
2. Add configuration to `ROUTER_CONFIG` in `router_registry.py`
3. The router is automatically registered on startup

### Autonomous Multi-Agent System

The system coordinates specialized AI agents for scientific research:

- **Orchestrator** (llama-3.3-70b-versatile via Groq) - Decomposes goals, plans experiments
- **Bio Hypothesis** (kimi-k2-instruct via Groq) - Generates falsifiable biological hypotheses
- **PhysChem Coder** (qwen3-32b via Groq) - Designs computational experiments
- **Reviewer** (llama-3.3-70b-versatile via Groq) - Critical evaluation and evidence synthesis
- **Publisher** (kimi-k2-instruct via Groq) - Report generation and documentation

**Production**: Uses **Groq API** for high-performance inference.
**Local development**: Can fallback to **Ollama** (uncomment in `config/agents.yaml`).

Configuration: `config/agents.yaml`

Key components:
- `app/autonomous/core/` - Agent coordination and orchestration
- `app/autonomous/pipelines/` - Multi-stage research workflows
- `app/autonomous/evaluation/` - Hypothesis validation and metrics

### Service Architecture

Services implement domain logic and are organized by responsibility:

- **Domain Services** - Scientific computations (e.g., `ai_scientist_service.py`, `advanced_earth_sciences_service.py`)
- **Infrastructure Services** - Caching, monitoring, async processing
- **Orchestration Services** - Workflow coordination (`master_orchestration_service_refactored.py`)
- **Data Services** - Persistence, versioning, provenance

Services should extend `BaseService` when available and follow consistent error handling patterns.

## Key Patterns and Conventions

### Pydantic v2 Models

All models use Pydantic v2 with `ConfigDict`:

```python
from pydantic import BaseModel, ConfigDict

class MyModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        arbitrary_types_allowed=False
    )

    field_name: str
    # ... fields
```

**Never use** the deprecated `class Config` pattern.

### Router Definition Pattern

```python
from fastapi import APIRouter

my_feature_router = APIRouter()

@my_feature_router.post("/endpoint")
async def handler(data: MyModel):
    # Implementation
    return {"success": True}
```

Router variable names must match the `router_var` in `router_registry.py`.

### Error Handling

Use consistent error handling with logging:

```python
import logging
logger = logging.getLogger(__name__)

try:
    result = perform_operation()
    return {"success": True, "data": result}
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    logger.exception("Unexpected error")
    raise HTTPException(status_code=500, detail="Internal server error")
```

### Async by Default

Most operations are async. Use `async def` for route handlers and service methods that perform I/O:

```python
@router.post("/process")
async def process_data(data: InputModel):
    result = await service.process_async(data)
    return result
```

### Anti-Patterns to Avoid

**1. Destructors with domain-specific exceptions:**
```python
# ❌ WRONG - ImportError during shutdown
def __del__(self):
    try:
        import shutil
        shutil.rmtree(self.temp_dir)
    except ChemistryError:  # Won't catch ImportError!
        pass

# ✅ CORRECT - Catch all exceptions
def __del__(self):
    try:
        import shutil
        import os
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    except Exception:
        pass
```

**2. Heavy imports at module level:**
```python
# ❌ WRONG - Slows startup
from rdkit import Chem
from transformers import AutoModel

# ✅ CORRECT - Lazy loading
def analyze_molecule(smiles: str):
    from rdkit import Chem
    return Chem.MolFromSmiles(smiles)
```

**3. Services without BaseService:**
```python
# ❌ WRONG
class MyService:
    pass

# ✅ CORRECT
from app.core.base_service import BaseService

class MyService(BaseService):
    def __init__(self):
        super().__init__("MyService")
```

### Configuration Management

Configuration is centralized in `app/core/config.py` and domain-specific YAML files:

- `config/agents.yaml` - Multi-agent configuration
- `config/models.yaml` - Model registry
- `config/plausibility.yaml` - Hypothesis evaluation
- `config/ethics_policy.yaml` - Safety gates
- `.env` - Environment variables (database, API keys)

Load config through the centralized config service, not directly.

## Database and Persistence

### SQLAlchemy ORM

Database setup is in `app/core/database.py`:

```python
from app.core.database import get_db

@router.get("/items")
async def get_items(db: Session = Depends(get_db)):
    return db.query(MyModel).all()
```

### Key Tables

- `mathematical_conjectures` - Hypothesis tracking
- `hypothesis_persistence` - Experiment results
- `reproducibility_records` - Reproducibility metadata
- `migrations` - Alembic version tracking

### Migrations

Located in `alembic/versions/`. Always create migrations for schema changes:

```bash
alembic revision --autogenerate -m "add new field to table"
alembic upgrade head
```

## Testing Conventions

### pytest Configuration

Configuration in `pytest.ini`:
- `asyncio_mode = auto` - Automatic async test detection
- Deprecation warnings are filtered to reduce noise
- Concise output by default (`-q`)

### Test Organization

```
tests/
├── unit/          # Fast, isolated tests (mock dependencies)
├── integration/   # Test multiple components together
├── smoke/         # Quick sanity checks for critical paths
├── e2e/           # Full end-to-end workflows
└── conftest.py    # Shared fixtures
```

### Writing Tests

```python
import pytest
from fastapi.testclient import TestClient

@pytest.mark.asyncio
async def test_async_operation():
    result = await service.process()
    assert result.success

def test_endpoint(client: TestClient):
    response = client.post("/api/endpoint", json={...})
    assert response.status_code == 200
```

Use `@pytest.mark.asyncio` for async tests. Fixtures are in `tests/conftest.py`.

## Scientific Computing Stack

The platform integrates extensive scientific libraries:

**Core Scientific:**
- NumPy, SciPy, pandas - Numerical computing
- SymPy - Symbolic mathematics
- scikit-learn, PyTorch - Machine learning
- statsmodels, PyMC, arviz - Statistical modeling

**Domain-Specific:**
- Qiskit, Cirq - Quantum computing
- RDKit, OpenBabel - Chemistry
- BioPython, scanpy - Biology/genomics
- pyvista, PyMatGen - Materials science
- Transformers, LangChain - AI/NLP

**Infrastructure:**
- FastAPI, uvicorn - Web framework
- SQLAlchemy, Alembic - Database ORM/migrations
- Redis - Caching layer
- MLflow - Experiment tracking

## Important Directories

- `docs/` - Comprehensive documentation (architecture, guides, API specs)
- `config/` - YAML configuration files
- `scripts/` - Utility scripts (QA, tools, analysis, maintenance)
- `examples/` - Usage examples for various scientific domains
- `notebooks/` - Jupyter notebooks for exploration
- `data/` - Sample datasets (not committed, use DVC)
- `models/` - Trained model artifacts

## CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/ci.yml`) runs:

1. **Build & Test** - pytest with coverage (≥60%), linting (ruff), security (bandit), dependency audit
2. **Manifest Validation** - Validates model manifests against JSON schema
3. **Signature Verification** - Cryptographic verification of model integrity
4. **Merkle Verification** - Builds and verifies Merkle tree for reproducibility
5. **Data Validation** - Runs data quality checks
6. **API Contract & Fuzzing** - OpenAPI contract tests and fuzz testing
7. **Reproducible Bundle** - Generates reproducible research bundles

All gates must pass before merging.

## Security and Ethics

The platform implements multi-layer safety validation:

- **Ethics Gate** (`app/ethics_gate.py`) - Blocks potentially harmful requests
- **Risk Assessment** (`app/risk_policy.py`) - Domain-specific risk scoring (bio, chem, clinical)
- **Integrity Validation** (`app/integrity_core.py`) - SHA-256 hashes and blockchain verification
- **License Compliance** - Automated checking in validation layers
- **Secrets Detection** - Pre-commit hook prevents credential commits

Review `config/ethics_policy.yaml` before modifying safety systems.

## Common Development Tasks

### Adding a New Scientific Domain

1. Create domain directory: `app/domains/my_domain/`
2. Add domain routers: `app/domains/my_domain/routers/`
3. Implement services: `app/domains/my_domain/services/`
4. Register in domain registry: `app/domains/registry.py`
5. Add tests: `tests/unit/test_my_domain_service.py`

### Adding a New Router

1. Create router file: `app/routers/my_feature.py`
2. Define router: `my_feature_router = APIRouter()`
3. Add to `ROUTER_CONFIG` in `app/routers/router_registry.py`
4. Test at `/docs` endpoint

### Debugging Startup Issues

If startup fails:
1. Check `main_refactored.py` lifespan logs for initialization errors
2. Verify database connection in `.env`
3. Ensure all router modules exist and have correct `router_var`
4. Check for circular imports in service layer
5. Review router registry config for typos in module paths

**Common errors and solutions:**

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError: experiment_scheduler_service` | Shim exists at `app/services/experiment_scheduler_service.py` |
| `AttributeError: module has no attribute 'xxx_router'` | Match `router_var` with actual variable name |
| `ImportError: sys.meta_path is None` on shutdown | Catch `Exception` in `__del__`, not domain errors |
| `Redis connection refused` | Safe to ignore - falls back to in-memory |

**Quick health check:**
```bash
"/Volumes/Ganador disk/atlas/.venv_new/bin/python" -c "from main_refactored import app; print('OK')"

### Performance Optimization

- Use lazy loading for heavy imports
- Cache expensive computations with `@lru_cache` or Redis
- Profile with `app/performance_profiler.py`
- Monitor metrics via `/metrics` endpoint
- Check memory usage patterns in logs

## Additional Resources

- **Architecture**: `docs/architecture.md`
- **Architecture Improvements**: `docs/ARCHITECTURE_IMPROVEMENTS.md` (technical debt and improvement plan)
- **Router Registry**: `docs/router_registry.md`
- **Entry Points**: `docs/app_entrypoints.md`
- **Configuration**: `docs/configuration.md`
- **Index**: `docs/INDEX.md` (complete documentation map)
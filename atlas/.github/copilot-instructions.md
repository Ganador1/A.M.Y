# GitHub Copilot Instructions for AXIOM ATLAS

## Project Overview

AXIOM ATLAS is an **autonomous scientific research platform** combining multi-agent AI systems with scientific computing across mathematics, physics, chemistry, biology, medicine, and engineering. The system generates hypotheses, designs experiments, executes workflows, and validates results with reproducibility guarantees.

**Key capabilities**: 130+ FastAPI routers, 160+ services, autonomous multi-agent research, workflow orchestration, hypothesis validation, and industrial-grade scientific computing.

**Tech Stack**: FastAPI + Pydantic v2 + SQLAlchemy + Alembic + Redis (optional) + Ollama (LLMs) + PostgreSQL + pytest + 150+ scientific libraries (SymPy, RDKit, Qiskit, BioPython, PyTorch, etc.)

## Environment & Dependencies (Updated Dec 2025)

- **Active virtualenv**: `.venv_new` (Python 3.13.5). Always invoke Python tooling via `"/Volumes/Ganador disk/atlas/.venv_new/bin/python" ...` to avoid `python: command not found` in VS Code tasks.
- **Freshly provisioned packages**: `mlflow`, `anthropic`, `openai`, `ollama`, `groq`, and `Faker` are now installed and required by their respective routers/services (MLflow registry, multimodal reasoning, scientific hypothesis agent, synthetic data generation).
- **LLM Provider**: Production uses **Groq API** with high-performance models (`llama-3.3-70b-versatile`, `qwen3-32b`, `kimi-k2-instruct`). Local development can fallback to Ollama.
- **Autonomous Research Agent**: New feature (`run_agent_with_tools.py`) with 44+ dynamic tools across 5 domains (mathematics, chemistry, biology, physics, statistics). Uses modern LangChain ReAct pattern. Features iterative peer review loop that continues until paper acceptance (score ≥ target_score), auto-extends iterations if showing progress, and returns structured results `{status, final_score, iterations_used, paper, review}`.
- **Redis**: Optional. When not running, services fall back to in-memory caches; startup logs will emit a warning but can be ignored for local development.
- **GPU / MPS**: Apple MPS is auto-selected when present. Quantum and astronomy services log capability warnings if optional toolkits (e.g., Pennylane, Photutils, SciPy extras) are missing.
- **Configuration validation**: Application bootstrapping now validates key YAML files (agents, models, ethics, etc.) on import. Keep configs in sync or imports will fail early.
- **MLflow registry fallback**: The router now degrades gracefully if `mlflow` is missing, returning informative errors rather than crashing the app. Ensure the dependency and tracking server are available in production.

### VS Code Tasking & Smoke Checks

- All workspace tasks call the interpreter directly: `"/Volumes/Ganador disk/atlas/.venv_new/bin/python" ...`. When adding new entries keep that quoting (wrap the path in escaped double quotes) instead of activating `.venv`.
- The `Quick import smoke` task provides a fast import sanity check without booting Uvicorn. You can run the same payload manually:
    ```bash
    "/Volumes/Ganador disk/atlas/.venv_new/bin/python" - <<'PY'
    import importlib
    for mod in (
            "app.models.database_models",
            "app.services.hypothesis_persistence",
            "app.routers.hypothesis_persistence",
    ):
            importlib.import_module(mod)
    print("OK")
    PY
    ```
- Prefer the bundled tasks for focused pytest runs (`Run unit tests: data_versioning`, `Run unit tests: hypothesis_persistence`, etc.). They already pin the interpreter and flags, so the same commands in a terminal should mirror their arguments exactly.

## Critical Architecture Patterns

### Dual Entry Points (ALWAYS Use Refactored)

```bash
# ✅ PREFERRED - Modular architecture with lazy loading
uvicorn main_refactored:app --host 0.0.0.0 --port 8000 --reload

# ❌ LEGACY - Only for backwards compatibility
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Why**: `main_refactored.py` provides 60-80% faster startup and 40-60% lower memory through automatic router registry and lazy loading. See `docs/app_entrypoints.md`.

### Router Registry System (Auto-Discovery)

Routers are **automatically registered** via `app/routers/router_registry.py`. Configuration structure:

```python
ROUTER_CONFIG = {
    'domain': [
        {
            'name': 'feature',
            'module': 'app.routers.feature',
            'router_var': 'feature_router',  # Must match variable name in module
            'prefix': '/api/domain/feature',
            'tags': ['feature', 'domain'],
            'lazy_load': True  # Defers import until first request
        }
    ]
}
```

**Adding new routers**:
1. Create `app/routers/my_feature.py` with `my_feature_router = APIRouter()`
2. Add configuration to `ROUTER_CONFIG` in `router_registry.py`
3. Router auto-registers on startup - NO manual imports in main.py

**Common mistakes**:
- Forgetting to match `router_var` with actual variable name causes `AttributeError`.
- Leaving routers pointing to legacy module paths (e.g., `app.domains.*`) now requires lightweight compatibility wrappers under `app/routers/` that re-export the domain routers.

### Pydantic v2 Migration (CRITICAL)

```python
# ✅ CORRECT - Pydantic v2
from pydantic import BaseModel, ConfigDict

class MyModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )
    field: str

# ❌ WRONG - Deprecated v1 pattern
class MyModel(BaseModel):
    class Config:  # Don't use this!
        orm_mode = True
```

**All models must use `model_config = ConfigDict(...)`**. This is enforced across 160+ services.

### Async-First Pattern

```python
# ✅ Route handlers are async
@router.post("/process")
async def process_data(data: InputModel):
    result = await service.process_async(data)
    return result

# ✅ Services extend BaseService
from app.services.base_service import BaseService

class MyService(BaseService):
    async def process_request(self, request_data: Dict) -> Dict:
        # Implementation
        pass
```

**All I/O operations must be async**. Use `async def` for database queries, file operations, external API calls.

## Domain-Driven Organization

```
app/
├── domains/              # Scientific domain implementations
│   ├── biology/         # DNABERT2, genomics, protein analysis
│   ├── chemistry/       # RDKit, molecular dynamics, quantum chemistry
│   ├── engineering/     # Materials science, additive manufacturing
│   ├── mathematics/     # SymPy, numerical methods, optimization
│   ├── medicine/        # DICOM/NIfTI imaging, clinical validation
│   ├── physics/         # Quantum computing (Qiskit/Cirq), plasma physics
│   └── neuroscience/    # Brain imaging, neural networks
├── routers/             # 130+ auto-registered FastAPI endpoints
├── services/            # 160+ business logic services
├── core/                # Database, config, logging, telemetry
├── autonomous/          # Multi-agent research coordination
│   ├── pipelines/       # Research workflow orchestration
│   ├── evaluation/      # Hypothesis validation
│   └── generators/      # Scientific hypothesis generation
└── infrastructure/      # Caching, monitoring, distributed systems
```

**Pattern**: Domain services in `app/domains/{domain}/services/`, routers in `app/routers/` (flat namespace for auto-discovery).

## Multi-Agent Autonomous System

**5 specialized agents** coordinate scientific research cycles:

```yaml
# config/agents.yaml (Production - Groq API)
roles:
  orchestrator:
    model: llama-3.3-70b-versatile  # Planning and decomposition
    provider: groq
  bio_hypothesis:
    model: moonshotai/kimi-k2-instruct  # Biological hypothesis generation
    provider: groq
  physchem_coder:
    model: qwen/qwen3-32b  # Computational experiment design
    provider: groq
  reviewer:
    model: llama-3.3-70b-versatile  # Critical evaluation
    provider: groq
  publisher:
    model: moonshotai/kimi-k2-instruct  # Report synthesis
    provider: groq
```

**Local development** (Ollama fallback):
```yaml
# Uncomment in agents.yaml for offline development
orchestrator:
  model: llama3:8b
  provider: ollama
```

**Key endpoints**:
- `POST /api/plausibility/evaluate` - Evaluate hypothesis plausibility
- `POST /api/scheduler/jobs` - Schedule autonomous experiments
- `POST /api/research-cycle/start` - Launch closed-loop research

**Workflow**: Orchestrator → Hypothesis Generator → Experiment Designer → Executor → Reviewer → Publisher

## Essential Developer Workflows

### Running Tests

```bash
# Quick smoke tests (< 1 min)
pytest tests/smoke/ -v

# Domain-specific tests
pytest tests/unit/test_arithmetic.py -v

# Full suite with coverage
pytest --cov=app --cov-report=term-missing

# Async tests auto-detected (asyncio_mode=auto in pytest.ini)
```

**Test organization**: `tests/unit/` (fast, mocked), `tests/integration/` (multi-component), `tests/smoke/` (critical paths), `tests/e2e/` (full workflows).

### Database Migrations

```bash
# Create migration (auto-detects schema changes)
alembic revision --autogenerate -m "add hypothesis table"

# Apply migrations
alembic upgrade head

# Check status
python scripts/tools/migration_status.sh
```

**SQLAlchemy models** in `app/models/database_models.py`. Use `get_db()` dependency:

```python
from app.core.database import get_db

@router.post("/items")
async def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = Item(**item.dict())
    db.add(db_item)
    db.commit()
    return db_item
```

### Configuration Management

**Centralized config** in `app/config/`:
- `agents.yaml` - Multi-agent model configuration
- `ethics_policy.yaml` - Safety gates and risk assessment
- `plausibility.yaml` - Hypothesis evaluation weights
- `.env` - Secrets, database URLs, API keys

**Never hardcode credentials**. Use `app.core.config.settings`:

```python
from app.config import settings

ollama_url = settings.OLLAMA_BASE_URL  # From .env
```

## Critical Patterns & Gotchas

### Router Variable Naming

```python
# ✅ CORRECT - Variable name matches router_var in registry
arithmetic_router = APIRouter()

# ❌ WRONG - Mismatch causes AttributeError on startup
router = APIRouter()  # Unless router_var='router' in config
```

### Error Handling Standard

```python
import logging
logger = logging.getLogger(__name__)

@router.post("/analyze")
async def analyze(data: AnalysisInput):
    try:
        result = await service.analyze(data)
        return {"success": True, "data": result}
    except ValidationError as e:
        logger.error(f"Validation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error in analysis")
        raise HTTPException(status_code=500, detail="Internal error")
```

**Always**: (1) Log with context, (2) Distinguish validation vs. system errors, (3) Use `logger.exception()` for unexpected errors.

### Service Layer Pattern

```python
from app.services.base_service import BaseService

class MyService(BaseService):
    def __init__(self):
        super().__init__("MyService")  # Required name for logging
    
    async def process_request(self, request_data: Dict) -> Dict:
        # Abstract method from BaseService - must implement
        operation = request_data.get('operation')
        if operation == 'analyze':
            return await self._analyze(request_data)
        raise ValueError(f"Unknown operation: {operation}")
```

**Services inherit from `BaseService`** for consistent logging, health checks, and telemetry.

**BaseService provides**:
- `log_request(request_data)` - Log incoming requests
- `log_response(response_data)` - Log responses
- `handle_error(error, context)` - Standardized error handling
- Abstract `process_request()` - Must be implemented by subclasses

**Optional mixin**:
```python
from app.services.base_service import ScientificServiceMixin

class MyScientificService(BaseService, ScientificServiceMixin):
    required_input_fields = ['data', 'parameters']  # Auto-validated
    
    async def process_request(self, request_data: Dict) -> Dict:
        # Automatic validation
        validation = self.validate_scientific_input(request_data)
        if not validation['valid']:
            raise ValueError(validation['error'])
        
        results = await self._compute(request_data)
        return self.format_scientific_output(results)  # Adds metadata
```

### ⚠️ Anti-Patterns to Avoid

#### 1. Destructors with Domain-Specific Exceptions
```python
# ❌ WRONG - ImportError during shutdown crashes Python
def __del__(self):
    try:
        import shutil
        shutil.rmtree(self.temp_dir)
    except ChemistryError:  # Won't catch ImportError!
        pass

# ✅ CORRECT - Catch all exceptions including ImportError
def __del__(self):
    try:
        import shutil
        import os
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    except Exception:  # Catches ImportError during shutdown
        pass
```

#### 2. Wrong Exception Domain in Services
```python
# ❌ WRONG - BiologyError in a physics service makes no sense
class QuantumChemistryService:
    def __del__(self):
        try:
            # cleanup
        except BiologyError:  # Semantically wrong!
            pass

# ✅ CORRECT - Use appropriate exception hierarchy
from app.exceptions.domain.chemistry import ChemistryError
from app.exceptions.base import AtlasInfrastructureError
```

#### 3. Heavy Imports at Module Level
```python
# ❌ WRONG - Slows startup, breaks tests
from rdkit import Chem  # 500ms import
from transformers import AutoModel  # 2s import

# ✅ CORRECT - Lazy loading inside functions
def analyze_molecule(smiles: str):
    from rdkit import Chem  # Import when needed
    return Chem.MolFromSmiles(smiles)
```

#### 4. Services Without BaseService Inheritance
```python
# ❌ WRONG - Loses logging, health checks, telemetry
class MyService:
    def __init__(self):
        pass

# ✅ CORRECT - Consistent service pattern
from app.core.base_service import BaseService

class MyService(BaseService):
    def __init__(self):
        super().__init__("MyService")  # Name for logging
    
    async def process_request(self, request_data: Dict) -> Dict:
        # Required abstract method
        pass
```

#### 5. Router Variable Name Mismatch
```python
# In app/routers/my_feature.py:
router = APIRouter()  # Variable named 'router'

# In router_registry.py:
{
    'router_var': 'my_feature_router',  # ❌ Mismatch!
    ...
}

# ✅ CORRECT - Match names or use fallback
my_feature_router = APIRouter()  # Matches registry
# OR
{'router_var': 'router', ...}  # Match actual name
```

### Data Versioning Guardrails

- `DataVersioningService` enforces a per-file cap via `MAX_VERSION_FILE_BYTES` (defaults to 500 MB). Set it in `.env` when handling very large datasets to prevent silent truncation.
- Enable `STRICT_DATA_PATHS=1` together with `ALLOWED_DATA_ROOT=/absolute/path` to block versioning outside the workspace. Passing `allow_external_path=True` in the payload is the only opt-out.
- DVC integration is opportunistic: if the `dvc` binary is missing the service returns success but logs a warning. Keep this behavior when extending the command runner (return code 127 should not crash the request).
- Version metadata is stored under `data/versions.json`. Use the provided helper methods instead of editing the file manually so hashes and history stay consistent.

### Hypothesis Persistence & Risk Gate

- When scripting against `HypothesisPersistenceService`, call `from app.database import init_database; init_database()` once the env vars are in place. Tests set `ENABLE_DATABASE=true`, `DATABASE_URL=sqlite:///...`, `SKIP_DB_INIT=true`, and `PYTEST_RUNNING=1` to point to an isolated SQLite file.
- The compliance gate blocks any `CRITICAL` risk outcome and `HIGH` entries without both `justification` and `justification_signature`. Expect callers to handle the `risk_level` field even on successful responses.
- `add_evidence` and `add_refinement` update counters through direct SQL; wrap new writes in transactions and roll back on exceptions to avoid partial counter updates.

### Model Registry Storage

- `ModelManagementService` persists to `app/services/model_management_service.REGISTRY_PATH` (default JSON file under the repo). Monkeypatch this path in tests to a tmp location to avoid polluting real artifacts.
- `register_model`, `update_model`, and `list_models` all operate on that shared file. Acquire the service once per test to reuse the in-memory cache, mirroring the fixture in `tests/unit/test_model_management_service.py`.

## Scientific Computing Stack

**Core libraries** (150+ dependencies):
- **Math**: SymPy (symbolic), NumPy/SciPy (numerical)
- **ML/AI**: PyTorch, scikit-learn, Transformers, LangChain
- **Quantum**: Qiskit, Cirq, QuTiP
- **Chemistry**: RDKit, OpenBabel, PySCF
- **Biology**: BioPython, scanpy (genomics)
- **Physics**: PyMatGen (materials), PyVista (visualization)

**Import pattern for heavy libs** (lazy loading):

```python
# ✅ Import inside function for lazy loading
def analyze_molecule(smiles: str):
    from rdkit import Chem  # Heavy import deferred
    mol = Chem.MolFromSmiles(smiles)
    return mol
```

## Database & Persistence

### SQLAlchemy Models & Migrations

**ORM models** in `app/models/database_models.py` with comprehensive documentation:

```python
from app.core.database import Base
from sqlalchemy import Column, Integer, String, JSON, DateTime

class Calculation(Base):
    """Stores mathematical calculation history"""
    __tablename__ = "calculations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    operation_type = Column(String(50), index=True)
    input_data = Column(JSON)
    result_data = Column(JSON)
    execution_time = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**Key tables**:
- `users` - User authentication and profiles
- `calculations` - Computation history
- `cached_results` - Performance caching
- `system_metrics` - Monitoring data
- `scientific_datasets` - Research data storage

**Using database in routes**:
```python
from app.core.database import get_db
from sqlalchemy.orm import Session

@router.get("/items")
async def get_items(db: Session = Depends(get_db)):
    return db.query(MyModel).all()
```

### Alembic Migrations

**Critical scripts** in `scripts/tools/`:

```bash
# Check migration status
./scripts/tools/migration_status.sh

# Apply migrations (checks PostgreSQL connectivity)
./scripts/tools/migrate_database.sh

# Create new migration
alembic revision --autogenerate -m "description"
```

**Migration workflow**:
1. Modify models in `app/models/database_models.py`
2. Generate migration: `alembic revision --autogenerate -m "add field"`
3. Review migration in `alembic/versions/`
4. Apply: `alembic upgrade head`
5. Rollback if needed: `alembic downgrade -1`

**Important**: Migrations auto-create tables, add indexes, and handle schema changes safely.

## LLM Integration (Groq + Ollama)

**Production**: Uses **Groq API** for high-performance inference:

```yaml
# config/agents.yaml (current production config)
roles:
  orchestrator:
    model: llama-3.3-70b-versatile
    provider: groq
    params:
      max_new_tokens: 4096
      temperature: 0.7
  bio_hypothesis:
    model: moonshotai/kimi-k2-instruct
    provider: groq
  physchem_coder:
    model: qwen/qwen3-32b
    provider: groq
  reviewer:
    model: llama-3.3-70b-versatile
    provider: groq
  publisher:
    model: moonshotai/kimi-k2-instruct
    provider: groq
```

**Environment setup**:
```bash
# .env for Groq (production)
GROQ_API_KEY=gsk_your_key_here

# .env for Ollama (local development)
OLLAMA_BASE_URL=http://localhost:11434
```

**Local Ollama fallback** (uncomment in agents.yaml for offline development):
```bash
# Install Ollama (macOS)
brew install ollama

# Pull required models
ollama pull llama3:8b
ollama pull mistral:7b
ollama pull codellama:7b
ollama pull qwen:7b
```

## Monitoring & Metrics

**Metrics collection** in `app/monitoring/metrics.py`:

```python
from app.monitoring.metrics import metrics

# Counter metrics
metrics.increment_counter("api_requests_total", tags={"endpoint": "/predict"})

# Gauge metrics (current value)
metrics.set_gauge("active_connections", 42)

# Histogram metrics (distributions)
metrics.record_histogram("request_duration_ms", 125.3)

# Tool adapter execution
metrics.record_tool_adapter_execution("dnabert2", success=True, duration_ms=234.5)

# Get summary
summary = metrics.get_metrics_summary()
# Returns: {"counters": {...}, "gauges": {...}, "histograms": {...}}
```

**Available endpoints**:
- `GET /metrics` - Prometheus-compatible metrics
- `GET /health` - Basic health check
- `GET /health/detailed` - System metrics (CPU, memory, disk)

**Monitoring stack** (optional):
```bash
# Start Prometheus + Grafana
cd monitoring
docker-compose up -d

# Access dashboards
open http://localhost:3000  # Grafana
open http://localhost:9090  # Prometheus
```

## Exception Hierarchy & Error Handling

AXIOM uses a **structured exception system** in `app/exceptions/`:

```python
# Base exception hierarchy
AtlasException                    # Root exception with auto-logging
├── AtlasValidationError         # Input validation failures
├── AtlasInfrastructureError     # DB, cache, storage issues
├── AtlasDomainError             # Scientific domain errors (base)
│   ├── BiologyError             # Biology domain
│   │   ├── ProteinAnalysisError
│   │   ├── SequenceAlignmentError
│   │   └── GenomicsError
│   ├── ChemistryError
│   ├── PhysicsError
│   └── MathematicsError
├── AtlasExternalError           # External API/LLM failures
└── AtlasSecurityError           # Security & ethics violations
```

**Using exceptions**:
```python
from app.exceptions.base import AtlasException, handle_atlas_errors_async
from app.exceptions.domain.biology import GenomicsError

# Raise domain-specific errors
raise GenomicsError(
    "Sequence alignment failed",
    error_code="SEQ_ALIGN_001",
    details={"sequence_length": 1024, "algorithm": "BLAST"}
)

# Decorator auto-converts generic exceptions
@handle_atlas_errors_async("Failed to process data")
async def process_data(data):
    # Any Exception → AtlasException with context
    pass
```

**All exceptions serialize to dict** via `.to_dict()` for API responses and include auto-logging.

## Security Headers & Middleware

**Security middleware stack** in `app/middleware/`:

```python
# app/middleware/security_headers.py
SecurityHeadersMiddleware  # Adds 15+ security headers
├── X-Content-Type-Options: nosniff
├── X-Frame-Options: DENY
├── Strict-Transport-Security (HSTS)
├── Content-Security-Policy (configurable by env)
├── Permissions-Policy (restrictive defaults)
└── Cross-Origin-* headers
```

**CSP policies by environment**:
```python
from app.middleware.security_headers import SecurityHeadersConfig

# Production: strict CSP
csp = SecurityHeadersConfig.get_csp_policy("production")

# Development: allows eval/inline
csp = SecurityHeadersConfig.get_csp_policy("development")
```

**Other middleware**:
- `trace_id_middleware.py` - Request tracing with X-Request-ID
- `auth_middleware.py` - Authentication/authorization
- `profiling.py` - Performance profiling

## Caching System

**Unified caching** in `app/cache/unified_cache.py`:

```python
# Features
CacheBackend: MEMORY | REDIS | FILE
CompressionType: NONE | GZIP | ZLIB
EvictionPolicy: LRU | LFU | TTL | RANDOM

# Configuration
@dataclass
class CacheConfig:
    backend: CacheBackend = CacheBackend.MEMORY
    max_memory_size: int = 100 * 1024 * 1024  # 100MB
    default_ttl: int = 3600
    compression: CompressionType = CompressionType.GZIP
    # ... more options
```

**Redis fallback**: System gracefully degrades to in-memory if Redis unavailable. Set `ENABLE_REDIS_CACHE=false` in `.env` to disable.

## Security & Ethics

**Multi-layer validation** before execution:

1. **Ethics Gate** (`app/compliance/ethics_gate.py`) - Blocks harmful requests via heuristic scoring
2. **Risk Assessment** (`app/risk_policy.py`) - Domain-specific scoring (bio/chem/clinical)
3. **Integrity Validation** (`app/integrity_core.py`) - SHA-256 hashing, blockchain verification
4. **License Compliance** - Automated checking in validation pipeline

**Review `config/ethics_policy.yaml` before modifying safety systems**.

## Common Tasks

### Adding New Domain Service

```bash
# 1. Create domain structure
mkdir -p app/domains/my_domain/{services,models}

# 2. Implement service (must extend BaseService)
cat > app/domains/my_domain/services/my_service.py
# (extend BaseService, implement process_request)

# 3. Create router
cat > app/routers/my_domain.py
# (define my_domain_router)

# 4. Register in router_registry.py
# Add to ROUTER_CONFIG['scientific']

# 5. Add tests
cat > tests/unit/test_my_domain_service.py
```

### Running Tests (pytest)

**pytest configuration** in `pytest.ini`:
```ini
[pytest]
asyncio_mode = auto              # Auto-detect async tests
testpaths = tests
python_files = test_*.py
markers =
    smoke: Smoke tests (fast, basic functionality)
    integration: Integration tests (slower)
    unit: Unit tests (individual components)
```

**Shared fixtures** in `tests/conftest.py`:
```python
@pytest.fixture
def client():
    """FastAPI TestClient with in-memory database"""
    # Auto-configured SQLite :memory: for isolation
    
@pytest.fixture
def test_db():
    """SQLAlchemy session for database tests"""
    # Transaction rollback after each test
```

**Running tests**:
```bash
# All tests
pytest

# Specific markers
pytest -m smoke          # Fast smoke tests
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests

# With coverage
pytest --cov=app --cov-report=term-missing

# Specific file/function
pytest tests/unit/test_arithmetic.py::test_addition -v
```

**Test environment**: Automatically set to SQLite in-memory, Redis disabled, debug mode enabled.

### Targeted Regression Suites

- Data versioning safeguards: `"/Volumes/Ganador disk/atlas/.venv_new/bin/python" -m pytest -q tests/unit/test_data_versioning_service.py` (validates size limits via `MAX_VERSION_FILE_BYTES` and path policies controlled by `STRICT_DATA_PATHS`/`ALLOWED_DATA_ROOT`).
- Hypothesis persistence CRUD flow: `"/Volumes/Ganador disk/atlas/.venv_new/bin/python" -m pytest -q tests/unit/test_hypothesis_persistence.py` (fixture sets `ENABLE_DATABASE=true`, `SKIP_DB_INIT=true`, and runs `init_database()` against a temp SQLite file).
- Offline model registry: `"/Volumes/Ganador disk/atlas/.venv_new/bin/python" -m pytest -q tests/unit/test_model_management_service.py` (tests reroute `REGISTRY_PATH` to a tmp directory so copy the monkeypatch pattern for new cases).
- MLflow registry integration: `"/Volumes/Ganador disk/atlas/.venv_new/bin/python" -m pytest -q tests/unit/test_mlflow_registry_service.py` (requires the `mlflow` package installed in `.venv_new`).

### Debugging Startup Failures

```python
# Check main_refactored.py lifespan logs
# Common issues:
# - Router module path typo in router_registry.py
# - Missing router_var in module
# - Circular imports in services
# - Database connection failure (.env misconfigured)
```

**Logs show**: Router registration progress, service initialization, health checks.

### Utility Scripts

**Essential scripts** in `scripts/`:

```bash
# Database
./scripts/tools/migration_status.sh      # Check migration state
./scripts/tools/migrate_database.sh      # Apply migrations

# Testing & QA
./scripts/qa/test_scientific_dependencies.sh  # Verify scipy/numpy/etc
./scripts/qa/validate_optimizations.sh        # Performance validation

# Maintenance
./scripts/maintenance/batch_process_routers.sh  # Router batch operations

# Monitoring
./scripts/start_grafana.sh               # Start monitoring stack
./scripts/stop_grafana.sh                # Stop monitoring

# Deployment
./scripts/tools/deploy.sh                # Production deployment
./scripts/tools/deploy-k8s.sh            # Kubernetes deployment
```

**All scripts validate**:
- Tool availability (`command -v`)
- Timeout protection (`timeout 10s`)
- Error handling (`set -euo pipefail`)
- No credential logging (security policy)

### Performance Profiling

```python
# Built-in profiler
from app.performance_profiler import profile_async

@profile_async
async def expensive_operation():
    # Auto-logged timing and resource usage
    pass

# Metrics endpoint
# GET /metrics - Prometheus-style metrics
```

## Autonomous Research Pipelines

**Pipeline structure** in `app/autonomous/pipelines/`:

```python
# Example: materials_loop.py
class MaterialsLoop:
    def __init__(self, provider=None, state=None):
        self.state = state or StateManager()
        self.scorer = PriorityScorer()
        self.scheduler = TaskScheduler(diversity_quota=6)
        self.budget = BudgetAllocator(total_budget=9.0)
        self.materials_service = MaterialsDiscoveryService()
        
    async def run_iteration(self, limit=10):
        # 1. Discover candidates
        candidates = await self._get_candidates(limit)
        
        # 2. Score and prioritize
        scored = self.scorer.score(candidates)
        
        # 3. Schedule experiments
        tasks = self.scheduler.schedule(scored)
        
        # 4. Execute and collect results
        results = await self._execute_tasks(tasks)
        
        # 5. Update state and learn
        self.state.update(results)
```

**Available loops**:
- `biology_loop.py` - Protein/genomics research
- `chemistry_loop.py` - Molecular discovery
- `materials_loop.py` - Materials science
- `quantum_loop.py` - Quantum computing experiments
- `mathematics_loop.py` - Mathematical conjectures

**Key components**:
- `StateManager` - Iteration tracking and history
- `PriorityScorer` - Multi-objective scoring
- `TaskScheduler` - Experiment scheduling with diversity
- `BudgetAllocator` - Resource allocation
- `NoveltyAssessor` - Novelty detection
- `ToolEvidenceBridge` - Evidence aggregation

## Environment Variables & Configuration

**Critical `.env` variables**:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/axiom_meta4
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# Application
ENV=development  # development|staging|production
SECRET_KEY=<generate-with-secrets.token_urlsafe(32)>
HOST=0.0.0.0
PORT=8000

# LLM (Ollama)
OLLAMA_BASE_URL=http://localhost:11434
ORCHESTRATOR_MODEL=llama3:8b
BIO_HYPOTHESIS_MODEL=mistral:7b
PHYSCHEM_CODER_MODEL=codellama:7b
REVIEWER_MODEL=qwen:7b
PUBLISHER_MODEL=llama3:8b

# Caching
ENABLE_REDIS_CACHE=false  # true for production
REDIS_URL=redis://localhost:6379
REDIS_TTL=300

# Async Tool Adapter
ASYNC_TOOL_MAX_CONCURRENT=5
ASYNC_TOOL_TIMEOUT=30.0
ASYNC_TOOL_RETRY_ATTEMPTS=2
ASYNC_TOOL_FAIL_FAST=false

# Monitoring
LOG_LEVEL=INFO  # DEBUG|INFO|WARNING|ERROR|CRITICAL
ENABLE_OTEL=false  # OpenTelemetry tracing

# Security
VALIDATION_MATRIX_DB=./data/validation_matrix.db
VALIDATION_RETENTION_DAYS=30
```

**YAML configs** in `config/`:
- `agents.yaml` - Multi-agent roles and models
- `ethics_policy.yaml` - Safety gates and risk thresholds
- `plausibility.yaml` - Hypothesis evaluation weights
- `models.yaml` - Model registry and metadata

**Access config**:
```python
from app.config import settings

# Environment variables
db_url = settings.DATABASE_URL
ollama_url = settings.OLLAMA_BASE_URL

# YAML configs (via config_loader)
from app.config.config_loader import load_config_section

agents_config = load_config_section("agents")
ethics_config = load_config_section("ethics_policy")
```

## Documentation Structure

- `docs/INDEX.md` - Complete documentation map
- `docs/architecture.md` - System architecture
- `docs/ARCHITECTURE_IMPROVEMENTS.md` - Technical debt and improvement plan
- `docs/router_registry.md` - Router auto-discovery guide
- `docs/app_entrypoints.md` - Entry point migration guide
- `docs/configuration.md` - Config system reference
- `CLAUDE.md` - Claude-specific development guidance (this file's sibling)
- `README.md` - User-facing overview

**When in doubt**: Check `docs/INDEX.md` for comprehensive topic index.

## 🔧 Troubleshooting Guide

### Common Startup Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError: experiment_scheduler_service` | Missing shim | Shim created at `app/services/experiment_scheduler_service.py` |
| `AttributeError: module has no attribute 'xxx_router'` | `router_var` mismatch in registry | Match variable name in file or use fallback `router` |
| `ImportError: sys.meta_path is None` during shutdown | `__del__` catches wrong exception | Catch `Exception` not domain-specific errors |
| `Redis connection refused` warning | Redis not running | Safe to ignore - falls back to in-memory |
| YAML validation fails on import | Config file out of sync | Check `config/*.yaml` files match expected schema |

### Test Collection Errors

If `pytest --collect-only` fails with import errors:

1. **Avoid importing `main.py` in tests** - It loads all routers
2. **Use lazy fixtures** - `tests/conftest.py` uses `_get_app()` for deferred loading
3. **Mock heavy dependencies** - RDKit, Transformers, etc.

```python
# ✅ Good test pattern - doesn't trigger full app import
def test_my_service():
    from app.services.my_service import MyService
    service = MyService()
    result = service.process({"data": "test"})
    assert result["success"]
```

### Database Issues

```bash
# Check migration status
alembic current

# If migrations are out of sync
alembic stamp head  # Mark current as applied
alembic upgrade head  # Apply pending

# Reset for development
rm -f data/*.db  # Remove SQLite files
alembic upgrade head  # Recreate
```

### Memory Issues with Scientific Libraries

```python
# Heavy libraries should be lazy-loaded
# ❌ Don't do this at module level
import torch
from transformers import AutoModel

# ✅ Load inside function when needed
def predict(data):
    import torch
    from transformers import AutoModel
    # Use and release
```

### Circular Import Resolution

If you see `ImportError: cannot import name 'X' from partially initialized module`:

1. Move import inside function (lazy import)
2. Use `TYPE_CHECKING` for type hints only
3. Create shim module to break the cycle

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.services.heavy_service import HeavyService

def my_function() -> "HeavyService":
    from app.services.heavy_service import HeavyService
    return HeavyService()
```

## 📊 Project Metrics & Health

| Metric | Current Value | Target |
|--------|---------------|--------|
| Python files | 1,220+ | - |
| Test files | 403 | - |
| Routers | 130+ | - |
| Services | 160+ | - |
| BaseService adoption | ~28% | >80% |
| Test pass rate | Verify regularly | >95% |
| Startup time (refactored) | <30s | <15s |

### Health Check Commands

```bash
# Quick import smoke test
"/Volumes/Ganador disk/atlas/.venv_new/bin/python" - <<'PY'
import importlib
for mod in (
    "app.models.database_models",
    "app.services.experiment_scheduler_service",
    "app.routers.experiment_scheduler",
):
    importlib.import_module(mod)
print("✅ Core imports OK")
PY

# Run smoke tests
"/Volumes/Ganador disk/atlas/.venv_new/bin/python" -m pytest tests/smoke/ -v --timeout=60

# Check for shutdown errors (should be clean)
"/Volumes/Ganador disk/atlas/.venv_new/bin/python" -m pytest tests/unit/test_simple.py -v
```

## Quick Reference

```bash
# Start application (ALWAYS use refactored)
uvicorn main_refactored:app --reload

# Run tests
pytest -q                          # Quick run
pytest tests/unit/ -v              # Verbose unit tests
pytest --cov=app                   # With coverage

# Database
alembic upgrade head               # Apply migrations
alembic revision --autogenerate    # Create migration

# Code quality
black app tests                    # Format
ruff check . --fix                 # Lint
mypy app                           # Type check (optional)

# API docs
# http://localhost:8000/docs       # OpenAPI Swagger UI
```

---

**Critical Rules**:
1. ✅ Use `main_refactored.py` (not main.py)
2. ✅ Pydantic v2 `model_config = ConfigDict(...)` (not `class Config`)
3. ✅ Match `router_var` in registry with actual variable name
4. ✅ Async by default for I/O operations
5. ✅ Never hardcode secrets - use `.env` and `settings`
6. ✅ Review ethics/safety config before modifying validation layers
7. ✅ Catch `Exception` in `__del__` methods (not domain errors)
8. ✅ Use lazy imports for heavy libraries (RDKit, Transformers, etc.)
9. ✅ Inherit from `BaseService` for all new services
10. ✅ Create shims when renaming/moving services to maintain compatibility

**Most common pitfalls**:
- Router registry `router_var` mismatch → `AttributeError` on startup
- `__del__` catching domain exceptions → `ImportError` during shutdown
- Module-level heavy imports → Slow startup, test collection failures
- Services without `BaseService` → Inconsistent logging and error handling

**Quick Debugging**:
```bash
# Check if app imports cleanly
"/Volumes/Ganador disk/atlas/.venv_new/bin/python" -c "from main_refactored import app; print('OK')"

# Find services not inheriting BaseService
grep -rL "BaseService" app/services/*.py | head -10

# Check for problematic __del__ methods
grep -rn "except.*Error:" app/domains/ app/services/ | grep "__del__" -A2
```

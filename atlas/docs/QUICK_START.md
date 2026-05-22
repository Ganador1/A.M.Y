# 🚀 Quick Start Guide - AXIOM ATLAS

Get AXIOM ATLAS running in **under 10 minutes**.

---

## Prerequisites

- Python 3.11 or higher
- PostgreSQL 14+ (or use Docker)
- 8GB RAM minimum
- Git

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/your-org/axiom-atlas.git
cd axiom-atlas
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Core dependencies
pip install -r requirements.txt

# Optional: Biology domain
pip install -r requirements-biology.txt

# Optional: Physics/Quantum
pip install -r requirements-physics.txt
```

### 4. Setup Database

**Option A: Local PostgreSQL**
```bash
# Create database
createdb axiom_meta4

# Run migrations
alembic upgrade head
```

**Option B: Docker**
```bash
docker-compose up -d postgres
alembic upgrade head
```

### 5. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Minimal config (edit .env):
DATABASE_URL=postgresql://localhost:5432/axiom_meta4
SECRET_KEY=your-secret-key-here
```

### 6. Run Application

```bash
# Start server (preferred method)
uvicorn main_refactored:app --reload

# Server will start at: http://localhost:8000
```

### 7. Verify Installation

```bash
# Open browser
open http://localhost:8000/docs

# Or test with curl
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "database": "connected"
}
```

---

## First API Call

### Option 1: Interactive Docs (Easiest)

1. Open http://localhost:8000/docs
2. Find **`POST /api/biology/protein/analyze`**
3. Click **"Try it out"**
4. Enter:
   ```json
   {
     "uniprot_id": "P04637"
   }
   ```
5. Click **"Execute"**

### Option 2: curl

```bash
curl -X POST "http://localhost:8000/api/biology/protein/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "uniprot_id": "P04637",
    "predict_structure": false
  }'
```

### Option 3: Python

```python
import httpx
import asyncio

async def analyze_protein():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/biology/protein/analyze",
            json={"uniprot_id": "P04637"}
        )
        return response.json()

result = asyncio.run(analyze_protein())
print(result)
```

---

## Key Endpoints to Try

### Biology

```bash
# Analyze protein
POST /api/biology/protein/analyze
{"uniprot_id": "P04637"}

# Population dynamics
POST /api/biology/population/simulate
{"model": "lotka_volterra", "initial_prey": 100}

# Biodiversity metrics
POST /api/biology/biodiversity/analyze
{"species_data": {"oak": 50, "pine": 30}}
```

### Quantum Computing

```bash
# Grover's algorithm
POST /api/quantum-computing/grover-search
{"target_state": "101", "num_qubits": 3}

# VQE optimization
POST /api/quantum-computing/vqe
{"molecule": "H2", "basis": "sto-3g"}
```

### Mathematics

```bash
# Solve differential equation
POST /api/mathematics/differential-equations/solve
{"equation": "y'' + y = 0", "initial_conditions": [0, 1]}

# Topology analysis
POST /api/mathematics/topology/homology
{"simplicial_complex": [[0,1], [1,2], [2,0]]}
```

---

## Example Workflows

### 1. Protein Analysis Pipeline

```python
import httpx
import asyncio

async def protein_pipeline(uniprot_id: str):
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Step 1: Analyze protein
        protein = await client.post(
            "/api/biology/protein/analyze",
            json={"uniprot_id": uniprot_id}
        )
        protein_data = protein.json()

        # Step 2: Check disease relevance
        if "cancer" in protein_data['disease_relevance']:
            print(f"⚠️  {protein_data['gene_name']} linked to cancer")

        # Step 3: Get interactions (if available)
        # interactions = await client.get(f"/api/biology/protein/{uniprot_id}/interactions")

        return protein_data

# Run
result = asyncio.run(protein_pipeline("P04637"))  # TP53
print(f"Analyzed: {result['gene_name']}")
```

### 2. Autonomous Research Loop

```python
from app.autonomous.pipelines.biology_loop import BiologyLoop

async def run_research():
    loop = BiologyLoop()

    # Run one iteration
    results = await loop.run_iteration(
        k_targets=5,  # Analyze 5 proteins
        enable_ethics_check=True
    )

    # Print hypotheses
    for hyp in results['hypotheses']:
        print(f"Hypothesis: {hyp['statement']}")
        print(f"Priority: {hyp['priority_score']:.2f}\n")

asyncio.run(run_research())
```

---

## Common Issues

### Database Connection Error

```bash
# Error: connection refused
# Fix: Ensure PostgreSQL is running
pg_ctl status

# Or start with Docker
docker-compose up -d postgres
```

### Import Errors

```bash
# Error: ModuleNotFoundError
# Fix: Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Port Already in Use

```bash
# Error: Port 8000 already in use
# Fix: Use different port
uvicorn main_refactored:app --port 8001
```

### Config Import Error

```bash
# Error: cannot import 'settings'
# Fix: Ensure .env exists
cp .env.example .env

# Or set manually
export DATABASE_URL=postgresql://localhost:5432/axiom_meta4
```

---

## What's Next?

### Explore Domains

- [Biology](app/domains/biology/README.md) - Genomics, proteins, population dynamics
- [Physics](app/domains/physics/README.md) - Quantum computing, simulations
- [Mathematics](app/domains/mathematics/README.md) - 22 routers for advanced math
- [Chemistry](app/domains/chemistry/README.md) - Molecular dynamics, reactions

### Try Examples

```bash
# Interactive Jupyter notebooks
pip install jupyterlab
jupyter lab docs/notebooks/

# Run example scripts
python examples/biology/protein_analysis.py
python examples/quantum/grover_demo.py
```

### Read Documentation

- [Architecture Overview](docs/architecture.md)
- [API Reference](docs/api/API_REFERENCE.md)
- [Contributing Guide](CONTRIBUTING.md)
- [Roadmaps](docs/roadmaps/)

### Run Tests

```bash
# Quick smoke tests
pytest tests/smoke/ -q

# Full test suite
pytest tests/ -v

# With coverage
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

---

## Production Deployment

### Docker Compose

```bash
# Full stack (app + postgres + redis)
docker-compose up -d

# Scale workers
docker-compose up -d --scale worker=4

# View logs
docker-compose logs -f
```

### Environment Variables

```bash
# Production .env
DATABASE_URL=postgresql://user:pass@host:5432/axiom_prod
SECRET_KEY=<strong-random-key>
REDIS_URL=redis://redis:6379
ENABLE_OTEL=true
LOG_LEVEL=INFO

# Generate secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Run with Gunicorn

```bash
# Install
pip install gunicorn uvicorn[standard]

# Run with workers
gunicorn main_refactored:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

---

## Performance Tips

### 1. Enable Caching

```python
# In .env
ENABLE_REDIS_CACHE=true
REDIS_URL=redis://localhost:6379
```

### 2. Increase DB Pool

```python
# In app/core/config.py
database_pool_size = 20  # Default: 10
database_max_overflow = 40  # Default: 20
```

### 3. Use Async Client

```python
# ✅ Good - async
async with httpx.AsyncClient() as client:
    response = await client.get(url)

# ❌ Slow - sync
response = requests.get(url)
```

---

## Getting Help

- **Documentation:** http://localhost:8000/docs
- **GitHub Issues:** [Report bugs](https://github.com/org/axiom-atlas/issues)
- **Discussions:** [Ask questions](https://github.com/org/axiom-atlas/discussions)
- **Discord:** Join our community

---

## Success! 🎉

You now have AXIOM ATLAS running locally. Try these next steps:

1. ✅ Explore the interactive API docs at `/docs`
2. ✅ Run a protein analysis (see examples above)
3. ✅ Try the autonomous BiologyLoop
4. ✅ Check out the Jupyter notebooks
5. ✅ Read the full documentation

**Happy researching!** 🚀

---

**Last Updated:** 2025-09-30
**Version:** 2.0.0

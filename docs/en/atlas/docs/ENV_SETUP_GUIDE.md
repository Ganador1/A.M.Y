> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="axiom-atlas--entorno-de-ejecución-completo"></a>
# AXIOM ATLAS – Complete Execution Environment

This document summarizes everything that must be installed and configured so that I can run:

- The smoke tests (`pytest tests/unit/test_pipeline_debug.py -q` and similar).
- The production loops (`run_all_loops_production.py`, `run_remaining_loops.py`, etc.).
- The hypothesis generator (`app/autonomous/generators/hypothesis_generator.py` and pipelines that use it).

> **Note:** The repository includes several reference virtualenvs (`.venv`, `.venv_new`, `venv_improvements`), but they do not guarantee that they contain all dependencies. The following steps assume that you will use `.venv_new` as the active environment.

---

<a id="1-crear--activar-el-virtualenv"></a>
## 1. Create / activate the virtualenv

```bash
python3 -m venv .venv_new            # si no existe
source .venv_new/bin/activate
python3 -m pip install --upgrade pip setuptools wheel
```

<a id="2-instalar-dependencias-python"></a>
## 2. Install Python dependencies

1. **Base layer (API + lightweight services)**
   ```bash
   pip install -r requirements-core.txt
   ```

2. **Full layer (scientific loops + orchestration)**
   ```bash
   pip install -r requirements.txt
   ```

   This file includes many heavy scientific packages. On Apple Silicon/macOS it is advisable to install some with specialized managers:

   | Dependency | Recommended method (example) |
   |-------------|-------------------------------|
   | PyTorch (GPU/CPU) | `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu` (or the MPS variant) |
   | RDKit, COBRApy, OpenMM, PySCF, pymatgen, Brian2, NEURON | Better via Conda/Mamba:<br>`mamba install -c conda-forge rdkit cobra openmm pyscf pymatgen brian2 neuron` |
   | DeepXDE, astropy, yt | `pip install deepxde astropy yt` |

   > If you decide to use Conda/Mamba for the scientific stack, activate that environment and then install the rest with `pip` inside the same environment.

3. **Dependencies that the repository assumes are installed but may be missing**
   ```bash
   pip install httpx slowapi aiofiles qiskit
   ```

<a id="3-servicios-externos-y-variables-de-entorno"></a>
## 3. External services and environment variables

| Service / variable | Action |
|---------------------|--------|
| **Redis** | `brew install redis` and `brew services start redis`, or define `export REDIS_URL=redis://localhost:6379/0`. If you do not want Redis, disable the cache: `export AXIOM_DISABLE_REDIS=1` and adapt `settings.enable_redis_cache`. |
| **Matplotlib directory** | `mkdir -p ~/.config/matplotlib && export MPLCONFIGDIR=~/.config/matplotlib` to avoid fontcache errors in read-only environments. |
| **GPU / PyTorch** | On Apple Silicon without an NVIDIA GPU, MPS is used; if it is not available, the app falls back to CPU (this is not a blocker). |

<a id="4-archivos-de-configuración-yaml"></a>
## 4. YAML configuration files

The startup validator is in `app/config/startup_validation.py` and currently uses an absolute path:

```python
config_dir = Path("./config")
```

<a id="opciones"></a>
### Options:

1. **Create the expected directory** (simple, without touching code):
   ```bash
   mkdir -p /home/amy
   ln -sf "$(pwd)/config" .
   ```

2. **Update the code to use a relative path** (recommended):
   ```python
   PROJECT_ROOT = Path(__file__).resolve().parents[2]
   config_dir = PROJECT_ROOT / "config"
   ```

3. **Define an environment variable** and read it in the validator:
   ```bash
   export AXIOM_CONFIG_ROOT="$(pwd)/config"
   ```
   and in `startup_validation.py`:
   ```python
   config_dir = Path(os.getenv("AXIOM_CONFIG_ROOT", PROJECT_ROOT / "config"))
   ```

Verify that the following files exist (and are valid):

- `config/agents.yaml`
- `config/models.yaml`
- `config/plausibility.yaml`
- `config/policy_engine_config.yaml`
- `config/ethics_policy.yaml`
- `config/improvements_config.yaml`
- `config/prompts/hypothesis_agent.yaml`

<a id="5-banderas-y-ajustes-recomendados"></a>
## 5. Recommended flags and settings

- `export ENV=development` (so that `app/config/__init__.py` loads `env.development`).
- If you install packages with `pip` inside a venv, you do not need `--break-system-packages`. Avoid running it on the global system.
- To prevent Redis and RateLimiter from failing when there is no server, you can set `export DISABLE_RATE_LIMITER=1` (if you decide to create that flag) or modify `app/core/rate_limit_setup.py` to skip the connection when `settings.redis_url` is null.

<a id="6-validaciones-rápidas"></a>
## 6. Quick validations

1. **Import test**  
   ```bash
   source .venv_new/bin/activate
   python -c "import app; import app.services.master_orchestration_service_refactored"
   ```

2. **Orchestration smoke test**  
   ```bash
   pytest tests/unit/test_pipeline_debug.py -q
   ```

3. **Example loop (isolated mode)**  
   ```bash
   python run_loops_isolated.py --loop quantum --limit 1 --output tmp/isolated_quantum.json
   ```

4. **Hypothesis generator (minimal CLI)**  
   ```bash
   python - <<'PY'
   from app.autonomous.generators.hypothesis_generator import HypothesisGenerator
   import asyncio

   async def main():
       gen = HypothesisGenerator()
       h = await gen.generate_hypothesis("quantum_physics")
       print(h)

   asyncio.run(main())
   PY
   ```

If any of these steps fails, review the message and check the corresponding section of this guide (missing dependencies, external services, configuration files, etc.).

---

<a id="7-resumen-rápido"></a>
## 7. Quick summary

1. **Activate `.venv_new`.**
2. **Install `requirements-core.txt` + `requirements.txt`.**
3. **Install heavy scientific packages** (PyTorch, RDKit, Brian2, NEURON, etc.; preferably via conda/mamba).
4. **Ensure Redis and `MPLCONFIGDIR`.**
5. **Fix the configuration path** or create the expected folder.
6. **Run smoke tests and example loops.**

With all of this ready, I will be able to run and analyze the production loops and the hypothesis generator without additional blockers.

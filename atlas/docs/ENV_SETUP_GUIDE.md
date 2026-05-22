# AXIOM ATLAS – Entorno de Ejecución Completo

Este documento resume todo lo que debe estar instalado y configurado para que yo pueda ejecutar:

- Los smoke tests (`pytest tests/unit/test_pipeline_debug.py -q` y similares).
- Los loops de producción (`run_all_loops_production.py`, `run_remaining_loops.py`, etc.).
- El generador de hipótesis (`app/autonomous/generators/hypothesis_generator.py` y pipelines que lo usan).

> **Nota:** El repositorio trae varias virtualenvs de referencia (`.venv`, `.venv_new`, `venv_improvements`), pero no garantizan que contengan todas las dependencias. Los pasos siguientes asumen que usarás `.venv_new` como entorno activo.

---

## 1. Crear / activar el virtualenv

```bash
python3 -m venv .venv_new            # si no existe
source .venv_new/bin/activate
python3 -m pip install --upgrade pip setuptools wheel
```

## 2. Instalar dependencias Python

1. **Capa base (API + servicios ligeros)**
   ```bash
   pip install -r requirements-core.txt
   ```

2. **Capa completa (loops científicos + orquestación)**
   ```bash
   pip install -r requirements.txt
   ```

   Este fichero incluye muchos paquetes científicos pesados. En Apple Silicon/macOS conviene instalar algunos con gestores especializados:

   | Dependencia | Método recomendado (ejemplo) |
   |-------------|-------------------------------|
   | PyTorch (GPU/CPU) | `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu` (o la variante MPS) |
   | RDKit, COBRApy, OpenMM, PySCF, pymatgen, Brian2, NEURON | Mejor vía Conda/Mamba:<br>`mamba install -c conda-forge rdkit cobra openmm pyscf pymatgen brian2 neuron` |
   | DeepXDE, astropy, yt | `pip install deepxde astropy yt` |

   > Si decides usar Conda/Mamba para la pila científica, activa ese entorno y luego instala el resto con `pip` dentro del mismo entorno.

3. **Dependencias que el repositorio asume instaladas pero pueden faltar**
   ```bash
   pip install httpx slowapi aiofiles qiskit
   ```

## 3. Servicios externos y variables de entorno

| Servicio / variable | Acción |
|---------------------|--------|
| **Redis** | `brew install redis` y `brew services start redis`, o define `export REDIS_URL=redis://localhost:6379/0`. Si no quieres Redis, desactiva la caché: `export AXIOM_DISABLE_REDIS=1` y adapta `settings.enable_redis_cache`. |
| **Directorio de Matplotlib** | `mkdir -p ~/.config/matplotlib && export MPLCONFIGDIR=~/.config/matplotlib` para evitar errores de fontcache en entornos de sólo lectura. |
| **GPU / PyTorch** | En Apple Silicon sin GPU NVIDIA se utiliza MPS; si no está disponible, la app cae a CPU (no es bloqueo). |

## 4. Archivos de configuración YAML

El validador de arranque está en `app/config/startup_validation.py` y hoy usa una ruta absoluta:

```python
config_dir = Path("./config")
```

### Opciones:

1. **Crear el directorio esperado** (simple, sin tocar código):
   ```bash
   mkdir -p /Users/giovanniarangio
   ln -sf "$(pwd)/config" .
   ```

2. **Actualizar el código para usar una ruta relativa** (recomendado):
   ```python
   PROJECT_ROOT = Path(__file__).resolve().parents[2]
   config_dir = PROJECT_ROOT / "config"
   ```

3. **Definir una variable de entorno** y leerla en el validador:
   ```bash
   export AXIOM_CONFIG_ROOT="$(pwd)/config"
   ```
   y en `startup_validation.py`:
   ```python
   config_dir = Path(os.getenv("AXIOM_CONFIG_ROOT", PROJECT_ROOT / "config"))
   ```

Verifica que existan (y sean válidos) los siguientes archivos:

- `config/agents.yaml`
- `config/models.yaml`
- `config/plausibility.yaml`
- `config/policy_engine_config.yaml`
- `config/ethics_policy.yaml`
- `config/improvements_config.yaml`
- `config/prompts/hypothesis_agent.yaml`

## 5. Banderas y ajustes recomendados

- `export ENV=development` (para que `app/config/__init__.py` cargue `env.development`).
- Si instalas paquetes con `pip` dentro de una venv, no necesitas `--break-system-packages`. Evita ejecutarlo en el sistema global.
- Para evitar que Redis y RateLimiter fallen cuando no hay servidor, puedes establecer `export DISABLE_RATE_LIMITER=1` (si decides crear esa bandera) o modificar `app/core/rate_limit_setup.py` para omitir la conexión cuando `settings.redis_url` sea nula.

## 6. Validaciones rápidas

1. **Prueba de importación**  
   ```bash
   source .venv_new/bin/activate
   python -c "import app; import app.services.master_orchestration_service_refactored"
   ```

2. **Smoke test de orquestación**  
   ```bash
   pytest tests/unit/test_pipeline_debug.py -q
   ```

3. **Loop de ejemplo (modo aislado)**  
   ```bash
   python run_loops_isolated.py --loop quantum --limit 1 --output tmp/isolated_quantum.json
   ```

4. **Generador de hipótesis (CLI mínimo)**  
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

Si cualquiera de estos pasos falla, revisa el mensaje y verifica la sección correspondiente de esta guía (dependencias faltantes, servicios externos, archivos de configuración, etc.).

---

## 7. Resumen rápido

1. **Activar `.venv_new`.**
2. **Instalar `requirements-core.txt` + `requirements.txt`.**
3. **Instalar científicas pesadas** (PyTorch, RDKit, Brian2, NEURON, etc.; preferible vía conda/mamba).
4. **Asegurar Redis y `MPLCONFIGDIR`.**
5. **Corregir la ruta de configuración** o crear la carpeta esperada.
6. **Ejecutar smoke tests y loops de ejemplo.**

Con todo esto listo, podré ejecutar y analizar los loops de producción y el generador de hipótesis sin bloqueos adicionales.

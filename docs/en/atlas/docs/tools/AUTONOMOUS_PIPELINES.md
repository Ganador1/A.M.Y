> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="sistema-autónomo-pipelines-y-loops"></a>
# Autonomous system: pipelines and loops

<a id="qué-es"></a>
## What it is
AXIOM ATLAS includes autonomous loops/pipelines to run research cycles per domain (generate hypotheses → design experiments → execute → evaluate → publish).

<a id="ubicación-en-el-código"></a>
## Location in the code
- Pipelines per domain: `app/autonomous/pipelines/`

Detected pipelines:
- `astronomy_loop.py`
- `biology_loop.py`
- `chemistry_loop.py`
- `climate_loop.py`
- `engineering_loop.py`
- `materials_loop.py`
- `mathematics_loop.py`
- `medicine_loop.py`
- `neuroscience_loop.py`
- `quantum_loop.py`
- `enhanced_chemistry_loop.py`

<a id="cómo-se-usan"></a>
## How they are used
- Direct execution (scripts): many commands live in `scripts/run_*`.
- Execution via routers: some routers internally call loops (e.g., Chemistry enhanced).

<a id="recomendación-de-documentación-por-loop"></a>
## Documentation recommendation per loop
Each loop should have:
- Objective and stopping criterion
- Inputs (datasets/config)
- Outputs (artifacts and paths)
- Optional dependencies (toolkits)
- Evaluation and reproducibility strategy

If you want, the next step is for me to generate a short `README.md` for each loop with that format.

> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="scientific-setup--scientific-dependencies-spanish-original"></a>
# Scientific Setup / Scientific Dependencies (Spanish Original)

Complete guide to prepare the optional scientific environment (computational chemistry, quantum physics, quantum computing, scientific AI) and base components of the AXIOM laboratory.

<a id="1-capas-de-dependencias"></a>
## 1. Dependency Layers

| Layer | Objective | Technologies |
|------|----------|-------------|
| Numerical Base | Symbolic computation / vectorization | sympy, numpy, scipy |
| AI / ML | Models and utilities | scikit-learn, mlflow (optional) |
| Data / Manipulation | Series, tables, labeled arrays | pandas, xarray |
| Visualization | 2D/3D and scientific plots | matplotlib, pyvista (3D) |
| Graphs / Networks | Structural analysis | networkx |
| Web Orchestration | API & validation | fastapi, pydantic |
| Versioning / Reproducibility | Experiments/data | dvc (optional), mlflow (optional) |
| SMT / Logic | Symbolic reasoning | z3-solver (optional) |
| Quantum / Chemistry | Simulation and structures | rdkit, qutip, qiskit, cirq, pyscf |
| Bio / Sequences | Bioinformatics | biopython |
| PDE / PINNs | Scientific AI | deepxde |

<a id="2-requisitos-base"></a>
## 2. Base Requirements

```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install --upgrade pip
pip install sympy numpy scipy pandas networkx matplotlib fastapi pydantic
```

<a id="3-instalación-científica-completa-conda-recomendada"></a>
## 3. Full Scientific Installation (Conda Recommended)

```bash
conda create -n axiom-scientific python=3.11
conda activate axiom-scientific

<a id="núcleo-científico-pesado"></a>
# Núcleo científico pesado
conda install -c conda-forge rdkit qutip pyvista

<a id="quantum-computing"></a>
# Quantum computing
pip install qiskit qiskit-aer cirq

<a id="ai-científica--pinns"></a>
# AI científica / PINNs
pip install deepxde langchain openai

<a id="química--bio-extra"></a>
# Química / Bio extra
pip install pyscf biopython
```

<a id="instalación-automática"></a>
### Automatic Installation

```bash
chmod +x install_scientific_dependencies.sh
./install_scientific_dependencies.sh
```

<a id="4-verificación-rápida"></a>
## 4. Quick Verification

```bash
python -c "import rdkit; import qutip; import qiskit; import cirq; import deepxde; print('OK scientific stack')"
python test_scientific_dependencies.py  # si el script está disponible
```

<a id="5-servicios-que-se-habilitan"></a>
## 5. Services That Are Enabled

| Domain | Router / Prefix | Capabilities |
|---------|-----------------|-------------|
| Computational Chemistry | /api/computational-chemistry | Molecular properties, 3D generation, sequences |
| Quantum Physics | /api/quantum-physics | Harmonic oscillator, spin, entanglement |
| Quantum Computing | /api/quantum-computing | Bell, Grover, QFT, VQE |
| Scientific AI | /api/scientific-ai | PINNs, inverse, scientific agents |

<a id="6-requisitos-de-sistema-sugeridos"></a>
## 6. System Requirements (Suggested)

- RAM: 4GB+ (8GB ideal if you use PySCF + RDKit)
- Storage: 2GB+ (caches + libs)
- Python: 3.11+ (3.13 tested in roadmap)
- OS: Linux / macOS (Windows via WSL)

<a id="7-resolución-de-problemas"></a>
## 7. Troubleshooting

| Problem | Frequent Cause | Solution |
|----------|-----------------|----------|
| RDKit does not install | Missing compilation dependencies | `conda install -c conda-forge rdkit=2023.09.1` |
| ImportError qutip | SciPy not aligned | `conda install -c conda-forge qutip scipy` |
| Qiskit GPU | Missing GPU backend | `pip install qiskit-aer-gpu` |
| Conda timeout | Slow network | `conda config --set remote_read_timeout_secs 600` |

<a id="8-uso-de-entorno-científico"></a>
## 8. Using the Scientific Environment

```bash
conda activate axiom-scientific
pip install -e .
uvicorn app.main:app --reload

<a id="ejemplo-endpoint-químico"></a>
# Ejemplo endpoint químico
curl -X POST "http://localhost:8000/api/computational-chemistry/analyze" \
	-H "Content-Type: application/json" \
	-d '{"smiles": "CCO", "properties": ["molecular_weight"]}'
```

<a id="9-optimización-de-rendimiento"></a>
## 9. Performance Optimization

- Use conda for complex binaries (rdkit, qutip)
- Enable caching of intermediate results when possible
- GPU: only needed for certain backends (Aer GPU, future accelerated PINNs)
- Parallelize long molecular calculations with small batches

<a id="10-extensiones-futuras-roadmap"></a>
## 10. Future Extensions (Roadmap)

- OpenMM integration (molecular dynamics)
- Coupled multiscale simulation (chemistry → materials → biology)
- Optimized hybrid quantum-classical pipelines

<a id="11-mantenimiento-y-actualizaciones"></a>
## 11. Maintenance and Updates

```bash
conda update --all
pip list --outdated
```

Check the CHANGELOG to see whether new heavy dependencies were added.

<a id="12-tabla-resumen"></a>
## 12. Summary Table

| Group | Packages | Status |
|-------|----------|--------|
| Core | sympy, numpy, scipy, pandas | Stable |
| Visualization | matplotlib, pyvista | Stable |
| Quantum | qiskit, cirq, qutip | Stable (optimizable) |
| Chemistry | rdkit, pyscf | Basic stable |
| Bio | biopython | Stable |
| PINNs | deepxde | Experimental |
| Agents | langchain, openai | Integrated |

<a id="13-mínimo-vs-completo"></a>
## 13. Minimum vs Full

```bash
<a id="mínimo"></a>
# Mínimo
pip install sympy numpy scipy fastapi pydantic

<a id="completo-ver-arriba---activa-todos-los-routers-científicos"></a>
# Completo (ver arriba) -> activa todos los routers científicos
```

---
Consolidated document. The README now references this file to avoid duplication.

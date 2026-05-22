<!-- CONSOLIDATED SCIENTIFIC SETUP (migrated from README duplicates) -->
# Scientific Setup / Scientific Dependencies

Complete guide to preparing the optional scientific environment (computational chemistry, quantum physics, quantum computing, scientific AI) and core components of the AXIOM laboratory.

## 1. Dependency Layers

| Layer | Goal | Technologies |
|------|----------|-------------|
| Numerical Core | Symbolic calculation / vectorization | sympy, numpy, scipy |
| AI / ML | Models and utilities | scikit-learn, mlflow (optional) |
| Data / Manipulation | Series, tables, labeled arrays | pandas, xarray |
| Visualization | 2D/3D and scientific graphics | matplotlib, pyvista (3D) |
| Graphs / Networks | Structural analysis | networkx |
| Web Orchestration | API & validation | fastapi, pydantic |
| Versioning / Reproducibility | Experiments/data | dvc (optional), mlflow (optional) |
| SMT / Logic | Symbolic reasoning | z3-solver (optional) |
| Quantum / Chemistry | Simulation and structures | rdkit, qutip, qiskit, cirq, pyscf |
| Bio / Sequences | Bioinformatics | biopython |
| PDE / PINNs | Scientific AI | deepxde |

## 2. Base Requirements

```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install --upgrade pip
pip install sympy numpy scipy pandas networkx matplotlib fastapi pydantic
```

## 3. Full Scientific Installation (Conda Recommended)

```bash
conda create -n axiom-scientific python=3.11
conda activate axiom-scientific

# Heavy scientific core
conda install -c conda-forge rdkit qutip pyvista

# Quantum computing
pip install qiskit qiskit-aer cirq

# Scientific AI / PINNs
pip install deepxde langchain openai

# Extra Chemistry / Bio
pip install pyscf biopython
```

### Automatic Installation

```bash
chmod +x install_scientific_dependencies.sh
./install_scientific_dependencies.sh
```

## 4. Quick Verification

```bash
python -c "import rdkit; import qutip; import qiskit; import cirq; import deepxde; print('OK scientific stack')"
python test_scientific_dependencies.py  # if script is available
```

## 5. Enabled Services

| Domain | Router / Prefix | Capabilities |
|---------|-----------------|-------------|
| Computational Chemistry | /api/computational-chemistry | Molecular properties, 3D generation, sequences |
| Quantum Physics | /api/quantum-physics | Harmonic oscillator, spin, entanglement |
| Quantum Computing | /api/quantum-computing | Bell, Grover, QFT, VQE |
| Scientific AI | /api/scientific-ai | PINNs, inverse problems, scientific agents |

## 6. System Requirements (Suggested)

- RAM: 4GB+ (8GB ideal if using PySCF + RDKit)
- Storage: 2GB+ (caches + libs)
- Python: 3.11+ (3.13 tested in roadmap)
- OS: Linux / macOS (Windows via WSL)

## 7. Troubleshooting

| Problem | Frequent Cause | Solution |
|----------|-----------------|----------|
| RDKit fails to install | Missing build dependencies | `conda install -c conda-forge rdkit=2023.09.1` |
| ImportError qutip | SciPy not aligned | `conda install -c conda-forge qutip scipy` |
| Qiskit GPU | Missing GPU backend | `pip install qiskit-aer-gpu` |
| Conda timeout | Slow network | `conda config --set remote_read_timeout_secs 600` |

## 8. Using the Scientific Environment

```bash
conda activate axiom-scientific
pip install -e .
uvicorn app.main:app --reload

# Example chemical endpoint
curl -X POST "http://localhost:8000/api/computational-chemistry/analyze" \
	-H "Content-Type: application/json" \
	-d '{"smiles": "CCO", "properties": ["molecular_weight"]}'
```

## 9. Performance Optimization

- Use conda for complex binaries (rdkit, qutip)
- Enable intermediate results caching when possible
- GPU: only necessary for certain backends (Aer GPU, future accelerated PINNs)
- Parallelize long molecular calculations with small batches

## 10. Future Extensions (Roadmap)

- OpenMM integration (molecular dynamics)
- Coupled multi-scale simulation (chemistry → materials → biology)
- Optimized hybrid quantum-classical pipelines

## 11. Maintenance and Updates

```bash
conda update --all
pip list --outdated
```

Check CHANGELOG for new heavy dependencies.

## 12. Summary Table

| Group | Packages | Status |
|-------|----------|--------|
| Core | sympy, numpy, scipy, pandas | Stable |
| Visualization | matplotlib, pyvista | Stable |
| Quantum | qiskit, cirq, qutip | Stable (optimizable) |
| Chemistry | rdkit, pyscf | Basic Stable |
| Bio | biopython | Stable |
| PINNs | deepxde | Experimental |
| Agents | langchain, openai | Integrated |

## 13. Minimum vs Full

```bash
# Minimum
pip install sympy numpy scipy fastapi pydantic

# Full (see above) -> enables all scientific routers
```

---
Consolidated document. The README now references this file to avoid duplication.
<!-- END CONSOLIDATED SCIENTIFIC SETUP -->

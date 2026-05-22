# Scientific Dependencies Setup

## Overview
AXIOM includes advanced scientific computing capabilities through optional dependencies. These libraries enable capabilities for computational chemistry, quantum physics, quantum computing, and scientific AI.

## Core Scientific Libraries

| Library | Purpose | Installation |
|---------|---------|--------------|
| **RDKit** | Molecular modeling and computational chemistry | `conda install -c conda-forge rdkit` |
| **QuTiP** | Quantum physics simulations | `conda install -c conda-forge qutip` |
| **Qiskit** | Quantum computing (IBM) | `pip install qiskit qiskit-aer` |
| **Cirq** | Quantum computing (Google) | `pip install cirq` |
| **DeepXDE** | Physics-Informed Neural Networks | `pip install deepxde` |
| **LangChain** | AI agents for scientific discovery | `pip install langchain` |
| **PyVista** | 3D scientific visualization | `conda install -c conda-forge pyvista` |
| **BioPython** | Bioinformatics tools | `pip install biopython` |
| **PySCF** | Quantum chemistry calculations | `pip install pyscf` |

## Automated Installation

Use the provided installation script for the complete scientific environment:

```bash
# Make script executable
chmod +x install_scientific_dependencies.sh

# Run automated installation
./install_scientific_dependencies.sh
```

## Manual Installation

For manual installation with conda (recommended):

```bash
# Create scientific environment (optional)
conda create -n axiom-scientific python=3.11
conda activate axiom-scientific

# Install core scientific libraries
conda install -c conda-forge rdkit qutip pyvista

# Install quantum computing libraries
pip install qiskit qiskit-aer cirq

# Install scientific AI libraries
pip install deepxde langchain openai

# Install additional libraries
pip install biopython pyscf
```

## Testing Scientific Dependencies

After installation, test all scientific libraries:

```bash
# Run comprehensive test
python test_scientific_dependencies.py

# Or test individual libraries
python -c "import rdkit; print('RDKit OK')"
python -c "import qutip; print('QuTiP OK')"
python -c "import qiskit; print('Qiskit OK')"
```

## Scientific Services Available

Once dependencies are installed, these services become available:

### 🧬 Computational Chemistry (`/api/computational-chemistry/`)
- Molecular property analysis
- 3D structure generation
- Biological sequence analysis
- Quantum chemical calculations

### ⚛️ Quantum Physics (`/api/quantum-physics/`)
- Quantum spin dynamics
- Harmonic oscillator simulations
- Entanglement quantification
- Two-level system analysis

### 🧠 Quantum Computing (`/api/quantum-computing/`)
- Bell state preparation
- Grover search algorithm
- Quantum Fourier Transform
- Variational Quantum Eigensolver (VQE)

### 🤖 Scientific AI (`/api/scientific-ai/`)
- PDE solving with PINNs
- Inverse problem solutions
- Scientific AI agent creation
- Research workflow automation

## System Requirements

**For Scientific Computing:**
- **RAM**: 4GB+ recommended
- **Storage**: 2GB+ for libraries and data
- **Python**: 3.11+ (3.13 recommended)
- **OS**: Linux/macOS (Windows with WSL recommended)

## Troubleshooting

**Common Issues:**

1. **RDKit Installation Issues**:
   ```bash
   # Try with specific channel
   conda install -c conda-forge rdkit=2023.09.1
   ```

2. **QuTiP Import Errors**:
   ```bash
   # Install with dependencies
   conda install -c conda-forge qutip scipy
   ```

3. **Qiskit GPU Support**:
   ```bash
   # For GPU acceleration
   pip install qiskit-aer-gpu
   ```

4. **Memory Issues**:
   ```bash
   # Increase conda timeout
   conda config --set remote_read_timeout_secs 600
   ```

## Development with Scientific Libraries

When working with scientific dependencies:

```bash
# Activate scientific environment
conda activate axiom-scientific

# Install in development mode
pip install -e .

# Run with scientific features
python main.py

# Test scientific endpoints
curl -X POST "http://localhost:8002/api/chemistry/analyze-molecule" \
     -H "Content-Type: application/json" \
     -d '{"smiles": "CCO", "properties": ["molecular_weight"]}'
```

## Performance Optimization

**For Scientific Computing:**
- Use conda environments for dependency isolation
- Install libraries with conda when possible (better dependency resolution)
- Consider GPU acceleration for quantum simulations
- Use parallel processing for large computations

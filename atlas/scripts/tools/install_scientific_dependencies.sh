#!/bin/bash

# AXIOM - Scientific Dependencies Installation Script
# This script installs all scientific computing libraries required for AXIOM

set -e  # Exit on any error

echo "🚀 AXIOM - Scientific Dependencies Installation"
echo "=============================================="

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ Conda is not installed. Please install Miniconda or Anaconda first."
    echo "   Visit: https://docs.conda.io/projects/miniconda/en/latest/"
    exit 1
fi

# Check current conda environment
CURRENT_ENV=$(conda info --envs | grep "*" | awk '{print $1}')
if [ "$CURRENT_ENV" = "base" ]; then
    echo "⚠️  You are in the base conda environment."
    echo "   It's recommended to create a separate environment for scientific computing."
    read -p "   Do you want to create a new environment 'axiom-scientific'? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📦 Creating new conda environment 'axiom-scientific'..."
        conda create -n axiom-scientific python=3.11 -y
        conda activate axiom-scientific
        echo "✅ Environment created and activated."
    fi
fi

echo "🔧 Installing scientific computing libraries..."
echo "This may take several minutes depending on your internet connection."
echo

# Update conda
echo "📦 Updating conda..."
conda update -n base -c defaults conda -y

# Install core scientific libraries
echo "🔬 Installing core scientific libraries..."
conda install -c conda-forge \
    numpy \
    scipy \
    matplotlib \
    sympy \
    pandas \
    scikit-learn \
    -y

# Install RDKit for computational chemistry
echo "🧬 Installing RDKit for computational chemistry..."
conda install -c conda-forge rdkit -y

# Install QuTiP for quantum physics
echo "⚛️ Installing QuTiP for quantum physics..."
conda install -c conda-forge qutip -y

# Install PyVista for 3D visualization
echo "📊 Installing PyVista for 3D visualization..."
conda install -c conda-forge pyvista -y

# Install additional libraries with pip
echo "📚 Installing additional libraries with pip..."

# Quantum computing libraries
pip install qiskit
pip install qiskit-aer
pip install cirq

# Scientific AI libraries
pip install deepxde
pip install langchain
pip install openai  # For LangChain OpenAI integration

# Additional scientific libraries
pip install biopython  # For bioinformatics
pip install pyscf      # For quantum chemistry calculations

# Visualization and utilities
pip install plotly
pip install seaborn
pip install tqdm

echo
echo "✅ Scientific dependencies installation completed!"
echo
echo "📋 Installed Libraries:"
echo "  🧬 RDKit - Computational chemistry and molecular modeling"
echo "  ⚛️ QuTiP - Quantum physics simulations"
echo "  🧠 Qiskit - Quantum computing (IBM)"
echo "  🔬 Cirq - Quantum computing (Google)"
echo "  🤖 DeepXDE - Physics-Informed Neural Networks"
echo "  🗣️ LangChain - AI agents for scientific discovery"
echo "  🧬 BioPython - Bioinformatics tools"
echo "  ⚛️ PySCF - Quantum chemistry calculations"
echo "  📊 PyVista - 3D scientific visualization"
echo
echo "🧪 Testing installations..."

# Test RDKit
python -c "import rdkit; print('✅ RDKit:', rdkit.__version__)" 2>/dev/null || echo "❌ RDKit test failed"

# Test QuTiP
python -c "import qutip; print('✅ QuTiP:', qutip.__version__)" 2>/dev/null || echo "❌ QuTiP test failed"

# Test Qiskit
python -c "import qiskit; print('✅ Qiskit:', qiskit.__version__)" 2>/dev/null || echo "❌ Qiskit test failed"

# Test Cirq
python -c "import cirq; print('✅ Cirq:', cirq.__version__)" 2>/dev/null || echo "❌ Cirq test failed"

# Test DeepXDE
python -c "import deepxde; print('✅ DeepXDE:', deepxde.__version__)" 2>/dev/null || echo "❌ DeepXDE test failed"

# Test LangChain
python -c "import langchain; print('✅ LangChain available')" 2>/dev/null || echo "❌ LangChain test failed"

echo
echo "🎯 Next Steps:"
echo "1. Restart your Python environment to use the new libraries"
echo "2. Run the AXIOM server: python main.py"
echo "3. Test scientific endpoints at http://localhost:8002/docs"
echo "4. Run scientific integration tests"
echo
echo "📚 Useful Commands:"
echo "  conda activate axiom-scientific    # Activate scientific environment"
echo "  conda env list                     # List all environments"
echo "  pip list | grep -E '(rdkit|qutip|qiskit|deepxde|langchain)'  # Check installations"
echo
echo "🚀 AXIOM is now ready for advanced scientific computing!"

#!/bin/bash

# AXIOM - Scientific Dependencies Test Script
# Tests all scientific computing libraries to ensure they work correctly

echo "🧪 AXIOM - Scientific Dependencies Test"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TOTAL_TESTS=0
PASSED_TESTS=0

test_library() {
    local library_name=$1
    local import_command=$2
    local description=$3

    echo -n "Testing $library_name... "
    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    if python -c "$import_command" 2>/dev/null; then
        echo -e "${GREEN}✅ PASSED${NC} - $description"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ FAILED${NC} - $description"
    fi
}

echo "🔬 Testing Core Scientific Libraries:"
echo "-------------------------------------"

# Test core libraries
test_library "NumPy" "import numpy as np; print('NumPy version:', np.__version__)" "Numerical computing library"
test_library "SciPy" "import scipy; print('SciPy version:', scipy.__version__)" "Scientific computing library"
test_library "Matplotlib" "import matplotlib; print('Matplotlib version:', matplotlib.__version__)" "Plotting library"
test_library "SymPy" "import sympy; print('SymPy version:', sympy.__version__)" "Symbolic mathematics"
test_library "Pandas" "import pandas as pd; print('Pandas version:', pd.__version__)" "Data analysis library"

echo
echo "🧬 Testing Chemistry Libraries:"
echo "-------------------------------"

# Test chemistry libraries
test_library "RDKit" "from rdkit import Chem; print('RDKit available')" "Molecular modeling and chemistry"
test_library "BioPython" "import Bio; print('BioPython version:', Bio.__version__)" "Bioinformatics tools"
test_library "PySCF" "import pyscf; print('PySCF available')" "Quantum chemistry calculations"

echo
echo "⚛️ Testing Quantum Physics Libraries:"
echo "-------------------------------------"

# Test quantum physics libraries
test_library "QuTiP" "import qutip as qt; print('QuTiP version:', qt.__version__)" "Quantum physics simulations"

echo
echo "🧠 Testing Quantum Computing Libraries:"
echo "----------------------------------------"

# Test quantum computing libraries
test_library "Qiskit" "import qiskit; print('Qiskit version:', qiskit.__version__)" "IBM quantum computing framework"
test_library "Cirq" "import cirq; print('Cirq version:', cirq.__version__)" "Google quantum computing framework"

echo
echo "🤖 Testing Scientific AI Libraries:"
echo "-----------------------------------"

# Test scientific AI libraries
test_library "DeepXDE" "import deepxde as dde; print('DeepXDE version:', dde.__version__)" "Physics-Informed Neural Networks"
test_library "LangChain" "import langchain; print('LangChain available')" "AI agents and chains"

echo
echo "📊 Testing Visualization Libraries:"
echo "-----------------------------------"

# Test visualization libraries
test_library "Plotly" "import plotly; print('Plotly version:', plotly.__version__)" "Interactive plotting"
test_library "PyVista" "import pyvista as pv; print('PyVista version:', pv.__version__)" "3D scientific visualization"
test_library "Seaborn" "import seaborn; print('Seaborn available')" "Statistical visualization"

echo
echo "📈 Test Results Summary:"
echo "========================"
echo "Total Tests: $TOTAL_TESTS"
echo "Passed: $PASSED_TESTS"
echo "Failed: $((TOTAL_TESTS - PASSED_TESTS))"
echo "Success Rate: $((PASSED_TESTS * 100 / TOTAL_TESTS))%"

if [ $PASSED_TESTS -eq $TOTAL_TESTS ]; then
    echo -e "${GREEN}🎉 All scientific dependencies are working correctly!${NC}"
    echo
    echo "🚀 AXIOM is ready for advanced scientific computing!"
    echo "   You can now use all scientific services:"
    echo "   - Computational Chemistry (/api/computational-chemistry)"
    echo "   - Quantum Physics (/api/quantum-physics)"
    echo "   - Quantum Computing (/api/quantum-computing)"
    echo "   - Scientific AI (/api/scientific-ai)"
else
    echo -e "${YELLOW}⚠️  Some dependencies are missing or not working.${NC}"
    echo
    echo "🔧 To fix missing dependencies:"
    echo "   1. Run: ./install_scientific_dependencies.sh"
    echo "   2. Or install manually with conda/pip"
    echo "   3. Restart your Python environment"
    echo "   4. Run this test again"
fi

echo
echo "📝 Notes:"
echo "- Some libraries may show warnings but still work correctly"
echo "- GPU acceleration may require additional CUDA/OpenCL setup"
echo "- API keys may be needed for some cloud services"

exit 0

#!/usr/bin/env python3
"""
AXIOM - Scientific Dependencies Test Script
Tests all scientific computing libraries to ensure they work correctly
"""

import sys
import subprocess

# Colors for output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
NC = '\033[0m'  # No Color

class ScientificDependenciesTester:
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = []

    def test_library(self, library_name: str, import_command: str, description: str) -> bool:
        """Test a single library import"""
        print(f"Testing {library_name}... ", end="", flush=True)
        self.total_tests += 1

        try:
            # Execute the import command
            result = subprocess.run(
                [sys.executable, "-c", import_command],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                print(f"{GREEN}✅ PASSED{NC} - {description}")
                if result.stdout.strip():
                    print(f"  Version/Info: {result.stdout.strip()}")
                self.passed_tests += 1
                return True
            else:
                print(f"{RED}❌ FAILED{NC} - {description}")
                if result.stderr:
                    print(f"  Error: {result.stderr.strip()}")
                self.failed_tests.append(library_name)
                return False

        except subprocess.TimeoutExpired:
            print(f"{RED}❌ TIMEOUT{NC} - {description}")
            self.failed_tests.append(library_name)
            return False
        except Exception as e:
            print(f"{RED}❌ ERROR{NC} - {description}")
            print(f"  Exception: {str(e)}")
            self.failed_tests.append(library_name)
            return False

    def print_summary(self):
        """Print test results summary"""
        print("\n" + "="*50)
        print("📈 Test Results Summary:")
        print("="*50)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {len(self.failed_tests)}")
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        if self.failed_tests:
            print(f"Failed Libraries: {', '.join(self.failed_tests)}")

        if self.passed_tests == self.total_tests:
            print(f"\n{GREEN}🎉 All scientific dependencies are working correctly!{NC}")
            print("\n🚀 AXIOM is ready for advanced scientific computing!")
            print("   You can now use all scientific services:")
            print("   - Computational Chemistry (/api/computational-chemistry)")
            print("   - Quantum Physics (/api/quantum-physics)")
            print("   - Quantum Computing (/api/quantum-computing)")
            print("   - Scientific AI (/api/scientific-ai)")
        else:
            print(f"\n{YELLOW}⚠️  Some dependencies are missing or not working.{NC}")
            print("\n🔧 To fix missing dependencies:")
            print("   1. Run: ./install_scientific_dependencies.sh")
            print("   2. Or install manually with conda/pip")
            print("   3. Restart your Python environment")
            print("   4. Run this test again: python test_scientific_dependencies.py")

def main():
    print("🧪 AXIOM - Scientific Dependencies Test")
    print("======================================")

    tester = ScientificDependenciesTester()

    print("\n🔬 Testing Core Scientific Libraries:")
    print("-" * 40)

    # Test core libraries
    tester.test_library(
        "NumPy",
        "import numpy as np; print(f'NumPy version: {np.__version__}')",
        "Numerical computing library"
    )
    tester.test_library(
        "SciPy",
        "import scipy; print(f'SciPy version: {scipy.__version__}')",
        "Scientific computing library"
    )
    tester.test_library(
        "Matplotlib",
        "import matplotlib; print(f'Matplotlib version: {matplotlib.__version__}')",
        "Plotting library"
    )
    tester.test_library(
        "SymPy",
        "import sympy; print(f'SymPy version: {sympy.__version__}')",
        "Symbolic mathematics"
    )
    tester.test_library(
        "Pandas",
        "import pandas as pd; print(f'Pandas version: {pd.__version__}')",
        "Data analysis library"
    )

    print("\n🧬 Testing Chemistry Libraries:")
    print("-" * 30)

    # Test chemistry libraries
    tester.test_library(
        "RDKit",
        "from rdkit import Chem; print('RDKit available')",
        "Molecular modeling and chemistry"
    )
    tester.test_library(
        "BioPython",
        "import Bio; print(f'BioPython version: {Bio.__version__}')",
        "Bioinformatics tools"
    )
    tester.test_library(
        "PySCF",
        "import pyscf; print('PySCF available')",
        "Quantum chemistry calculations"
    )

    print("\n⚛️ Testing Quantum Physics Libraries:")
    print("-" * 35)

    # Test quantum physics libraries
    tester.test_library(
        "QuTiP",
        "import qutip as qt; print(f'QuTiP version: {qt.__version__}')",
        "Quantum physics simulations"
    )

    print("\n🧠 Testing Quantum Computing Libraries:")
    print("-" * 40)

    # Test quantum computing libraries
    tester.test_library(
        "Qiskit",
        "import qiskit; print(f'Qiskit version: {qiskit.__version__}')",
        "IBM quantum computing framework"
    )
    tester.test_library(
        "Cirq",
        "import cirq; print(f'Cirq version: {cirq.__version__}')",
        "Google quantum computing framework"
    )

    print("\n🤖 Testing Scientific AI Libraries:")
    print("-" * 35)

    # Test scientific AI libraries
    tester.test_library(
        "DeepXDE",
        "import deepxde as dde; print(f'DeepXDE version: {dde.__version__}')",
        "Physics-Informed Neural Networks"
    )
    tester.test_library(
        "LangChain",
        "import langchain; print('LangChain available')",
        "AI agents and chains"
    )

    print("\n📊 Testing Visualization Libraries:")
    print("-" * 35)

    # Test visualization libraries
    tester.test_library(
        "Plotly",
        "import plotly; print(f'Plotly version: {plotly.__version__}')",
        "Interactive plotting"
    )
    tester.test_library(
        "PyVista",
        "import pyvista as pv; print(f'PyVista version: {pv.__version__}')",
        "3D scientific visualization"
    )
    tester.test_library(
        "Seaborn",
        "import seaborn; print('Seaborn available')",
        "Statistical visualization"
    )

    tester.print_summary()

    print("\n📝 Notes:")
    print("- Some libraries may show warnings but still work correctly")
    print("- GPU acceleration may require additional CUDA/OpenCL setup")
    print("- API keys may be needed for some cloud services")

    # Return appropriate exit code
    return 0 if tester.passed_tests == tester.total_tests else 1

if __name__ == "__main__":
    sys.exit(main())

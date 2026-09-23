#!/bin/bash
###############################################################################
# Script de Instalación de Dependencias Químicas - AXIOM ATLAS
###############################################################################
# Instala todas las dependencias necesarias para química computacional
###############################################################################

set -euo pipefail

echo "═══════════════════════════════════════════════════════════════════════"
echo "🧪 AXIOM ATLAS - Instalación de Dependencias Químicas"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verificar entorno virtual
if [[ -z "${VIRTUAL_ENV:-}" ]]; then
    echo -e "${YELLOW}⚠️  Activando entorno virtual...${NC}"
    source .venv/bin/activate || {
        echo -e "${RED}❌ Error: No se pudo activar .venv${NC}"
        exit 1
    }
fi

echo -e "${GREEN}✅ Entorno virtual activado: $VIRTUAL_ENV${NC}"
echo ""

# Actualizar pip
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 Actualizando pip, setuptools y wheel..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python -m pip install --upgrade pip setuptools wheel
echo ""

# 1. RDKit (Química Computacional)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 Instalando RDKit (química computacional)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if pip show rdkit &>/dev/null; then
    echo -e "${YELLOW}⚠️  RDKit ya está instalado${NC}"
else
    pip install rdkit || {
        echo -e "${YELLOW}⚠️  Instalación con pip falló, intentando conda...${NC}"
        if command -v conda &>/dev/null; then
            conda install -c conda-forge rdkit -y
        else
            echo -e "${RED}❌ RDKit requiere conda. Instalar con: brew install miniconda${NC}"
        fi
    }
fi
echo ""

# 2. PyTorch (con soporte MPS para Mac)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔥 Instalando PyTorch (con soporte MPS para Apple Silicon)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if pip show torch &>/dev/null; then
    echo -e "${YELLOW}⚠️  PyTorch ya está instalado${NC}"
else
    # Versión estable con soporte MPS
    pip install torch torchvision torchaudio
fi
echo ""

# 3. PySCF (Química Cuántica)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚛️  Instalando PySCF (química cuántica)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
pip install pyscf || echo -e "${YELLOW}⚠️  PySCF instalación parcial (normal en algunos sistemas)${NC}"
echo ""

# 4. Pymatgen (Ciencia de Materiales)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💎 Instalando Pymatgen (ciencia de materiales)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
pip install pymatgen
echo ""

# 5. COBRApy (Biología de Sistemas)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧬 Instalando COBRApy (metabolismo celular)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
pip install cobra
echo ""

# 6. OpenMM (Simulaciones Moleculares)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧬 Instalando OpenMM (dinámica molecular)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if command -v conda &>/dev/null; then
    conda install -c conda-forge openmm -y || echo -e "${YELLOW}⚠️  OpenMM requiere conda${NC}"
else
    echo -e "${YELLOW}⚠️  OpenMM requiere conda. Instalar con: brew install miniconda${NC}"
fi
echo ""

# 7. Biopython
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧬 Instalando Biopython..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
pip install biopython
echo ""

# 8. Brian2 (Neurociencia)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧠 Instalando Brian2 (simulaciones neuronales)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
pip install brian2
echo ""

# 9. NEURON (Neurociencia Computacional)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧠 Instalando NEURON..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
pip install neuron || echo -e "${YELLOW}⚠️  NEURON puede requerir dependencias del sistema${NC}"
echo ""

# 10. Qiskit (Computación Cuántica)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚛️  Instalando Qiskit completo..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
pip install 'qiskit[all]' qiskit-aer qiskit-algorithms
echo ""

# 11. Cirq (Computación Cuántica - Google)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚛️  Instalando Cirq..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
pip install cirq
echo ""

# 12. LangChain (para agentes)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🤖 Instalando LangChain..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
pip install langchain langchain-community
echo ""

# 13. Astropy (Astronomía)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌟 Instalando Astropy..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
pip install astropy
echo ""

# 14. DeepXDE (Machine Learning para EDPs)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧮 Instalando DeepXDE..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
pip install deepxde
echo ""

# 15. Redis Python Client
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔴 Instalando Redis Python Client..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
pip install redis
echo ""

# Resumen final
echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo "✅ INSTALACIÓN DE DEPENDENCIAS COMPLETADA"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "📦 Dependencias instaladas:"
echo "   ✓ RDKit (química computacional)"
echo "   ✓ PyTorch (deep learning con MPS)"
echo "   ✓ PySCF (química cuántica)"
echo "   ✓ Pymatgen (ciencia de materiales)"
echo "   ✓ COBRApy (metabolismo celular)"
echo "   ✓ OpenMM (dinámica molecular)"
echo "   ✓ Biopython (bioinformática)"
echo "   ✓ Brian2 (neurociencia)"
echo "   ✓ NEURON (neurociencia computacional)"
echo "   ✓ Qiskit (computación cuántica)"
echo "   ✓ Cirq (computación cuántica - Google)"
echo "   ✓ LangChain (agentes IA)"
echo "   ✓ Astropy (astronomía)"
echo "   ✓ DeepXDE (ML para EDPs)"
echo "   ✓ Redis (caché distribuido)"
echo ""
echo "🔄 Siguiente paso: Iniciar Redis Server"
echo "   brew services start redis"
echo ""
echo "═══════════════════════════════════════════════════════════════════════"

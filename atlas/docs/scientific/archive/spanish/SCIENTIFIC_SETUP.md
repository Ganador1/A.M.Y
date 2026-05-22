# Scientific Setup / Scientific Dependencies (Spanish Original)

Guía completa para preparar el entorno científico opcional (química computacional, física cuántica, computación cuántica, IA científica) y componentes base del laboratorio AXIOM.

## 1. Capas de Dependencias

| Capa | Objetivo | Tecnologías |
|------|----------|-------------|
| Base Numérica | Cálculo simbólico / vectorización | sympy, numpy, scipy |
| IA / ML | Modelos y utilidades | scikit-learn, mlflow (opcional) |
| Datos / Manipulación | Series, tablas, arrays etiquetados | pandas, xarray |
| Visualización | 2D/3D y gráficos científicos | matplotlib, pyvista (3D) |
| Grafos / Redes | Análisis estructural | networkx |
| Orquestación Web | API & validación | fastapi, pydantic |
| Versionado / Reproducibilidad | Experimentos/datos | dvc (opcional), mlflow (opcional) |
| SMT / Lógica | Razonamiento simbólico | z3-solver (opcional) |
| Quantum / Química | Simulación y estructuras | rdkit, qutip, qiskit, cirq, pyscf |
| Bio / Secuencias | Bioinformática | biopython |
| PDE / PINNs | IA científica | deepxde |

## 2. Requisitos Base

```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install --upgrade pip
pip install sympy numpy scipy pandas networkx matplotlib fastapi pydantic
```

## 3. Instalación Científica Completa (Conda Recomendada)

```bash
conda create -n axiom-scientific python=3.11
conda activate axiom-scientific

# Núcleo científico pesado
conda install -c conda-forge rdkit qutip pyvista

# Quantum computing
pip install qiskit qiskit-aer cirq

# AI científica / PINNs
pip install deepxde langchain openai

# Química / Bio extra
pip install pyscf biopython
```

### Instalación Automática

```bash
chmod +x install_scientific_dependencies.sh
./install_scientific_dependencies.sh
```

## 4. Verificación Rápida

```bash
python -c "import rdkit; import qutip; import qiskit; import cirq; import deepxde; print('OK scientific stack')"
python test_scientific_dependencies.py  # si el script está disponible
```

## 5. Servicios que se Habilitan

| Dominio | Router / Prefix | Capacidades |
|---------|-----------------|-------------|
| Computational Chemistry | /api/computational-chemistry | Propiedades moleculares, generación 3D, secuencias |
| Quantum Physics | /api/quantum-physics | Oscilador armónico, spin, entanglement |
| Quantum Computing | /api/quantum-computing | Bell, Grover, QFT, VQE |
| Scientific AI | /api/scientific-ai | PINNs, inversos, agentes científicos |

## 6. Requisitos de Sistema (Sugeridos)

- RAM: 4GB+ (8GB ideal si usas PySCF + RDKit)
- Almacenamiento: 2GB+ (cachés + libs)
- Python: 3.11+ (3.13 probado en roadmap)
- OS: Linux / macOS (Windows vía WSL)

## 7. Resolución de Problemas

| Problema | Causa Frecuente | Solución |
|----------|-----------------|----------|
| RDKit no instala | Dependencias de compilación faltantes | `conda install -c conda-forge rdkit=2023.09.1` |
| ImportError qutip | SciPy no alineado | `conda install -c conda-forge qutip scipy` |
| GPU Qiskit | Falta backend GPU | `pip install qiskit-aer-gpu` |
| Timeout conda | Red lenta | `conda config --set remote_read_timeout_secs 600` |

## 8. Uso de Entorno Científico

```bash
conda activate axiom-scientific
pip install -e .
uvicorn app.main:app --reload

# Ejemplo endpoint químico
curl -X POST "http://localhost:8000/api/computational-chemistry/analyze" \
	-H "Content-Type: application/json" \
	-d '{"smiles": "CCO", "properties": ["molecular_weight"]}'
```

## 9. Optimización de Rendimiento

- Usa conda para binarios complejos (rdkit, qutip)
- Activa caché de resultados intermedios cuando sea posible
- GPU: solo necesaria para ciertos backends (Aer GPU, futuros PINNs acelerados)
- Paraleliza cálculos moleculares largos con lotes pequeños

## 10. Extensiones Futuras (Roadmap)

- Integración OpenMM (dinámica molecular)
- Simulación multi-escala acoplada (química → materiales → biología)
- Pipelines híbridos cuántico-clásicos optimizados

## 11. Mantenimiento y Actualizaciones

```bash
conda update --all
pip list --outdated
```

Revisa CHANGELOG para saber si se añadieron nuevas dependencias pesadas.

## 12. Tabla Resumen

| Grupo | Paquetes | Estado |
|-------|----------|--------|
| Núcleo | sympy, numpy, scipy, pandas | Estable |
| Visualización | matplotlib, pyvista | Estable |
| Quantum | qiskit, cirq, qutip | Estable (optimizable) |
| Química | rdkit, pyscf | Estable básico |
| Bio | biopython | Estable |
| PINNs | deepxde | Experimental |
| Agentes | langchain, openai | Integrado |

## 13. Mínimo vs Completo

```bash
# Mínimo
pip install sympy numpy scipy fastapi pydantic

# Completo (ver arriba) -> activa todos los routers científicos
```

---
Documento consolidado. El README ahora referencia este archivo para evitar duplicación.

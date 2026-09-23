> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="-guía-del-desarrollador---nuevas-funcionalidades-septiembre-2025"></a>
# 🚀 Developer Guide - New Features (September 2025)

<a id="-resumen-de-implementaciones"></a>
## 📋 Implementation Summary

This guide documents the new features implemented in Agent 2 (MathLab) following the recommendations of the consolidated roadmap.

<a id="-funcionalidades-completadas"></a>
### ✅ Completed Features

1. **Lean4 Management Suite** - Complete Lean4 management
2. **Uncertainty Quantification** - Advanced uncertainty quantification  
3. **Quantum Computing Extended** - Additional quantum algorithms
4. **Testing Infrastructure** - Comprehensive test suite

---

<a id="-lean4-management-suite"></a>
## 🔧 Lean4 Management Suite

<a id="-archivos-principales"></a>
### 📁 Main Files
- `app/services/lean4_installer.py` - Installation service
- `app/services/theorem_proving/lean4_integration.py` - Integration and validation  
- `app/routers/lean4_management.py` - REST endpoints

<a id="-funcionalidades"></a>
### 🛠️ Features

<a id="instalación-asistida"></a>
#### Assisted Installation
```python
# Detección automática de SO y arquitectura
installer = Lean4InstallerService()
result = await installer.install_lean4()
```

<a id="validación-de-configuración"></a>
#### Configuration Validation
```python
# Verificación completa del environment
lean4_service = Lean4Service()
validation = await lean4_service.validate_configuration()
```

<a id="diagnóstico-de-errores"></a>
#### Error Diagnosis
```python
# Clasificación automática de errores
diagnosis = await lean4_service.diagnose_error("lean: command not found")
```

<a id="-api-endpoints"></a>
### 🌐 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/lean4/detect` | GET | Detects existing installation |
| `/api/lean4/install` | POST | Installs Lean4 automatically |
| `/api/lean4/validate` | GET | Validates configuration |
| `/api/lean4/diagnose` | POST | Diagnoses errors |
| `/api/lean4/uninstall` | DELETE | Uninstalls Lean4 |
| `/api/lean4/system-info` | GET | System information |

<a id="-testing"></a>
### 🧪 Testing
```bash
# Test básico de funcionalidad
python tests/test_isolated_validation.py
```

---

<a id="-uncertainty-quantification"></a>
## 📊 Uncertainty Quantification

<a id="-archivos-principales-1"></a>
### 📁 Main Files
- `app/uncertainty_quantification.py` - Main quantifiers
- `app/services/conformal_prediction.py` - Conformal prediction service
- `app/routers/uncertainty_quantification.py` - REST endpoints

<a id="-funcionalidades-1"></a>
### 🛠️ Features

<a id="monte-carlo-dropout"></a>
#### Monte Carlo Dropout
```python
quantifier = MonteCarloDropoutQuantifier()
result = quantifier.quantify_uncertainty(X, y, n_samples=100)
# Resultado incluye: mean_prediction, epistemic_uncertainty, confidence_intervals
```

<a id="ensemble-methods"></a>
#### Ensemble Methods
```python
ensemble = EnsembleQuantifier()
result = ensemble.quantify_uncertainty(X, y, n_estimators=10)
# Incluye: ensemble_prediction, ensemble_uncertainty, diversity_metrics
```

<a id="conformal-prediction"></a>
#### Conformal Prediction
```python
service = ConformalPredictionService()
result = service.split_conformal_prediction(X_cal, y_cal, X_test, alpha=0.1)
# Garantiza cobertura probabilística
```

<a id="-api-endpoints-1"></a>
### 🌐 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/uncertainty-quantification/monte-carlo` | POST | MC Dropout |
| `/api/uncertainty-quantification/ensemble` | POST | Ensemble methods |
| `/api/uncertainty-quantification/conformal` | POST | Conformal prediction |
| `/api/uncertainty-quantification/bootstrap` | POST | Bootstrap sampling |
| `/api/uncertainty-quantification/compare-methods` | POST | Method comparison |
| `/api/uncertainty-quantification/methods` | GET | List available methods |

---

<a id="-quantum-computing-extended"></a>
## ⚛️ Quantum Computing Extended

<a id="-archivos-principales-2"></a>
### 📁 Main Files
- `app/services/quantum_computing.py` - Extended quantum services
- `app/routers/quantum_computing.py` - REST endpoints

<a id="-funcionalidades-2"></a>
### 🛠️ Features

<a id="algoritmo-de-grover"></a>
#### Grover's Algorithm
```python
service = QuantumComputingService()
result = await service.simulate_grover_search(
    target_items=[0, 3], 
    database_size=8
)
# Búsqueda cuántica con speedup cuadrático
```

<a id="algoritmo-de-shor"></a>
#### Shor's Algorithm
```python
result = await service.simulate_shor_algorithm(N=15)
# Factorización cuántica de enteros
```

<a id="simulación-con-ruido"></a>
#### Simulation with Noise
```python
result = await service.simulate_noisy_circuit(
    circuit_type="grover",
    noise_model="depolarizing",
    noise_strength=0.01
)
# Análisis realista con modelos de ruido
```

<a id="-api-endpoints-2"></a>
### 🌐 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/quantum-computing/grover-search` | POST | Grover's algorithm |
| `/api/quantum-computing/shor-factorization` | POST | Shor's factorization |
| `/api/quantum-computing/noisy-simulation` | POST | Simulation with noise |

---

<a id="-testing-infrastructure"></a>
## 🧪 Testing Infrastructure

<a id="-archivos-de-test"></a>
### 📁 Test Files
- `tests/test_isolated_validation.py` - Main isolated tests
- `tests/test_quick_validation.py` - Quick validation
- `tests/test_endpoints_simple.py` - Endpoint tests
- `tests/pytest.ini` - pytest configuration

<a id="-ejecutar-tests"></a>
### 🚀 Run Tests

<a id="setup-del-environment"></a>
#### Environment Setup
```bash
# Crear virtualenv
python3 -m venv test_env
source test_env/bin/activate

# Instalar dependencias
pip install pytest numpy scikit-learn networkx
```

<a id="ejecutar-tests"></a>
#### Run Tests
```bash
# Tests aislados (recomendado)
python tests/test_isolated_validation.py

# Validación rápida
python tests/test_quick_validation.py

# Con pytest (requiere setup completo)
python -m pytest tests/ -v
```

<a id="-resultados-esperados"></a>
### ✅ Expected Results
```
🧪 Ejecutando tests de validación aislada...

✅ Lean4 error patterns: PASS
✅ Quantum algorithms math: PASS  
✅ Uncertainty statistical methods: PASS
✅ Conformal prediction math: PASS
✅ File structure validation: PASS

📊 Resultados: 5/5 tests pasaron
🎉 ¡Todos los tests de validación aislada pasaron!
```

---

<a id="-troubleshooting"></a>
## 🔍 Troubleshooting

<a id="problemas-comunes"></a>
### Common Issues

<a id="error-no-module-named-psycopg2"></a>
#### Error: "No module named 'psycopg2'"
```bash
# Solución: Usar tests aislados
python tests/test_isolated_validation.py
```

<a id="error-command-not-found"></a>
#### Error: "command not found"
```bash
# Verificar environment
source test_env/bin/activate
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

<a id="error-de-importación-de-módulos"></a>
#### Module import error
```bash
# Instalar dependencias específicas
pip install numpy scikit-learn networkx
```

<a id="debug-mode"></a>
### Debug Mode
```python
# Para debugging detallado, habilitar logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

<a id="-métricas-de-rendimiento"></a>
## 📈 Performance Metrics

<a id="tiempos-de-ejecución-típicos"></a>
### Typical Execution Times
- **Lean4 Detection**: ~100ms
- **Monte Carlo Dropout**: ~2-5s (depends on n_samples)
- **Grover Search**: ~500ms (simulation)
- **Shor Algorithm**: ~1-3s (small numbers)

<a id="memoria-utilizada"></a>
### Memory Used
- **Uncertainty Quantification**: ~50-100MB
- **Quantum Simulation**: ~100-200MB
- **Lean4 Operations**: ~10-50MB

---

<a id="-próximos-pasos"></a>
## 🚀 Next Steps

<a id="integraciones-pendientes"></a>
### Pending Integrations
1. **Database Persistence**: Integrate with conjecture persistence
2. **Agent Bridges**: Direct connection with Agent 1
3. **Real Hardware**: Integration with real quantum hardware
4. **Production Deployment**: Production configuration

<a id="optimizaciones-futuras"></a>
### Future Optimizations
1. **Caching**: Computational results cache
2. **Async Processing**: Massive asynchronous processing
3. **Resource Management**: Intelligent resource management
4. **Monitoring**: Advanced metrics and logging

---

<a id="-soporte"></a>
## 📞 Support

For specific issues:
1. Check logs in `app/logs/`
2. Run diagnostic tests
3. Verify environment configuration
4. Consult API documentation

**Last update**: September 2025

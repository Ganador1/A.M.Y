# Guía de Inicio Rápido

## 1. Clonar y Preparar Entorno
```bash
git clone <repo>
cd atlas
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Ejecutar Aplicación
```bash
python main.py
```
Endpoint salud: `http://localhost:8000/health` (plan). 

## 3. Primera Optimización
Utiliza servicio de optimización inteligente (cuando expuesto) o scripts de ejemplo.

## 4. Validar Integridad
Revisa logs de hashing y verifica artefactos generados.

## 5. Ejecutar Tests Clave
```bash
pytest -q tests/unit/test_reproducibility_service.py
```

## 6. Explorar Documentación
- Infraestructura Oculta: README sección correspondiente
- Optimización: INTELLIGENT_OPTIMIZATION_GUIDE.md
- Integridad: BLOCKCHAIN_VALIDATION_GUIDE.md

## 7. Siguientes Pasos
| Objetivo | Acción |
|----------|-------|
| Añadir servicio propio | Implementar adapter (plan) |
| Medir speedup | Activar profiler |
| Asegurar reproducibilidad | Congelar versiones y hash configs |

---
Inicio rápido completo.

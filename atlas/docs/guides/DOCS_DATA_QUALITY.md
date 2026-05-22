# Data Quality con Great Expectations (y fallback)

Este proyecto incluye un ejemplo de validación de calidad de datos que funciona aun sin instalar Great Expectations.

## ¿Qué valida?
- id: no nulo y único (si existe)
- value: numérico; si todos los valores están entre [0,1], también verifica ese rango
- label: en {A, B} (si existe)

## Cómo correrlo
- VS Code: Terminal > Run Task… > "Data quality: validate toy dataset"
- O manual:

```bash
source .venv/bin/activate
python examples/ge_validate_toy_dataset.py
```

Salida:
- `data/data_quality_report.json` con el detalle de checks ejecutados y estado (PASSED/FAILED en consola).

## Dependencias opcionales
- Si `great_expectations` está disponible, usa expectativas GE.
- Si no, usa pandas (si existe) o stdlib (csv) — no es necesario instalar nada extra para un smoke test.

## Integración con DVC E2E
- El ejemplo DVC (`examples/dvc_versioning_e2e.py`) genera un CSV toy en `data/` que puede ser validado por este script.

## Siguientes pasos sugeridos
- Añadir Data Docs de GE (HTML) y versionar suites.
- Integrar validaciones a CI para datasets críticos.

# Engineering: guía de API

Este dominio se expone principalmente vía routers de plataforma en `app/routers/`.

Puntos de entrada frecuentes:
- Lab automation: `app/routers/lab_automation.py`, `app/routers/advanced_lab_automation.py`
- Hardware abstraction: `app/routers/hardware_abstraction.py`
- Synthesis: `app/routers/synthesis_equipment.py`

Para la lista exacta de endpoints y prefijos, ver:
- `app/routers/router_registry.py` (prefijos, tags, lazy-load)
- Archivos individuales en `app/routers/`

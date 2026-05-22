# Dominio: Engineering

## Qué es
Dominio para automatización de laboratorio, equipamiento, síntesis y workflows experimentales.

## Ubicación en el código
- Paquete: `app/domains/engineering/`
- Routers (dominio): `app/domains/engineering/routers/` (no hay `routers/api.py` consolidado)
- Servicios: `app/domains/engineering/services/`

## Servicios principales
- `LabAutomationService`: `app/domains/engineering/services/lab_automation_service.py`
- `LabEquipmentBridge`: `app/domains/engineering/services/lab_equipment_bridge.py`
- `HardwareAbstractionService`: `app/domains/engineering/services/hardware_abstraction_service.py`
- `AdvancedLabAutomationService`: `app/domains/engineering/services/advanced_lab_automation_service.py`
- `ExperimentalValidator`: `app/domains/engineering/services/experimental_validator.py`
- `MaterialsDiscoveryService`: `app/domains/engineering/services/materials_discovery_service.py`

## Entrada HTTP (routers de plataforma)
En este repo hay routers generales en `app/routers/` que actúan como fachada:
- `app/routers/lab_automation.py`
- `app/routers/advanced_lab_automation.py`
- `app/routers/hardware_abstraction.py`
- `app/routers/synthesis_equipment.py`
- `app/routers/experimental_toolkit.py` / `experimental_protocols.py`

## Referencias cercanas al código
- `app/domains/engineering/README.md`
- `app/domains/engineering/API_GUIDE.md`
- `app/domains/engineering/SERVICES.md`
- `app/domains/engineering/EXAMPLES.md`

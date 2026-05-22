# Dominio: Neuroscience

## Qué es
Dominio para neurociencia computacional: neuroimaging, simulación, neuromorphic, análisis ligero de EEG y servicios de redes neuronales.

## Ubicación en el código
- Paquete: `app/domains/neuroscience/`
- Routers (dominio): `app/domains/neuroscience/routers/` (no hay `routers/api.py` consolidado)
- Servicios: `app/domains/neuroscience/services/`

## Servicios principales
- `NeuroscienceLightService`: `app/domains/neuroscience/services/neuroscience_light_service.py`
- `NeuralNetworksService`: `app/domains/neuroscience/services/neural_networks_service.py`
- `ComputationalBiologyService`: `app/domains/neuroscience/services/computational_biology.py`
- Submódulos: `neuroimaging/`, `neuromorphic/`

## Entrada HTTP (routers de plataforma)
El repo expone endpoints también en `app/routers/`:
- `app/routers/neuro_simulation.py`
- `app/routers/neuroscience_light.py`

## Referencias cercanas al código
- `app/domains/neuroscience/README.md`
- `app/domains/neuroscience/API_GUIDE.md`
- `app/domains/neuroscience/SERVICES.md`
- `app/domains/neuroscience/EXAMPLES.md`
- `app/domains/neuroscience/IMAGING_PROTOCOLS.md`

# Physics: ejemplos

## Ejemplo (SDK Python) - QAOA/VQE vía servicio
```python
from app.domains.physics.services.quantum_algorithms_service import QuantumAlgorithmsService

service = QuantumAlgorithmsService()
result = await service.compute_vqe_ground_state(
    molecule_data={"geometry": "H 0 0 0; H 0 0 0.735", "basis": "sto3g"}
)
print(result)
```

## Ejemplo (REST)
La ruta exacta depende del router usado:
- Router de dominio: `/physics/...`
- Router de plataforma: ver `app/routers/quantum_algorithms.py`

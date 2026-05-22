# Examples for Physics Domain

## Quantum Spin Evolution
```python
from app.domains.physics.quantum import QuantumPhysicsService

service = QuantumPhysicsService()
result = service.simulate_spin_evolution(Bx=0, By=0, Bz=1.0, t_max=10, n_points=100)
print(result)
```

## Particle Physics Analysis
```python
from app.domains.physics.quantum import ParticlePhysicsService

service = ParticlePhysicsService()
events = [...]  # Sample event data
result = service.analyze_events(events, analysis_type="jet_reconstruction")
print(result)
```

## QAOA Optimization
```bash
curl -X POST "http://localhost:8000/api/physics/quantum/algorithms/qaoa" \
     -H "Content-Type: application/json" \
     -d '{"problem": "maxcut", "graph": [[0,1],[1,2],[2,0]], "p": 2}'
```
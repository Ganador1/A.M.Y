# Examples for Neuroscience Domain

## EEG Band Power Analysis
```python
from app.domains.neuroscience.services import NeuroscienceLightService

service = NeuroscienceLightService()
result = service.analyze_band_powers(eeg_data)
```

## Neural Simulation
```python
from app.domains.neuroscience.services import NeuroSimulationService

service = NeuroSimulationService()
simulation = service.run_brian2_simulation(params)
```

## API Example
```bash
curl -X POST "http://localhost:8000/neuroscience/advanced/analyze" \
     -H "Content-Type: application/json" \
     -d '{"modality": "fMRI", "data": "path/to/data"}'
```
# Examples for Chemistry Domain

## Molecular Analysis
```python
from app.domains.chemistry.services.computational_chemistry import ComputationalChemistryService
service = ComputationalChemistryService()
result = service.calculate_descriptors({'smiles': 'C1CCCCC1'})
print(result)
```

## Property Prediction
```bash
curl -X POST \"http://localhost:8000/api/chemistry/chemml/predict\" -H \"Content-Type: application/json\" -d '{\"smiles\": \"CCO\", \"property\": \"solubility\"}'
```

## NMR Analysis
```python
from app.domains.chemistry.services.advanced_nmr_service import AdvancedNMRService
service = AdvancedNMRService()
result = service.analyze_spectrum({'data': [1.2, 2.3, 7.8]})
print(result)
```
# Examples for Medicine Domain

## Protein Structure Prediction
```python
# Assuming service import
service = AlphaFold3ProteinStructureService()
result = service.predict_structure('sequence')
print(result)
```

## Clinical Text Analysis
```bash
curl -X POST \"http://localhost:8000/medical/clinicalbert/analyze\" -d '{\"text\": \"Patient presents with symptoms...\"}'
```

## Personalized Medicine
```python
service = PersonalizedMedicineService()
recommendation = service.recommend_treatment({'genotype': '...'})
print(recommendation)
```
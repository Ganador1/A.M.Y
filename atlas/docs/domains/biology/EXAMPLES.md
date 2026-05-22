# Examples for Biology Domain

## Entity Extraction with BiomedicalNLPService
```python
from axiom.domains.biology.services.biomedical_nlp_service import BiomedicalNLPService

# Initialize the service
nlp_service = BiomedicalNLPService()

# Extract entities from biomedical text
text = "The p53 protein plays a crucial role in cancer development and is often mutated in tumors."
entities = nlp_service.extract_entities(text)

# Print the extracted entities
print("Extracted Entities:")
for entity_type, entity_list in entities.items():
    print(f"{entity_type}: {', '.join(entity_list)}")

# Expected output:
# Extracted Entities:
# Gene/Protein: p53
# Disease: cancer, tumors
```

## Text Generation with BioGPT
```python
from axiom.domains.biology.services.biogpt_service import BioGPTService

# Initialize the service
biogpt_service = BioGPTService()

# Generate biomedical text
prompt = "Explain the process of DNA replication in simple terms."
response = biogpt_service.generate(prompt, max_length=200)

print(f"BioGPT Response: {response}")
```

## API Example: Advanced Genomics Variant Calling
```bash
curl -X POST "http://localhost:8000/api/biology/advanced-genomics/variant-calling" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -d '{
       "sample_id": "SAMPLE001",
       "reference_genome": "GRCh38",
       "sequencing_type": "WGS",
       "quality_threshold": 30
     }'
```

## Computational Biology Neural Simulation
```python
from axiom.domains.biology.services.computational_biology import ComputationalBiologyService

# Initialize the service
comp_bio_service = ComputationalBiologyService()

# Define neural simulation parameters
simulation_params = {
    "neurons": 100,
    "simulation_time": 1000,  # ms
    "input_current": 0.7,     # nA
    "model_type": "LIF"       # Leaky Integrate-and-Fire
}

# Run the simulation
simulation_id = comp_bio_service.run_neural_simulation(simulation_params)

# Get simulation results
results = comp_bio_service.get_simulation_results(simulation_id)

# Plot spike raster
comp_bio_service.plot_spike_raster(results)
```
# API Guide for Biology Domain

## Overview
This guide covers the key API endpoints for the Biology domain in AXIOM. All endpoints require authentication via API key.

## Key Endpoints

### Biomedical NLP
- **Endpoint**: `/api/biology/biomedical-nlp/extract-entities`
- **Method**: POST
- **Description**: Extract biomedical entities from text.
- **Example Request**:
  ```bash
  curl -X POST "http://localhost:8000/api/biology/biomedical-nlp/extract-entities" \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer YOUR_API_KEY" \
       -d '{"text": "The p53 protein plays a crucial role in cancer development."}'
  ```

### BioGPT Text Generation
- **Endpoint**: `/api/biology/biogpt/generate`
- **Method**: POST
- **Description**: Generate biomedical text using BioGPT.
- **Example Request**:
  ```bash
  curl -X POST "http://localhost:8000/api/biology/biogpt/generate" \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer YOUR_API_KEY" \
       -d '{"prompt": "Explain DNA replication", "max_length": 200}'
  ```

### Advanced Genomics
- **Endpoint**: `/api/biology/advanced-genomics/variant-calling`
- **Method**: POST
- **Description**: Perform variant calling on genomic data.
- **Example Request**:
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

### Computational Biology
- **Endpoint**: `/api/biology/computational/simulate`
- **Method**: POST
- **Description**: Run computational biology simulations.
- **Example Request**:
  ```bash
  curl -X POST "http://localhost:8000/api/biology/computational/simulate" \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer YOUR_API_KEY" \
       -d '{
         "simulation_type": "neural",
         "parameters": {
           "neurons": 100,
           "simulation_time": 1000,
           "input_current": 0.7,
           "model_type": "LIF"
         }
       }'
  ```

## Authentication
All endpoints require an API key in the Authorization header.

## Error Handling
Standard HTTP status codes are used, with detailed error messages in the response body.

## Rate Limiting
API requests are limited to 100 requests per minute per API key.

## Response Format
All responses follow a standard format:
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { ... },
  "timestamp": "2023-06-15T12:34:56Z"
}
```
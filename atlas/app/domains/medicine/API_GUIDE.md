# API Guide for Medicine Domain

## Authentication
- Most endpoints require API key. Include `Authorization: Bearer YOUR_API_KEY`.

## Unified REST Endpoints
- `GET /medical/services` — List available medical services. Optional `include_capabilities=true`.
- `GET /medical/service/{service_name}/capabilities` — Get capabilities for a service.
- `POST /medical/analyze` — Generic medical analysis across services.
- `POST /medical/predict` — Generic medical predictions (e.g., protein structure, NLP).
- `POST /medical/process` — Generic medical data processing.
- `GET /medical/health` — Health status for all medical services.

## Legacy REST Endpoints
- `POST /medical/compute` — Generic compute operation (legacy consolidated API).
- `GET /medical/` — Domain info metadata.

## WebSocket Endpoints
- `WS /ws/medical/stream/{patient_id}` — Patient data streams. Query: `stream_types`, `processing_mode`.
- `WS /ws/medical/alerts` — Global medical alerts stream.
- `WS /ws/medical/monitor/{device_id}` — Device monitoring stream.
- `WS /ws/medical/dashboard` — Real-time multi-stream dashboard.
- `POST /ws/medical/simulate/{patient_id}` — Start data simulation for demos.

## Examples
- List services with capabilities
```bash
curl -X GET "http://localhost:8000/medical/services?include_capabilities=true" \
     -H "Authorization: Bearer YOUR_API_KEY"
```

- Unified analysis (genomics)
```bash
curl -X POST "http://localhost:8000/medical/analyze" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
           "service_type": "genomics",
           "analysis_type": "variant_calling",
           "data": {"sequence": "ATCG...", "reference_genome": "hg38"},
           "parameters": {"quality_threshold": 30}
         }'
```

- Unified prediction (AlphaFold3)
```bash
curl -X POST "http://localhost:8000/medical/predict" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
           "service_type": "alphafold3",
           "prediction_type": "protein_structure",
           "input_data": {"sequence": "MKTVRQ..."},
           "confidence_threshold": 0.8
         }'
```

- WebSocket patient stream
```bash
ws://localhost:8000/ws/medical/stream/PATIENT_123?stream_types=ecg,vital_signs&processing_mode=analyzed
```

- Start data simulation (demo)
```bash
curl -X POST "http://localhost:8000/ws/medical/simulate/PATIENT_123" \
     -d 'stream_type=vital_signs&duration_seconds=30'
```
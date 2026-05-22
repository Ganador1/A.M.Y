# API Guide for Climate Domain

## Authentication
Required for data access.

## Key Endpoints

### Climate Evidence
- **POST /climate/evidence**: Get climate evidence analysis.
  - Parameters: action = "climate_evidence"
  - Example:
    ```bash
    curl -X POST "http://localhost:8000/api/climate/evidence" \
         -H "Content-Type: application/json" \
         -d '{"action": "climate_evidence"}'
    ```
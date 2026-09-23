# API Guide for Astronomy Domain

## Authentication
API key required for most endpoints.

## Key Endpoints

### Telescope Data Analysis
- **POST /astronomy/telescope-data**: Analyze telescope observations.
  - Parameters: data
  - Example:
    ```bash
    curl -X POST "http://localhost:8000/api/astronomy/telescope-data" \
         -H "Content-Type: application/json" \
         -d '{"data": {...}}'
    ```

### Exoplanet Detection
- **POST /astronomy/exoplanet-detection**: Detect exoplanets.
  - Parameters: light_curve
  - Example:
    ```bash
    curl -X POST "http://localhost:8000/api/astronomy/exoplanet-detection" \
         -H "Content-Type: application/json" \
         -d '{"light_curve": {...}}'
    ```

### Galaxy Analysis
- **POST /astronomy/galaxy-analysis**: Analyze galaxy data.
  - Parameters: image_data
  - Example:
    ```bash
    curl -X POST "http://localhost:8000/api/astronomy/galaxy-analysis" \
         -H "Content-Type: application/json" \
         -d '{"image_data": {...}}'
    ```

See /docs for full API.
# API Guide for Engineering Domain

## Authentication
Requires scopes like "lab-equipment".

## Key Endpoints

### List Equipment
- **GET /engineering/lab-equipment/equipment**: List available equipment.

### Submit Task
- **POST /engineering/lab-equipment/tasks**: Submit lab task.
  - Example:
    ```bash
    curl -X POST "http://localhost:8000/api/engineering/lab-equipment/tasks" \
         -H "Content-Type: application/json" \
         -d '{"equipment_id": "spec1", "parameters": {...}}'
    ```

### Run Experiment
- **POST /api/v1/experimental/run**: Run experimental tool.
  - Example:
    ```bash
    curl -X POST "http://localhost:8000/api/v1/experimental/run" \
         -H "Content-Type: application/json" \
         -d '{"domain": "chemistry", "tool": "molecular_properties", "parameters": {...}}'
    ```
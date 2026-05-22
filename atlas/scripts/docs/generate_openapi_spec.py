import json
from app.main import app  # Asumiendo que app es la instancia FastAPI en main.py

def generate_openapi():
    openapi_schema = app.openapi()
    with open('docs/api/openapi_spec.json', 'w') as f:
        json.dump(openapi_schema, f, indent=2)
    print("OpenAPI spec generado en docs/api/openapi_spec.json")

if __name__ == "__main__":
    generate_openapi()
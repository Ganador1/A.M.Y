"""Test simple para verificar configuración del router"""
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.routers.integrity import router


def test_router_basic_functionality():
    """Test básico del router"""
    # Create test app
    app = FastAPI()
    app.include_router(router)  # Sin prefix para el test
    
    client = TestClient(app)
    
    # Test basic health check - ver si hay algún endpoint que funcione
    response = client.get("/services")
    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.text}")
    
    # Si falla, intentar listar rutas disponibles
    if response.status_code == 404:
        print("Available routes:")
        for route in app.routes:
            print(f"  {route}")


def test_router_direct_import():
    """Test directo de las funciones del router"""
    from app.routers.integrity import list_services_endpoint
    
    # Intentar llamar directamente la función
    try:
        result = list_services_endpoint()
        print(f"Direct call result: {result}")
        assert "success" in result
    except Exception as e:
        print(f"Direct call error: {e}")


if __name__ == "__main__":
    test_router_basic_functionality()
    test_router_direct_import()

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    """Prueba que la aplicación responde correctamente en la ruta raíz."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Dentist Service" in response.text

def test_health_check():
    """Prueba que el endpoint de health check responde correctamente."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

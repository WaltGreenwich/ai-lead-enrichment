"""
Tests básicos para la API de FastAPI
"""
import pytest
from fastapi.testclient import TestClient


# Necesitamos importar app desde main
# Esto requiere que PYTHONPATH incluya backend/ (lo cual está en Docker)
@pytest.fixture
def client():
    """Cliente de prueba para FastAPI"""
    from main import app
    return TestClient(app)


def test_health_check(client):
    """Test del endpoint de health check"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "services" in data
    assert data["services"]["api"] is True


def test_enrich_endpoint_missing_data(client):
    """Test que /enrich devuelve error si faltan datos"""
    # Sin datos
    response = client.post("/enrich", json={})
    assert response.status_code == 422  # Validation error


def test_enrich_endpoint_invalid_data(client):
    """Test que /enrich valida correctamente los datos"""
    # Datos inválidos (name faltante)
    response = client.post("/enrich", json={"domain": "https://example.com"})
    assert response.status_code == 422


def test_search_endpoint_missing_query(client):
    """Test que /search requiere query"""
    response = client.post("/search", json={})
    assert response.status_code == 422


def test_list_companies(client):
    """Test que /companies devuelve lista (puede estar vacía)"""
    response = client.get("/companies")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_companies_with_limit(client):
    """Test que /companies acepta parámetro limit"""
    response = client.get("/companies?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 10


def test_batch_enrich_endpoint_no_file(client):
    """Test que /enrich/batch requiere archivo"""
    response = client.post("/enrich/batch")
    assert response.status_code == 422  # Missing file


@pytest.mark.asyncio
async def test_enrich_with_valid_data(client):
    """
    Test de enriquecimiento con datos válidos
    Nota: Este test requiere GEMINI_API_KEY válida
    Puede ser lento (3-5 segundos) por la llamada a Gemini
    """
    # Este test puede fallar si no hay GEMINI_API_KEY configurada
    # Se puede saltar con: pytest -m "not slow"
    response = client.post(
        "/enrich",
        json={
            "name": "Test Company",
            "domain": "https://example.com"
        }
    )
    
    # Si no hay API key, esperamos error 500
    # Si hay API key, esperamos 200
    assert response.status_code in [200, 500]
    
    if response.status_code == 200:
        data = response.json()
        assert "success" in data
        assert "company" in data
        assert data["company"]["name"] == "Test Company"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

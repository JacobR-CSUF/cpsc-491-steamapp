from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_returns_200():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "api" in data
    assert "postgres" in data
    assert "redis" in data
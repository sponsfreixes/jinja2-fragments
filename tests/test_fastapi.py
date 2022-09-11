from fastapi.testclient import TestClient


def test_app(fastapi_app):
    client = TestClient(fastapi_app)
    response = client.get("/")
    assert response.status_code == 200

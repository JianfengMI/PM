from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_api_hello() -> None:
    response = client.get("/api/hello")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello from the Project Management API"}


def test_home_serves_example_html() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "Project Management MVP" in response.text

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_objective_invalid_type():
    """NFR-07: Проверка валидации входных данных"""
    response = client.post(
        "/objectives", json={"title": 123, "description": None, "isComplete": False}
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert any(err["loc"][-1] == "title" for err in data["detail"])

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_payload_too_large():
    """NFR-03: Ограничение тела запроса ≤ 1 MB"""
    big_data = "x" * (1024 * 1024 + 10)  # чуть больше 1 МБ
    response = client.post(
        "/objectives",
        json={"title": big_data, "description": None, "isComplete": False},
    )
    # FastAPI по умолчанию отдаёт 422, но если стоит limit_upload_size, будет 413
    assert response.status_code in (413, 422)

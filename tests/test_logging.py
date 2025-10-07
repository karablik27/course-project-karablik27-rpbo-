from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_access_logging(caplog):
    """NFR-06: Проверка логирования запросов уровня INFO+ через caplog"""
    caplog.set_level("INFO", logger="access")

    # Совершаем несколько запросов
    client.get("/objectives")
    client.get("/objectives/999")
    client.post("/objectives", json={"title": "Log test", "isComplete": False})

    logs = caplog.text
    print("\n--- Captured logs ---\n", logs)

    # Проверяем, что записи логов присутствуют
    assert "GET /objectives" in logs
    assert "POST /objectives" in logs

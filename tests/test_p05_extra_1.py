# NFR-07 / R7: Валидация и whitelisting полей ответа (response_model)
# Threat Model: F14/F16/F19 (чтение из DB через ORM), TB1 (HTTP boundary)
from starlette.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_response_model_does_not_leak_extra_fields():
    """
    Проверяем, что лишние поля из запроса не "просачиваются" в ответ.
    Это подтверждает whitelisting на уровне Pydantic response_model.
    NFR-07 (валидация ввода) + Risk R7 (info disclosure).
    """
    payload = {
        "title": "Secure Objective",
        "description": "no leaks",
        "isComplete": False,
        "internal": "should_not_be_returned",
    }
    r = client.post("/objectives", json=payload)
    assert r.status_code in (
        200,
        201,
        409,
        400,
    ), r.text  # допускаем разные статусы домена
    data = r.json()
    # Ответ должен соответствовать Objective (id, title, description, isComplete)
    assert "internal" not in data, "response_model пропустил приватное поле"
    assert "title" in data and "id" in data

# tests/test_r1_api_key_gate.py
from starlette.testclient import TestClient

from app.main import app


def test_post_requires_api_key_when_set():
    # Включаем ключ «на лету», чтобы не перезагружать модуль
    app.state.API_EDGE_KEY = "secret123"
    client = TestClient(app)

    # Без ключа — 401 Problem+JSON
    r = client.post("/objectives", json={"title": "x"})
    assert r.status_code == 401
    assert r.headers["content-type"].startswith("application/problem+json")
    assert r.json()["title"] == "Unauthorized"

    # С правильным ключом — проходит дальше (409/400/200 — неважно, главное не 401)
    r2 = client.post("/objectives", json={"title": "x"}, headers={"X-API-Key": "secret123"})
    assert r2.status_code != 401

    # вернём ключ в «выключено», чтобы не влиял на другие тесты
    app.state.API_EDGE_KEY = None

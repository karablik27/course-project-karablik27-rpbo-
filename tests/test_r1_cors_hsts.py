# tests/test_r1_cors_hsts.py
from starlette.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_hsts_header_present():
    r = client.get("/objectives")
    assert "Strict-Transport-Security" in r.headers


def test_cors_allows_known_origin():
    # Если ALLOWED_ORIGINS задан и включает этот Origin — должен пройти preflight
    r = client.options(
        "/objectives",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    # если origin в allowlist, middleware вернёт CORS заголовок
    acr = {k.lower(): v for k, v in r.headers.items()}
    assert r.status_code in (200, 204)
    assert acr.get("access-control-allow-origin") in ("*", "http://localhost:5173")


def test_cors_blocks_unknown_origin():
    r = client.options(
        "/objectives",
        headers={
            "Origin": "https://evil.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    # для неразрешённого origin заголовка быть не должно
    acr = {k.lower(): v for k, v in r.headers.items()}
    assert "access-control-allow-origin" not in acr

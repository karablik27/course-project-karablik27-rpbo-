# NFR-07 / R1: HSTS заголовок правильно сформирован
# Threat Model: F1 (User->API), TB1 (периметр)
from starlette.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_hsts_policy_contains_directives():
    """
    Дополнительная проверка HSTS-политики: должны присутствовать max-age и includeSubDomains.
    Это усиливает проверку безопасности периметра (R1).
    """
    r = client.get("/objectives")
    assert r.status_code in (200, 204)
    hsts = r.headers.get("Strict-Transport-Security", "")
    assert "max-age=" in hsts
    assert "includeSubDomains" in hsts

# tests/test_p06_c3_masking.py
import os

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_email_and_password_masked_in_logs(tmp_path):
    """C3★★ — Проверяем, что PII (email/password) маскируются в логах"""
    log_file = "error.log"
    if os.path.exists(log_file):
        os.remove(log_file)

    @app.get("/crash_pii")
    def crash_pii():
        raise ValueError("User test@example.com password='12345'")

    r = client.get("/crash_pii")
    assert r.status_code == 500
    data = r.json()
    assert "Internal Server Error" in data["title"]

    with open(log_file) as f:
        logs = f.read()
        # email должен быть скрыт
        assert "[email]" in logs
        # пароль должен быть замаскирован
        assert "password:[MASKED]" in logs
        # оригинальный пароль не должен встречаться
        assert "12345" not in logs

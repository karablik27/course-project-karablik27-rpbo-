import os

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_exception_logging(tmp_path):
    """NFR-04: Проверка централизованной обработки ошибок"""

    @app.get("/crash")
    def crash():
        raise ValueError("Test crash")

    r = client.get("/crash")
    assert r.status_code == 500
    data = r.json()
    assert "title" in data and data["title"] == "Internal Server Error"
    assert os.path.exists("error.log")
    with open("error.log") as f:
        logs = f.read()
        assert "Unhandled error" in logs

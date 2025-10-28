# tests/test_p06_negative_cases.py

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# Negative — BodySizeLimitMiddleware
def test_oversized_body_rejected():
    """P06/R3 — тело запроса превышает лимит (1МБ)"""
    too_big = "X" * (1_100_000)
    r = client.post("/objectives", json={"title": too_big})
    assert r.status_code in (413, 422), f"Unexpected status {r.status_code}"


# Negative — RFC7807 unified errors
def test_internal_error_masked_from_client(tmp_path):
    """P06/R11 — исключение не раскрывает stacktrace"""

    @app.get("/explode")
    def explode():
        raise RuntimeError("Sensitive server info")

    r = client.get("/explode")
    assert r.status_code == 500
    data = r.json()
    assert "Internal Server Error" in data["title"]
    assert "Sensitive" not in r.text  # клиент не должен видеть сообщение


#  Negative — Secure file upload
def test_invalid_file_type_rejected(tmp_path):
    """P06/R6 — загрузка не-изображения отклоняется"""
    fake_file = tmp_path / "payload.txt"
    fake_file.write_text("MALWARE CODE")
    with open(fake_file, "rb") as f:
        r = client.post("/files/upload", files={"file": ("payload.txt", f, "text/plain")})
    assert r.status_code == 400
    assert "Invalid file type" in r.text


def test_too_large_file_rejected(tmp_path):
    """P06/R6 — загрузка слишком большого файла (>5МБ)"""
    huge_path = tmp_path / "huge.jpg"
    with open(huge_path, "wb") as f:
        f.write(b"x" * (5 * 1024 * 1024 + 10))
    with open(huge_path, "rb") as f:
        r = client.post("/files/upload", files={"file": ("huge.jpg", f, "image/jpeg")})
    assert r.status_code == 413


#  Negative — API Key Gate
def test_invalid_api_key_rejected():
    """P06/R9 — модифицирующие операции без ключа/с неверным ключом"""
    app.state.API_EDGE_KEY = "secret-key"
    r = client.post("/objectives", json={"title": "Bad key"})
    assert r.status_code == 401
    assert "Unauthorized" in r.text

    r2 = client.post(
        "/objectives",
        json={"title": "Wrong"},
        headers={"X-API-Key": "wrong-key"},
    )
    assert r2.status_code == 401
    app.state.API_EDGE_KEY = None  # вернуть в исходное состояние


# ⃣ Negative — Validation / normalization
def test_invalid_input_rejected():
    """P06/NFR07 — типы и логика ввода нарушены"""
    # current_value >= target_value → ошибка
    payload = {"objective_id": 1, "title": "bad", "target_value": 10, "current_value": 15}
    r = client.post("/key_results", json=payload)
    assert r.status_code == 400
    assert "must be strictly less" in r.text

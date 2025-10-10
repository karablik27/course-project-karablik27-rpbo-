from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_error_rate_under_1_percent():
    """NFR-02: Проверка, что error_rate ≤ 1%"""
    total_requests = 100
    errors = 0

    for i in range(total_requests):
        obj_id = 1 if i != 99 else 999
        response = client.get(f"/objectives/{obj_id}")
        if response.status_code >= 400:
            errors += 1

    error_rate = errors / total_requests * 100
    print(f"\n Error rate: {error_rate:.2f}%")
    assert error_rate <= 1.0, f"Error rate too high: {error_rate:.2f}%"

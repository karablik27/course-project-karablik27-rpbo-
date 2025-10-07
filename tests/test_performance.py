import time
from statistics import quantiles

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_api_performance_p95():
    """NFR-01: Проверка, что p95 времени ответа ≤ 500 мс"""
    durations = []
    for _ in range(50):
        start = time.perf_counter()
        response = client.get("/objectives")
        end = time.perf_counter()
        assert response.status_code == 200
        durations.append((end - start) * 1000)

    p95 = quantiles(durations, n=100)[94]
    print(f"\n p95 = {p95:.2f} ms")
    assert p95 <= 500, f"p95 слишком большой: {p95:.2f} мс"

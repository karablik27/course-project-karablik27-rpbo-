from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_objective_not_found():
    r = client.get("/objectives/999")
    assert r.status_code == 404
    body = r.json()
    assert body["detail"] == "Objective not found"


def test_keyresult_not_found():
    r = client.put("/key_results/999", params={"current_value": 5})
    assert r.status_code == 404
    body = r.json()
    assert body["detail"] == "KeyResult not found"

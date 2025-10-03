from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_key_result_and_get_by_objective():
    # создаём цель
    client.post(
        "/objectives",
        json={"id": 4, "title": "KR Parent", "description": None, "isComplete": False},
    )
    # создаём KR
    payload = {
        "id": 30,
        "objective_id": 4,
        "title": "KR-1",
        "target_value": 100,
        "current_value": 10,
    }
    r = client.post("/key_results", json=payload)
    assert r.status_code == 200
    kr = r.json()
    assert kr["title"] == "KR-1"
    # получаем KR по objective
    r2 = client.get("/key_results/4/by_objective")
    assert r2.status_code == 200
    assert len(r2.json()) >= 1


def test_create_key_result_objective_not_found():
    payload = {
        "id": 31,
        "objective_id": 999,
        "title": "Invalid",
        "target_value": 10,
        "current_value": 5,
    }
    r = client.post("/key_results", json=payload)
    assert r.status_code == 404
    assert r.json()["detail"] == "Objective not found"


def test_update_key_result():
    client.post(
        "/objectives",
        json={"id": 5, "title": "Upd KR", "description": None, "isComplete": False},
    )
    client.post(
        "/key_results",
        json={
            "id": 40,
            "objective_id": 5,
            "title": "KR-upd",
            "target_value": 10,
            "current_value": 2,
        },
    )
    r = client.put("/key_results/40", params={"current_value": 7})
    assert r.status_code == 200
    assert r.json()["current_value"] == 7


def test_update_key_result_not_found():
    r = client.put("/key_results/999", params={"current_value": 5})
    assert r.status_code == 404
    assert r.json()["detail"] == "KeyResult not found"


def test_delete_key_result():
    r_obj = client.post(
        "/objectives",
        json={"title": "Del KR", "description": None, "isComplete": False},
    )
    obj_id = r_obj.json()["id"]

    r_kr = client.post(
        "/key_results",
        json={
            "objective_id": obj_id,
            "title": "KR-del",
            "target_value": 5,
            "current_value": 1,
        },
    )
    kr_id = r_kr.json()["id"]

    # удаляем key result
    r = client.delete(f"/key_results/{kr_id}")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "deleted"
    assert body["key_result_id"] == kr_id

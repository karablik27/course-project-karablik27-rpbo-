from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_key_result_and_get_by_objective():
    # создаём цель
    r_obj = client.post(
        "/objectives",
        json={"title": "KR Parent", "description": None, "isComplete": False},
    )
    assert r_obj.status_code == 200
    obj_id = r_obj.json()["id"]

    # создаём KR
    payload = {
        "objective_id": obj_id,
        "title": "KR-1",
        "target_value": 100,
        "current_value": 10,
    }
    r = client.post("/key_results", json=payload)
    assert r.status_code == 200
    kr = r.json()
    assert kr["title"] == "KR-1"

    # получаем KR по objective
    r2 = client.get(f"/key_results/{obj_id}/by_objective")
    assert r2.status_code == 200
    assert len(r2.json()) >= 1


def test_create_key_result_objective_not_found():
    payload = {
        "objective_id": 999,
        "title": "Invalid",
        "target_value": 10,
        "current_value": 5,
    }
    r = client.post("/key_results", json=payload)
    assert r.status_code == 404
    assert r.json()["detail"] == "Objective not found"


def test_update_key_result():
    # создаём цель
    r_obj = client.post(
        "/objectives",
        json={"title": "Upd KR", "description": None, "isComplete": False},
    )
    obj_id = r_obj.json()["id"]

    # создаём KR
    r_kr = client.post(
        "/key_results",
        json={
            "objective_id": obj_id,
            "title": "KR-upd",
            "target_value": 10,
            "current_value": 2,
        },
    )
    assert r_kr.status_code == 200
    kr_id = r_kr.json()["id"]

    # обновляем current_value
    r = client.put(f"/key_results/{kr_id}", params={"current_value": 7})
    assert r.status_code == 200
    assert r.json()["current_value"] == 7


def test_update_key_result_not_found():
    r = client.put("/key_results/999", params={"current_value": 5})
    assert r.status_code == 404
    assert r.json()["detail"] == "KeyResult not found"


def test_delete_key_result():
    # создаём цель
    r_obj = client.post(
        "/objectives",
        json={"title": "Del KR", "description": None, "isComplete": False},
    )
    obj_id = r_obj.json()["id"]

    # создаём KR
    r_kr = client.post(
        "/key_results",
        json={
            "objective_id": obj_id,
            "title": "KR-del",
            "target_value": 5,
            "current_value": 1,
        },
    )
    assert r_kr.status_code == 200
    kr_id = r_kr.json()["id"]

    # удаляем key result
    r = client.delete(f"/key_results/{kr_id}")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "deleted"
    assert body["key_result_id"] == kr_id

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_and_get_objective():
    payload = {
        "id": 1,
        "title": "Learn FastAPI",
        "description": "Build API",
        "isComplete": False,
    }
    r = client.post("/objectives", json=payload)
    assert r.status_code == 200
    obj = r.json()
    assert obj["title"] == "Learn FastAPI"
    assert obj["isComplete"] is False

    r2 = client.get("/objectives/1")
    assert r2.status_code == 200
    assert r2.json()["id"] == 1


def test_get_objective_not_found():
    r = client.get("/objectives/999")
    assert r.status_code == 404
    assert r.json()["detail"] == "Objective not found"


def test_get_all_objectives():
    r = client.get("/objectives")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_progress_objective():
    # создаём новую цель
    client.post(
        "/objectives",
        json={"id": 2, "title": "With KR", "description": None, "isComplete": False},
    )
    # создаём KR
    client.post(
        "/key_results",
        json={
            "id": 10,
            "objective_id": 2,
            "title": "Write tests",
            "target_value": 10,
            "current_value": 5,
        },
    )
    r = client.get("/objectives/2/progress")
    assert r.status_code == 200
    assert "progress" in r.json()


def test_delete_objective_cascade():
    # создаём objective
    r_obj = client.post(
        "/objectives",
        json={"title": "Cascade", "description": None, "isComplete": False},
    )
    obj_id = r_obj.json()["id"]

    # создаём KR
    client.post(
        "/key_results",
        json={
            "objective_id": obj_id,
            "title": "KR",
            "target_value": 5,
            "current_value": 2,
        },
    )

    # удаляем objective
    r = client.delete(f"/objectives/{obj_id}")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "deleted"
    assert body["objective_id"] == obj_id
    assert body["deleted_key_results"] == 1

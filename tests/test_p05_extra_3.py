# NFR-05 / R4: Интеграционная проверка каскадного удаления через ORM
# Threat Model: F15 (Delete cascade KRs), F12–F20 (ORM<->DB), TB2 (DB boundary)
from starlette.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_delete_objective_cascades_key_results():
    """
    Создаём Objective и привязанный KeyResult. Удаляем Objective.
    Проверяем, что попытка обновить удалённый KR возвращает 404 (каскад сработал).
    NFR-05 (ORM-only и целостность) + Risk R4 (SQL-инъекции/несогласованные изменения).
    """
    # 1) создаём Objective
    r_obj = client.post(
        "/objectives",
        json={"title": "OBJ for cascade", "description": None, "isComplete": False},
    )
    assert r_obj.status_code in (200, 201), r_obj.text
    obj_id = r_obj.json()["id"]

    # 2) создаём KeyResult, связанный с Objective
    kr_payload = {
        "title": "KR for cascade",
        "target_value": 10,
        "current_value": 0,
        "objective_id": obj_id,
    }
    r_kr = client.post("/key_results", json=kr_payload)
    assert r_kr.status_code in (200, 201), r_kr.text
    kr_id = r_kr.json()["id"]

    # 3) удаляем Objective
    r_del = client.delete(f"/objectives/{obj_id}")
    assert r_del.status_code in (200, 204), r_del.text

    # 4) пытаемся обновить KR по id — должен быть 404
    r_update = client.put(f"/key_results/{kr_id}", params={"current_value": 5})
    assert r_update.status_code == 404, r_update.text
    assert r_update.json().get("detail") == "KeyResult not found"

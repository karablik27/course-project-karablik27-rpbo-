from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="SecDev Course App", version="0.1.0")


# Проект называется OKR Tracker то есть Objective and KeyResult Tracker
# Тут 2 модели первая это цель, а вторая на сколько цель выполнена
class Objective(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    isComplete: bool


class KeyResult(BaseModel):
    id: int
    objective_id: int  # Айди цели
    title: str
    target_value: int  # Цель результата
    current_value: int = 0  # Текущий результат


# Временное "хранилище" данных
objectives: List[Objective] = []
key_results: List[KeyResult] = []


# 1. Создать цель (POST /objectives)
@app.post("/objectives", response_model=Objective)
def create_objective(obj: Objective):
    # Проверка на уникальность id
    for existing in objectives:
        if existing.id == obj.id:
            raise HTTPException(
                status_code=400, detail="Objective with this id already exists"
            )
    objectives.append(obj)
    return obj


# 2. Получить все цели (GET /objectives)
@app.get("/objectives", response_model=List[Objective])
def get_objectives():
    return objectives


# 3. Создать ключевой результат для цели (POST /key_results)
@app.post("/key_results", response_model=KeyResult)
def create_key_result(kr: KeyResult):
    # Проверяем, что есть цель с таким objective_id
    if not any(o.id == kr.objective_id for o in objectives):
        raise HTTPException(status_code=404, detail="Objective not found")

    # Проверяем уникальность id
    if any(existing.id == kr.id for existing in key_results):
        raise HTTPException(
            status_code=400, detail="KeyResult with this id already exists"
        )

    # Проверяем, что current_value != target_value
    if kr.current_value == kr.target_value:
        raise HTTPException(
            status_code=400,
            detail="current_value cannot be equal to target_value at creation",
        )

    key_results.append(kr)
    return kr


# 4. Обновить прогресс ключевого результата (PUT /key_results/{kr_id})
@app.put("/key_results/{kr_id}", response_model=KeyResult)
def update_key_result(kr_id: int, current_value: int):
    for kr in key_results:
        if kr.id == kr_id:
            if current_value > kr.target_value:
                raise HTTPException(
                    status_code=400,
                    detail="current_value cannot exceed target_value",
                )

            kr.current_value = current_value
            return kr

    raise HTTPException(status_code=404, detail="KeyResult not found")


# 5. Получить все ключевые результаты для конкретной цели (GET /objectives/{obj_id}/key_results)
@app.get("/objectives/{obj_id}/key_results", response_model=List[KeyResult])
def get_key_results_for_objective(obj_id: int):
    return [kr for kr in key_results if kr.objective_id == obj_id]


# 6. Получить цель по ID (GET /objectives/{obj_id})
@app.get("/objectives/{obj_id}", response_model=Objective)
def get_objective(obj_id: int):
    for obj in objectives:
        if obj.id == obj_id:
            return obj
    raise HTTPException(status_code=404, detail="Objective not found")


# 7. Удалить цель (DELETE /objectives/{obj_id})
@app.delete("/objectives/{obj_id}")
def delete_objective(obj_id: int):
    global objectives, key_results
    # удаляем все key_results этой цели
    key_results = [kr for kr in key_results if kr.objective_id != obj_id]
    # удаляем саму цель
    before = len(objectives)
    objectives = [o for o in objectives if o.id != obj_id]
    if len(objectives) == before:
        raise HTTPException(status_code=404, detail="Objective not found")
    return {"status": "deleted", "objective_id": obj_id}


# 8. Получить прогресс по цели (GET /objectives/{obj_id}/progress)
@app.get("/objectives/{obj_id}/progress")
def get_objective_progress(obj_id: int):
    krs = [kr for kr in key_results if kr.objective_id == obj_id]
    if not krs:
        raise HTTPException(status_code=404, detail="No Key Results for this Objective")
    total = sum(kr.target_value for kr in krs)
    current = sum(kr.current_value for kr in krs)
    percent = round(current / total * 100, 2) if total > 0 else 0
    return {"objective_id": obj_id, "progress": f"{percent}%"}

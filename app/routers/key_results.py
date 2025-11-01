# app/routers/key_results.py
from typing import Any, cast

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import KeyResultDB, ObjectiveDB
from ..schemas import KeyResult, KeyResultCreate

router = APIRouter()


@router.post("", response_model=KeyResult)
def create_key_result(kr: KeyResultCreate, db: Session = Depends(get_db)) -> KeyResult:
    """Создание нового KeyResult, связанного с Objective."""
    if not db.query(ObjectiveDB).filter(ObjectiveDB.id == kr.objective_id).first():
        raise HTTPException(status_code=404, detail="Objective not found")

    if kr.current_value >= kr.target_value:
        raise HTTPException(
            status_code=400,
            detail="current_value must be strictly less than target_value at creation",
        )

    db_kr = KeyResultDB(**kr.model_dump())
    db.add(db_kr)
    db.commit()
    db.refresh(db_kr)
    return db_kr


@router.put("/{kr_id}", response_model=KeyResult)
def update_key_result(
    kr_id: int,
    current_value: int,
    db: Session = Depends(get_db),
) -> KeyResult:
    """Обновление текущего значения KeyResult."""
    kr: KeyResultDB | None = db.query(KeyResultDB).filter(KeyResultDB.id == kr_id).first()
    if not kr:
        raise HTTPException(status_code=404, detail="KeyResult not found")

    if current_value > kr.target_value:
        raise HTTPException(
            status_code=400,
            detail="current_value cannot exceed target_value",
        )

    # безопасное присваивание, чтобы не конфликтовало с Column[int]
    cast(Any, kr).current_value = int(current_value)

    db.commit()
    db.refresh(kr)
    return kr


@router.get("/{obj_id}/by_objective", response_model=list[KeyResult])
def get_key_results_for_objective(
    obj_id: int,
    db: Session = Depends(get_db),
) -> list[KeyResultDB]:
    """Получение всех KeyResults, привязанных к Objective."""
    results: list[KeyResultDB] = (
        db.query(KeyResultDB).filter(KeyResultDB.objective_id == obj_id).all()
    )
    return results


@router.delete("/{kr_id}")
def delete_key_result(
    kr_id: int,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Удаление KeyResult по ID."""
    kr: KeyResultDB | None = db.query(KeyResultDB).filter(KeyResultDB.id == kr_id).first()
    if not kr:
        raise HTTPException(status_code=404, detail="KeyResult not found")

    db.delete(kr)
    db.commit()
    return {"status": "deleted", "key_result_id": kr_id}

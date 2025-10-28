from collections.abc import Sequence
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import KeyResultDB, ObjectiveDB
from ..schemas import Objective, ObjectiveCreate

router = APIRouter()


@router.post("", response_model=Objective)
def create_objective(obj: ObjectiveCreate, db: Session = Depends(get_db)) -> Objective:
    db_obj = ObjectiveDB(**obj.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


@router.get("", response_model=list[Objective])
def get_objectives(db: Session = Depends(get_db)) -> Sequence[ObjectiveDB]:
    """Возвращает список целей (ORM-объекты). FastAPI конвертирует их в Pydantic-модели."""
    return db.query(ObjectiveDB).all()


@router.get("/{obj_id}", response_model=Objective)
def get_objective(obj_id: int, db: Session = Depends(get_db)) -> ObjectiveDB:
    obj = db.query(ObjectiveDB).filter(ObjectiveDB.id == obj_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Objective not found")
    return obj


@router.delete("/{obj_id}")
def delete_objective(obj_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    obj = db.query(ObjectiveDB).filter(ObjectiveDB.id == obj_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Objective not found")

    kr_count = db.query(KeyResultDB).filter(KeyResultDB.objective_id == obj_id).count()
    db.delete(obj)
    db.commit()
    return {
        "status": "deleted",
        "objective_id": obj_id,
        "deleted_key_results": kr_count,
    }


@router.get("/{obj_id}/progress")
def get_objective_progress(obj_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Возвращает прогресс цели в процентах."""
    krs = db.query(KeyResultDB).filter(KeyResultDB.objective_id == obj_id).all()
    if not krs:
        raise HTTPException(status_code=404, detail="No Key Results for this Objective.")
    total = sum(kr.target_value for kr in krs)
    current = sum(kr.current_value for kr in krs)
    percent = round(current / total * 100, 2) if total > 0 else 0
    return {"objective_id": obj_id, "progress": f"{percent}%"}

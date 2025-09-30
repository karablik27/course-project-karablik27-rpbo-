from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base, relationship, sessionmaker

# --- Настройки базы ---
DATABASE_URL = "sqlite:///./okr.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


# --- Модели БД ---
class ObjectiveDB(Base):
    __tablename__ = "objectives"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    isComplete = Column(Boolean, default=False)

    key_results = relationship(
        "KeyResultDB", back_populates="objective", cascade="all, delete"
    )


class KeyResultDB(Base):
    __tablename__ = "key_results"

    id = Column(Integer, primary_key=True, index=True)
    objective_id = Column(Integer, ForeignKey("objectives.id", ondelete="CASCADE"))
    title = Column(String, nullable=False)
    target_value = Column(Integer, nullable=False)
    current_value = Column(Integer, default=0)

    objective = relationship("ObjectiveDB", back_populates="key_results")


Base.metadata.create_all(bind=engine)


# --- Pydantic схемы ---
class Objective(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    isComplete: bool

    class Config:
        orm_mode = True


class KeyResult(BaseModel):
    id: int
    objective_id: int
    title: str
    target_value: int
    current_value: int = 0

    class Config:
        orm_mode = True


# --- FastAPI app ---
app = FastAPI(title="SecDev Course App", version="0.2.0")


# Dependency для сессии
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 1. Создать цель
@app.post("/objectives", response_model=Objective)
def create_objective(obj: Objective, db: Session = Depends(get_db)):
    if db.query(ObjectiveDB).filter(ObjectiveDB.id == obj.id).first():
        raise HTTPException(
            status_code=400, detail="Objective with this id already exists"
        )

    db_obj = ObjectiveDB(**obj.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


# 2. Получить все цели
@app.get("/objectives", response_model=List[Objective])
def get_objectives(db: Session = Depends(get_db)):
    return db.query(ObjectiveDB).all()


# 3. Создать ключевой результат
@app.post("/key_results", response_model=KeyResult)
def create_key_result(kr: KeyResult, db: Session = Depends(get_db)):
    if not db.query(ObjectiveDB).filter(ObjectiveDB.id == kr.objective_id).first():
        raise HTTPException(status_code=404, detail="Objective not found")

    if db.query(KeyResultDB).filter(KeyResultDB.id == kr.id).first():
        raise HTTPException(
            status_code=400, detail="KeyResult with this id already exists"
        )

    # Проверка: текущее значение должно быть строго меньше цели
    if kr.current_value >= kr.target_value:
        raise HTTPException(
            status_code=400,
            detail="current_value must be strictly less than target_value at creation",
        )

    db_kr = KeyResultDB(**kr.dict())
    db.add(db_kr)
    db.commit()
    db.refresh(db_kr)
    return db_kr


# 4. Обновить прогресс ключевого результата
@app.put("/key_results/{kr_id}", response_model=KeyResult)
def update_key_result(kr_id: int, current_value: int, db: Session = Depends(get_db)):
    kr = db.query(KeyResultDB).filter(KeyResultDB.id == kr_id).first()
    if not kr:
        raise HTTPException(status_code=404, detail="KeyResult not found")

    if current_value > kr.target_value:
        raise HTTPException(
            status_code=400, detail="current_value cannot exceed target_value"
        )

    kr.current_value = current_value
    db.commit()
    db.refresh(kr)
    return kr


# 5. Получить key results по objective
@app.get("/objectives/{obj_id}/key_results", response_model=List[KeyResult])
def get_key_results_for_objective(obj_id: int, db: Session = Depends(get_db)):
    return db.query(KeyResultDB).filter(KeyResultDB.objective_id == obj_id).all()


# 6. Получить цель по ID
@app.get("/objectives/{obj_id}", response_model=Objective)
def get_objective(obj_id: int, db: Session = Depends(get_db)):
    obj = db.query(ObjectiveDB).filter(ObjectiveDB.id == obj_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Objective not found")
    return obj


# 7. Удалить цель (и её key results каскадом)
@app.delete("/objectives/{obj_id}")
def delete_objective(obj_id: int, db: Session = Depends(get_db)):
    obj = db.query(ObjectiveDB).filter(ObjectiveDB.id == obj_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Objective not found")

    # считаем связанные key results перед удалением
    kr_count = db.query(KeyResultDB).filter(KeyResultDB.objective_id == obj_id).count()

    db.delete(obj)
    db.commit()
    return {
        "status": "deleted",
        "objective_id": obj_id,
        "deleted_key_results": kr_count,
    }


# 8. Получить прогресс по цели
@app.get("/objectives/{obj_id}/progress")
def get_objective_progress(obj_id: int, db: Session = Depends(get_db)):
    krs = db.query(KeyResultDB).filter(KeyResultDB.objective_id == obj_id).all()
    if not krs:
        raise HTTPException(status_code=404, detail="No Key Results for this Objective")

    total = sum(kr.target_value for kr in krs)
    current = sum(kr.current_value for kr in krs)
    percent = round(current / total * 100, 2) if total > 0 else 0
    return {"objective_id": obj_id, "progress": f"{percent}%"}


# 9. Удалить key result по id
@app.delete("/key_results/{kr_id}")
def delete_key_result(kr_id: int, db: Session = Depends(get_db)):
    kr = db.query(KeyResultDB).filter(KeyResultDB.id == kr_id).first()
    if not kr:
        raise HTTPException(status_code=404, detail="KeyResult not found")

    db.delete(kr)
    db.commit()
    return {"status": "deleted", "key_result_id": kr_id}

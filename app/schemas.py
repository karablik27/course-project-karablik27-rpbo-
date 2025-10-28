from pydantic import BaseModel, ConfigDict


# --- Objective ---
class ObjectiveBase(BaseModel):
    title: str
    description: str | None = None
    isComplete: bool = False


class ObjectiveCreate(ObjectiveBase):
    pass


class Objective(ObjectiveBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# --- KeyResult ---
class KeyResultBase(BaseModel):
    title: str
    target_value: int
    current_value: int = 0
    objective_id: int


class KeyResultCreate(KeyResultBase):
    pass


class KeyResult(KeyResultBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

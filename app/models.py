from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .db import Base


class ObjectiveDB(Base):
    __tablename__ = "objectives"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    isComplete = Column(Boolean, default=False)

    key_results = relationship("KeyResultDB", back_populates="objective", cascade="all, delete")


class KeyResultDB(Base):
    __tablename__ = "key_results"

    id = Column(Integer, primary_key=True, index=True)
    objective_id = Column(Integer, ForeignKey("objectives.id", ondelete="CASCADE"))
    title = Column(String, nullable=False)
    target_value = Column(Integer, nullable=False)
    current_value = Column(Integer, default=0)

    objective = relationship("ObjectiveDB", back_populates="key_results")

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, date
from app.core.database import Base


class ProgressRecord(Base):
    __tablename__ = "progress_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(String(20), default=lambda: date.today().isoformat())
    calories_burned = Column(Float, default=0)
    workouts_completed = Column(Integer, default=0)
    weight = Column(Float, nullable=True)
    sets_completed = Column(Integer, default=0)
    workout_duration = Column(Integer, default=0)  # minutes
    healthy_meals = Column(Integer, default=0)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="progress_records")

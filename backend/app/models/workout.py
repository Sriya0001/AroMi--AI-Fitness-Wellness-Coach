from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    day = Column(Integer, nullable=False)            # 1-7
    day_name = Column(String(20), nullable=True)     # Monday, Tuesday...
    exercises = Column(Text, nullable=False)          # JSON string
    youtube_queries = Column(Text, nullable=True)     # JSON string
    warmup = Column(Text, nullable=True)
    cooldown = Column(Text, nullable=True)
    tips = Column(Text, nullable=True)
    duration_minutes = Column(Integer, default=45)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="workout_plans")


class FavouriteExercise(Base):
    __tablename__ = "favourite_exercises"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    muscle_group = Column(String(50), nullable=True)
    sets = Column(String(20), nullable=True)
    reps = Column(String(20), nullable=True)
    rest_seconds = Column(Integer, default=60)
    instructions = Column(Text, nullable=True)
    video_url = Column(String(255), nullable=True)
    video_id = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="favourite_exercises")

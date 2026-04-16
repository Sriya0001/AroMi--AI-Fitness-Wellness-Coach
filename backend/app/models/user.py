from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    role = Column(String(20), default="user")

    # Profile fields
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    height = Column(Integer, nullable=True)   # cm
    weight = Column(Integer, nullable=True)   # kg
    fitness_level = Column(String(30), nullable=True)   # beginner/intermediate/advanced
    fitness_goal = Column(String(50), nullable=True)
    workout_preference = Column(String(30), nullable=True)  # home/gym
    workout_time = Column(String(20), nullable=True)  # morning/evening/flexible
    diet_preference = Column(String(30), nullable=True)  # veg/non-veg/vegan
    allergies = Column(Text, nullable=True)
    medical_history = Column(Text, nullable=True)
    health_conditions = Column(Text, nullable=True)
    injuries = Column(Text, nullable=True)
    medications = Column(Text, nullable=True)
    calendar_sync = Column(String(10), default="no")
    google_token_data = Column(Text, nullable=True) # Stores JSON of credentials
    assessment_completed = Column(String(10), default="no")

    created_at = Column(DateTime, default=datetime.utcnow)

    workout_plans = relationship("WorkoutPlan", back_populates="user", cascade="all, delete")
    nutrition_plans = relationship("NutritionPlan", back_populates="user", cascade="all, delete")
    progress_records = relationship("ProgressRecord", back_populates="user", cascade="all, delete")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete")
    favourite_exercises = relationship("FavouriteExercise", back_populates="user", cascade="all, delete")
    reviews = relationship("Review", back_populates="user", cascade="all, delete")

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserProfile(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[int] = None
    weight: Optional[int] = None
    fitness_level: Optional[str] = None
    fitness_goal: Optional[str] = None
    workout_preference: Optional[str] = None
    workout_time: Optional[str] = None
    diet_preference: Optional[str] = None
    allergies: Optional[str] = None
    medical_history: Optional[str] = None
    health_conditions: Optional[str] = None
    injuries: Optional[str] = None
    medications: Optional[str] = None
    calendar_sync: Optional[str] = None
    assessment_completed: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    age: Optional[int]
    gender: Optional[str]
    height: Optional[int]
    weight: Optional[int]
    fitness_level: Optional[str]
    fitness_goal: Optional[str]
    workout_preference: Optional[str]
    workout_time: Optional[str]
    diet_preference: Optional[str]
    allergies: Optional[str]
    medical_history: Optional[str]
    health_conditions: Optional[str]
    injuries: Optional[str]
    medications: Optional[str]
    calendar_sync: Optional[str]
    assessment_completed: Optional[str]
    google_token_data: Optional[str]
    spotify_token_data: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

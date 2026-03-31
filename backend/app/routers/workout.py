from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.workout_service import generate_7_day_plan, get_today_workout, get_all_workouts
from app.models.progress import ProgressRecord
from datetime import date

router = APIRouter(prefix="/workout", tags=["Workout"])


@router.post("/generate")
async def generate_workout_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate AI-powered 7-day workout plan."""
    if not current_user.assessment_completed == "yes":
        raise HTTPException(status_code=400, detail="Please complete health assessment first")
    
    user_profile = {
        "age": current_user.age,
        "gender": current_user.gender,
        "weight": current_user.weight,
        "height": current_user.height,
        "fitness_level": current_user.fitness_level,
        "fitness_goal": current_user.fitness_goal,
        "workout_preference": current_user.workout_preference,
        "workout_time": current_user.workout_time,
        "health_conditions": current_user.health_conditions,
        "injuries": current_user.injuries
    }
    
    try:
        plan = await generate_7_day_plan(user_profile, db, current_user.id)
        return {"status": "success", "plan": plan, "message": "Your 7-day workout plan is ready!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plan")
def get_workout_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all 7-day workout plans."""
    plans = get_all_workouts(db, current_user.id)
    return {"plan": plans}


@router.get("/today")
def get_todays_workout(
    day: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get today's workout."""
    workout = get_today_workout(db, current_user.id, day)
    if not workout:
        return {"workout": None, "message": "No workout plan found. Generate a plan first!"}
    return {"workout": workout}


@router.post("/complete")
async def complete_workout(
    calories_burned: float,
    sets_completed: int,
    duration_minutes: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log a completed workout and update progress."""
    today = date.today().isoformat()
    
    # Check if already logged today
    existing = db.query(ProgressRecord).filter(
        ProgressRecord.user_id == current_user.id,
        ProgressRecord.date == today
    ).first()
    
    if existing:
        existing.calories_burned += calories_burned
        existing.workouts_completed += 1
        existing.sets_completed += sets_completed
        existing.workout_duration += duration_minutes
    else:
        record = ProgressRecord(
            user_id=current_user.id,
            date=today,
            calories_burned=calories_burned,
            workouts_completed=1,
            sets_completed=sets_completed,
            workout_duration=duration_minutes
        )
        db.add(record)
    
    db.commit()
    
    messages = [
        "Shabash! You crushed it today! 💪",
        "Wah! Amazing work! Keep going! 🔥",
        "Fantastic effort! AROMI is proud of you! 🌟",
        "You're unstoppable! Great workout! 🏆"
    ]
    import random
    return {
        "status": "success",
        "message": random.choice(messages),
        "calories_burned": calories_burned,
        "sets_completed": sets_completed
    }

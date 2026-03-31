import json
from sqlalchemy.orm import Session
from app.models.workout import WorkoutPlan
from app.services.ai_service import generate_plan_with_groq
from app.services.youtube_service import search_youtube, enrich_exercise
from app.ai.prompts import get_workout_prompt

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


async def generate_7_day_plan(user_profile: dict, db: Session, user_id: int) -> list:
    """Generate a 7-day workout plan using Groq AI + YouTube videos."""
    import asyncio
    
    prompt = get_workout_prompt(user_profile)
    plan_data = await generate_plan_with_groq(prompt)
    
    days_data = plan_data.get("plan", [])
    if not days_data:
        raise Exception("AI returned empty plan data")

    # 1. Collect all exercises across all days for parallel enrichment
    all_exercises = []
    for day_data in days_data:
        exercises = day_data.get("exercises", [])
        all_exercises.extend(exercises)
    
    # 2. Parallelize YouTube enrichment (massively faster)
    await asyncio.gather(*[enrich_exercise(ex) for ex in all_exercises])
    
    # 3. Start Transaction: Delete old and save new
    try:
        # Delete existing plans for user
        db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id).delete()
        
        saved_plans = []
        for day_data in days_data:
            exercises = day_data.get("exercises", [])
            
            # Save to DB
            workout = WorkoutPlan(
                user_id=user_id,
                day=day_data.get("day", 1),
                day_name=day_data.get("day_name", DAYS[day_data.get("day", 1) - 1]),
                exercises=json.dumps(exercises),
                warmup=day_data.get("warmup", ""),
                cooldown=day_data.get("cooldown", ""),
                tips=json.dumps(day_data.get("tips", "")),
                duration_minutes=day_data.get("duration_minutes", 45),
                youtube_queries=json.dumps([ex.get("youtube_query", "") for ex in exercises])
            )
            db.add(workout)
            # No individual commits here
            
            plan_dict = {
                "day": workout.day,
                "day_name": workout.day_name,
                "exercises": exercises,
                "warmup": workout.warmup,
                "cooldown": workout.cooldown,
                "tips": day_data.get("tips", ""),
                "duration_minutes": workout.duration_minutes,
                "focus": day_data.get("focus", ""),
                "calories_estimate": day_data.get("calories_estimate", 250)
            }
            saved_plans.append(plan_dict)
        
        db.commit() # Atomic commit for the entire 7-day plan
        return saved_plans
        
    except Exception as e:
        db.rollback()
        print(f"Database error in workout generation: {e}")
        raise Exception(f"Failed to save workout plan: {str(e)}")


def get_today_workout(db: Session, user_id: int, day: int = None) -> dict:
    """Get today's workout plan."""
    from datetime import date
    if day is None:
        day = date.today().weekday() + 1  # 1=Monday ... 7=Sunday
    
    workout = db.query(WorkoutPlan).filter(
        WorkoutPlan.user_id == user_id,
        WorkoutPlan.day == day
    ).first()
    
    if not workout:
        return None
    
    return {
        "id": workout.id,
        "day": workout.day,
        "day_name": workout.day_name,
        "exercises": json.loads(workout.exercises) if workout.exercises else [],
        "warmup": workout.warmup,
        "cooldown": workout.cooldown,
        "tips": json.loads(workout.tips) if workout.tips else "",
        "duration_minutes": workout.duration_minutes
    }


def get_all_workouts(db: Session, user_id: int) -> list:
    """Get all 7-day workout plans."""
    workouts = db.query(WorkoutPlan).filter(
        WorkoutPlan.user_id == user_id
    ).order_by(WorkoutPlan.day).all()
    
    result = []
    for w in workouts:
        result.append({
            "id": w.id,
            "day": w.day,
            "day_name": w.day_name,
            "exercises": json.loads(w.exercises) if w.exercises else [],
            "warmup": w.warmup,
            "cooldown": w.cooldown,
            "tips": json.loads(w.tips) if w.tips else "",
            "duration_minutes": w.duration_minutes
        })
    return result

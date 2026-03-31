
import asyncio
import os
import sys
import json
from app.models import User, WorkoutPlan, NutritionPlan
from app.core.database import SessionLocal
from app.services.workout_service import generate_7_day_plan
from app.services.nutrition_service import generate_meal_plan

async def debug_gen():
    db = SessionLocal()
    user_id = 7 # user 'xyz'
    user_profile = {
        "age": 25,
        "gender": "male",
        "weight": 70,
        "height": 170,
        "fitness_level": "beginner",
        "fitness_goal": "muscle gain",
        "workout_preference": "home",
        "workout_time": "morning",
        "diet_preference": "non-vegetarian",
        "allergies": "none",
        "health_conditions": "none",
        "injuries": "none"
    }
    
    try:
        print("--- Testing Workout Plan Generation ---")
        try:
            wp = await generate_7_day_plan(user_profile, db, user_id)
            print(f"SUCCESS: Workout Plan generated: {len(wp)} days")
        except Exception as e:
            print(f"FAILED Workout Gen: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            
        print("\n--- Testing Nutrition Plan Generation ---")
        try:
            np = await generate_meal_plan(user_profile, db, user_id)
            print(f"SUCCESS: Nutrition Plan generated: {len(np)} days")
        except Exception as e:
            print(f"FAILED Nutrition Gen: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            
    finally:
        db.close()

if __name__ == "__main__":
    # Add project root to sys.path
    sys.path.append(os.getcwd())
    asyncio.run(debug_gen())

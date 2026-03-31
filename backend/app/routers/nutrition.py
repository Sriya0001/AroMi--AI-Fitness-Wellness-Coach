from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.nutrition_service import generate_meal_plan, get_all_nutrition, get_shopping_list

router = APIRouter(prefix="/nutrition", tags=["Nutrition"])


@router.post("/generate")
async def generate_nutrition_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate AI-powered 7-day nutrition plan."""
    if not current_user.assessment_completed == "yes":
        raise HTTPException(status_code=400, detail="Please complete health assessment first")
    
    user_profile = {
        "age": current_user.age,
        "gender": current_user.gender,
        "weight": current_user.weight,
        "height": current_user.height,
        "fitness_goal": current_user.fitness_goal,
        "diet_preference": current_user.diet_preference,
        "allergies": current_user.allergies,
        "health_conditions": current_user.health_conditions
    }
    
    try:
        plan = await generate_meal_plan(user_profile, db, current_user.id)
        return {"status": "success", "plan": plan, "message": "Your 7-day nutrition plan is ready!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plan")
def get_nutrition_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all nutrition plans."""
    plans = get_all_nutrition(db, current_user.id)
    return {"plan": plans}


@router.get("/shopping-list")
def get_shopping_list_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get consolidated weekly shopping list."""
    items = get_shopping_list(db, current_user.id)
    first_item_query = items[0]["name"] if items else "groceries"
    bigbasket_url = f"https://www.bigbasket.com/ps/?q={first_item_query}"
    return {
        "items": items,
        "bigbasket_url": bigbasket_url,
        "total_items": len(items)
    }

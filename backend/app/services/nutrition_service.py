import json
from sqlalchemy.orm import Session
from app.models.nutrition import NutritionPlan
from app.services.ai_service import generate_plan_with_groq
from app.ai.prompts import get_nutrition_prompt

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


async def generate_meal_plan(user_profile: dict, db: Session, user_id: int) -> list:
    """Generate a 7-day nutrition plan using Groq AI."""
    
    prompt = get_nutrition_prompt(user_profile)
    plan_data = await generate_plan_with_groq(prompt)
    
    days_data = plan_data.get("plan", [])
    if not days_data:
        raise Exception("AI returned empty plan data")
        
    try:
        # Delete existing plans for user
        db.query(NutritionPlan).filter(NutritionPlan.user_id == user_id).delete()
        
        saved_plans = []
        for day_data in days_data:
            grocery = day_data.get("grocery_list", [])
            
            nutrition = NutritionPlan(
                user_id=user_id,
                day=day_data.get("day", 1),
                day_name=day_data.get("day_name", DAYS[day_data.get("day", 1) - 1]),
                meals=json.dumps(day_data.get("meals", {})),
                calories=day_data.get("calories", 2000),
                protein=day_data.get("protein", 80),
                carbs=day_data.get("carbs", 200),
                fat=day_data.get("fat", 50),
                grocery_list=json.dumps(grocery)
            )
            db.add(nutrition)
            
            plan_dict = {
                "day": nutrition.day,
                "day_name": nutrition.day_name,
                "meals": day_data.get("meals", {}),
                "calories": nutrition.calories,
                "protein": nutrition.protein,
                "carbs": nutrition.carbs,
                "fat": nutrition.fat,
                "grocery_list": grocery,
                "hydration": day_data.get("hydration", "Drink 8 glasses of water")
            }
            saved_plans.append(plan_dict)
        
        db.commit() # Atomic commit for the entire 7-day meal plan
        return saved_plans
        
    except Exception as e:
        db.rollback()
        print(f"Database error in nutrition generation: {e}")
        raise Exception(f"Failed to save nutrition plan: {str(e)}")


def get_all_nutrition(db: Session, user_id: int) -> list:
    """Get all saved nutrition plans."""
    plans = db.query(NutritionPlan).filter(
        NutritionPlan.user_id == user_id
    ).order_by(NutritionPlan.day).all()
    
    result = []
    for n in plans:
        result.append({
            "id": n.id,
            "day": n.day,
            "day_name": n.day_name,
            "meals": json.loads(n.meals) if n.meals else {},
            "calories": n.calories,
            "protein": n.protein,
            "carbs": n.carbs,
            "fat": n.fat,
            "grocery_list": json.loads(n.grocery_list) if n.grocery_list else []
        })
    return result


def get_shopping_list(db: Session, user_id: int) -> list:
    """Get consolidated shopping list from nutrition plans."""
    plans = db.query(NutritionPlan).filter(
        NutritionPlan.user_id == user_id
    ).all()
    
    item_map = {}
    for plan in plans:
        if plan.grocery_list:
            items = json.loads(plan.grocery_list)
            for item in items:
                if isinstance(item, str):
                    name = item
                    quantity = "1 unit"
                else:
                    name = item.get("name", "Unknown")
                    quantity = item.get("quantity", "1 unit")
                
                # Consolidate if same name (crude consolidation)
                if name in item_map:
                    # If quantities are numeric-ish, we could sum them, 
                    # but for now we'll just keep the first one or a list
                    pass 
                else:
                    item_map[name] = quantity
    
    result = []
    for name, qty in item_map.items():
        result.append({"name": name, "quantity": qty, "checked": True})
        
    return sorted(result, key=lambda x: x["name"])

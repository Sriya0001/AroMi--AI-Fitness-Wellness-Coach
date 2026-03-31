from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.chat import ChatSession
from app.schemas.fitness import ChatRequest, ChatResponse
from app.services.ai_service import chat_with_aromi
from app.schemas.user import UserProfile

router = APIRouter(prefix="/ai", tags=["AI Coach"])


@router.post("/chat")
async def chat_with_aromi_endpoint(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Chat with AROMI AI coach."""
    user_profile = {
        "age": current_user.age,
        "gender": current_user.gender,
        "weight": current_user.weight,
        "height": current_user.height,
        "fitness_level": current_user.fitness_level,
        "fitness_goal": current_user.fitness_goal,
        "diet_preference": current_user.diet_preference,
        "health_conditions": current_user.health_conditions,
        "injuries": current_user.injuries,
        "username": current_user.username
    }
    
    # Get recent chat history
    recent_chats = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).order_by(ChatSession.timestamp.desc()).limit(6).all()
    
    chat_history = [
        {"message": c.message, "response": c.response}
        for c in reversed(recent_chats)
    ]
    
    response_text, plan_modified = await chat_with_aromi(
        user_message=request.message,
        user_profile=user_profile,
        chat_history=chat_history,
        db=db,
        user_id=current_user.id
    )
    
    return {
        "response": response_text,
        "plan_modified": plan_modified,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/chat/history")
def get_chat_history(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AROMI chat history."""
    chats = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).order_by(ChatSession.timestamp.asc()).limit(limit).all()
    
    return {
        "history": [
            {
                "id": c.id,
                "message": c.message,
                "response": c.response,
                "timestamp": c.timestamp.isoformat()
            }
            for c in chats
        ]
    }


@router.post("/adaptive-regen")
async def trigger_adaptive_regen(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger the Weekly Performance Analyzer and regenerate the plan."""
    from app.services.adaptive_engine import adaptive_engine
    
    try:
        new_plan = await adaptive_engine.analyze_and_regenerate_plan(db, current_user)
        return {
            "status": "success",
            "message": "AROMI has analyzed your last 7 days and updated your plan for next week! 🚀",
            "plan": new_plan
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-plan")
async def generate_full_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate both workout and nutrition plan after assessment."""
    from app.services.workout_service import generate_7_day_plan
    from app.services.nutrition_service import generate_meal_plan

    user_profile = {
        "age": current_user.age,
        "gender": current_user.gender,
        "weight": current_user.weight,
        "height": current_user.height,
        "fitness_level": current_user.fitness_level,
        "fitness_goal": current_user.fitness_goal,
        "workout_preference": current_user.workout_preference,
        "workout_time": current_user.workout_time,
        "diet_preference": current_user.diet_preference,
        "allergies": current_user.allergies,
        "health_conditions": current_user.health_conditions,
        "injuries": current_user.injuries
    }

    try:
        workout_plan = await generate_7_day_plan(user_profile, db, current_user.id)
        nutrition_plan = await generate_meal_plan(user_profile, db, current_user.id)

        return {
            "status": "success",
            "message": "Your personalized plans are ready!",
            "workout_plan": workout_plan,
            "nutrition_plan": nutrition_plan
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

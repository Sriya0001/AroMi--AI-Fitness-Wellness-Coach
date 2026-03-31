from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.progress import ProgressRecord
from app.schemas.fitness import ProgressCreate, ProgressResponse

router = APIRouter(prefix="/progress", tags=["Progress"])


@router.post("/log", response_model=ProgressResponse)
def log_progress(
    progress: ProgressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log daily progress."""
    today = progress.date or date.today().isoformat()
    
    existing = db.query(ProgressRecord).filter(
        ProgressRecord.user_id == current_user.id,
        ProgressRecord.date == today
    ).first()
    
    if existing:
        for field, value in progress.model_dump(exclude_unset=True, exclude={"date"}).items():
            if value is not None:
                setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        return existing
    
    record = ProgressRecord(
        user_id=current_user.id,
        **progress.model_dump(exclude_unset=True)
    )
    if not record.date:
        record.date = today
    
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/history", response_model=List[ProgressResponse])
def get_progress_history(
    limit: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get last N days of progress."""
    records = db.query(ProgressRecord).filter(
        ProgressRecord.user_id == current_user.id
    ).order_by(ProgressRecord.date.desc()).limit(limit).all()
    return records


@router.get("/stats")
def get_progress_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get aggregated stats for dashboard."""
    records = db.query(ProgressRecord).filter(
        ProgressRecord.user_id == current_user.id
    ).all()
    
    total_calories = sum(r.calories_burned for r in records)
    total_workouts = sum(r.workouts_completed for r in records)
    total_meals = sum(r.healthy_meals for r in records)
    streak = len(records)  # simplified streak count
    
    # Charity impact: ₹2 per workout, ₹1 per healthy meal
    charity_amount = (total_workouts * 2) + (total_meals * 1)
    
    return {
        "total_calories_burned": total_calories,
        "total_workouts": total_workouts,
        "total_healthy_meals": total_meals,
        "streak_days": streak,
        "charity_amount_inr": charity_amount,
        "people_impacted": total_workouts // 3,
        "records": len(records)
    }

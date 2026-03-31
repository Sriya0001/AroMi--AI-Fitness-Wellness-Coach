from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class NutritionPlan(Base):
    __tablename__ = "nutrition_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    day = Column(Integer, nullable=False)        # 1-7
    day_name = Column(String(20), nullable=True)
    meals = Column(Text, nullable=False)          # JSON: breakfast/lunch/dinner/snacks
    calories = Column(Integer, nullable=True)
    protein = Column(Float, nullable=True)        # grams
    carbs = Column(Float, nullable=True)
    fat = Column(Float, nullable=True)
    grocery_list = Column(Text, nullable=True)    # JSON list
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="nutrition_plans")

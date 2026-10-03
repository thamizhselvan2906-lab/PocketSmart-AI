import datetime
import json
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    planner_type = Column(String(50), nullable=False)  # 'home', 'party', 'jewelry'
    currency = Column(String(10), default="$")
    total_budget = Column(Float, nullable=False, default=0.0)
    estimated_spending = Column(Float, nullable=False, default=0.0)
    remaining_budget = Column(Float, nullable=False, default=0.0)
    user_inputs = Column(Text, nullable=True)  # JSON string of raw parameters
    ai_summary = Column(Text, nullable=True)
    image_path = Column(String(500), nullable=True)  # For outfit or room image if uploaded
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    recommendations = relationship("RecommendationItem", back_populates="plan", cascade="all, delete-orphan", order_by="RecommendationItem.id")
    allocations = relationship("BudgetAllocation", back_populates="plan", cascade="all, delete-orphan")

    def to_dict(self):
        inputs = {}
        if self.user_inputs:
            try:
                inputs = json.loads(self.user_inputs)
            except Exception:
                inputs = {"raw": self.user_inputs}

        return {
            "id": self.id,
            "title": self.title,
            "planner_type": self.planner_type,
            "currency": self.currency,
            "total_budget": round(self.total_budget, 2),
            "estimated_spending": round(self.estimated_spending, 2),
            "remaining_budget": round(self.remaining_budget, 2),
            "user_inputs": inputs,
            "ai_summary": self.ai_summary,
            "image_path": self.image_path,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "recommendations": [rec.to_dict() for rec in self.recommendations],
            "allocations": [alloc.to_dict() for alloc in self.allocations]
        }


class RecommendationItem(Base):
    __tablename__ = "recommendation_items"

    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    estimated_price = Column(Float, nullable=False, default=0.0)
    quantity = Column(Integer, default=1)
    why_recommended = Column(Text, nullable=False)
    platform_name = Column(String(100), nullable=False)  # e.g., 'Amazon', 'IKEA', 'Etsy', 'Target', 'Tanishq'
    shopping_link = Column(String(500), nullable=False)
    is_selected = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    plan = relationship("Plan", back_populates="recommendations")

    def to_dict(self):
        return {
            "id": self.id,
            "plan_id": self.plan_id,
            "name": self.name,
            "category": self.category,
            "estimated_price": round(self.estimated_price, 2),
            "quantity": self.quantity,
            "total_price": round(self.estimated_price * (self.quantity or 1), 2),
            "why_recommended": self.why_recommended,
            "platform_name": self.platform_name,
            "shopping_link": self.shopping_link,
            "is_selected": self.is_selected,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }


class BudgetAllocation(Base):
    __tablename__ = "budget_allocations"

    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    category_name = Column(String(100), nullable=False)
    allocated_amount = Column(Float, nullable=False, default=0.0)
    spent_amount = Column(Float, nullable=False, default=0.0)
    percentage = Column(Float, default=0.0)

    plan = relationship("Plan", back_populates="allocations")

    def to_dict(self):
        return {
            "id": self.id,
            "plan_id": self.plan_id,
            "category_name": self.category_name,
            "allocated_amount": round(self.allocated_amount, 2),
            "spent_amount": round(self.spent_amount, 2),
            "percentage": round(self.percentage, 1)
        }

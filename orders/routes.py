from fastapi import APIRouter, status, Depends, HTTPException
from typing import List, Optional
from core.database import get_db
from core.security import get_current_user
from orders.services import create_meal, get_meals, get_meal, update_meal, delete_meal, create_user_order, get_user_orders
from orders.schemas import OrderCreate, OrderBase, Order, MealBase, MealCreate, MealUpdate, Meal
from sqlalchemy.orm import Session
from services.recommendation_service import MealRecommender


order_router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
    responses={404: {"description": "Not found"}, 401: {"description": "Unauthorized"}}
)

meal_router = APIRouter(
    prefix="/meals",
    tags=["Meals"],
    responses={404: {"description": "Not found"}, 401: {"description": "Unauthorized"}}
)


@meal_router.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}

@meal_router.get("/", response_model=MealBase)
async def meal_create(data: MealCreate, db: Session = Depends(get_db)):
    return create_meal(db, data)

@meal_router.get("/", response_model=List[MealBase])
def meals_get(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_meals(db, skip=skip, limit=limit)

@meal_router.get("/{meal_id}", response_model=MealBase)
def meal_get(meal_id: int, db: Session = Depends(get_db)):
    return get_meal(db, meal_id)

@meal_router.put("/{meal_id}", response_model=MealBase)
def meal_update(meal_id: int, data: MealUpdate, db: Session = Depends(get_db)):
    return update_meal(db, meal_id, data)

@meal_router.delete("/{meal_id}", response_model=MealBase)
def meal_delete(meal_id: int, db: Session = Depends(get_db)):
    return delete_meal(db, meal_id)

@order_router.post("/", response_model=OrderBase)
def create_order(order: OrderCreate, current_user: OrderBase = Depends(get_current_user), db: Session = Depends(get_db)):
    return create_user_order(db, order, current_user.id)

@order_router.get("/", response_model=List[OrderBase])
def read_user_orders(skip: int = 0, limit: int = 100, current_user: OrderBase = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_user_orders(db, user_id=current_user.id, skip=skip, limit=limit)

@meal_router.get("/recommendations/", response_model=List[MealBase])
async def get_recommendations(current_user: OrderBase = Depends(get_current_user), db: Session = Depends(get_db)):
    recommender = MealRecommender()
    recommendations = recommender.get_recommendations(current_user)
    return recommendations


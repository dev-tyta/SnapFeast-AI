from sqlalchemy.orm import Session
from typing import List
from orders.schemas import MealCreate, MealUpdate, OrderCreate
from orders.models import Meal, Order

def get_meals(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Meal).offset(skip).limit(limit).all()

def create_meal(db: Session, meal: MealCreate):
    db_meal = Meal(**meal.dict())
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    return db_meal

def get_meal(db: Session, meal_id: int):
    return db.query(Meal).filter(Meal.id == meal_id).first()

def update_meal(db: Session, meal_id: int, meal: MealUpdate):
    db_meal = db.query(Meal).filter(Meal.id == meal_id).first()
    if db_meal:
        update_data = meal.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_meal, key, value)
        db.commit()
        db.refresh(db_meal)
    return db_meal

def delete_meal(db: Session, meal_id: int):
    db_meal = db.query(Meal).filter(Meal.id == meal_id).first()
    if db_meal:
        db.delete(db_meal)
        db.commit()
    return db_meal

def create_user_order(db: Session, order: OrderCreate, user_id: int):
    db_order = Order(**order.dict(), user_id=user_id)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def get_user_orders(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(Order).filter(Order.user_id == user_id).offset(skip).limit(limit).all()

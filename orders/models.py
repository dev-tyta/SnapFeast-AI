# models.py
from sqlalchemy import Column, ForeignKey, Integer, String, Float, JSON, ARRAY
from sqlalchemy.orm import relationship
from core.database import Base

class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Float)

    orders = relationship("Order", back_populates="meal")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    meal_id = Column(Integer, ForeignKey("meals.id"))
    quantity = Column(Integer)

    user = relationship("User", back_populates="orders")
    meal = relationship("Meal", back_populates="orders")

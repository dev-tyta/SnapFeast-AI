from pydantic import BaseModel


class MealBase(BaseModel):
    name: str
    description: str
    price: float

class MealCreate(MealBase):
    pass

class MealUpdate(MealBase):
    pass

class Meal(MealBase):
    id: int

    class Config:
        orm_mode = True

class OrderBase(BaseModel):
    quantity: int

class OrderCreate(OrderBase):
    meal_id: int

class Order(OrderBase):
    id: int
    user_id = int
    meal_id = int

    class Config:
        orm_mode = True

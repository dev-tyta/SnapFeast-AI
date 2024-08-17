from pydantic import BaseModel, EmailStr
from typing import Optional, List

class UserBase(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    age: Optional[int] = None
    preferences: Optional[dict] = None
    is_active: Optional[bool] = True


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class UserEmbeddingsBase(BaseModel):
    embeddings: List[float]

class UserEmbeddingsCreate(UserEmbeddingsBase):
    pass


class UserEmbeddings(UserEmbeddingsBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


from users.models import User, UserEmbeddings
from fastapi import HTTPException
from core.security import get_password_hash
from datetime import datetime
from sqlalchemy.orm import Session
from users.schemas import UserCreate, UserUpdate, UserEmbeddingsBase

async def create_user_account(data: UserCreate, db: Session):
    user = db.query(User).filter(User.email == data.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        email=data.email,
        username=data.username,
        first_name=data.first_name,
        last_name=data.last_name,
        age=data.age,
        preferences=data.preferences,
        hashed_password=get_password_hash(data.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

async def create_user_embeddings(user_id: int, embeddings: UserEmbeddingsBase, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_embeddings = UserEmbeddings(user_id=user_id, embeddings=embeddings.embeddings)
    db.add(db_embeddings)
    db.commit()
    db.refresh(db_embeddings)
    return db_embeddings

def get_user_by_id(user_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_user_by_email(email: str, db: Session):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def update_user(db: Session, user_id: int, user: UserUpdate):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user.dict(exclude_unset=True)
    if 'password' in update_data:
        update_data['hashed_password'] = get_password_hash(update_data['password'])
        del update_data['password']
    
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(user_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return user

async def update_user_embeddings(user_id: int, embeddings: UserEmbeddingsBase, db: Session):
    db_embeddings = db.query(UserEmbeddings).filter(UserEmbeddings.user_id == user_id).first()
    if not db_embeddings:
        raise HTTPException(status_code=404, detail="User embeddings not found")
    
    db_embeddings.embeddings = embeddings.embeddings
    db.commit()
    db.refresh(db_embeddings)
    return db_embeddings
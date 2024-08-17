from users.models import User, UserEmbeddings
from fastapi.exceptions import HTTPException
from core.security import get_password_hash
from datetime import datetime
from sqlalchemy.orm import Session
from users.schemas import UserCreate, UserUpdate, UserEmbeddingsModel


async def create_user_account(data:UserCreate, db:Session):
    user = db.query(User).filter(User.email == data.email).first()
    if user:
        raise HTTPException(status_code=422, detail="Email already registered")
    
    new_user = User(
        email=data.email,
        first_name=data.first_name,
        last_name=data.last_name,
        age=data.age,
        preferences=data.preferences,
        password = get_password_hash(data.password),
        registered_at=datetime.now(),
        updated_at=datetime.now(),   
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

async def create_user_embeddings(user_id:int, embeddings:UserEmbeddingsModel, db:Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        embeddings = UserEmbeddings(user_id=user_id, embeddings=embeddings.embeddings)
        db.add(embeddings)
        db.commit()
        db.refresh(embeddings)
        return embeddings
        
def get_user_by_id(user_id, db:Session):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(email, db:Session):
    return db.query(User).filter(User.email == email).first()


def get_users(db:Session, skip=0, limit=100):
    return db.query(User).offset(skip).limit(limit).all()


def update_user(db:Session, user_id:int, user:UserUpdate):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        update_data = user.dict(exclude_unset=True)
        if 'password' in update_data:
            update_data['password'] = get_password_hash(update_data['password'])
            del update_data['password']
        
        for key, value in update_data.items():
            setattr(user, key, value)
        db.commit()
        db.refresh(user)
    return user


def delete_user(user_id, db:Session):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return user
    return None


async def update_user_embeddings(user_id:int, embeddings:UserEmbeddingsModel, db:Session):
    embeddings = db.query(UserEmbeddings).filter(UserEmbeddings.user_id == user_id).first()
    if embeddings:
        embeddings.embeddings = embeddings.embeddings
        db.commit()
        db.refresh(embeddings)
        return embeddings
    return None



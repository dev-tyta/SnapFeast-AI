from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from datetime import timedelta, datetime
from jose import JWTError, jwt
from core.config import get_settings
from users.services import get_user_by_email
from sqlalchemy.orm import Session
from core.database import get_db


settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2scheme = OAuth2PasswordBearer(tokenUrl="auth/token/")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

async def create_access_token(data:dict, expiry:timedelta):
    payload = data.copy()
    expire = datetime.utcnow() + expiry
    payload.update({"exp": expire})
    token = jwt.encode(payload,
                       settings.JWT_SECRET_KEY,
                       algorithm=settings.JWT_ALGORITHM)
    
    return token

async def create_refresh_token(data:dict):
    payload = data.copy()
    token = jwt.encode(payload,
                       settings.JWT_SECRET_KEY,
                       algorithm=settings.JWT_ALGORITHM)
    return token

def get_token_payload(token:str):
    try:
        payload = jwt.decode(token,
                             settings.JWT_SECRET_KEY,
                             algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
    
async def get_current_user(token:str = Depends(oauth2scheme), db:Session = Depends(get_db)):
    try:
        payload = get_token_payload(token)
        email = payload.get("sub")
        if email is None:
            return HTTPException(status_code=401,
                                 detail="Invalid Token",
                                 headers={"WWW-Authenticate": "Bearer"})
    except JWTError:
        return HTTPException(status_code=401,
                             detail="Invalid Token",
                             headers={"WWW-Authenticate": "Bearer"}
                             )
    
    user = get_user_by_email(email, db=db)
    if user is None:
        return HTTPException(status_code=401,
                             detail="Invalid Token",
                             headers={"WWW-Authenticate": "Bearer"}
                             )
    return user



    
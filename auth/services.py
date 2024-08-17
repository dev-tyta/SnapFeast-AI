from fastapi import HTTPException, Depends
from users.models import User
from core.security import verify_password
from core.security import create_access_token, create_refresh_token, get_token_payload
from core.config import get_settings
from auth.responses import TokenResponse
from datetime import timedelta
from sqlalchemy.orm import Session
from core.database import get_db


settings = get_settings()

async def get_token(data, db:Session):
    user = db.query(User).filter(User.email == data.username).first()
    if not user:
        raise HTTPException(status_code=401,
                             detail="Invalid Login Credentials",
                             headers={"WWW-Authenticate": "Bearer"})
    
    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=401,
                             detail="Invalid Login Credentials",
                             headers={"WWW-Authenticate": "Bearer"})
    
    _verify_user_access(user=user)

    return _get_user_token(user=user)


async def get_refresh_token(token: str, db):
    paylod = get_token_payload(token)
    user_id = paylod.get("id")
    if not user_id:
        raise HTTPException(status_code=400,
                            detail="Invalid Token",
                            headers={"WWW-Authenticate": "Bearer"}
                            )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=400,
                            detail="Invalid Token",
                            headers={"WWW-Authenticate": "Bearer"}
                            )

def _verify_user_access(user: User):
    if not user.is_active:
        raise HTTPException(status_code=400,
                            detail="User is inactive",
                            headers={"WWW-Authenticate": "Bearer"}
                            )
    return True

async def _get_user_token(user:User, refresh_token: bool = False):
    payload = {"id": user.id, "sub": user.email}

    access_token_expiry = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = await create_access_token(data=payload, expiry=access_token_expiry)
    if not refresh_token:
        refresh_token = await create_refresh_token(data=payload)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in= access_token_expiry.seconds
        )


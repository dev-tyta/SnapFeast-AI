from fastapi import APIRouter, status, Depends, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from core.database import get_db
from auth.services import get_refresh_token, get_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}},
)

@router.get("/token", status_code=status.HTTP_200_OK)
async def authenticate_user(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return await get_token(data, db)


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh_token(refresh_token: str , db: Session = Depends(get_db)):
    return await get_refresh_token(token=refresh_token, db=db)

from fastapi import APIRouter, status, Depends, Request, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user, create_access_token
from users.schemas import UserCreate, UserBase, UserEmbeddingsBase, User, UserUpdate
from users.services import create_user_account, create_user_embeddings, update_user, update_user_embeddings, get_user_by_id, get_user_by_email
from services.facial_processing import FacialProcessing
from services.face_match import FaceMatch
import os
from datetime import timedelta
from dotenv import load_dotenv
from auth.services import get_token

load_dotenv()

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserBase)
async def create_user(data: UserCreate, db: Session = Depends(get_db)):
    new_user = await create_user_account(data, db)
    return new_user

@router.get("/me", response_model=UserBase)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserBase)
async def update_user_me(user: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    updated_user = update_user(db, current_user.id, user)
    return updated_user

@router.post("/me/face", status_code=status.HTTP_200_OK)
async def create_face_embeddings(file: UploadFile = File(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    face_processor = FacialProcessing()

    image_path = f"faces/{user.id}.jpg"
    with open(image_path, "wb") as buffer:
        buffer.write(await file.read())

    embeddings = face_processor.extract_embeddings_vgg(image_path)
    if embeddings:
        user_embeddings = UserEmbeddingsBase(embeddings=embeddings)
        await create_user_embeddings(user.id, user_embeddings, db)
        return {"message": "Face embeddings created successfully"}

    raise HTTPException(status_code=400, detail="Failed to process face")

@router.get("/me/face", status_code=status.HTTP_200_OK)
async def get_face_embeddings(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    face = db.query(UserEmbeddingsBase).filter(UserEmbeddingsBase.user_id == user.id).first()
    if not face:
        raise HTTPException(status_code=404, detail="Face embeddings not found")
    return JSONResponse(content={"embeddings": face.embeddings}, status_code=status.HTTP_200_OK)

@router.put("/me/face", status_code=status.HTTP_200_OK)
async def update_face_embeddings(file: UploadFile = File(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    face_processor = FacialProcessing()

    image_path = f"faces/{user.id}.jpg"
    with open(image_path, "wb") as buffer:
        buffer.write(await file.read())

    embeddings = face_processor.extract_embeddings_vgg(image_path)
    if embeddings:
        user_embeddings = UserEmbeddingsBase(embeddings=embeddings)
        await update_user_embeddings(user.id, user_embeddings, db)
        return {"message": "Face embeddings updated successfully"}

    raise HTTPException(status_code=400, detail="Failed to process face")

@router.post("/login/face")
async def face_login(file: UploadFile = File(...), db: Session = Depends(get_db)):
    face_processor = FacialProcessing()
    face_matcher = FaceMatch(db)

    image_path = f"temp_{file.filename}"
    with open(image_path, "wb") as buffer:
        buffer.write(await file.read())

    embeddings = await face_processor.extract_embeddings(image_path)
    if not embeddings:
        raise HTTPException(status_code=400, detail="Failed to process face")
    
    match_result = face_matcher.new_face_matching(embeddings)
    if match_result['status'] == 'Success':
        user = get_user_by_id(match_result['user_id'], db)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")))
        payload = {"id": user.id, "sub": user.email}
        token = get_token(payload, db)
        return JSONResponse(content=token.dict(), status_code=status.HTTP_200_OK)
    
    raise HTTPException(status_code=401, detail="Face not recognized")
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserOut
from app.crud import user as crud_user
from app.controller.deps import get_db

router = APIRouter()

@router.post("/", response_model=UserOut)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return await crud_user.create_user(db, user)

@router.get("/", response_model=list[UserOut])
async def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return await crud_user.get_users(db, skip, limit)

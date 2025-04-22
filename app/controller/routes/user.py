from app.utils.jwt import create_access_token
from app.utils.security import verify_password
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserOut, LoginUser
from app.crud import user as crud_user
from app.controller.deps import get_db
from fastapi import HTTPException, status

router = APIRouter()

@router.post("/login")
def login(form_data: LoginUser, db: Session = Depends(get_db)):
    user = crud_user.get_user_by_email(db, email=form_data.email)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = crud_user.get_user_by_email(db, email=user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = crud_user.create_user(db=db, user=user)
    return new_user

@router.get("/")
async def get_anything():
    return {"message": "Test Successfully"}

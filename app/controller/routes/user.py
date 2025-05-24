from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.enum.user_role import UserRole
from app.services.user_service import UserService
from app.utils.jwt import create_access_token
from app.utils.security import verify_password
from fastapi import APIRouter, Depends, Query
from app.schemas.user import UserCreate, UserOut, LoginUser, UserResponse, UserWithResources
from app.controller.deps import get_db
from fastapi import HTTPException, status

router = APIRouter()
user_service = UserService()

@router.post("/login")
async def login(form_data: LoginUser, db: AsyncSession = Depends(get_db)):
    user = await user_service.get_user_by_email(db, email=form_data.email)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await user_service.get_user_by_email(db, email=user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = await user_service.create_user(db=db, user_data=user)
    return new_user


@router.post("/users/", response_model=UserResponse)
async def create_user(
        user: UserCreate, db: AsyncSession = Depends(get_db)
):
    # Check if username already exists
    existing_user = await user_service.get_user_by_email(db, user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    return await user_service.create_user(db, user)


@router.get("/users/", response_model=List[UserWithResources])
async def get_users(db: AsyncSession = Depends(get_db)):
    return await user_service.get_users(db)


@router.get("/users/{user_id}", response_model=UserWithResources)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/users/search/", response_model=List[UserWithResources])
async def search_users(
        query: str = Query(..., description="Search query"),
        role: Optional[UserRole] = Query(None, description="Filter by role"),
        is_active: Optional[bool] = Query(None, description="Filter by active status"),
        db: AsyncSession = Depends(get_db)
):
    return await user_service.search_users(db, query, role, is_active)


@router.put("/users/{user_id}/role", response_model=UserResponse)
async def update_user_role(
        user_id: int, role: UserRole, db: AsyncSession = Depends(get_db)
):
    user = await user_service.update_user_role(db, user_id, role)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


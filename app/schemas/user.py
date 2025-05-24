from datetime import datetime
from typing import List

from pydantic import BaseModel

from app.enum.user_role import UserRole


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    password: str
    email: str

class LoginUser(BaseModel):
    email: str
    password: str

class UserOut(UserCreate):
    id: int

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str
    email: str
    full_name: str
    role: UserRole = UserRole.user


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserWithResources(UserResponse):
    resources: List["CloudResourceResponse"] = []
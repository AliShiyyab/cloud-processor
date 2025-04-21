from pydantic import BaseModel

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    password: str
    email: str

class UserOut(UserCreate):
    id: int

    class Config:
        from_attributes = True

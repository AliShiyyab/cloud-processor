from sqlalchemy import Column, Integer, String, Enum, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.enum.user_role import UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    role = Column(Enum(UserRole), default=UserRole.user)
    is_active = Column(Boolean, default=True)
    password = Column(String, nullable=False, index=True)
    resources = relationship("CloudResource", back_populates="owner", cascade="all, delete-orphan")

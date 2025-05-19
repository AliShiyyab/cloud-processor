from datetime import datetime
from sqlalchemy import (
    Boolean, Column, DateTime, Enum, Integer, String
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.enum.resource_type import ResourceType
from app.enum.status_enum import StatusEnum

class CloudResource(Base):
    __tablename__ = "cloud_resources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    resource_type = Column(Enum(ResourceType, name="resource_type", create_type=False), nullable=True)
    status = Column(Enum(StatusEnum, name="status", create_type=False), default=StatusEnum.provisioning)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    under_attack = Column(Boolean, default=False)

    # Relationships
    logs = relationship("Log", back_populates="resource", cascade="all, delete-orphan")
    attacks = relationship("Attack", back_populates="resource", cascade="all, delete-orphan")


from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy import (
    Boolean, Column, DateTime, Enum, Integer, String
)
from sqlalchemy.orm import relationship
from app.enum.resource_type import ResourceType
from app.enum.status_enum import StatusEnum

Base = declarative_base()

class CloudResource(Base):
    __tablename__ = "cloud_resources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    resource_type = Column(Enum(ResourceType), nullable=False)
    status = Column(Enum(StatusEnum), default=StatusEnum.provisioning)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    under_attack = Column(Boolean, default=False)

    # Relationships
    logs = relationship("Log", back_populates="resource", cascade="all, delete-orphan")
    attacks = relationship("Attack", back_populates="resource", cascade="all, delete-orphan")


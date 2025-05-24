from datetime import datetime
from sqlalchemy import (
    Boolean, Column, DateTime, Enum, Integer, String, Float, ForeignKey
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.enum.resource_type import ResourceType
from app.enum.status_enum import StatusEnum
from app.models.attack import Base


class CloudResource(Base):
    __tablename__ = "cloud_resources"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    resource_type = Column(Enum(ResourceType, name="resource_type", create_type=False), nullable=True)
    status = Column(Enum(StatusEnum, name="status", create_type=False), default=StatusEnum.provisioning)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    under_attack = Column(Boolean, default=False)
    # Memory and resource metrics
    cpu_usage = Column(Float, default=0.0)
    memory_usage = Column(Float, default=0.0)
    memory_total = Column(Float, default=8.0)  # GB
    memory_available = Column(Float, default=8.0)  # GB
    disk_usage = Column(Float, default=0.0)
    network_usage = Column(Float, default=0.0)

    # Relationships
    owner = relationship("User", back_populates="resources")
    logs = relationship("Log", back_populates="resource", cascade="all, delete-orphan")
    attacks = relationship("Attack", back_populates="resource", cascade="all, delete-orphan")
    metrics = relationship("ResourceMetric", back_populates="resource", cascade="all, delete-orphan")

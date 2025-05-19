from datetime import datetime
from sqlalchemy import (
    Column, DateTime, Enum, Integer, Text, ForeignKey
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.enum.attack_type import AttackType
from app.enum.status_enum import StatusEnum


class Attack(Base):
    __tablename__ = "attacks"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("cloud_resources.id"))
    attack_type = Column(Enum(AttackType, name='attack_type', create_type=False), nullable=False)
    status = Column(Enum(StatusEnum, name='attack_status', create_type=False), default=StatusEnum.detected)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resource = relationship("CloudResource", back_populates="attacks")

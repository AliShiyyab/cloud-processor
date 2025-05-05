from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy import (
    Column, DateTime, Enum, Integer, Text, ForeignKey
)
from sqlalchemy.orm import relationship
from app.enum.attack_type import AttackType
from app.enum.status_enum import StatusEnum

Base = declarative_base()

class Attack(Base):
    __tablename__ = "attacks"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("cloud_resources.id"))
    attack_type = Column(Enum(AttackType), nullable=False)
    status = Column(Enum(StatusEnum), default=StatusEnum.detected)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resource = relationship("CloudResource", back_populates="attacks")

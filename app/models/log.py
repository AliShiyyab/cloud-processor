from datetime import datetime
from sqlalchemy import (
    Column, DateTime, ForeignKey, Integer, String, Text
)
from sqlalchemy.orm import relationship

from app.models.attack import Base


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("cloud_resources.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    level = Column(String, nullable=False)  # info, warning, error, debug
    message = Column(Text, nullable=False)
    process = Column(String, nullable=True)
    pid = Column(Integer, nullable=True)
    resource = relationship("CloudResource", back_populates="logs")

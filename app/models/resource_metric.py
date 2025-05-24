from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship

from app.core.database import Base


class ResourceMetric(Base):
    __tablename__ = "resource_metrics"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("cloud_resources.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)

    # System metrics
    cpu_usage = Column(Float, nullable=False)
    memory_usage = Column(Float, nullable=False)
    memory_total = Column(Float, nullable=False)
    memory_available = Column(Float, nullable=False)
    disk_usage = Column(Float, nullable=False)
    network_usage = Column(Float, nullable=False)

    # Security metrics
    vulnerability_count = Column(Integer, default=0)
    attack_count = Column(Integer, default=0)
    anomaly_score = Column(Float, default=0.0)

    # Relationships
    resource = relationship("CloudResource", back_populates="metrics")

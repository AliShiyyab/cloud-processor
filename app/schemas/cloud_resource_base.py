from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.enum.attack_type import AttackType
from app.enum.resource_type import ResourceType
from app.enum.status_enum import StatusEnum

class CloudResourceBase(BaseModel):
    name: str
    resource_type: ResourceType

class CloudResourceCreate(CloudResourceBase):
    pass

class CloudResourceResponse(CloudResourceBase):
    id: int
    status: StatusEnum
    ip_address: Optional[str] = None
    created_at: datetime
    under_attack: bool

    class Config:
        orm_mode = True

class LogBase(BaseModel):
    resource_id: int
    level: str
    message: str
    process: Optional[str] = None
    pid: Optional[int] = None

class LogCreate(LogBase):
    pass

class LogResponse(LogBase):
    id: int
    timestamp: datetime
    resource: CloudResourceResponse

    class Config:
        orm_mode = True

class AttackBase(BaseModel):
    resource_id: int
    attack_type: AttackType
    status: StatusEnum
    details: Optional[str] = None

class AttackCreate(AttackBase):
    pass

class AttackResponse(AttackBase):
    id: int
    created_at: datetime
    updated_at: datetime
    resource: CloudResourceResponse

    class Config:
        orm_mode = True

class SimulateAttackRequest(BaseModel):
    resource_id: int
    attack_type: AttackType

class CountermeasureRequest(BaseModel):
    attack_id: int

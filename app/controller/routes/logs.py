from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.controller.deps import get_db
from app.schemas.cloud_resource_base import LogResponse
from app.services.log_service import LogService

log_service = LogService()
router = APIRouter()

@router.get("/logs/", response_model=List[LogResponse])
async def get_logs(
    resource_id: Optional[int] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    return await log_service.get_logs(db, resource_id, limit)

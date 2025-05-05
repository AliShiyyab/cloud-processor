import logging
from typing import List

from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.controller.deps import get_db
from app.schemas.cloud_resource_base import CloudResourceResponse, CloudResourceCreate
from app.services.resource_service import ResourceService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
router = APIRouter()

resource_service = ResourceService()

@router.post("/resources/", response_model=CloudResourceResponse)
async def create_resource(
    resource: CloudResourceCreate, db: AsyncSession = Depends(get_db)
):
    return await resource_service.create_resource(db, resource)


@router.get("/resources/", response_model=List[CloudResourceResponse])
async def get_resources(db: AsyncSession = Depends(get_db)):
    return await resource_service.get_resources(db)


@router.get("/resources/{resource_id}", response_model=CloudResourceResponse)
async def get_resource(resource_id: int, db: AsyncSession = Depends(get_db)):
    resource = await resource_service.get_resource(db, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource


@router.delete("/resources/{resource_id}")
async def delete_resource(resource_id: int, db: AsyncSession = Depends(get_db)):
    success = await resource_service.delete_resource(db, resource_id)
    if not success:
        raise HTTPException(status_code=404, detail="Resource not found")
    return {"message": "Resource deleted successfully"}


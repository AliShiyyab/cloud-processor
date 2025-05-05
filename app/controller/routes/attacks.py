import asyncio

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.controller.deps import get_db
from app.controller.routes.websocket import manager
from app.enum.status_enum import StatusEnum
from app.schemas.cloud_resource_base import SimulateAttackRequest, AttackResponse, AttackCreate
from app.services.attack_service import AttackService
from app.services.log_service import LogService
from app.services.resource_service import ResourceService

router = APIRouter()

resource_service = ResourceService()
attack_service = AttackService()
log_service = LogService()


@router.post("/attacks/simulate", response_model=AttackResponse)
async def simulate_attack(
        request: SimulateAttackRequest, db: AsyncSession = Depends(get_db)
):
    # Get the resource
    resource = await resource_service.get_resource(db, request.resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    # Create attack record
    attack = await attack_service.create_attack(
        db,
        AttackCreate(
            resource_id=request.resource_id,
            attack_type=request.attack_type,
            status=StatusEnum.in_progress,
            details=f"Simulating {request.attack_type} attack on {resource.name}"
        )
    )

    # Log the attack
    await log_service.create_log(
        db,
        resource_id=request.resource_id,
        level="warning",
        message=f"Attack simulation started: {request.attack_type}",
        process="attack-simulator"
    )

    # Simulate the attack (async)
    asyncio.create_task(
        attack_service.simulate_attack(
            db, attack.id, resource.id, request.attack_type, manager
        )
    )

    return attack

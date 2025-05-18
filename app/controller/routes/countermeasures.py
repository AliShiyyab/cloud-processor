import asyncio

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.controller.deps import get_db
from app.enum.status_enum import StatusEnum
from app.schemas.cloud_resource_base import CountermeasureRequest, AttackResponse
from app.services.attack_service import AttackService
from app.services.countermeasure_service import CountermeasureService
from app.services.log_service import LogService
from app.services.resource_service import ResourceService
from app.utils.websocket_manager import ConnectionManager

router = APIRouter()

resource_service = ResourceService()
attack_service = AttackService()
log_service = LogService()
countermeasure_service = CountermeasureService()
manager = ConnectionManager()


@router.post("/countermeasures/deploy", response_model=AttackResponse)
async def deploy_countermeasure(
        request: CountermeasureRequest, db: AsyncSession = Depends(get_db)
):
    # Get the attack
    attack = await attack_service.get_attack(db, request.attack_id)
    if not attack:
        raise HTTPException(status_code=404, detail="Attack not found")

    # Get the resource
    resource = await resource_service.get_resource(db, attack.resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    # Log the countermeasure deployment
    await log_service.create_log(
        db,
        resource_id=attack.resource_id,
        level="info",
        message=f"Deploying countermeasure for {attack.attack_type} attack",
        process="security-monitor"
    )
    # Deploy countermeasure (async)
    asyncio.create_task(
        countermeasure_service.deploy_countermeasure(
            db, attack.id, attack.resource_id, attack.attack_type, manager
        )
    )
    # Update attack status
    updated_attack = await attack_service.update_attack_status(
        db, attack.id, StatusEnum.mitigating
    )
    return updated_attack

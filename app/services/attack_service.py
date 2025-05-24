import asyncio
from datetime import datetime
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.enum.attack_type import AttackType
from app.enum.status_enum import StatusEnum
from app.models.attack import Attack
from app.schemas.cloud_resource_base import AttackCreate
from app.services.log_service import LogService
from app.services.resource_service import ResourceService
from app.utils.websocket_manager import ConnectionManager


class AttackService:
    def __init__(self):
        self.log_service = LogService()
        self.resource_service = ResourceService()

    async def create_attack(self, db: AsyncSession, attack_data: AttackCreate) -> Attack:
        attack = Attack(
            resource_id=attack_data.resource_id,
            attack_type=attack_data.attack_type,
            status=attack_data.status,
            details=attack_data.details,
        )
        db.add(attack)
        db.commit()
        db.refresh(attack)
        return attack

    async def get_attack(
            self, db: AsyncSession, attack_id: int
    ) -> Optional[Attack]:
        """Get a specific attack by ID"""
        result =  db.execute(
            select(Attack)
            .options(joinedload(Attack.resource))
            .where(Attack.id == attack_id)
        )
        return result.scalars().first()

    async def get_attacks(
            self, db: AsyncSession, resource_id: Optional[int] = None
    ) -> List[Attack]:
        """Get all attacks, optionally filtered by resource"""
        query = select(Attack).options(joinedload(Attack.resource))

        if resource_id:
            query = query.where(Attack.resource_id == resource_id)

        result = db.execute(query)
        return result.scalars().all()

    async def update_attack_status(
            self, db: AsyncSession, attack_id: int, status: StatusEnum
    ) -> Optional[Attack]:
        """Update an attack's status"""
        attack = await self.get_attack(db, attack_id)
        if attack:
            attack.status = status
            attack.updated_at = datetime.utcnow()
            await db.commit()
            await db.refresh(attack)
        return attack

    async def simulate_attack(
            self,
            db: AsyncSession,
            attack_id: int,
            resource_id: int,
            attack_type: AttackType,
            manager: ConnectionManager,
    ):
        """Simulate an attack on a resource"""
        # Update resource to show it's under attack
        await self.resource_service.update_attack_status(db, resource_id, True)

        # Get attack details
        attack_details = self._get_attack_details(attack_type)

        # Update attack with details
        attack = await self.update_attack(
            db, attack_id, StatusEnum.in_progress, attack_details
        )

        # Broadcast attack update
        if attack:
            await manager.broadcast_attack(self._attack_to_dict(attack))

        # Generate attack logs
        await self._generate_attack_logs(db, resource_id, attack_type, manager)

        # After some time, mark the attack as detected if not mitigated
        await asyncio.sleep(30)

        # Check if attack still exists and is in progress
        attack = await self.get_attack(db, attack_id)
        if attack and attack.status == StatusEnum.in_progress:
            await self.update_attack_status(db, attack_id, StatusEnum.detected)

            # Broadcast updated attack
            attack = await self.get_attack(db, attack_id)
            if attack:
                await manager.broadcast_attack(self._attack_to_dict(attack))

    async def update_attack(
            self, db: AsyncSession, attack_id: int, status: StatusEnum, details: str
    ) -> Optional[Attack]:
        """Update an attack's status and details"""
        attack = await self.get_attack(db, attack_id)
        if attack:
            attack.status = status
            attack.details = details
            attack.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(attack)
        return attack

    async def _generate_attack_logs(
            self, db: AsyncSession, resource_id: int, attack_type: AttackType, manager: ConnectionManager
    ):
        """Generate realistic logs for the attack simulation"""
        # Common attack patterns
        attack_logs = self._get_attack_logs(attack_type)

        # Send logs with delays to simulate real-time attack
        for log_entry in attack_logs:
            # Create and broadcast log
            log = await self.log_service.create_log(
                db,
                resource_id=resource_id,
                level=log_entry["level"],
                message=log_entry["message"],
                process=log_entry["process"],
            )

            # Convert to dict and broadcast
            log_dict = {
                "id": str(log.id),
                "timestamp": log.timestamp.isoformat(),
                "resource": log.resource.name,
                "level": log.level,
                "message": log.message,
                "process": log.process,
                "pid": log.pid,
            }
            await manager.broadcast_log(log_dict)

            # Wait before next log
            await asyncio.sleep(log_entry.get("delay", 2))

    def _attack_to_dict(self, attack: Attack) -> dict:
        """Convert Attack object to dictionary for WebSocket broadcast"""
        return {
            "id": str(attack.id),
            "timestamp": attack.created_at.isoformat(),
            "resourceId": str(attack.resource_id),
            "resourceName": attack.resource.name,
            "attackType": attack.attack_type,
            "status": attack.status,
            "details": attack.details,
        }

    def _get_attack_details(self, attack_type: AttackType) -> str:
        """Get detailed description for an attack type"""
        details = {
            AttackType.format_string: (
                "Format string vulnerability exploited in printf-like function "
                "allowing arbitrary memory reads and writes"
            ),
            AttackType.off_by_one: (
                "Off-by-one error in boundary checking allowing buffer to be "
                "overwritten by one byte"
            ),
            AttackType.heap_overflow: (
                "Heap buffer overflow detected in dynamic memory allocation, "
                "potentially corrupting heap metadata"
            ),
            AttackType.stack_overflow: (
                "Stack buffer overflow detected, potentially overwriting return "
                "address and function pointers"
            ),
        }
        return details.get(attack_type, "Unknown attack vector detected")

    def _get_attack_logs(self, attack_type: AttackType) -> List[dict]:
        """Get a sequence of logs for simulating an attack"""
        # Common initial logs
        logs = [
            {
                "level": "warning",
                "message": "Unusual memory access pattern detected",
                "process": "security-monitor",
                "delay": 1,
            },
            {
                "level": "warning",
                "message": "Potential buffer manipulation attempt",
                "process": "security-monitor",
                "delay": 2,
            },
        ]

        # Attack-specific logs
        if attack_type == AttackType.format_string:
            logs.extend([
                {
                    "level": "error",
                    "message": "Format string vulnerability exploited in printf() call",
                    "process": "libc",
                    "delay": 1,
                },
                {
                    "level": "error",
                    "message": "Arbitrary memory read detected at address 0x7fff5534a000",
                    "process": "libc",
                    "delay": 1,
                },
                {
                    "level": "error",
                    "message": "Attempt to write to memory location 0x7fff5534a008",
                    "process": "libc",
                    "delay": 2,
                },
                {
                    "level": "error",
                    "message": "Format string attack in progress - attempting to overwrite GOT entry",
                    "process": "security-monitor",
                    "delay": 3,
                },
            ])
        elif attack_type == AttackType.off_by_one:
            logs.extend([
                {
                    "level": "warning",
                    "message": "Buffer access at boundary condition",
                    "process": "application",
                    "delay": 1,
                },
                {
                    "level": "error",
                    "message": "Off-by-one error: Writing past buffer boundary by 1 byte",
                    "process": "application",
                    "delay": 2,
                },
                {
                    "level": "error",
                    "message": "Memory corruption detected in adjacent variable",
                    "process": "security-monitor",
                    "delay": 1,
                },
                {
                    "level": "error",
                    "message": "Control flow integrity violation attempted via off-by-one overflow",
                    "process": "security-monitor",
                    "delay": 3,
                },
            ])
        elif attack_type == AttackType.heap_overflow:
            logs.extend([
                {
                    "level": "warning",
                    "message": "Heap memory allocation exceeds requested size",
                    "process": "malloc",
                    "delay": 1,
                },
                {
                    "level": "error",
                    "message": "Heap metadata corruption detected",
                    "process": "malloc",
                    "delay": 2,
                },
                {
                    "level": "error",
                    "message": "Double-free attempt detected",
                    "process": "malloc",
                    "delay": 1,
                },
                {
                    "level": "error",
                    "message": "Heap overflow attack attempting to overwrite function pointer",
                    "process": "security-monitor",
                    "delay": 3,
                },
            ])
        elif attack_type == AttackType.stack_overflow:
            logs.extend([
                {
                    "level": "warning",
                    "message": "Stack buffer overflow detected in function call",
                    "process": "application",
                    "delay": 1,
                },
                {
                    "level": "error",
                    "message": "Stack canary value modified",
                    "process": "application",
                    "delay": 2,
                },
                {
                    "level": "error",
                    "message": "Return address overwritten with 0x41414141",
                    "process": "application",
                    "delay": 1,
                },
                {
                    "level": "error",
                    "message": "Stack-based buffer overflow attack attempting to execute shellcode",
                    "process": "security-monitor",
                    "delay": 3,
                },
            ])

        # Final detection log
        logs.append({
            "level": "error",
            "message": f"Buffer overflow attack confirmed: {attack_type}",
            "process": "security-monitor",
            "delay": 2,
        })

        return logs

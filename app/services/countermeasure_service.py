import asyncio
from typing import Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.enum.attack_type import AttackType
from app.enum.status_enum import StatusEnum
from app.services.attack_service import AttackService
from app.services.log_service import LogService
from app.services.resource_service import ResourceService
from app.utils.websocket_manager import ConnectionManager


class CountermeasureService:
    def __init__(self):
        self.attack_service = AttackService()
        self.log_service = LogService()
        self.resource_service = ResourceService()

    async def deploy_countermeasure(
            self,
            db: AsyncSession,
            attack_id: int,
            resource_id: int,
            attack_type: AttackType,
            manager: ConnectionManager,
    ):
        """Deploy a countermeasure for a specific attack"""
        # Log the countermeasure deployment
        await self.log_service.create_log(
            db,
            resource_id=resource_id,
            level="info",
            message=f"Deploying countermeasure for {attack_type} attack",
            process="security-monitor"
        )

        # Update attack status to mitigating
        await self.attack_service.update_attack_status(
            db, attack_id, StatusEnum.mitigating
        )

        # Get attack for broadcasting
        attack = await self.attack_service.get_attack(db, attack_id)
        if attack:
            await manager.broadcast_attack(self.attack_service._attack_to_dict(attack))

        # Generate countermeasure logs
        await self._generate_countermeasure_logs(db, resource_id, attack_type, manager)

        # Apply specific countermeasure based on attack type
        countermeasure_method = self._get_countermeasure_method(attack_type)
        await countermeasure_method(db, resource_id, manager)

        # After countermeasure is applied, update attack status to mitigated
        await self.attack_service.update_attack_status(
            db, attack_id, StatusEnum.mitigated
        )

        # Update resource to show it's no longer under attack
        await self.resource_service.update_attack_status(db, resource_id, False)

        # Get updated attack for broadcasting
        attack = await self.attack_service.get_attack(db, attack_id)
        if attack:
            await manager.broadcast_attack(self.attack_service._attack_to_dict(attack))

    def _get_countermeasure_method(self, attack_type: AttackType):
        """Get the appropriate countermeasure method for an attack type"""
        countermeasures = {
            AttackType.format_string: self._apply_format_string_countermeasure,
            AttackType.off_by_one: self._apply_off_by_one_countermeasure,
            AttackType.heap_overflow: self._apply_heap_overflow_countermeasure,
            AttackType.stack_overflow: self._apply_stack_overflow_countermeasure,
        }
        return countermeasures.get(attack_type, self._apply_generic_countermeasure)

    async def _apply_format_string_countermeasure(
            self, db: AsyncSession, resource_id: int, manager: ConnectionManager
    ):
        """Apply countermeasures for format string vulnerabilities"""
        countermeasure_steps = [
            {
                "level": "info",
                "message": "Applying format string sanitization to vulnerable functions",
                "process": "security-patch",
                "delay": 1,
            },
            {
                "level": "info",
                "message": "Implementing compiler protection flags: -Wformat -Wformat-security",
                "process": "security-patch",
                "delay": 2,
            },
            {
                "level": "info",
                "message": "Replacing vulnerable printf() calls with safe alternatives",
                "process": "security-patch",
                "delay": 1,
            },
            {
                "level": "info",
                "message": "Adding format string validation to input processing",
                "process": "security-patch",
                "delay": 2,
            },
            {
                "level": "info",
                "message": "Format string vulnerability patched successfully",
                "process": "security-monitor",
                "delay": 1,
            },
        ]

        await self._execute_countermeasure_steps(db, resource_id, countermeasure_steps, manager)

    async def _apply_off_by_one_countermeasure(
            self, db: AsyncSession, resource_id: int, manager: ConnectionManager
    ):
        """Apply countermeasures for off-by-one vulnerabilities"""
        countermeasure_steps = [
            {
                "level": "info",
                "message": "Implementing strict bounds checking in loop conditions",
                "process": "security-patch",
                "delay": 1,
            },
            {
                "level": "info",
                "message": "Adding buffer size validation before memory operations",
                "process": "security-patch",
                "delay": 2,
            },
            {
                "level": "info",
                "message": "Replacing vulnerable string functions with length-aware alternatives",
                "process": "security-patch",
                "delay": 1,
            },
            {
                "level": "info",
                "message": "Implementing safe integer arithmetic for buffer calculations",
                "process": "security-patch",
                "delay": 2,
            },
            {
                "level": "info",
                "message": "Off-by-one vulnerability patched successfully",
                "process": "security-monitor",
                "delay": 1,
            },
        ]

        await self._execute_countermeasure_steps(db, resource_id, countermeasure_steps, manager)

    async def _apply_heap_overflow_countermeasure(
            self, db: AsyncSession, resource_id: int, manager: ConnectionManager
    ):
        """Apply countermeasures for heap overflow vulnerabilities"""
        countermeasure_steps = [
            {
                "level": "info",
                "message": "Implementing heap canaries to detect metadata corruption",
                "process": "security-patch",
                "delay": 1,
            },
            {
                "level": "info",
                "message": "Adding memory allocation validation and size checks",
                "process": "security-patch",
                "delay": 2,
            },
            {
                "level": "info",
                "message": "Implementing ASLR (Address Space Layout Randomization) for heap memory",
                "process": "security-patch",
                "delay": 1,
            },
            {
                "level": "info",
                "message": "Deploying double-free detection mechanisms",
                "process": "security-patch",
                "delay": 2,
            },
            {
                "level": "info",
                "message": "Heap overflow vulnerability patched successfully",
                "process": "security-monitor",
                "delay": 1,
            },
        ]

        await self._execute_countermeasure_steps(db, resource_id, countermeasure_steps, manager)

    async def _apply_stack_overflow_countermeasure(
            self, db: AsyncSession, resource_id: int, manager: ConnectionManager
    ):
        """Apply countermeasures for stack overflow vulnerabilities"""
        countermeasure_steps = [
            {
                "level": "info",
                "message": "Deploying stack canaries to detect stack corruption",
                "process": "security-patch",
                "delay": 1,
            },
            {
                "level": "info",
                "message": "Implementing non-executable stack protection (NX bit)",
                "process": "security-patch",
                "delay": 2,
            },
            {
                "level": "info",
                "message": "Enabling ASLR (Address Space Layout Randomization) for stack memory",
                "process": "security-patch",
                "delay": 1,
            },
            {
                "level": "info",
                "message": "Adding buffer size validation in function calls",
                "process": "security-patch",
                "delay": 2,
            },
            {
                "level": "info",
                "message": "Stack overflow vulnerability patched successfully",
                "process": "security-monitor",
                "delay": 1,
            },
        ]

        await self._execute_countermeasure_steps(db, resource_id, countermeasure_steps, manager)

    async def _apply_generic_countermeasure(
            self, db: AsyncSession, resource_id: int, manager: ConnectionManager
    ):
        """Apply generic countermeasures for unknown attack types"""
        countermeasure_steps = [
            {
                "level": "info",
                "message": "Applying general memory protection mechanisms",
                "process": "security-patch",
                "delay": 1,
            },
            {
                "level": "info",
                "message": "Implementing input validation and sanitization",
                "process": "security-patch",
                "delay": 2,
            },
            {
                "level": "info",
                "message": "Deploying runtime memory safety checks",
                "process": "security-patch",
                "delay": 1,
            },
            {
                "level": "info",
                "message": "Generic vulnerability patched successfully",
                "process": "security-monitor",
                "delay": 1,
            },
        ]

        await self._execute_countermeasure_steps(db, resource_id, countermeasure_steps, manager)

    async def _execute_countermeasure_steps(
            self, db: AsyncSession, resource_id: int, steps: List[Dict], manager: ConnectionManager
    ):
        """Execute a sequence of countermeasure steps with logs"""
        for step in steps:
            # Create and broadcast log
            log = await self.log_service.create_log(
                db,
                resource_id=resource_id,
                level=step["level"],
                message=step["message"],
                process=step["process"],
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

            # Wait before next step
            await asyncio.sleep(step.get("delay", 1))

    async def _generate_countermeasure_logs(
            self, db: AsyncSession, resource_id: int, attack_type: AttackType, manager: ConnectionManager
    ):
        """Generate initial logs for countermeasure deployment"""
        logs = [
            {
                "level": "info",
                "message": f"Initiating countermeasure deployment for {attack_type} attack",
                "process": "security-monitor",
                "delay": 1,
            },
            {
                "level": "info",
                "message": "Analyzing attack vector and vulnerable components",
                "process": "security-monitor",
                "delay": 2,
            },
            {
                "level": "info",
                "message": f"Selected appropriate countermeasure for {attack_type} attack",
                "process": "security-monitor",
                "delay": 1,
            },
        ]

        for log_entry in logs:
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
            await asyncio.sleep(log_entry.get("delay", 1))

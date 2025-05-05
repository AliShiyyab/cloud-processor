from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.enum.resource_type import ResourceType
from app.enum.status_enum import StatusEnum
from app.models.cloud_resource import CloudResource
from app.schemas.cloud_resource_base import CloudResourceCreate


class ResourceService:
    async def create_resource(
        self, db: AsyncSession, resource_data: CloudResourceCreate
    ) -> CloudResource:
        """Create a new cloud resource"""
        # Generate a random IP address for VMs and services
        ip_address = None
        if resource_data.resource_type in [ResourceType.VM, ResourceType.SERVICE]:
            import random
            ip_address = f"192.168.1.{random.randint(2, 254)}"

        # Create the resource
        resource = CloudResource(
            name=resource_data.name,
            resource_type=resource_data.resource_type,
            status=StatusEnum.provisioning,
            ip_address=ip_address,
            under_attack=False
        )
        db.add(resource)
        await db.commit()
        await db.refresh(resource)

        # Simulate resource becoming available after creation
        import asyncio
        asyncio.create_task(self._activate_resource(db, resource.id))

        return resource

    async def _activate_resource(self, db: AsyncSession, resource_id: int):
        """Simulate resource activation after a delay"""
        import asyncio
        await asyncio.sleep(5)  # Wait 5 seconds

        async with AsyncSession(db.bind) as session:
            resource = await self.get_resource(session, resource_id)
            if resource:
                resource.status = StatusEnum.running
                await session.commit()

    async def get_resources(self, db: AsyncSession) -> List[CloudResource]:
        """Get all cloud resources"""
        result = await db.execute(select(CloudResource))
        return result.scalars().all()

    async def get_resource(
        self, db: AsyncSession, resource_id: int
    ) -> Optional[CloudResource]:
        """Get a specific cloud resource by ID"""
        result = await db.execute(
            select(CloudResource).where(CloudResource.id == resource_id)
        )
        return result.scalars().first()

    async def update_resource_status(
        self, db: AsyncSession, resource_id: int, status: StatusEnum
    ) -> Optional[CloudResource]:
        """Update a resource's status"""
        resource = await self.get_resource(db, resource_id)
        if resource:
            resource.status = status
            await db.commit()
            await db.refresh(resource)
        return resource

    async def update_attack_status(
        self, db: AsyncSession, resource_id: int, under_attack: bool
    ) -> Optional[CloudResource]:
        """Update a resource's under_attack status"""
        resource = await self.get_resource(db, resource_id)
        if resource:
            resource.under_attack = under_attack
            await db.commit()
            await db.refresh(resource)
        return resource

    async def delete_resource(self, db: AsyncSession, resource_id: int) -> bool:
        """Delete a cloud resource"""
        resource = await self.get_resource(db, resource_id)
        if resource:
            await db.delete(resource)
            await db.commit()
            return True
        return False

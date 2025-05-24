from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.enum.resource_type import ResourceType
from app.enum.status_enum import StatusEnum
from app.models.cloud_resource import CloudResource
from app.models.resource_metric import ResourceMetric
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

        # Set initial memory values based on resource type
        memory_total = 8.0  # Default 8GB
        if resource_data.resource_type == ResourceType.VM:
            memory_total = 16.0  # VMs get 16GB
        elif resource_data.resource_type == ResourceType.SERVICE:
            memory_total = 4.0  # Services get 4GB

        # Create the resource
        resource = CloudResource(
            name=resource_data.name,
            resource_type=resource_data.resource_type,
            status=StatusEnum.provisioning,
            ip_address=ip_address,
            under_attack=False,
            owner_id=resource_data.owner_id,
            memory_total=memory_total,
            memory_available=memory_total,
            memory_usage=0.0,
            cpu_usage=0.0,
            disk_usage=0.0,
            network_usage=0.0
        )
        db.add(resource)
        await db.commit()
        await db.refresh(resource)

        # Create initial metrics
        await self.create_initial_metrics(db, resource.id)

        # Simulate resource becoming available after creation
        import asyncio
        asyncio.create_task(self._activate_resource(db, resource.id))

        return resource

    async def create_initial_metrics(self, db: AsyncSession, resource_id: int):
        """Create initial metrics for a resource"""
        resource = await self.get_resource(db, resource_id)
        if not resource:
            return

        metric = ResourceMetric(
            resource_id=resource_id,
            cpu_usage=0.0,
            memory_usage=0.0,
            memory_total=resource.memory_total,
            memory_available=resource.memory_total,
            disk_usage=0.0,
            network_usage=0.0,
            vulnerability_count=0,
            attack_count=0,
            anomaly_score=0.0
        )
        db.add(metric)
        await db.commit()

    async def _activate_resource(self, db: AsyncSession, resource_id: int):
        """Simulate resource activation after a delay"""
        import asyncio
        await asyncio.sleep(5)  # Wait 5 seconds

        async with AsyncSession(db.bind) as session:
            resource = await self.get_resource(session, resource_id)
            if resource:
                resource.status = StatusEnum.running
                # Set some baseline usage
                resource.cpu_usage = 5.0 + (hash(resource.name) % 10)  # 5-15%
                resource.memory_usage = 1.0 + (hash(resource.name) % 3)  # 1-4GB
                resource.memory_available = resource.memory_total - resource.memory_usage
                resource.disk_usage = 10.0 + (hash(resource.name) % 20)  # 10-30%
                resource.network_usage = 50.0 + (hash(resource.name) % 100)  # 50-150 Mbps
                await session.commit()

    async def get_resources(self, db: AsyncSession, owner_id: Optional[int] = None) -> List[CloudResource]:
        """Get all cloud resources, optionally filtered by owner"""
        query = select(CloudResource).options(joinedload(CloudResource.owner))

        if owner_id:
            query = query.where(CloudResource.owner_id == owner_id)

        result = await db.execute(query)
        return result.scalars().all()

    async def get_resource(
            self, db: AsyncSession, resource_id: int
    ) -> Optional[CloudResource]:
        """Get a specific cloud resource by ID"""
        result = await db.execute(
            select(CloudResource)
            .options(joinedload(CloudResource.owner))
            .where(CloudResource.id == resource_id)
        )
        return result.scalars().first()

    async def update_resource_metrics(
            self, db: AsyncSession, resource_id: int,
            cpu_usage: float = None, memory_usage: float = None,
            disk_usage: float = None, network_usage: float = None
    ) -> Optional[CloudResource]:
        """Update a resource's metrics"""
        resource = await self.get_resource(db, resource_id)
        if resource:
            if cpu_usage is not None:
                resource.cpu_usage = cpu_usage
            if memory_usage is not None:
                resource.memory_usage = memory_usage
                resource.memory_available = resource.memory_total - memory_usage
            if disk_usage is not None:
                resource.disk_usage = disk_usage
            if network_usage is not None:
                resource.network_usage = network_usage

            await db.commit()
            await db.refresh(resource)
        return resource

    async def simulate_attack_impact(
            self, db: AsyncSession, resource_id: int, attack_type: str
    ) -> Optional[CloudResource]:
        """Simulate the impact of an attack on resource metrics"""
        resource = await self.get_resource(db, resource_id)
        if not resource:
            return None

        # Calculate attack impact based on attack type
        memory_impact = 0.0
        cpu_impact = 0.0

        if attack_type == "heap-overflow":
            memory_impact = 2.0 + (hash(str(resource_id)) % 3)  # 2-5GB memory leak
            cpu_impact = 15.0 + (hash(str(resource_id)) % 10)  # 15-25% CPU spike
        elif attack_type == "stack-overflow":
            memory_impact = 1.5 + (hash(str(resource_id)) % 2)  # 1.5-3.5GB
            cpu_impact = 20.0 + (hash(str(resource_id)) % 15)  # 20-35% CPU spike
        elif attack_type == "format-string":
            memory_impact = 0.5 + (hash(str(resource_id)) % 1)  # 0.5-1.5GB
            cpu_impact = 10.0 + (hash(str(resource_id)) % 10)  # 10-20% CPU spike
        elif attack_type == "off-by-one":
            memory_impact = 0.3 + (hash(str(resource_id)) % 1)  # 0.3-1.3GB
            cpu_impact = 8.0 + (hash(str(resource_id)) % 7)  # 8-15% CPU spike

        # Apply the impact
        new_memory_usage = min(resource.memory_usage + memory_impact, resource.memory_total * 0.95)
        new_cpu_usage = min(resource.cpu_usage + cpu_impact, 100.0)

        resource.memory_usage = new_memory_usage
        resource.memory_available = resource.memory_total - new_memory_usage
        resource.cpu_usage = new_cpu_usage
        resource.under_attack = True

        await db.commit()
        await db.refresh(resource)
        return resource

    async def restore_resource_after_mitigation(
            self, db: AsyncSession, resource_id: int
    ) -> Optional[CloudResource]:
        """Restore resource metrics after attack mitigation"""
        resource = await self.get_resource(db, resource_id)
        if not resource:
            return None

        # Gradually restore to baseline levels
        baseline_memory = 1.0 + (hash(resource.name) % 3)  # 1-4GB baseline
        baseline_cpu = 5.0 + (hash(resource.name) % 10)  # 5-15% baseline

        resource.memory_usage = baseline_memory
        resource.memory_available = resource.memory_total - baseline_memory
        resource.cpu_usage = baseline_cpu
        resource.under_attack = False

        await db.commit()
        await db.refresh(resource)
        return resource

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

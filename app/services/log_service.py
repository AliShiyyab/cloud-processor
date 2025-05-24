from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.log import Log


class LogService:
    async def create_log(
            self,
            db: AsyncSession,
            resource_id: int,
            level: str,
            message: str,
            process: Optional[str] = None,
            pid: Optional[int] = None,
    ) -> Log:
        """Create a new log entry"""
        log = Log(
            resource_id=resource_id,
            level=level,
            message=message,
            process=process,
            pid=pid if pid else self._generate_random_pid(),
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    async def get_logs(
            self, db: AsyncSession, resource_id: Optional[int] = None, limit: int = 100
    ) -> List[Log]:
        """Get logs, optionally filtered by resource"""
        query = select(Log).options(joinedload(Log.resource)).order_by(Log.timestamp.desc()).limit(limit)

        if resource_id:
            query = query.where(Log.resource_id == resource_id)

        result = db.execute(query)
        return result.scalars().all()

    def _generate_random_pid(self) -> int:
        """Generate a random process ID for simulation"""
        import random
        return random.randint(1000, 9999)

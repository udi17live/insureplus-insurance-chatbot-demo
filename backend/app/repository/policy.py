import uuid
from sqlalchemy import select
from app.models.policy import Policy
from app.models.enums import PolicyStatus
from app.repository.base import BaseRepository


class PolicyRepository(BaseRepository[Policy]):
    model = Policy

    async def get_by_policy_number(self, policy_number: str) -> Policy | None:
        result = await self.db.execute(
            select(Policy).where(Policy.policy_number == policy_number)
        )
        return result.scalar_one_or_none()

    async def get_active_by_user(self, user_id: uuid.UUID) -> list[Policy]:
        result = await self.db.execute(
            select(Policy).where(
                Policy.user_id == user_id,
                Policy.status == PolicyStatus.active,
            ).order_by(Policy.start_date.desc())
        )
        return list(result.scalars().all())

    async def get_all_by_user(self, user_id: uuid.UUID, limit: int = 50, offset: int = 0) -> list[Policy]:
        result = await self.db.execute(
            select(Policy)
            .where(Policy.user_id == user_id)
            .order_by(Policy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

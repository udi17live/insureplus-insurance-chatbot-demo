import uuid
from sqlalchemy import select
from app.models.payment import Payment
from app.models.enums import PaymentStatus
from app.repository.base import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    model = Payment

    async def get_all_by_user(self, user_id: uuid.UUID, limit: int = 50, offset: int = 0) -> list[Payment]:
        result = await self.db.execute(
            select(Payment)
            .where(Payment.user_id == user_id)
            .order_by(Payment.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_by_policy(self, policy_id: uuid.UUID) -> list[Payment]:
        result = await self.db.execute(
            select(Payment)
            .where(Payment.policy_id == policy_id)
            .order_by(Payment.created_at.desc())
        )
        return list(result.scalars().all())

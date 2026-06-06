import uuid
from sqlalchemy import select
from app.models.quote import Quote
from app.models.enums import QuoteStatus
from app.repository.base import BaseRepository


class QuoteRepository(BaseRepository[Quote]):
    model = Quote

    async def get_active_by_user(self, user_id: uuid.UUID) -> list[Quote]:
        result = await self.db.execute(
            select(Quote).where(
                Quote.user_id == user_id,
                Quote.status == QuoteStatus.active,
            ).order_by(Quote.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_policy_creation_state(self, policy_creation_state_id: uuid.UUID) -> list[Quote]:
        result = await self.db.execute(
            select(Quote).where(Quote.policy_creation_state_id == policy_creation_state_id)
            .order_by(Quote.created_at.desc())
        )
        return list(result.scalars().all())

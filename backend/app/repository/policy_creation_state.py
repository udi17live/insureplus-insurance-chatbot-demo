import uuid
from sqlalchemy import select
from app.models.policy_creation_state import PolicyCreationState
from app.models.enums import CollectionStatus
from app.repository.base import BaseRepository


class PolicyCreationStateRepository(BaseRepository[PolicyCreationState]):
    model = PolicyCreationState

    async def get_active_by_user(self, user_id: uuid.UUID) -> PolicyCreationState | None:
        result = await self.db.execute(
            select(PolicyCreationState).where(
                PolicyCreationState.user_id == user_id,
                PolicyCreationState.status == CollectionStatus.in_progress,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_thread(self, thread_id: uuid.UUID) -> PolicyCreationState | None:
        result = await self.db.execute(
            select(PolicyCreationState).where(PolicyCreationState.thread_id == thread_id)
        )
        return result.scalar_one_or_none()

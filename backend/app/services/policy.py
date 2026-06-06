import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.policy import PolicyRepository
from app.repository.quote import QuoteRepository
from app.models.enums import PolicyStatus, QuoteStatus
from app.schemas.policy import PolicyOut


class PolicyService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = PolicyRepository(db)
        self.quote_repo = QuoteRepository(db)

    async def get_user_policies(self, user_id: uuid.UUID) -> list[PolicyOut]:
        policies = await self.repo.get_all_by_user(user_id)
        return [PolicyOut.model_validate(p) for p in policies]

    async def get_policy(self, policy_id: uuid.UUID, user_id: uuid.UUID) -> PolicyOut:
        policy = await self.repo.get_by_id(policy_id)
        if not policy or policy.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")
        return PolicyOut.model_validate(policy)

    async def cancel_policy(self, policy_id: uuid.UUID, user_id: uuid.UUID) -> PolicyOut:
        policy = await self.repo.get_by_id(policy_id)
        if not policy or policy.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")
        if policy.status != PolicyStatus.active:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Policy is not active")
        policy = await self.repo.update(policy, status=PolicyStatus.cancelled)
        return PolicyOut.model_validate(policy)

import uuid
from datetime import timezone, timedelta, datetime
from fastapi import HTTPException, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.chat_session import ChatSessionRepository
from app.repository.payment import PaymentRepository
from app.repository.policy import PolicyRepository
from app.repository.policy_creation_state import PolicyCreationStateRepository
from app.repository.quote import QuoteRepository
from app.models.enums import CollectionStatus, PaymentStatus, PolicyStatus, QuoteStatus
from app.schemas.agent import AgentQuoteCreate, AgentQuoteOut, AgentPolicyOut
from app.services.payment import PaymentService


class AgentToolsService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.session_repo = ChatSessionRepository(db)
        self.policy_repo = PolicyRepository(db)
        self.quote_repo = QuoteRepository(db)
        self.state_repo = PolicyCreationStateRepository(db)

    async def _resolve_user(self, session_id: uuid.UUID) -> uuid.UUID:
        thread = await self.session_repo.get_by_id(session_id)
        if not thread:
            logger.warning("_resolve_user: thread {} not found", session_id)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found")
        if not thread.user_id:
            logger.warning("_resolve_user: thread {} has no user_id — raising 401", session_id)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="This action requires an authenticated user. Please log in.",
            )
        logger.info("_resolve_user: thread {} → user {}", session_id, thread.user_id)
        return thread.user_id

    async def list_policies(self, session_id: uuid.UUID) -> list[AgentPolicyOut]:
        user_id = await self._resolve_user(session_id)
        policies = await self.policy_repo.get_all_by_user(user_id)
        return [
            AgentPolicyOut(
                policy_id=str(p.id),
                policy_number=p.policy_number,
                product_type=p.product_type,
                status=p.status.value,
                premium_amount=float(p.premium_amount),
                currency=p.currency,
                coverage_data=p.coverage_data,
                start_date=p.start_date,
                end_date=p.end_date,
            )
            for p in policies
        ]

    async def create_quote(self, data: AgentQuoteCreate) -> AgentQuoteOut:
        try:
            session_uuid = uuid.UUID(str(data.session_id))
        except (ValueError, AttributeError):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid session_id")
        user_id = await self._resolve_user(session_uuid)
        expires_at = data.expires_at or (datetime.now(timezone.utc) + timedelta(days=7))

        state = await self.state_repo.get_by_thread(session_uuid)
        if state:
            state = await self.state_repo.update(
                state,
                product_type=data.product_type,
                status=CollectionStatus.quoting,
                collected_data=data.collected_fields,
            )
        else:
            state = await self.state_repo.create(
                user_id=user_id,
                session_id=session_uuid,
                product_type=data.product_type,
                status=CollectionStatus.quoting,
                collected_data=data.collected_fields,
                field_attempts={},
            )

        quote = await self.quote_repo.create(
            user_id=user_id,
            policy_creation_state_id=state.id,
            product_type=data.product_type,
            status=QuoteStatus.pending,
            premium_amount=data.premium_amount,
            currency=data.currency,
            coverage_summary=data.coverage_summary,
            expires_at=expires_at,
        )

        return AgentQuoteOut(
            quote_id=str(quote.id),
            product_type=quote.product_type,
            premium_amount=float(quote.premium_amount),
            currency=quote.currency,
            coverage_summary=quote.coverage_summary,
            expires_at=quote.expires_at,
        )

    async def cancel_policy(self, policy_id: uuid.UUID, session_id: uuid.UUID) -> AgentPolicyOut:
        user_id = await self._resolve_user(session_id)
        policy = await self.policy_repo.get_by_id(policy_id)
        if not policy or policy.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")
        if policy.status != PolicyStatus.active:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Policy is not active")
        policy = await self.policy_repo.update(policy, status=PolicyStatus.cancelled)
        return AgentPolicyOut(
            policy_id=str(policy.id),
            policy_number=policy.policy_number,
            product_type=policy.product_type,
            status=policy.status.value,
            premium_amount=float(policy.premium_amount),
            currency=policy.currency,
            coverage_data=policy.coverage_data,
            start_date=policy.start_date,
            end_date=policy.end_date,
        )

    async def confirm_payment(self, quote_id: uuid.UUID, session_id: uuid.UUID) -> AgentPolicyOut:
        user_id = await self._resolve_user(session_id)
        policy_out = await PaymentService(self.db).confirm_payment(quote_id, user_id)
        return AgentPolicyOut(
            policy_id=str(policy_out.id),
            policy_number=policy_out.policy_number,
            product_type=policy_out.product_type,
            status=policy_out.status,
            premium_amount=policy_out.premium_amount,
            currency=policy_out.currency,
            coverage_data=policy_out.coverage_data,
            start_date=policy_out.start_date,
            end_date=policy_out.end_date,
        )

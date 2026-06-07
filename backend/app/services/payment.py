import random
import string
import uuid
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.payment import PaymentRepository
from app.repository.quote import QuoteRepository
from app.repository.policy import PolicyRepository
from app.models.enums import PaymentStatus, PolicyStatus, QuoteStatus
from app.schemas.payment import PaymentOut
from app.schemas.policy import PolicyOut


def _make_ref() -> str:
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return f"MOCK-{suffix}"


def _make_policy_number() -> str:
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"IP-{suffix}"


class PaymentService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = PaymentRepository(db)
        self.quote_repo = QuoteRepository(db)
        self.policy_repo = PolicyRepository(db)

    async def confirm_payment(self, quote_id: uuid.UUID, user_id: uuid.UUID) -> PolicyOut:
        """Simulate a successful payment: accept the quote and create an active policy."""
        quote = await self.quote_repo.get_by_id(quote_id)
        if not quote or quote.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quote not found")
        if quote.status != QuoteStatus.pending:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Quote is no longer available")

        await self.quote_repo.update(quote, status=QuoteStatus.accepted)

        now = datetime.now(timezone.utc)
        policy = await self.policy_repo.create(
            user_id=user_id,
            quote_id=quote_id,
            policy_number=_make_policy_number(),
            product_type=quote.product_type,
            status=PolicyStatus.active,
            coverage_data=quote.coverage_summary,
            premium_amount=quote.premium_amount,
            currency=quote.currency,
            start_date=now,
            end_date=now + timedelta(days=365),
        )

        await self.repo.create(
            user_id=user_id,
            quote_id=quote_id,
            policy_id=policy.id,
            payment_reference=_make_ref(),
            amount=quote.premium_amount,
            currency=quote.currency,
            status=PaymentStatus.succeeded,
            metadata_={},
        )

        return PolicyOut.model_validate(policy)

    async def get_user_payments(self, user_id: uuid.UUID) -> list[PaymentOut]:
        payments = await self.repo.get_all_by_user(user_id)
        return [PaymentOut.model_validate(p) for p in payments]

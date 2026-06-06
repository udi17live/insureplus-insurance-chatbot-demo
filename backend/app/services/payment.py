import uuid
import stripe
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.repository.payment import PaymentRepository
from app.repository.quote import QuoteRepository
from app.repository.policy import PolicyRepository
from app.models.enums import PaymentStatus, PolicyStatus, QuoteStatus
from app.schemas.payment import PaymentIntentResponse, PaymentOut

stripe.api_key = settings.stripe_secret_key


class PaymentService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = PaymentRepository(db)
        self.quote_repo = QuoteRepository(db)
        self.policy_repo = PolicyRepository(db)

    async def create_payment_intent(
        self, quote_id: uuid.UUID, user_id: uuid.UUID, currency: str = "GBP"
    ) -> PaymentIntentResponse:
        quote = await self.quote_repo.get_by_id(quote_id)
        if not quote or quote.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quote not found")
        if quote.status != QuoteStatus.active:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Quote is not active")

        amount_pence = int(quote.premium_amount * 100)
        intent = stripe.PaymentIntent.create(
            amount=amount_pence,
            currency=currency.lower(),
            metadata={"quote_id": str(quote_id), "user_id": str(user_id)},
        )

        await self.repo.create(
            user_id=user_id,
            quote_id=quote_id,
            stripe_payment_intent_id=intent["id"],
            amount=quote.premium_amount,
            currency=currency.upper(),
            status=PaymentStatus.pending,
            stripe_metadata=dict(intent),
        )

        return PaymentIntentResponse(
            client_secret=intent["client_secret"],
            payment_intent_id=intent["id"],
            amount=quote.premium_amount,
            currency=currency.upper(),
        )

    async def handle_webhook(self, payload: bytes, sig_header: str) -> None:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_secret)
        except stripe.error.SignatureVerificationError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid webhook signature")

        if event["type"] == "payment_intent.succeeded":
            await self._on_payment_succeeded(event["data"]["object"])
        elif event["type"] == "payment_intent.payment_failed":
            await self._on_payment_failed(event["data"]["object"])

    async def _on_payment_succeeded(self, intent: dict) -> None:
        payment = await self.repo.get_by_stripe_payment_intent(intent["id"])
        if not payment:
            return
        await self.repo.update(payment, status=PaymentStatus.succeeded, stripe_metadata=intent)

        if payment.quote_id:
            quote = await self.quote_repo.get_by_id(payment.quote_id)
            if quote:
                await self.quote_repo.update(quote, status=QuoteStatus.accepted)

    async def _on_payment_failed(self, intent: dict) -> None:
        payment = await self.repo.get_by_stripe_payment_intent(intent["id"])
        if not payment:
            return
        await self.repo.update(payment, status=PaymentStatus.failed, stripe_metadata=intent)

    async def get_user_payments(self, user_id: uuid.UUID) -> list[PaymentOut]:
        payments = await self.repo.get_all_by_user(user_id)
        return [PaymentOut.model_validate(p) for p in payments]

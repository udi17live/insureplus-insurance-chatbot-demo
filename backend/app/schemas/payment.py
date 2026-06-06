from datetime import datetime
from typing import Any
from pydantic import BaseModel
from app.models.enums import PaymentStatus


class CreatePaymentIntentRequest(BaseModel):
    quote_id: str
    currency: str = "GBP"


class PaymentOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    user_id: str
    policy_id: str | None
    quote_id: str | None
    stripe_payment_intent_id: str
    amount: float
    currency: str
    status: PaymentStatus
    stripe_metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class PaymentIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str
    amount: float
    currency: str

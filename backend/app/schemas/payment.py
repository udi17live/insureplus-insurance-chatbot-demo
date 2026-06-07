from datetime import datetime
from pydantic import BaseModel
from app.models.enums import PaymentStatus


class ConfirmPaymentRequest(BaseModel):
    quote_id: str


class PaymentOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    user_id: str
    policy_id: str | None
    quote_id: str | None
    payment_reference: str
    amount: float
    currency: str
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime

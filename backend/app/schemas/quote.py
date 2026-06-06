from datetime import datetime
from typing import Any
from pydantic import BaseModel
from app.models.enums import ProductType, QuoteStatus


class QuoteOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    user_id: str
    policy_creation_state_id: str
    product_type: ProductType
    status: QuoteStatus
    premium_amount: float
    currency: str
    coverage_summary: dict[str, Any]
    expires_at: datetime | None
    created_at: datetime

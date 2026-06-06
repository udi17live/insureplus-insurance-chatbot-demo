from datetime import datetime
from typing import Any
from pydantic import BaseModel
from app.models.enums import PolicyStatus, ProductType


class PolicyOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    user_id: str
    quote_id: str | None
    policy_number: str
    product_type: ProductType
    status: PolicyStatus
    coverage_data: dict[str, Any]
    premium_amount: float
    currency: str
    start_date: datetime | None
    end_date: datetime | None
    created_at: datetime
    updated_at: datetime

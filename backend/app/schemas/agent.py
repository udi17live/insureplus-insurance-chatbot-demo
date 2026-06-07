import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel
from app.models.enums import ProductType


class AgentQuoteCreate(BaseModel):
    session_id: str
    product_type: ProductType
    collected_fields: dict[str, Any]
    premium_amount: float
    currency: str = "GBP"
    coverage_summary: dict[str, Any]
    expires_at: datetime | None = None


class AgentQuoteOut(BaseModel):
    model_config = {"from_attributes": True}

    quote_id: str
    product_type: ProductType
    premium_amount: float
    currency: str
    coverage_summary: dict[str, Any]
    expires_at: datetime | None


class AgentPolicyOut(BaseModel):
    model_config = {"from_attributes": True}

    policy_id: str
    policy_number: str
    product_type: ProductType
    status: str
    premium_amount: float
    currency: str
    coverage_data: dict[str, Any]
    start_date: datetime | None
    end_date: datetime | None

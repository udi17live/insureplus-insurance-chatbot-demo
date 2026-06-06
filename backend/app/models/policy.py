import uuid
from datetime import datetime
from typing import Any
from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from app.models.mixins import UUIDMixin, TimestampMixin
from app.models.enums import PolicyStatus, ProductType


class Policy(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "policies"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    quote_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("quotes.id"), nullable=True)
    policy_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    product_type: Mapped[ProductType] = mapped_column(nullable=False)
    status: Mapped[PolicyStatus] = mapped_column(default=PolicyStatus.active, nullable=False)
    coverage_data: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    premium_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="GBP", nullable=False)
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

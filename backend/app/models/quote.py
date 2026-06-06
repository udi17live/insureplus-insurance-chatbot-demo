import uuid
from datetime import datetime
from typing import Any
from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from app.models.mixins import UUIDMixin, CreatedAtMixin
from app.models.enums import ProductType, QuoteStatus


class Quote(UUIDMixin, CreatedAtMixin, Base):
    __tablename__ = "quotes"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    policy_creation_state_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("policy_creation_states.id"), nullable=False)
    product_type: Mapped[ProductType] = mapped_column(nullable=False)
    status: Mapped[QuoteStatus] = mapped_column(default=QuoteStatus.pending, nullable=False)
    premium_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="GBP", nullable=False)
    coverage_summary: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

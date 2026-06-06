import uuid
from typing import Any
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from app.models.mixins import UUIDMixin, TimestampMixin
from app.models.enums import CollectionStatus, ProductType


class PolicyCreationState(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "policy_creation_states"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    thread_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("chat_threads.id"), nullable=False)
    product_type: Mapped[ProductType] = mapped_column(nullable=False)
    status: Mapped[CollectionStatus] = mapped_column(default=CollectionStatus.collecting, nullable=False)
    collected_data: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    field_attempts: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    current_field: Mapped[str | None] = mapped_column(String(100))

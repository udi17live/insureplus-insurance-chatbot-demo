import uuid
from typing import Any
from sqlalchemy import Boolean, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from app.models.mixins import UUIDMixin, CreatedAtMixin
from app.models.enums import ResolutionStatus, RevenuePotential, SentimentType


class ConversationAnalytics(UUIDMixin, CreatedAtMixin, Base):
    __tablename__ = "conversation_analytics"
    __table_args__ = (UniqueConstraint("thread_id"),)

    thread_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("chat_threads.id"), nullable=False)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    resolution_status: Mapped[ResolutionStatus | None] = mapped_column(nullable=True)
    sentiment: Mapped[SentimentType | None] = mapped_column(nullable=True)
    product_interests: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    revenue_potential: Mapped[RevenuePotential | None] = mapped_column(nullable=True)
    policy_creation_started: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    policy_creation_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    unresolved_questions: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    topics_discussed: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    turn_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    raw_analysis: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

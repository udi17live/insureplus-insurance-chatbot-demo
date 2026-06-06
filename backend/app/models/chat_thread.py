import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from app.models.mixins import UUIDMixin, TimestampMixin
from app.models.enums import ProductType, ThreadStatus


class ChatThread(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "chat_threads"

    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    foundry_thread_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    title: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[ThreadStatus] = mapped_column(default=ThreadStatus.active, nullable=False)
    product_interest: Mapped[ProductType | None] = mapped_column(nullable=True)
    total_tokens_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    context_summary: Mapped[str | None] = mapped_column(Text)
    last_message_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

import uuid
from datetime import datetime
from pydantic import BaseModel
from app.models.enums import ProductType, ThreadStatus


class ChatMessageRequest(BaseModel):
    message: str
    thread_id: uuid.UUID | None = None


class ThreadOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    foundry_thread_id: str
    title: str | None
    status: ThreadStatus
    product_interest: ProductType | None
    total_tokens_used: int
    last_message_at: datetime | None
    created_at: datetime
    updated_at: datetime


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    created_at: int

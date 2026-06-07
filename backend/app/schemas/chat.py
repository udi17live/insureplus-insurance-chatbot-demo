import uuid
from datetime import datetime
from pydantic import BaseModel
from app.models.enums import ProductType, ThreadStatus


class ChatMessageRequest(BaseModel):
    message: str
    session_id: uuid.UUID | None = None


class SessionOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    last_response_id: str | None
    title: str | None
    status: ThreadStatus
    product_interest: ProductType | None
    total_tokens_used: int
    last_message_at: datetime | None
    created_at: datetime
    updated_at: datetime

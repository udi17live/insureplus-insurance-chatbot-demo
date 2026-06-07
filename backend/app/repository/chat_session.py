import uuid
from sqlalchemy import select
from app.models.chat_session import ChatSession
from app.models.enums import ThreadStatus
from app.repository.base import BaseRepository


class ChatSessionRepository(BaseRepository[ChatSession]):
    model = ChatSession

    async def get_active_by_user(self, user_id: uuid.UUID) -> list[ChatSession]:
        result = await self.db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == user_id, ChatSession.status == ThreadStatus.active)
            .order_by(ChatSession.last_message_at.desc())
        )
        return list(result.scalars().all())

    async def get_all_by_user(self, user_id: uuid.UUID, limit: int = 50, offset: int = 0) -> list[ChatSession]:
        result = await self.db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(ChatSession.last_message_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

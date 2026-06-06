import uuid
from sqlalchemy import select
from app.models.chat_thread import ChatThread
from app.models.enums import ThreadStatus
from app.repository.base import BaseRepository


class ChatThreadRepository(BaseRepository[ChatThread]):
    model = ChatThread

    async def get_by_foundry_thread_id(self, foundry_thread_id: str) -> ChatThread | None:
        result = await self.db.execute(
            select(ChatThread).where(ChatThread.foundry_thread_id == foundry_thread_id)
        )
        return result.scalar_one_or_none()

    async def get_active_by_user(self, user_id: uuid.UUID) -> list[ChatThread]:
        result = await self.db.execute(
            select(ChatThread)
            .where(ChatThread.user_id == user_id, ChatThread.status == ThreadStatus.active)
            .order_by(ChatThread.last_message_at.desc())
        )
        return list(result.scalars().all())

    async def get_all_by_user(self, user_id: uuid.UUID, limit: int = 50, offset: int = 0) -> list[ChatThread]:
        result = await self.db.execute(
            select(ChatThread)
            .where(ChatThread.user_id == user_id)
            .order_by(ChatThread.last_message_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

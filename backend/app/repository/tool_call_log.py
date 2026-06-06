import uuid
from sqlalchemy import select
from app.repository.base import BaseRepository
from app.models.tool_call_log import ToolCallLog


class ToolCallLogRepository(BaseRepository[ToolCallLog]):
    model = ToolCallLog

    async def get_by_thread(self, thread_id: uuid.UUID) -> list[ToolCallLog]:
        result = await self.db.execute(
            select(ToolCallLog)
            .where(ToolCallLog.thread_id == thread_id)
            .order_by(ToolCallLog.created_at)
        )
        return list(result.scalars().all())

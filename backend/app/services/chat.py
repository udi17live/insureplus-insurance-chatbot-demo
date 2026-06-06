import uuid
from datetime import datetime, timezone
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.azure_ai import get_ai_client
from app.core.config import settings
from app.repository.chat_thread import ChatThreadRepository


class ChatService:
    def __init__(self, db: AsyncSession) -> None:
        self.thread_repo = ChatThreadRepository(db)

    async def _get_or_create_thread(
        self,
        thread_id: uuid.UUID | None,
        user_id: uuid.UUID | None,
    ):
        if thread_id:
            thread = await self.thread_repo.get_by_id(thread_id)
            if thread and (thread.user_id is None or thread.user_id == user_id):
                return thread

        async with get_ai_client() as client:
            foundry_thread = await client.agents.threads.create()

        return await self.thread_repo.create(
            user_id=user_id,
            foundry_thread_id=foundry_thread.id,
            last_message_at=datetime.now(timezone.utc),
        )

    async def stream_response(
        self,
        message: str,
        thread_id: uuid.UUID | None,
        user_id: uuid.UUID | None,
    ) -> AsyncIterator[str]:
        thread = await self._get_or_create_thread(thread_id, user_id)

        async with get_ai_client() as client:
            await client.agents.messages.create(
                thread_id=thread.foundry_thread_id,
                role="user",
                content=message,
            )

            total_tokens = 0

            async with client.agents.runs.stream(
                thread_id=thread.foundry_thread_id,
                agent_id=settings.primary_agent_id,
                max_prompt_tokens=settings.agent_max_prompt_tokens,
                max_completion_tokens=settings.agent_max_completion_tokens,
            ) as stream:
                async for event_type, event_data, _ in stream:
                    if event_type == "thread.message.delta":
                        for block in event_data.delta.content or []:
                            if hasattr(block, "text") and block.text:
                                yield f"data: {block.text.value}\n\n"

                    elif event_type == "thread.run.completed":
                        usage = getattr(event_data, "usage", None)
                        if usage:
                            total_tokens = usage.total_tokens

        await self.thread_repo.update(
            thread,
            last_message_at=datetime.now(timezone.utc),
            total_tokens_used=thread.total_tokens_used + total_tokens,
        )

        yield "data: [DONE]\n\n"

    async def list_threads(self, user_id: uuid.UUID) -> list:
        return await self.thread_repo.get_all_by_user(user_id)

    async def get_thread_messages(self, thread_id: uuid.UUID, user_id: uuid.UUID) -> list:
        thread = await self.thread_repo.get_by_id(thread_id)
        if not thread or thread.user_id != user_id:
            return []

        async with get_ai_client() as client:
            messages_page = await client.agents.messages.list(
                thread_id=thread.foundry_thread_id,
                order="asc",
            )

        result = []
        async for msg in messages_page:
            content = ""
            for block in msg.content or []:
                if hasattr(block, "text") and block.text:
                    content += block.text.value
            result.append({
                "id": msg.id,
                "role": msg.role,
                "content": content,
                "created_at": msg.created_at,
            })
        return result

import re
import uuid
from datetime import datetime, timezone
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.azure_ai import make_project_client
from app.core.config import settings
from app.repository.chat_thread import ChatThreadRepository

_CITATION_RE = re.compile(r"【[^】]*】")


def _strip_citations(text: str) -> str:
    return _CITATION_RE.sub("", text)


class ChatService:
    def __init__(self, db: AsyncSession) -> None:
        self.thread_repo = ChatThreadRepository(db)

    async def stream_response(
        self,
        message: str,
        thread_id: uuid.UUID | None,
        user_id: uuid.UUID | None,
    ) -> AsyncIterator[str]:
        thread = None
        previous_response_id = None

        if thread_id:
            thread = await self.thread_repo.get_by_id(thread_id)
            if thread and (thread.user_id is None or thread.user_id == user_id):
                previous_response_id = thread.foundry_thread_id
            else:
                thread = None

        async with make_project_client() as project_client:
            openai_client = project_client.get_openai_client(
                agent_name=settings.primary_agent_id
            )

            extra: dict = {
                "max_output_tokens": settings.agent_max_completion_tokens,
            }
            if previous_response_id:
                extra["previous_response_id"] = previous_response_id

            async with openai_client.responses.stream(
                model=settings.primary_agent_model,
                input=message,
                extra_body=extra,
            ) as stream:
                last_response_id = None
                async for event in stream:
                    if event.type == "response.output_text.delta":
                        delta = _strip_citations(event.delta)
                        if delta:
                            yield f"data: {delta}\n\n"
                    elif event.type == "response.completed":
                        last_response_id = event.response.id

        if last_response_id:
            now = datetime.now(timezone.utc)
            if thread:
                thread = await self.thread_repo.update(
                    thread,
                    foundry_thread_id=last_response_id,
                    last_message_at=now,
                )
            else:
                thread = await self.thread_repo.create(
                    user_id=user_id,
                    foundry_thread_id=last_response_id,
                    last_message_at=now,
                )

            yield f"event: thread\ndata: {thread.id}\n\n"

        yield "data: [DONE]\n\n"

    async def list_threads(self, user_id: uuid.UUID) -> list:
        return await self.thread_repo.get_all_by_user(user_id)

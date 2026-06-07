import asyncio
import json
import re
import uuid
from datetime import datetime, timezone
from typing import AsyncIterator

from openai import APIError
from sqlalchemy.ext.asyncio import AsyncSession

from loguru import logger
from app.core.azure_ai import make_openai_client
from app.core.config import settings
from app.repository.chat_session import ChatSessionRepository

_CITATION_RE = re.compile(r"【[^】]*】")

_KNOWN_TOOLS = {
    "agent_create_quote",
    "agent_confirm_payment",
    "agent_list_policies",
    "agent_cancel_policy",
}


def _strip_citations(text: str) -> str:
    return _CITATION_RE.sub("", text)


class ChatService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.session_repo = ChatSessionRepository(db)

    async def stream_response(
        self,
        message: str,
        session_id: uuid.UUID | None,
        user_id: uuid.UUID | None,
    ) -> AsyncIterator[str]:
        session = None
        previous_response_id = None

        if session_id:
            session = await self.session_repo.get_by_id(session_id)
            if session and (session.user_id is None or session.user_id == user_id):
                previous_response_id = session.last_response_id
                if session.user_id is None and user_id is not None:
                    session = await self.session_repo.update(session, user_id=user_id)
                    await self.db.commit()
                    await self.db.refresh(session)
            else:
                session = None

        # Create session upfront if authenticated and none exists yet — the agent needs
        # the session_id in additional_instructions so it can pass it to tool calls.
        if session is None and user_id is not None:
            now = datetime.now(timezone.utc)
            session = await self.session_repo.create(
                user_id=user_id,
                last_response_id=None,
                last_message_at=now,
            )
            # Commit immediately so the session row is visible to tool calls that
            # arrive mid-stream on a separate DB connection.
            await self.db.commit()
            await self.db.refresh(session)

        openai_client = make_openai_client()
        new_response_id = None

        extra_body: dict = {"agent_reference": settings.agent_reference}
        if previous_response_id:
            extra_body["previous_response_id"] = previous_response_id

        try:
            loop = asyncio.get_event_loop()
            queue: asyncio.Queue = asyncio.Queue()

            session_context = (
                f'[SYSTEM: session_id="{session.id}" — pass this as session_id in every tool call]\n\n'
                if session else ""
            )

            def _run_stream():
                try:
                    stream = openai_client.responses.create(
                        input=f"{session_context}{message}",
                        extra_body=extra_body,
                        max_output_tokens=settings.agent_max_completion_tokens,
                        store=True,
                        stream=True,
                    )
                    for event in stream:
                        loop.call_soon_threadsafe(queue.put_nowait, event)
                except Exception as exc:
                    loop.call_soon_threadsafe(queue.put_nowait, exc)
                finally:
                    loop.call_soon_threadsafe(queue.put_nowait, None)

            asyncio.get_event_loop().run_in_executor(None, _run_stream)

            while True:
                event = await queue.get()
                if event is None:
                    break
                if isinstance(event, Exception):
                    raise event

                event_type = getattr(event, "type", "")

                if event_type == "response.output_text.delta":
                    delta = _strip_citations(getattr(event, "delta", ""))
                    if delta:
                        yield f"data: {delta}\n\n"

                elif event_type == "response.completed":
                    response = getattr(event, "response", None)
                    if response:
                        new_response_id = response.id
                        output_items = getattr(response, "output", [])
                        for item in output_items:
                            item_type = getattr(item, "type", "")
                            if item_type == "openapi_call_output":
                                raw_name = getattr(item, "name", "") or ""
                                tool_name = next((t for t in _KNOWN_TOOLS if raw_name.startswith(t)), raw_name)
                                raw_output = getattr(item, "output", None)
                                try:
                                    result = json.loads(raw_output) if isinstance(raw_output, str) else raw_output
                                    yield f"event: tool_result\ndata: {json.dumps({'tool': tool_name, 'result': result})}\n\n"
                                except Exception as exc:
                                    logger.warning("Failed to parse tool output for {}: {}", tool_name, exc)

                elif event_type == "error":
                    err = getattr(event, "error", {}) or {}
                    msg = err.get("message", "") if isinstance(err, dict) else str(err)
                    logger.warning("Stream error event: {}", msg)
                    if "401" in msg or "Unauthorized" in msg or "authenticated user" in msg:
                        yield "event: auth_required\ndata: {}\n\n"
                        return
                    yield f"data: Sorry, something went wrong: {msg[:200]}\n\n"
                    return

                elif event_type == "response.failed":
                    return

        except APIError as exc:
            body = str(exc)
            if "401" in body or "Unauthorized" in body or "requires an authenticated user" in body:
                yield "event: auth_required\ndata: {}\n\n"
            else:
                yield f"data: Sorry, something went wrong: {body[:200]}\n\n"
            return
        except Exception as exc:
            yield f"data: Unexpected error: {str(exc)[:200]}\n\n"
            return

        if new_response_id:
            now = datetime.now(timezone.utc)
            if session:
                update_kwargs: dict = {
                    "last_response_id": new_response_id,
                    "last_message_at": now,
                }
                if session.user_id is None and user_id is not None:
                    update_kwargs["user_id"] = user_id
                session = await self.session_repo.update(session, **update_kwargs)
            else:
                session = await self.session_repo.create(
                    user_id=user_id,
                    last_response_id=new_response_id,
                    last_message_at=now,
                )

            yield f"event: thread\ndata: {session.id}\n\n"

        yield "data: [DONE]\n\n"

    async def list_sessions(self, user_id: uuid.UUID) -> list:
        return await self.session_repo.get_all_by_user(user_id)

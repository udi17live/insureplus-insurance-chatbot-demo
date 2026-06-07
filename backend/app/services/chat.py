import json
import logging
import re
import uuid
from datetime import datetime, timezone
from typing import AsyncIterator

from openai import APIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.azure_ai import make_project_client
from app.core.config import settings
from app.repository.chat_thread import ChatThreadRepository

_CITATION_RE = re.compile(r"【[^】]*】")
_log = logging.getLogger(__name__)

_KNOWN_TOOLS = {
    "agent_create_quote",
    "agent_confirm_payment",
    "agent_list_policies",
    "agent_cancel_policy",
}


def _strip_citations(text: str) -> str:
    return _CITATION_RE.sub("", text)


def _normalise_tool_name(raw: str) -> str:
    """Azure sometimes doubles the suffix: 'agent_create_quote_agent_create_quote' → 'agent_create_quote'."""
    for name in _KNOWN_TOOLS:
        if raw == name or raw.startswith(name + "_"):
            return name
    return raw


class ChatService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
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
                # Attach user to anonymous thread immediately so tool calls can resolve the user.
                if thread.user_id is None and user_id is not None:
                    thread = await self.thread_repo.update(thread, user_id=user_id)
            else:
                thread = None

        # Append thread_id so the model can always pass it to tool calls.
        if thread_id:
            input_payload: object = f"{message}\n\n[thread_id: {thread_id}]"
        else:
            input_payload = message

        async with make_project_client() as project_client:
            openai_client = project_client.get_openai_client(
                agent_name=settings.primary_agent_id
            )

            extra: dict = {"max_output_tokens": settings.agent_max_completion_tokens}
            if previous_response_id:
                extra["previous_response_id"] = previous_response_id

            last_response_id = None

            try:
                async with openai_client.responses.stream(
                    model=settings.primary_agent_model,
                    input=input_payload,
                    extra_body=extra,
                ) as stream:
                    # Iterate raw SSE events from the underlying stream so that
                    # Azure-specific events (e.g. openapi_call_output) are not
                    # silently dropped by the typed openai SDK iterator.
                    async for sse in stream._raw_stream._iter_events():
                        event_type = sse.event or ""
                        raw_data = sse.data or ""

                        if raw_data == "[DONE]":
                            break

                        if not raw_data:
                            continue

                        try:
                            payload = json.loads(raw_data)
                        except json.JSONDecodeError:
                            continue

                        payload_type = payload.get("type", "")
                        _log.info("[CHAT] sse type=%r event=%r", payload_type, event_type)

                        # Text delta
                        if payload.get("type") == "response.output_text.delta":
                            delta = _strip_citations(payload.get("delta", ""))
                            if delta:
                                yield f"data: {delta}\n\n"

                        # Response completed — capture ID for thread persistence
                        elif payload.get("type") == "response.completed":
                            last_response_id = payload.get("response", {}).get("id")
                            _log.debug("[CHAT] response.completed id=%s", last_response_id)

                        # Tool call returned 401 — user not authenticated, prompt login
                        elif payload.get("type") == "error":
                            err = payload.get("error", {})
                            msg = err.get("message", "")
                            if "401" in msg or "Unauthorized" in msg or "authenticated user" in msg:
                                yield "event: auth_required\ndata: {}\n\n"
                                return
                            yield f"data: Sorry, something went wrong: {msg[:200]}\n\n"
                            return

                        elif payload.get("type") == "response.failed":
                            # Already handled via the error event above; just stop streaming.
                            return

                        # Azure Foundry OpenAPI tool call output
                        elif payload.get("type") == "openapi_call_output":
                            raw_name = payload.get("name", "") or ""
                            tool_name = _normalise_tool_name(raw_name)
                            output = payload.get("output")

                            _log.info("[CHAT] openapi_call_output tool=%s", tool_name)

                            if tool_name in _KNOWN_TOOLS and output is not None:
                                try:
                                    result = json.loads(output) if isinstance(output, str) else output
                                    yield f"event: tool_result\ndata: {json.dumps({'tool': tool_name, 'result': result})}\n\n"
                                except Exception as exc:
                                    _log.warning("[CHAT] Failed to parse tool output for %s: %s", tool_name, exc)

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

        if last_response_id:
            now = datetime.now(timezone.utc)
            if thread:
                update_kwargs: dict = {
                    "foundry_thread_id": last_response_id,
                    "last_message_at": now,
                }
                if thread.user_id is None and user_id is not None:
                    update_kwargs["user_id"] = user_id
                thread = await self.thread_repo.update(thread, **update_kwargs)
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

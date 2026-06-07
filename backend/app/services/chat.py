import json
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

_KNOWN_TOOLS = {"agent_list_policies", "agent_create_quote", "agent_cancel_policy"}


def _strip_citations(text: str) -> str:
    return _CITATION_RE.sub("", text)


def _normalise_tool_name(raw: str) -> str:
    """Azure OpenAPI tools produce names like 'agent_create_quote_agent_create_quote'.
    Strip the doubled suffix to get the canonical tool name."""
    for tool in _KNOWN_TOOLS:
        if raw.startswith(tool):
            return tool
    return raw


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

            # Append thread_id to every user message as a hidden context line.
            # This ensures the agent always has it available when calling tools,
            # even on continuation turns where a system message is not allowed.
            if thread_id:
                input_payload = f"{message}\n\n[thread_id: {thread_id}]"
            else:
                input_payload = message

            async with openai_client.responses.stream(
                model=settings.primary_agent_model,
                input=input_payload,
                extra_body=extra,
            ) as stream:
                last_response_id = None
                _call_id_to_name: dict[str, str] = {}
                try:
                    async for event in stream:
                        if event.type == "response.output_text.delta":
                            delta = _strip_citations(event.delta)
                            if delta:
                                yield f"data: {delta}\n\n"
                        elif event.type == "response.output_item.done":
                            item = event.item
                            item_type = getattr(item, "type", None)
                            # Handle both function_call_output (direct) and openapi_call_output (Azure OpenAPI tools)
                            if item_type in ("function_call_output", "openapi_call_output"):
                                output = getattr(item, "output", "") or ""
                                print(f"[CHAT] raw output={output[:500]}", flush=True)
                                if "requires an authenticated user" in output or '"status_code":401' in output or '"status":401' in output:
                                    yield "event: auth_required\ndata: {}\n\n"
                                else:
                                    try:
                                        payload = json.loads(output)
                                        # Azure wraps the HTTP response body: {"response": "{...}"}
                                        if isinstance(payload, dict) and "response" in payload and isinstance(payload["response"], str):
                                            payload = json.loads(payload["response"])
                                        raw_name = getattr(item, "name", None) or _call_id_to_name.get(getattr(item, "call_id", ""), "")
                                        # Azure doubles the operation name: "agent_create_quote_agent_create_quote" → "agent_create_quote"
                                        tool_name = _normalise_tool_name(raw_name)
                                        yield f"event: tool_result\ndata: {json.dumps({'tool': tool_name, 'result': payload})}\n\n"
                                    except (json.JSONDecodeError, AttributeError):
                                        pass
                            elif item_type in ("function_call", "openapi_call"):
                                _call_id_to_name[getattr(item, "call_id", "")] = getattr(item, "name", "")
                        elif event.type == "response.completed":
                            last_response_id = event.response.id
                except APIError as exc:
                    body = str(exc)
                    if "401" in body or "Unauthorized" in body or "requires an authenticated user" in body:
                        yield "event: auth_required\ndata: {}\n\n"

        if last_response_id:
            now = datetime.now(timezone.utc)
            if thread:
                update_kwargs: dict = {
                    "foundry_thread_id": last_response_id,
                    "last_message_at": now,
                }
                # Claim the thread for the logged-in user if it was anonymous.
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

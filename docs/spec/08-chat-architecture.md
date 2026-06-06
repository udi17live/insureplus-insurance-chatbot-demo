# 08 — Chat Architecture

## End-to-End Flow
```
Browser → POST /api/chat/message (Next.js route handler)
  → Next.js reads JWT from HttpOnly cookie
  → Forwards to FastAPI with Authorization: Bearer <token>
  → FastAPI validates JWT, rate limits, resolves thread
  → Creates streaming AI Foundry Agent run
  → Returns StreamingResponse (text/event-stream)
  → Next.js pipes stream back to browser
  → Browser reads tokens via fetch ReadableStream
```

## Why Next.js Proxies the Stream
JWT is in an HttpOnly cookie — browser JS cannot read it. Next.js server-side route handler reads the cookie and forwards as Bearer token to FastAPI. This keeps auth secure and enables clean stream proxying.

## SSE Event Protocol
```
event: token          data: {"content": "Your motor insurance"}
event: tool_start     data: {"tool": "search_knowledge_base", "label": "Searching..."}
event: tool_end       data: {"tool": "search_knowledge_base"}
event: auth_required  data: {"message": "Please log in to continue", "action": "login"}
event: state_update   data: {"status": "payment_pending", "client_secret": "pi_xxx"}
event: message_complete data: {"thread_id": "uuid", "tokens_used": 312}
event: error          data: {"code": "stream_error", "message": "..."}
event: heartbeat      data: {}
```

## Key FastAPI Implementation Points
```python
return StreamingResponse(
    stream_agent_response(request, user, db),
    media_type="text/event-stream",
    headers={
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",   # Disables Nginx buffering — critical
        "Connection": "keep-alive",
    }
)
```

## Thread Resolution
```python
async def resolve_thread(thread_id, user, db):
    if thread_id:
        # Fetch existing — validate user owns it
        return thread.foundry_thread_id
    # Create new Foundry thread + chat_threads DB record
    return new_foundry_thread.id
```

## Context Injection Per Run
User identity and state injected as `additional_instructions` — not in the system prompt:
```python
await client.agents.runs.stream(
    thread_id=foundry_thread_id,
    agent_id=settings.PRIMARY_AGENT_ID,
    max_prompt_tokens=4000,
    max_completion_tokens=600,
    truncation_strategy={"type": "last_messages", "last_messages": 10},
    additional_instructions=build_context_injection(user, thread),
)
```

## Client-Side Stream Handling
`EventSource` cannot be used (POST requests only). Use `fetch` with `ReadableStream`:
```typescript
const response = await fetch('/api/chat/message', { method: 'POST', body: ... })
const reader = response.body.getReader()
// Parse SSE lines from buffer, dispatch by event type
```

## Heartbeat
Server sends `heartbeat` event every 15 seconds — prevents proxy/load balancer from dropping idle SSE connections during long tool calls.

## Rate Limiting in SSE Context
On rate limit exceeded, return SSE `error` event (not HTTP 429) so the stream handler renders it as a chat message rather than a broken connection.

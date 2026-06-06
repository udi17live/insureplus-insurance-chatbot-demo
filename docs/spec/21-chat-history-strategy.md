# 21 — Chat History Strategy

## Storage Split
- **Our DB (`chat_threads`):** Thread metadata only — title, status, product_interest, last_message_at, total_tokens_used, context_summary
- **AI Foundry:** All message content — source of truth. Retrieved on demand via `foundry_thread_id`

No message duplication. Foundry is optimised for this.

## Thread List (Sidebar)
```python
GET /chat/threads
→ Returns chat_threads ordered by last_message_at DESC
→ Paginated (default limit: 20)
→ Fields: id, title, status, product_interest, last_message_at
```

## Message Retrieval
```python
GET /chat/{thread_id}/messages
→ Validates thread belongs to current user
→ Fetches from Foundry: client.agents.messages.list(thread_id=foundry_thread_id)
→ Filters out [SYSTEM VERIFIED] messages (internal payment confirmations)
→ Paginated via Foundry's before/limit parameters
```

## Filtering Internal Messages
```python
def is_system_message(msg) -> bool:
    if msg.role != "user": return False
    content = extract_text_content(msg)
    return content.startswith("[SYSTEM VERIFIED")
```
These webhook-injected messages must never appear in user-facing chat history.

## Thread Title Generation
```python
# LLM-based (recommended) — ~30 tokens, ~$0.000005 per title
# "I'm looking for motor insurance for my Ford Focus"
# → "Motor Insurance for Ford Focus"

response = await openai_client.chat.completions.create(
    model=settings.OPENAI_DEPLOYMENT,
    max_tokens=15, temperature=0,
    messages=[
        {"role": "system", "content": "Generate a 4-6 word title. Return title only."},
        {"role": "user", "content": first_message}
    ]
)
```
Set on first message of each thread. Fallback: truncate to 50 chars.

## New Chat vs Resume
- **New chat:** No `thread_id` sent → backend creates new Foundry thread + DB record
- **Resume:** `thread_id` sent → backend resolves `foundry_thread_id` → agent continues in same thread
- Long-term Memory Store injected on both new and resumed sessions

## Graceful Degradation
If Foundry thread unavailable (service issue):
- Thread list still renders (from our DB)
- Opening thread shows: "Message history temporarily unavailable"
- New messages still work — new thread created

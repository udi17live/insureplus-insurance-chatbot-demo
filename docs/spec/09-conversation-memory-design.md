# 09 — Conversation Memory Design

## Two-Tier Memory Architecture

### Tier 1 — Thread Memory (Within-Session)
AI Foundry stores all messages natively per thread. We control what reaches the model via run parameters:
```python
max_prompt_tokens=4000,
max_completion_tokens=600,
truncation_strategy={"type": "last_messages", "last_messages": 10}
```
This caps context at 4,000 tokens regardless of thread length. Oldest messages dropped first when cap is hit.

**Problem:** Dropping early messages loses critical context ("User said they have a van" in turn 1).  
**Solution:** Rolling summary injected as `additional_instructions`.

### Tier 2 — Long-Term Memory Store (Cross-Session)
AI Foundry Memory Store (Preview) — managed, per-user, scoped by UUID:
```python
options = MemoryStoreDefaultOptions(
    chat_summary_enabled=True,
    user_profile_enabled=True,
    user_profile_details="Extract: insurance interests, vehicles mentioned, coverage preferences."
)
```
Automatically extracts user profile and chat summaries. Uses hybrid search to retrieve relevant memories at session start. Injected as `additional_instructions` prefix.

## Rolling Summary Strategy
Triggered when thread message count hits threshold (default: 15 turns):
1. Fetch messages from Foundry (all except last 5 turns)
2. Direct OpenAI call — 300 token summary of earlier conversation
3. Store in `chat_threads.context_summary`
4. Injected on every subsequent run in that thread

This is a background task — never blocks the user's response.

## Context Injection Structure
```
User: John Smith (ID: uuid-xxx)

Earlier in this conversation:
"User has a Ford Focus, interested in comprehensive motor. Quote given £45/mo"

From previous sessions:
- Previously got motor quote
- Expressed interest in breakdown cover
```

## Fallback — PostgreSQL Summary Injection
If Memory Store is unavailable (preview instability), fetch last 3 conversation summaries from `chat_threads.context_summary` and inject directly. Zero additional infrastructure required.

## Guest Memory
- No Memory Store (no UUID to scope with)
- Thread memory works within session only
- On logout: thread not persisted to DB
- On guest-to-auth: current thread reassigned to user.id, Memory Store updates from this point forward

## Token Budget Summary
| Component | Max Tokens |
|-----------|-----------|
| System prompt | 800 |
| Context injection (user + rolling summary) | 500 |
| Long-term memory | 300 |
| RAG chunks | 1,500 |
| Last 10 messages | 1,500 |
| **Hard cap (max_prompt_tokens)** | **4,000** |

## Production Note
Memory Store is in public preview. Always implement the PostgreSQL fallback. Monitor preview pricing before committing to production.

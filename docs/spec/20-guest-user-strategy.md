# 20 — Guest User Strategy

## Overview
Guests can chat freely and get RAG-backed answers. Any action requiring user data triggers an inline auth prompt — no hard redirect.

## Session Identification
```typescript
// Frontend — on first visit
const sessionId = crypto.randomUUID()
sessionStorage.setItem('guest_session_id', sessionId)

// Sent on every guest chat request
headers: { 'X-Session-ID': sessionId }
```
Session lives in `sessionStorage` — cleared on tab close. Never persisted server-side.

## Auth-Required Tool Pattern
When agent calls a tool requiring authentication and `user` is `None`:
```python
async def execute_tool(tool_name, arguments, user, db):
    if not user:
        return {"auth_required": True, "message": "Login required"}
```
Agent receives this response and streams:
```
"To do that I'll need you to log in first.
 [Login] [Register]"
```
This is the **only** change in guest vs authenticated behaviour. The chat interface, streaming, and RAG all work identically.

## Guest-to-Auth Context Continuity
1. User triggers auth-required action
2. Frontend stores current messages in `sessionStorage.pendingMessages`
3. User registers/logs in → JWT set in HttpOnly cookie
4. Frontend checks `pendingMessages` on return
5. If found: sends thread restore request to create authenticated thread with guest context prepended
6. `pendingMessages` cleared from sessionStorage

## What Is and Isn't Persisted for Guests
| Data | Guest | Authenticated |
|------|-------|--------------|
| Chat messages | In-memory (React state) only | Foundry thread |
| Thread metadata | Not stored | chat_threads table |
| Policy creation state | Not allowed | policy_creation_states table |
| Long-term memory | Not applicable | Memory Store |

## Rate Limiting
Guests rate limited by IP (20 messages/hour). More restrictive than authenticated users to prevent abuse without requiring login.

## No Analytics for Guests
Analytics agent not triggered for guest sessions — no user_id to associate insights with. Short guest sessions below 3 turns are skipped entirely.

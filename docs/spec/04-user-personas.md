# 04 — User Personas

## Persona 1 — Guest User
- No account, no JWT
- Identified by session ID (client-generated UUID, stored in sessionStorage)
- Full access to AI Q&A and RAG responses
- Blocked from any tool that reads/writes user data
- On auth-required tool: receives inline login prompt in chat stream
- Rate limited by IP
- No server-side chat history persisted

## Persona 2 — Authenticated User
- JWT-authenticated on every request
- Full access to all tools including policy creation and payment
- Chat threads persisted and linked to user UUID
- Cross-session memory via AI Foundry Memory Store
- Rate limited by user ID
- Sub-types handled by agent logic (not separate personas):
  - New user → full policy creation flow
  - Returning user → agent has memory context from prior sessions
  - Incomplete flow → agent detects and offers to restart

## Persona 3 — Platform Viewer (Analytics)
- Same JWT auth as authenticated user
- No dedicated role or separate auth — showcase only
- Access to `GET /analytics/conversations` endpoint
- Read-only view of conversation analytics table
- Demonstrates Analytics Agent output during presentation

## Permission Matrix
| Capability | Guest | Auth User | Platform Viewer |
|-----------|-------|-----------|-----------------|
| AI Q&A chat | ✅ | ✅ | ❌ |
| Policy creation | ❌ (prompt login) | ✅ | ❌ |
| View own policies | ❌ | ✅ | ❌ |
| View chat history | ❌ | ✅ | ❌ |
| Make payment | ❌ | ✅ | ❌ |
| Receive email | ❌ | ✅ | ❌ |
| View analytics | ❌ | ❌ | ✅ |
| Cross-session memory | ❌ | ✅ | ❌ |

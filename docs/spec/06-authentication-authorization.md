# 06 — Authentication & Authorization

## Overview
Simple JWT auth — email + password. No external IdP. JWT stored in HttpOnly cookie set by Next.js server route handler.

## Token Design
```json
{
  "sub": "uuid-user-id",
  "email": "user@example.com",
  "type": "access",
  "iat": 1700000000,
  "exp": 1700003600
}
```
- **Algorithm:** HS256
- **Expiry:** 60 minutes
- **Storage:** HttpOnly cookie — set server-side by Next.js, never accessible to client JS
- **Refresh tokens:** Not implemented (showcase)

## Cookie Flow
```
Browser POST /api/auth/login (Next.js route)
  → Next.js calls FastAPI /auth/login
  → Receives { access_token }
  → Sets HttpOnly cookie:
     cookies().set('access_token', token, {
       httpOnly: true, secure: true, sameSite: 'strict', maxAge: 3600
     })
  → Returns user profile to client
```

## API Endpoints
```
POST /auth/register  →  { email, password, full_name }  →  { access_token, user }
POST /auth/login     →  { email, password }              →  { access_token, user }
POST /auth/logout    →  Next.js clears cookie (no FastAPI call needed)
```

## FastAPI Dependencies
```python
get_current_user()    # Validates JWT cookie → returns User or raises 401
get_optional_user()   # Returns User if valid JWT, None if guest — no error
```
`get_optional_user` is used exclusively on `POST /chat/message` to support both guest and authenticated access.

## Route Protection
| Route | Auth Required |
|-------|--------------|
| POST /auth/register | ❌ |
| POST /auth/login | ❌ |
| POST /chat/message | ❌ (optional — guest or auth) |
| GET /chat/threads | ✅ |
| GET /policies | ✅ |
| POST /webhooks/stripe | Stripe signature only |

**Most data access happens through agent tools — not direct REST routes.**

## User UUID Flow
```
JWT → sub: user_uuid
         ├── AI Foundry Memory Store scope
         ├── Chat thread ownership
         ├── Policy records (user_id FK)
         ├── Tool call context (injected server-side)
         └── Analytics records
```
The UUID is the single identifier connecting all system data. It is **always extracted from the JWT** — never accepted as a parameter from the agent.

## DB Schema
```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name       VARCHAR(255),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```
Password hashed with bcrypt (cost factor 12).

## Production Upgrades
| Showcase | Production |
|----------|-----------|
| HS256 + env var secret | RS256 + Azure Key Vault |
| 60min expiry, no refresh | 15min access + 7-day rotating refresh token |
| localStorage fallback avoided | Full HttpOnly cookie refresh rotation |
| Custom JWT | Azure Entra External ID or Auth0 |

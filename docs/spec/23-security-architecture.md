# 23 — Security Architecture

## Threat Model
| Threat | Mitigation |
|--------|-----------|
| Prompt injection | Multi-layer: system prompt rules + user_id from JWT (not agent) |
| Data access bypass | user_id always from JWT — agent cannot influence which user's data is accessed |
| JWT forgery | HS256 with strong secret, algorithm explicitly validated |
| Webhook spoofing | Stripe signature verified before processing |
| Secret exposure | Environment variables, never in code or logs |
| Rate limit bypass | slowapi per-IP and per-user limits |
| Tool parameter injection | user_id injected server-side — never accepted from agent arguments |

## Prompt Injection Defence (4 Layers)
1. **System prompt framing:** Instructions are permanent, cannot be overridden by user messages
2. **user_id from JWT:** Agent cannot access another user's data even with injected instructions
3. **Input sanitisation:** Messages trimmed to 2,000 chars, control characters stripped
4. **Context separation:** `additional_instructions` is a separate parameter — never concatenated with user message

## Authentication Security
- bcrypt cost factor 12 for password hashing
- JWT algorithm explicitly set (HS256 only — no algorithm confusion attacks)
- `is_active` checked on every authenticated request
- HttpOnly + Secure + SameSite=Strict cookie

## CORS
```python
allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"]
allow_credentials=True
# Never: allow_origins=["*"] with allow_credentials=True
```

## Database Security
- SQLAlchemy parameterised queries everywhere — no string concatenation
- SSL required on all DB connections (`?ssl=require`)
- App DB user: SELECT, INSERT, UPDATE only — no DROP, no schema changes
- Migrations run by separate privileged user

## Input Validation — All Layers
1. Pydantic request models (FastAPI) — invalid types rejected before handler
2. `validate_field()` in tools — type, range, format, enum
3. DB ENUMs and constraints
4. All tool IDs verified against DB + JWT user

## Security Headers
```python
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self';
  script-src 'self' https://js.stripe.com;
  frame-src https://js.stripe.com;
  connect-src 'self' https://api.stripe.com
```
Stripe CSP entries are required — missing them breaks Stripe Elements.

## Rate Limiting
```python
GET /auth/login:      5 attempts / 15 minutes per IP
POST /chat/message:   20/hour (guest IP) / 60/hour (auth user)
POST /auth/register:  3/hour per IP
```

## Secrets Management
| Showcase | Production |
|----------|-----------|
| Environment variables | Azure Key Vault + managed identity |
| HS256 with env var secret | RS256 with Key Vault |
| .env gitignored | No .env file — all from Key Vault |

## Production Security Additions
WAF (Azure Front Door), VNet integration (DB not publicly accessible), DDoS Protection Standard, full refresh token rotation, API keys replaced with managed identity for all Azure services.

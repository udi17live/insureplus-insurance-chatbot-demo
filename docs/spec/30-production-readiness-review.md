# 30 — Production Readiness Review

## What This Showcase Implements (Production-Grade)
✅ JWT auth with HttpOnly cookie via Next.js  
✅ bcrypt password hashing (cost factor 12)  
✅ Parameterised SQL queries (no injection risk)  
✅ Stripe webhook signature verification  
✅ Idempotent payment and policy creation  
✅ State machine enforced at tool level (not just prompt)  
✅ Token budget hard caps (max_prompt_tokens/completion)  
✅ Anti-hallucination — RAG-grounded only, score threshold gate  
✅ Multi-layer prompt injection defence  
✅ Structured logging with correlation IDs  
✅ Graceful degradation on service failures  
✅ Rate limiting (per-IP and per-user)  
✅ SSE streaming with heartbeat keep-alive  
✅ Async analytics agent (non-blocking)  
✅ Rolling conversation summarisation  
✅ Input sanitisation and validation  
✅ Security headers (CSP, HSTS, X-Frame-Options)  
✅ CORS configured with explicit origins  

## Simplified for Showcase (Production Gaps)
| Item | Showcase | Production |
|------|----------|-----------|
| Auth | HS256 JWT, no refresh | RS256, refresh token rotation, Azure Entra |
| Secrets | Environment variables | Azure Key Vault + managed identity |
| DB access | Public endpoint (restricted) | VNet integration, no public access |
| SSE push (webhook) | In-memory queue (single instance) | Redis pub/sub |
| Rate limit storage | In-memory | Redis-backed |
| Thread storage | Microsoft-managed | BYO Cosmos DB |
| Memory Store | Preview API | Stable API (when available) |
| Policy approval | Auto-approved | Human-in-the-loop underwriter review |
| Payments | Sandbox only | Live Stripe + compliance review |
| Monitoring | App Insights basic | Full APM with alerting runbook |
| Deployment | Single region | Multi-region with geo-failover |
| DR | Manual restore | Automated failover, tested quarterly |
| Compliance | None | FCA authorisation, GDPR, ICO registration |

## Pre-Go-Live Checklist (If Productionising)
```
Security:
[ ] Rotate all secrets to Azure Key Vault
[ ] Enable RS256 + refresh token rotation
[ ] VNet integration for PostgreSQL
[ ] Enable Azure WAF on Front Door
[ ] Penetration test agent for prompt injection
[ ] Confirm Azure OpenAI zero-data-retention agreement

Reliability:
[ ] Load test at expected concurrent user count
[ ] Verify circuit breaker behaviour under OpenAI outage
[ ] Test Stripe webhook retry handling
[ ] Confirm Memory Store pricing and SLA

Compliance:
[ ] Legal review of AI-generated insurance quotes
[ ] FCA authorisation or appointed representative status
[ ] GDPR data processing agreements with Azure and Stripe
[ ] Privacy policy and cookie consent
[ ] Define data retention and deletion policy

Operational:
[ ] Alerting runbook documented
[ ] On-call rotation established
[ ] DR runbook tested
[ ] Rollback procedure documented and tested
```

## Key Technical Decisions — Summary
1. **requires_action over OpenAPI Tools** — better security, lower latency, streaming integration
2. **Foundry-managed RAG** — portal setup, no custom search code
3. **Webhook → Agent for policy creation** — consistent architecture, agent owns full flow
4. **State machine in DB** — survives disconnections, enforced at tool level not just prompt
5. **Rolling summary + Memory Store** — token budget controlled, cross-session context maintained
6. **user_id from JWT always** — agent cannot influence which user's data is accessed
7. **Two-tier memory** — thread memory for within-session, Memory Store + PostgreSQL fallback for cross-session
8. **Foundry as message store** — no duplication, messages fetched on demand

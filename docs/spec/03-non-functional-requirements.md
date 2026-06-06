# 03 — Non-Functional Requirements

## Response Latency Targets
| Metric | Target |
|--------|--------|
| Time to first token (TTFT) | < 1,500ms |
| Token render rate | ≥ 30 tokens/second |
| Tool call round-trip | < 3 seconds |
| Auth endpoints | < 500ms |
| Policy list / history | < 800ms |

## Token Budget Per Turn
| Component | Max Tokens |
|-----------|-----------|
| System prompt | 800 |
| Context injection (user + summaries) | 500 |
| Long-term memory injection | 300 |
| RAG chunks (top 3) | 1,500 |
| Conversation history (last 10 msgs) | 1,500 |
| **max_prompt_tokens hard cap** | **4,000** |
| **max_completion_tokens hard cap** | **600** |

Total worst case per turn: ~7,200 tokens at GPT-4o-mini ≈ **$0.001/turn**

## Retry Behaviour
| Scenario | Behaviour |
|----------|-----------|
| Azure OpenAI 429 | Exponential backoff, max 3 retries, then SSE error |
| Azure OpenAI timeout | 30s timeout, single retry, then graceful error |
| AI Search timeout | 10s timeout, fallback "cannot retrieve right now" |
| Stripe failure | Inform user, offer retry, do not create policy |
| ACS email failure | Log and continue — email is non-blocking |

## Session & Token Management
| Setting | Value |
|---------|-------|
| JWT expiry | 60 minutes |
| Storage | HttpOnly cookie (set by Next.js server route) |
| Refresh tokens | Not implemented (showcase) |
| Concurrent sessions | Allowed |
| Guest session | Browser session only, no server persistence |

## Error Handling Standards
- All API errors follow RFC 7807 Problem Detail format
- Stream errors injected as SSE `error` events — never raw HTTP errors in chat context
- Validation errors return field-level detail — no stack traces exposed
- All unhandled exceptions caught by global FastAPI handler

## Logging
- Every API request: method, path, status, latency, user UUID
- Every agent turn: tokens used, tools called, duration
- Every RAG retrieval: chunks returned, top score, threshold passed
- PII never in logs — user UUID only, never email or name

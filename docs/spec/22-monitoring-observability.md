# 22 — Monitoring & Observability

## Stack
- **Azure Application Insights** — operational monitoring (requests, errors, latency, tokens)
- **conversation_analytics table** — business insight from Analytics Agent (not App Insights)

## Correlation ID
Every request gets a UUID correlation ID — traceable across API → agent run → tool calls → DB writes:
```python
class CorrelationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response
```

## What We Log (Structured JSON)
```python
# Every agent turn
{"event": "agent_turn", "correlation_id": "...", "user_id": "uuid",
 "thread_id": "...", "tokens_used": 312, "duration_ms": 1840, "tool_calls": ["search_knowledge_base"]}

# Every tool call
{"event": "tool_call", "tool_name": "create_policy", "success": true, "duration_ms": 230}

# Every RAG retrieval
{"event": "rag_retrieval", "chunks_returned": 3, "top_score": 2.84,
 "passed_threshold": true, "duration_ms": 340}
```

## PII Rules
```
NEVER log: email, full name, policy details, message content, payment info
ALWAYS log: user UUID, thread UUID, correlation ID, event types, token counts, latency
DEBUG only: truncated message preview (max 50 chars) — OFF by default
```

## Key Metrics to Monitor
| Metric | Alert Threshold |
|--------|----------------|
| Time to first token | > 3,000ms P95 |
| Tokens per turn | > 8,000 (single turn) |
| Tool failure rate | > 3 failures in 5 min |
| RAG threshold pass rate | < 70% in 1 hour |
| create_payment_intent failure | Any failure |
| Unhandled exceptions (500s) | Any occurrence |

## Analytics Endpoint
```python
GET /analytics/conversations
→ Returns conversation_analytics table records
→ Paginated, ordered by created_at DESC
→ Protected: requires authenticated user
```
No dashboard to build — display raw table during demo or query directly. The structured JSON output from the Analytics Agent is the showcase, not the visualisation.

## Analytics Data Available
Per conversation: resolution_status, sentiment, product_interests, revenue_potential, policy_creation_started/completed, unresolved_questions, topics_discussed, turn_count.

**Key presentation point:** Unresolved questions list shows what the AI couldn't answer — a feedback loop for knowledge base gaps.

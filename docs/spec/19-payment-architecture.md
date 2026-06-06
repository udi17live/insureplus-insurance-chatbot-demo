# 19 — Payment Architecture

## Stripe Sandbox Only
This is a non-core showcase feature. Stripe sandbox — no real payments.

## Architecture
```
Agent calls create_payment_intent
  → client_secret sent to frontend via SSE state_update event
  → Frontend renders Stripe Elements inline in chat
  → User enters card → Stripe.js submits directly to Stripe
    (card data never touches our backend — PCI compliant)
  → Stripe processes → POST /webhooks/stripe (our FastAPI)
  → Backend verifies signature
  → Backend appends [SYSTEM VERIFIED] message to Foundry thread
  → Backend triggers new streaming agent run
  → Agent calls create_policy → create_policy record in DB
  → Agent calls send_confirmation_email
  → Agent streams confirmation to frontend
```

## Why Webhook → Agent (Not Webhook → Direct DB)
The agent owns the full conversation flow. By having the webhook trigger a new agent run (rather than bypassing the agent), we get:
- Consistent architecture — agent handles everything end to end
- Natural streaming of completion message to user
- Tool call logging for debugging
- Conversation continuity in same thread

## Thread IDs in Stripe Metadata
```python
intent = stripe.PaymentIntent.create(
    amount=int(quote.premium_amount * 100),
    currency="gbp",
    metadata={
        "quote_id": str(quote.id),
        "user_id": str(user.id),
        "thread_id": str(thread.id),
        "foundry_thread_id": thread.foundry_thread_id  # Critical for webhook
    }
)
```
Webhook has no JWT/session — uses Stripe metadata to find the correct thread.

## Idempotency
```python
# Webhook handler — prevents duplicate processing
if payment.status == "succeeded":
    return {"status": "already_processed"}
```
`stripe_payment_intent_id` unique constraint on payments table also prevents duplicate policy creation.

## create_policy Tool — Double Verification
Even though webhook already confirmed payment, `create_policy` tool calls Stripe directly:
```python
intent = stripe.PaymentIntent.retrieve(payment_intent_id)
if intent.status != "succeeded":
    return {"success": False, "error": "Payment not confirmed"}
```
The webhook is the trusted gate. The tool is the last line of defence.

## SSE Push From Webhook
Webhook fires outside the original request context. In-memory queue used to push events to open SSE connection:
```python
active_connections: dict[str, asyncio.Queue] = {}
# Production: replace with Redis pub/sub for multi-instance
```

## Stripe Test Cards
| Card | Scenario |
|------|---------|
| 4242 4242 4242 4242 | Succeeds |
| 4000 0000 0000 0002 | Declined |
| 4000 0025 0000 3155 | Requires 3D Secure |
| 4000 0000 0000 9995 | Insufficient funds |
Expiry: any future date. CVC: any 3 digits.

## Setup
```
Stripe Dashboard (Test mode):
STRIPE_PUBLISHABLE_KEY=pk_test_xxx   → Next.js env (public)
STRIPE_SECRET_KEY=sk_test_xxx        → FastAPI env (private)
STRIPE_WEBHOOK_SECRET=whsec_xxx      → FastAPI env (from webhook setup)

Local dev: stripe listen --forward-to localhost:8000/webhooks/stripe
```

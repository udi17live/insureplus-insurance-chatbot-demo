# 05 — User Journeys

## Journey 1 — Guest to Authenticated (Q&A → Login)
1. Guest lands on chat UI → frontend generates session ID
2. Sends message → rate limit check (IP) → Primary Agent
3. Agent calls `search_knowledge_base` → RAG retrieval → streams response
4. Guest asks for quote → agent detects auth-required tool
5. Agent streams: "To get a quote I'll need you to log in. [Login] [Register]"
6. Frontend stores pending messages in sessionStorage
7. User registers/logs in → JWT issued → cookie set by Next.js
8. Guest thread context restored → pending intent resumed

## Journey 2 — Policy Creation (Full Flow)
1. User logs in → long-term memory loaded from Memory Store
2. User requests motor insurance → agent calls `start_policy_creation`
3. Agent collects fields one at a time → validates each via `update_collected_field`
4. On validation failure: re-asks same field (max 3 attempts)
5. All fields collected → agent presents summary → user confirms
6. Agent calls `generate_quote` → streams quote with premium breakdown
7. User accepts → agent calls `create_payment_intent` → Stripe PaymentIntent created
8. `client_secret` sent to frontend via SSE `state_update` event
9. Frontend renders Stripe Elements inline in chat
10. User pays → Stripe.js handles card → Stripe webhook fires to our backend
11. Backend verifies signature → appends `[SYSTEM VERIFIED]` message to Foundry thread
12. Backend triggers new streaming run → agent calls `create_policy` → `send_confirmation_email`
13. Agent streams: "Your policy is active! Policy: INS-2025-MOT-XXXXXX"
14. Background: analytics agent triggered after idle timeout

## Journey 3 — Returning User
1. Logs in → Memory Store retrieves past session summaries and preferences
2. Starts new chat → memory context injected as `additional_instructions`
3. Agent references prior context naturally: "Last time you asked about motor insurance..."
4. User views sidebar → thread list from `GET /chat/threads`
5. Opens past thread → messages fetched from Foundry via `foundry_thread_id`
6. Browser closes → idle timeout (10 min) triggers analytics agent

## Edge Cases
| Scenario | Handling |
|----------|----------|
| Field fails 3 times | Offer skip or restart — never ask 4th time |
| RAG returns no results | "I don't have information on that" + offer related topics |
| Quote expires (30 min) | Tool returns error → agent regenerates quote automatically |
| Payment fails | Stripe.js error → agent offers retry, state stays `payment_pending` |
| User abandons flow | Idle timeout marks state `abandoned` — restart on return |
| OpenAI rate limit mid-stream | Retry with backoff → friendly error if all retries fail |

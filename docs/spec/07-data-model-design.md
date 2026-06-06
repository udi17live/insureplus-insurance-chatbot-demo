# 07 — Data Model Design

## Tables Overview
```
users → chat_threads → (messages via Foundry, not DB)
users → policy_creation_states → quotes → policies → payments
users → conversation_analytics (written by Analytics Agent only)
chat_threads → tool_call_logs (optional, debug)
```

## ENUMs (DB-level)
```sql
product_type:       motor | bike | life | device
thread_status:      active | ended | abandoned
collection_status:  collecting | confirming | quoting | payment_pending | complete | abandoned
quote_status:       pending | accepted | declined | expired
policy_status:      active | cancelled | expired
payment_status:     pending | succeeded | failed | refunded
sentiment_type:     positive | neutral | negative
resolution_status:  resolved | unresolved | partial
revenue_potential:  low | medium | high
```

## Key Tables

### chat_threads
```sql
id, user_id (nullable — NULL for guest), foundry_thread_id (UNIQUE),
title, status, product_interest, total_tokens_used,
context_summary (TEXT), last_message_at, created_at, updated_at
```
`foundry_thread_id` is the link to AI Foundry — used to retrieve messages and resume agent runs. Messages are **not stored in our DB** — fetched from Foundry on demand.

### policy_creation_states
```sql
id, user_id, thread_id, product_type, status (collection_status),
collected_data (JSONB), field_attempts (JSONB), current_field,
created_at, updated_at
```
Partial unique index: only one active creation per user at a time.
```sql
CREATE UNIQUE INDEX idx_policy_creation_active_per_user
ON policy_creation_states(user_id)
WHERE status NOT IN ('complete', 'abandoned');
```

### quotes
```sql
id, user_id, policy_creation_state_id, product_type,
status (quote_status), premium_amount (NUMERIC 10,2),
currency (CHAR 3, default 'GBP'), coverage_summary (JSONB),
expires_at, created_at
```

### policies
```sql
id, user_id, quote_id, policy_number (UNIQUE VARCHAR 50),
product_type, status, coverage_data (JSONB),
premium_amount, currency, start_date, end_date,
created_at, updated_at
```
Policy number format: `INS-{YEAR}-{PREFIX}-{6 alphanum}` e.g. `INS-2025-MOT-X7K2P1`

### payments
```sql
id, user_id, policy_id (nullable initially),
stripe_payment_intent_id (UNIQUE), amount, currency,
status (payment_status), stripe_metadata (JSONB),
created_at, updated_at
```
`stripe_payment_intent_id` unique constraint prevents duplicate webhook processing.

### conversation_analytics
```sql
id, thread_id (UNIQUE), user_id, resolution_status, sentiment,
product_interests (product_type[]), revenue_potential,
policy_creation_started (BOOL), policy_creation_completed (BOOL),
unresolved_questions (TEXT[]), topics_discussed (TEXT[]),
turn_count, raw_analysis (JSONB), created_at
```
Written exclusively by Analytics Agent. One record per conversation.

## JSONB Usage
| Table | Column | Why JSONB |
|-------|--------|-----------|
| policy_creation_states | collected_data | Different fields per product type |
| policy_creation_states | field_attempts | Dynamic retry tracking per field |
| quotes | coverage_summary | Product-specific quote breakdown |
| policies | coverage_data | Full coverage detail varies by product |
| payments | stripe_metadata | Stripe event structure varies |

## Auto-update Trigger
```sql
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$ LANGUAGE plpgsql;
-- Applied to: users, chat_threads, policy_creation_states, policies, payments
```

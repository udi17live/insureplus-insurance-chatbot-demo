# 17 — Tool / Function Calling Design

## Pattern: requires_action
Agent pauses run → FastAPI intercepts tool calls → executes logic → submits results back → agent continues streaming. Chosen over OpenAPI Tools for security (user_id from JWT, not agent), lower latency, and better streaming integration.

## Security Rule
`user_id` is **always** injected from the validated JWT in FastAPI. The agent never receives or passes user_id as a tool argument — this prevents prompt injection attacks where a user might attempt to access another user's data.

## Tool Response Contract
```json
// Success
{"success": true, "data": { ... }}

// Auth required (guest)
{"auth_required": true, "message": "Login required"}

// Failure
{"success": false, "error": "Human-readable description"}
```

## Tools Registered on Primary Agent

| Tool | Purpose | Auth Required |
|------|---------|--------------|
| `check_auth_status` | Returns authenticated/guest state | No |
| `get_user_profile` | Returns name, email, member since | Yes |
| `get_user_policies` | Returns all user policies from DB | Yes |
| `start_policy_creation` | Creates/resumes policy creation state | Yes |
| `update_collected_field` | Validates and stores one field | Yes |
| `generate_quote` | Calculates premium, creates quote record | Yes |
| `create_payment_intent` | Creates Stripe PaymentIntent, returns client_secret | Yes |
| `create_policy` | Creates policy record after payment confirmed | Yes |
| `send_confirmation_email` | Sends policy email via ACS | Yes |

## Parallel Tool Execution
When agent calls multiple tools in one requires_action event:
```python
results = await asyncio.gather(
    execute_tool("search_knowledge_base", args_1, user, db),
    execute_tool("get_user_policies", {}, user, db)
)
# Submit all results in single call back to run
```

## Field Validation
Single `validate_field()` function handles: enum, regex, date (with age checks), numeric range, free text. Called by `update_collected_field` before storing.

On validation failure: returns `attempts_remaining` count.
At 3 failures: returns `attempts_exceeded: true` → agent must offer skip/restart.

## Quote Calculation (Demo Logic)
Rule-based pricing — not actuarially accurate. Factors used:
- Motor: coverage_type base + age factor + NCD discount + mileage factor
- Bike: coverage_type base + age factor + CC factor
- Life: coverage_amount × rate + age factor + smoker factor + CI factor
- Device: device_value × 2% / 12 × coverage factor

## Email Tool — Non-Blocking
ACS email failure returns `{"success": false, "non_blocking": true}`. Agent informed but flow continues — policy creation is never blocked by email delivery.

## Tool → DB Operations
| Tool | Reads | Writes |
|------|-------|--------|
| get_user_policies | policies | — |
| start_policy_creation | policy_creation_states | policy_creation_states |
| update_collected_field | policy_creation_states | policy_creation_states |
| generate_quote | policy_creation_states | quotes |
| create_payment_intent | quotes | payments |
| create_policy | payments, quotes | policies |
| send_confirmation_email | users, policies | — |

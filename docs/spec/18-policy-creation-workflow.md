# 18 — Insurance Policy Creation Workflow

## State Machine
```
IDLE → COLLECTING → CONFIRMING → QUOTING → PAYMENT_PENDING → COMPLETE
                         ↑              ↓
                    (user edits)   (quote expired → regenerate)
At any point → ABANDONED
```

| State | Trigger |
|-------|---------|
| collecting | `start_policy_creation` tool |
| confirming | `update_collected_field` (last field stored) |
| quoting | `generate_quote` tool |
| payment_pending | `create_payment_intent` tool |
| complete | `create_policy` tool (post-webhook) |
| abandoned | Idle timeout or user request |

## State Machine Enforcement
Tools validate state before executing — not just prompt instructions:
```python
# generate_quote refuses if not in confirming state
if state.status != "confirming":
    return {"success": False, "error": f"Cannot quote. Status: {state.status}"}

# create_policy verifies Stripe payment status directly
intent = stripe.PaymentIntent.retrieve(payment_intent_id)
if intent.status != "succeeded":
    return {"success": False, "error": "Payment not confirmed"}
```

## Field Collection Pattern
1. Agent asks for one field with hint
2. User responds → `update_collected_field` validates
3. On failure: re-ask with explanation (max 3 attempts)
4. On 3rd failure: offer skip or restart — never ask a 4th time
5. On success: ask next field
6. All collected → status → `confirming` → agent presents summary

## Confirmation Summary (Always Required)
Agent presents all collected data before calling `generate_quote`. Rule 15 in system prompt and state machine both enforce this — cannot be skipped.

## Product Schemas (Field Counts)
| Product | Fields |
|---------|--------|
| Motor | 7 (registration, make, year, DOB, mileage, coverage type, NCD years) |
| Bike | 6 (make, model, engine CC, DOB, licence type, coverage type) |
| Life | 5 (DOB, smoker, coverage amount, term years, critical illness) |
| Device | 5 (device type, make, model, value, coverage type) |

## Error Paths

**Quote expired (30 min):**
Agent calls `create_payment_intent` → tool returns "Quote expired" → agent calls `generate_quote` automatically with same collected data → new quote presented.

**Payment failed:**
Stripe.js returns error to frontend → user sends message → agent offers retry. `payment_intent` remains active. State stays `payment_pending`.

**User abandons:**
Idle timeout marks `policy_creation_states.status = 'abandoned'`. On return, agent offers to start fresh (not auto-resume — avoids stale data issues).

## Resume Handling
`start_policy_creation` checks for existing active state first:
- Found active state → returns collected data + current field → agent resumes
- No active state → creates new state → starts from first field

## One Active Creation Per User
Enforced by partial unique index on `policy_creation_states`:
```sql
CREATE UNIQUE INDEX idx_policy_creation_active_per_user
ON policy_creation_states(user_id)
WHERE status NOT IN ('complete', 'abandoned');
```

## Policy Number Format
`INS-{YEAR}-{PREFIX}-{6 alphanum}` → e.g. `INS-2025-MOT-X7K2P1`
Prefixes: MOT, BIK, LIF, DEV

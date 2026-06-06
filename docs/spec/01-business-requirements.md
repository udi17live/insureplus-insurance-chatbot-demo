# 01 — Business Requirements

## What This System Is
A conversational AI platform for a fictional multi-product insurance company. Built to **production-grade engineering standards** as a technical showcase. Data and scale are demo-grade; patterns and implementation are production-grade.

## Insurance Products in Scope
- Motor Insurance
- Bike Insurance
- Life Insurance
- Device Insurance

## Primary Showcase Goals
- Anti-hallucination strategies (RAG-grounded only)
- Guardrail design and prompt engineering
- Tool/function calling via AI Foundry Agents
- SSE streaming responses (token-by-token)
- Policy creation state machine
- Async analytics agent (post-conversation)
- Conversation memory across sessions
- Rate limiting and loop prevention
- Token usage optimisation

## Three Core User Journeys
1. **Guest Q&A** — Chat freely, get RAG-backed answers, prompted to login on auth-required actions
2. **Policy Creation** — Guided AI data collection → quote → Stripe sandbox payment → policy
3. **Returning User** — Cross-session memory, view past conversations and policies

## Explicitly Not In Scope
- Regulatory compliance (FCA, GDPR etc.)
- Human underwriter review (documented as production requirement)
- Real payment processing (Stripe sandbox only)
- Mobile native app
- Admin portal
- Multi-language support

## Key Constraint
AI answers **only** from indexed knowledge base documents. No inference, no extrapolation. If a question cannot be answered from documents, the agent says so explicitly.

## Production Notes
Human-in-the-loop for policy approval, full compliance layer, and multi-region deployment are documented as production extensions throughout the spec — not implemented for showcase.

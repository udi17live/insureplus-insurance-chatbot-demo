# 02 — Functional Requirements

## Guest Users
| ID | Requirement |
|----|-------------|
| G-01 | Chat with AI without authentication |
| G-02 | Ask insurance questions — RAG-backed, document-grounded only |
| G-03 | Browse and compare products via chat |
| G-04 | On auth-required tool trigger, receive inline login prompt |
| G-05 | Guest chat context optionally carried over post-login |
| G-06 | No server-side persistence of guest chat |

## Authenticated Users
| ID | Requirement |
|----|-------------|
| A-01 | Register with email and password |
| A-02 | Login, receive JWT stored in HttpOnly cookie |
| A-03 | AI-guided policy creation flow |
| A-04 | View all created policies |
| A-05 | View full conversation history |
| A-06 | Start multiple independent chat sessions |
| A-07 | Make sandbox payment to complete policy |
| A-08 | Profile management *(optional/stretch)* |

## AI Assistant
| ID | Requirement |
|----|-------------|
| AI-01 | Answer only from knowledge base — zero hallucination policy |
| AI-02 | Explicitly state when information is not available |
| AI-03 | Stream responses token-by-token via SSE |
| AI-04 | Maintain within-session context via Foundry thread memory |
| AI-05 | Recall cross-session context via AI Foundry Memory Store |
| AI-06 | Detect policy creation intent and initiate workflow |
| AI-07 | Detect and break repetitive/looping states |
| AI-08 | Gracefully refuse off-topic or out-of-scope queries |

## Policy Creation
| ID | Requirement |
|----|-------------|
| PC-01 | Collect fields one at a time via structured conversation |
| PC-02 | Validate each field via Pydantic before storing |
| PC-03 | Re-ask only failed fields — not full form |
| PC-04 | After 3 failures on one field, offer skip or restart |
| PC-05 | Present full summary for user confirmation before quoting |
| PC-06 | Generate rule-based demo quote |
| PC-07 | Initiate Stripe sandbox payment on quote acceptance |
| PC-08 | Create policy record after webhook confirms payment |
| PC-09 | Send confirmation email via Azure Communication Services |

## Analytics Agent (Async)
| ID | Requirement |
|----|-------------|
| AN-01 | Triggered when conversation ends or goes idle (10 min) |
| AN-02 | Extract: resolution status, sentiment, product interest |
| AN-03 | Assign revenue potential score (low/medium/high) |
| AN-04 | Extract unresolved questions from conversation |
| AN-05 | Store structured JSON output to DB |

## Rate Limiting
- Guest: 20 messages/hour per IP
- Authenticated: 60 messages/hour per user
- Login: 5 attempts per 15 minutes per IP
- Rate limit errors delivered as SSE events — not raw HTTP 429

## Out of Scope
Email notifications beyond policy confirmation, document upload by user, agent/broker portal, WCAG accessibility, real payments, admin portal.

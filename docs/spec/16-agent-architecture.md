# 16 — Agent Architecture

## Two Agents

### Primary Orchestrator Agent
- **Role:** All user-facing conversation
- **Trigger:** Every user message
- **Mode:** Synchronous, SSE streaming
- **Config:** AI Foundry portal
- **Tools:** Azure AI Search (built-in) + 9 custom function tools
- **Memory:** Foundry thread + Memory Store

### Analytics Agent
- **Role:** Post-conversation insight extraction
- **Trigger:** Background task — conversation ended or idle 10 min
- **Mode:** Async, single run, no streaming
- **Config:** AI Foundry portal
- **Tools:** None
- **Output:** Structured JSON → conversation_analytics table

## Portal Configuration — Primary Agent
```
Model:          gpt-4o-mini
Temperature:    0.1
Instructions:   [System prompt from Section 15]
Knowledge:      Azure AI Search → insurance-knowledge-base index
Memory:         Memory Store → insure_plus_memory, scope: {{$userId}}
Tools:          [9 custom function schemas — see Section 17]
```

## Portal Configuration — Analytics Agent
```
Model:          gpt-4o-mini
Temperature:    0   (deterministic JSON output)
Instructions:   [Analytics system prompt — JSON only, no preamble]
Knowledge:      None
Memory:         None
Tools:          None
```

## Analytics System Prompt (Key Instruction)
```
You are a conversation analytics engine.
Respond with valid JSON ONLY. No explanation, no markdown.
Extract: resolution_status, sentiment, product_interests,
revenue_potential, policy_creation_started/completed,
unresolved_questions, topics_discussed, turn_count
```

## Code — What We Write
Our code calls portal-configured agents. It does not create or modify them.

**Primary agent — per message:**
```python
async with client.agents.runs.stream(
    thread_id=foundry_thread_id,
    agent_id=settings.PRIMARY_AGENT_ID,
    max_prompt_tokens=4000,
    max_completion_tokens=600,
    truncation_strategy={"type": "last_messages", "last_messages": 10},
    additional_instructions=build_context_injection(user, thread),
) as stream:
    # Handle token deltas, tool calls, completion
```

**Analytics agent — post-conversation:**
```python
run = await client.agents.runs.create_and_process(
    thread_id=analytics_thread_id,
    agent_id=settings.ANALYTICS_AGENT_ID,
    max_prompt_tokens=3000,
    max_completion_tokens=400,
)
# Parse JSON → write to conversation_analytics table
# Delete ephemeral analytics thread after use
```

## Agent Settings Summary
| Setting | Primary | Analytics |
|---------|---------|-----------|
| Model | gpt-4o-mini | gpt-4o-mini |
| Temperature | 0.1 | 0 |
| Streaming | Yes (SSE) | No |
| Thread | Persistent | Ephemeral (created+deleted per run) |
| max_prompt_tokens | 4,000 | 3,000 |
| max_completion_tokens | 600 | 400 |

## Multi-Agent — Production Pattern
For the presentation:
> "In production, as product range grows, the orchestrator routes to specialist agents — one per insurance domain. Each carries a smaller, focused system prompt. Foundry's connected agents pattern supports this natively. Infrastructure doesn't change, only the routing logic in the orchestrator's system prompt."

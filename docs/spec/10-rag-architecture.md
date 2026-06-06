# 10 — RAG Architecture

## Approach: Azure-Managed
All RAG infrastructure managed by Azure AI Foundry and Azure AI Search. No custom search code.

## Setup (One-Time, Portal Only)
```
1. Upload markdown documents to Azure Blob Storage
   Container: insure-plus-knowledge-base
   Folders: /motor/ /bike/ /life/ /device/ /generic/

2. AI Foundry portal → Data + Indexes → New Index
   Data source: Azure Blob Storage container
   Embedding model: text-embedding-3-small
   Enable semantic ranking: ON

   Foundry auto-creates:
   ├── AI Search index with correct schema
   ├── Indexer pointing at blob container
   ├── Skillset (chunking + embedding)
   └── Scheduled re-index on document change

3. AI Foundry portal → Agent → Knowledge → Add → Azure AI Search
   Select: insurance-knowledge-base index
   Agent now has built-in search capability — no code required
```

## How the Agent Uses It
The Azure AI Search tool is a built-in Foundry tool — agent decides when to call it, executes hybrid search, returns chunks with inline citations. No custom tool invocation code needed for RAG.

## Anti-Hallucination — 4 Layers

**Layer 1 — System Prompt (see Section 15)**
- ALWAYS call search_knowledge_base before answering
- Answer ONLY from retrieved context
- If no results: say "I don't have information on that"

**Layer 2 — Score Threshold**
Semantic reranker scores 0–4. Only chunks scoring ≥ 1.5 injected into prompt.
Below threshold → agent receives no context → must respond "I don't have information."
Threshold is a config value — adjustable without redeployment.

**Layer 3 — Product Context Filtering**
When product detected in conversation, injected via `additional_instructions`:
"Prioritise motor documents when searching."
Prevents cross-product contamination in results.

**Layer 4 — Citation Enforcement**
System prompt requires agent to reference source document when stating facts.
"According to our motor insurance exclusions guide..."
Hallucinated statements have no citation — immediately visible.

## Document Update Flow
Update file in Blob Storage → indexer detects change → re-chunks and re-embeds → index updated automatically. No code deployment required.

## Query Rewriting (Optional)
Not implemented by default. Add if retrieval quality is poor:
- Symptom: wrong product retrieved, conversational phrasing fails
- Implementation: direct OpenAI call (~50 tokens) to extract clean search query before agent searches
- Cost: ~$0.0001 per message — negligible

## Important Constraint
Azure AI Search tool targets **one index only**. All products live in a single index — product filtering via metadata, not separate indexes.

## Semantic Ranker — Cost Note
Semantic ranking requires **Basic tier minimum** (~$75/month).
Free tier fallback: hybrid search without semantic ranking — same code, remove `query_type="semantic"`.

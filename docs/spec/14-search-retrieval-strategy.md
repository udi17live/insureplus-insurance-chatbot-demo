# 14 — Search & Retrieval Strategy

## Retrieval Pipeline
```
Agent calls Azure AI Search tool (built-in)
        ↓
Stage 1: Parallel execution
  ├── BM25 keyword search  (exact + near-exact term matching)
  └── Vector search        (cosine similarity on embeddings)
        ↓
Stage 2: RRF Merge
  Reciprocal Rank Fusion combines both result sets
        ↓
Stage 3: Semantic Reranking
  Top 50 candidates re-evaluated for true relevance
  Each result gets reranker_score (0–4)
        ↓
Stage 4: Return top 3 results
  With content, metadata, score, caption
        ↓
Score threshold filter (≥ 1.5)
  Pass → inject into agent context
  Fail → agent responds "I don't have information on that"
```

## Why Each Stage Matters
| Stage | Problem Solved |
|-------|---------------|
| BM25 | Catches exact terms: "NCD", "excess", policy codes |
| Vector | Catches semantic variation: "no claims bonus" = "NCD" |
| RRF | Neither search alone is sufficient — balances both signals |
| Semantic reranker | Re-promotes genuinely relevant chunk to position 1 |
| Score threshold | Prevents low-confidence chunks from reaching the agent |

## Score Threshold Reference
| Score | Meaning | Action |
|-------|---------|--------|
| 3.0–4.0 | Directly answers the query | Always inject |
| 2.0–3.0 | Covers the topic | Inject |
| 1.5–2.0 | Marginally relevant | Inject |
| < 1.5 | Weakly related | **Filter out** |

**Default threshold: 1.5** — tunable config value.
- Too many "I don't know" responses → lower to 1.2
- Agent giving vaguely-related answers → raise to 2.0

## Product Filtering
When product context detected in conversation:
- `additional_instructions` includes: "Prioritise motor documents when searching"
- Agent applies `product_type = 'motor'` filter to search
- Generic documents always included regardless of filter

## Retrieval Quality Test Matrix
Run after index creation and after any document update:
```
Direct match tests:
"motor insurance flood exclusion"  → motor-exclusions.md ✅
"bike track day coverage"          → bike-exclusions.md ✅
"life insurance beneficiary"       → life-beneficiary.md ✅
"what is excess in insurance"      → insurance-glossary.md ✅

Semantic variation tests:
"my no claims bonus"               → motor-premium-factors.md ✅
"cracked screen phone insurance"   → device-accidental-damage-theft.md ✅

Out-of-scope tests (must fail threshold):
"home insurance coverage"          → Score < 1.5, no inject ✅
"average UK insurance premiums"    → Score < 1.5, no inject ✅
```

## Tuning Levers (in order of effort)
1. Adjust score threshold (config only — no redeploy)
2. Add content to thin document sections (< 80 words)
3. Enable query rewriting (see Section 10)
4. Enable agentic retrieval for multi-product queries (production upgrade)

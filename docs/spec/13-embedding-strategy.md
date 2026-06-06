# 13 — Embedding Strategy

## Selected Model: `text-embedding-3-small`

| Criterion | Value |
|-----------|-------|
| Dimensions | 1,536 |
| Cost | $0.02 per 1M tokens |
| Quality | Strong for retrieval tasks |
| Ingestion cost (27 docs) | ~$0.001 (one-time) |
| Query cost (per search) | ~$0.0000003 |

## Where Embeddings Are Generated
1. **Ingestion (once):** Each document chunk → text-embedding-3-small → vector stored in AI Search index
2. **Query time (every search):** User query → text-embedding-3-small → vector → cosine similarity against index

Both managed by Azure — configured once in Foundry portal. Same deployment must be used for both (Foundry enforces this automatically).

## Dimensionality Note
`text-embedding-3` family supports Matryoshka Representation Learning (MRL) — vectors can be shortened without retraining:
- 1,536 (default) — full quality, our choice
- 512 — ~95% quality, useful at scale if index size is a concern
- 256 — ~90% quality, large scale with millions of chunks

Use full 1,536 for this system.

## Document Quality > Model Quality
A well-written H2 section with specific terminology produces far better retrieval than a thin or vague section, regardless of model choice. Content authoring (Section 11) matters more than embedding model selection at this scale.

## Model Alternatives
| Model | Dimensions | Cost/1M tokens | Verdict |
|-------|-----------|----------------|---------|
| **text-embedding-3-small** | 1,536 | $0.02 | ✅ Recommended |
| text-embedding-3-large | 3,072 | $0.13 | 6.5× more expensive, marginal gain for 27 docs |
| text-embedding-ada-002 | 1,536 | $0.10 | Older, 5× more expensive — no advantage |
| Cohere Embed v3 | 1,024 | ~$0.10 | Vendor-independent alternative |
| BGE-small (self-hosted) | 384 | Free | Best for full vendor independence |

**At 1B tokens:** ada-002 = $100 vs 3-small = $20 — 5× saving with equal or better quality.

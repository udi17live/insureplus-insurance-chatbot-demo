# 12 — Document Ingestion Pipeline

## Overview
Entirely Azure-managed. No custom indexing code. Setup takes 15–20 minutes via AI Foundry portal.

## One-Time Setup
```
1. Create Blob Storage container: insure-plus-knowledge-base
   Upload all 27 documents in folder structure

2. AI Foundry portal → Data + Indexes → New Index
   └── Data source: Azure Blob Storage (point to container)
   └── Embedding model: text-embedding-3-small
   └── Semantic ranking: ON
   └── Click Create

   Auto-created:
   ├── Data source connection
   ├── Skillset (chunking + embedding)
   ├── Index schema
   └── Indexer (runs immediately)

3. Connect to agent:
   Agent → Knowledge → Add → Azure AI Search → select index
```

## What the Skillset Does
- **Document cracking:** Extracts text from Markdown files
- **Markdown-aware chunking:** Splits at H2 heading boundaries (Document Layout skill)
- **YAML front matter parsing:** Maps product/category/tags to index metadata fields
- **Embedding generation:** Calls text-embedding-3-small per chunk, stores 1,536-dim vector

## Incremental Updates
Indexer detects blob changes via ETag/LastModified. Only changed documents re-processed. Old chunks deleted, new chunks created. No downtime, no full re-index.

**Showcase:** Run indexer manually after document updates (portal → Indexer → Run)  
**Production:** Schedule every 5 min, or configure Azure Event Grid trigger for sub-minute latency

## Verification Checklist (Before Connecting to Agent)
```
1. Chunk count: expect 80–120 chunks (27 docs × ~3-4 H2 sections)
   If count = 27 → chunking failed, check H2 headings
   If count = 0  → indexer failed, check blob permissions

2. Spot-check queries in Search Explorer:
   "motor insurance flood damage"   → motor-exclusions.md ✅
   "what is an excess"              → insurance-glossary.md ✅
   "bike track day coverage"        → bike-exclusions.md ✅
   "device stolen from car"         → device-accidental-damage-theft.md ✅

3. Verify metadata: each result should have product_type, source_file populated

4. Check semantic scores: relevant results should score ≥ 2.0
   If consistently below 1.5 → document content may be too thin
```

## Common Failures
| Issue | Symptom | Fix |
|-------|---------|-----|
| Blob permission denied | Indexer fails with 403 | Assign Storage Blob Data Reader to AI Search managed identity |
| Embedding skipped | Indexer warning | Check text-embedding-3-small deployment is active |
| YAML not parsed | product_type null | Ensure YAML delimiters (---) have no leading whitespace |
| One chunk per doc | chunk_count = 27 | Verify H2 headings exist, Markdown parsing mode active |

## Cost
- Ingestion (one-time): ~$0.001 for all 27 documents at text-embedding-3-small pricing
- Blob storage: ~$0.02/month
- Indexer runs: included in AI Search tier

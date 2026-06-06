# 11 — Knowledge Base Design

## Document Standard
Every document follows this exact template:
```markdown
---
product: motor | bike | life | device | generic
category: overview | coverage | exclusions | claims | faq | addons | pricing | glossary
tags: [tag1, tag2, tag3]
source: insure-plus-knowledge-base
version: 1.0
---

# [Document Title]

> One sentence summary — used by semantic ranker.

## [Section One]
Content. 80–150 words per H2 section.

## [Section Two]
Content.
```

## Document Rules
- One H1 per document (title only)
- H2 = primary chunk boundaries — one topic per section
- Each H2 section: 80–150 words
- Total document: 400–700 words
- No tables (chunker handles prose better)
- No cross-document references ("see our FAQ")
- No marketing language
- Repeat key terms naturally (improves BM25 matching)
- Each H2 answers one question

## 27 Documents Inventory

**Generic / Platform (5)**
- how-the-assistant-works.md
- how-to-get-a-quote.md
- payment-and-policy-process.md
- insurance-glossary.md
- product-comparison-overview.md

**Motor Insurance (6)**
- motor-insurance-overview.md
- motor-premium-factors.md
- motor-exclusions.md
- motor-addons.md
- motor-claims-process.md
- motor-faq.md

**Bike Insurance (5)**
- bike-insurance-overview.md
- bike-coverage-options.md
- bike-rider-eligibility.md
- bike-exclusions.md
- bike-faq.md

**Life Insurance (6)**
- life-insurance-overview.md
- life-premium-calculation.md
- life-critical-illness.md
- life-exclusions.md
- life-beneficiary-guide.md
- life-faq.md

**Device Insurance (5)**
- device-insurance-overview.md
- device-accidental-damage-theft.md
- device-claim-limits.md
- device-exclusions.md
- device-faq.md

## Blob Storage Structure
```
insure-plus-knowledge-base/  (container)
├── generic/
├── motor/
├── bike/
├── life/
└── device/
```
Folder structure maps to `product` metadata field — enables product-filtered search.

## Why Structure Matters
Foundry's default chunker splits at H2 boundaries. Well-structured documents = clean chunks = accurate retrieval. Document quality is the single biggest factor in RAG performance.

## Content Note
All content is synthetic demo data — not actuarially accurate. State this clearly at the bottom of every document: *"This document contains demo content for showcase purposes only."*

# 28 — Cost Analysis

## Showcase Monthly Estimate (~$120/month)
| Service | Tier | Monthly Cost |
|---------|------|-------------|
| Azure OpenAI (GPT-4o-mini) | Pay-as-you-go, low volume | ~$10–15 |
| Azure AI Search | Basic (semantic ranking) | ~$75 |
| Azure AI Foundry | Consumption-based | ~$5–10 |
| PostgreSQL Flexible Server | Burstable B1ms | ~$12–15 |
| Azure Blob Storage | LRS, hot tier | ~$1–2 |
| App Service | B1 | ~$13 |
| Static Web Apps | Free | $0 |
| Application Insights | Free (5GB/month) | $0 |
| Azure Communication Services | Free (100 emails/day) | $0 |
| **Total** | | **~$116–130/month** |

*AI Foundry Memory Store pricing not yet published (preview). Monitor before committing.*

## Small Scale (~500 MAU) — ~$352/month
| Service | Tier | Monthly Cost |
|---------|------|-------------|
| Azure OpenAI | Pay-as-you-go, moderate | ~$150 |
| AI Search | Basic | ~$75 |
| PostgreSQL | B2s | ~$35 |
| App Service | P1v3 | ~$70 |
| Redis Cache | C0 Basic | ~$16 |
| Other | Various | ~$6 |
| **Total** | | **~$352/month** |

## Medium Scale (~5,000 MAU) — ~$1,445/month
| Service | Tier | Monthly Cost |
|---------|------|-------------|
| Azure OpenAI | High volume | ~$800 |
| AI Search | Standard S1 | ~$250 |
| PostgreSQL | General Purpose D2ds | ~$130 |
| App Service | P2v3 × 2 | ~$140 |
| Redis | C1 Standard | ~$55 |
| Other | Various | ~$70 |
| **Total** | | **~$1,445/month** |

## Per-Turn Cost Breakdown
| Component | Cost per Turn |
|-----------|--------------|
| GPT-4o-mini (~7,200 tokens) | ~$0.001 |
| Embedding (query, 15 tokens) | ~$0.0000003 |
| AI Search query | Included in tier |
| **Total per user message** | **~$0.001** |

## Cost Optimisation Levers
1. **Reduce max_prompt_tokens:** Lowering from 4,000 to 3,000 saves ~15% per turn
2. **Rolling summary:** Prevents unbounded token growth on long conversations
3. **RAG score threshold:** Higher threshold = fewer chunks injected = lower token usage
4. **Model choice:** GPT-4o-mini is already the most cost-efficient option. Consider GPT-4.1-mini when available
5. **AI Search tier:** Free tier + no semantic ranker saves $75/month (quality trade-off)

## Free Tier Fallback (Minimal Cost ~$40/month)
| Service | Tier | Cost |
|---------|------|------|
| AI Search | Free (no semantic ranker) | $0 |
| App Service | F1 Free | $0 |
| PostgreSQL | B1ms | ~$15 |
| Azure OpenAI | Pay-as-you-go | ~$10–15 |
| Other | Free tiers | ~$10 |
| **Total** | | **~$25–40/month** |
Trade-off: no semantic ranking, App Service F1 has limited bandwidth and CPU minutes.

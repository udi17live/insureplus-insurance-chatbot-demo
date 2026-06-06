# 27 — Scalability Planning

## Bottlenecks by Component

### Azure OpenAI (Primary Bottleneck)
- GPT-4o-mini has TPM (tokens per minute) limits
- Each concurrent user consumes ~7,200 tokens per turn
- At 50 concurrent users: ~360,000 TPM needed
- **Solution:** Request higher quota via Azure portal, or move to PTU (Provisioned Throughput Units) at medium scale

### SSE Connections
- App Service B1: handles ~100 concurrent SSE connections
- Each SSE connection is a persistent HTTP connection
- **Solution:** Scale up to P-series App Service, or use Azure Container Apps (scales to zero, handles many concurrent connections)

### PostgreSQL
- B1ms handles showcase load easily
- Bottleneck at medium scale: analytics queries on large conversation_analytics table
- **Solution:** Add read replica for analytics queries, index on created_at and sentiment columns

### AI Search
- Basic tier: adequate for 27 documents, moderate query volume
- Semantic ranker adds ~100–200ms per query
- **Solution:** Standard S1 at medium scale, add replicas for higher throughput

## Scaling Path

### Showcase → Small (up to 500 MAU)
- App Service B1 → P1v3
- PostgreSQL B1ms → B2s
- AI Search: Basic stays sufficient
- Add Redis for rate limiting (replace in-memory)

### Small → Medium (up to 5,000 MAU)
- App Service P1v3 → P2v3 × 2 with autoscale
- PostgreSQL B2s → General Purpose D2ds + read replica
- AI Search Basic → Standard S1
- Azure Cache for Redis (C1) for session and rate limit state
- Azure OpenAI: increase TPM quota or move to PTU

### Medium → Large (50,000+ MAU)
- App Service → Azure Kubernetes Service (AKS)
- Azure Front Door + WAF for edge routing
- PostgreSQL → HA + geo-replication
- AI Search S2/S3 + multiple replicas
- OpenAI PTU deployment (~$3,000/month flat, predictable cost)
- Redis Premium for distributed state

## Token Cost Scaling
| Scale | Daily Turns | Daily Token Cost |
|-------|------------|-----------------|
| Showcase | ~100 | ~$0.10 |
| Small (500 MAU) | ~2,500 | ~$20 |
| Medium (5K MAU) | ~25,000 | ~$200 |
| Large (50K MAU) | ~250,000 | ~$2,000 |

## Connection Pooling
FastAPI + asyncpg requires connection pooling for PostgreSQL at scale:
```python
# SQLAlchemy async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=10,          # Persistent connections
    max_overflow=20,       # Burst connections
    pool_pre_ping=True     # Verify connections before use
)
```
Pool size should not exceed PostgreSQL's `max_connections` (default 100 on B1ms).

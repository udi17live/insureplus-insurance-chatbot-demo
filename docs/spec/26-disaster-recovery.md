# 26 — Disaster Recovery

## RTO / RPO Summary
| Component | RPO | RTO |
|-----------|-----|-----|
| PostgreSQL | 5 minutes | 15–20 min (point-in-time restore) |
| Knowledge base docs | 0 (Git is source of truth) | 5 min re-upload |
| App Service | N/A | 3–5 min (redeploy from Git) |
| AI Search index | N/A | 15–20 min (re-index from blob) |
| Foundry threads | Best effort | Non-recoverable (Microsoft-managed) |

## PostgreSQL Backup
Azure PostgreSQL Flexible Server automated backups:
- Full weekly, differential daily, transaction logs every 5 min
- 7-day retention (free)
- Point-in-time restore: Azure portal → PostgreSQL → Restore → select timestamp

## Knowledge Base Backup
Git repository is the source of truth. `knowledge-base/` folder committed. Re-upload to blob takes ~5 minutes. No blob-level backup needed.

## Graceful Degradation
```
AI Search down:
  → Q&A returns "temporarily unavailable"
  → Policy creation continues (no RAG needed for field collection)

Azure OpenAI down:
  → All chat fails with friendly message
  → Policy state preserved in DB — resumable when service recovers
  → Circuit breaker: opens after 3 failures, retries after 60 seconds

PostgreSQL down:
  → All authenticated features fail
  → Guest Q&A may work (no DB writes needed for chat)

App Service crash:
  → Redeploy from last working Git commit (~3–5 min)
```

## Foundry Thread Loss
If Foundry threads are lost (Microsoft-managed storage incident):
- Our DB retains thread metadata and `foundry_thread_id`
- Chat history unavailable — shows "History temporarily unavailable"
- New conversations start fresh
- Policy records unaffected (in PostgreSQL)
- **Production pattern:** BYO Cosmos DB for thread storage — full backup control

## Production Upgrades
| Showcase | Production |
|----------|-----------|
| 7-day backup retention | 35 days |
| Single region | Multi-region geo-replication |
| Manual failover | Azure Traffic Manager automatic failover |
| No deployment slots | Blue/green with App Service slots |
| Microsoft-managed threads | BYO Cosmos DB |

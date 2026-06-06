# 29 — Alternative Technology Evaluation

Key alternatives evaluated per component. Recommended choices marked ✅.

## AI Agent Framework
| Option | Cost | Vendor Lock | Complexity | Notes |
|--------|------|-------------|-----------|-------|
| ✅ **Azure AI Foundry Agents** | Consumption | High (Azure) | Low | Portal-managed, Memory Store, built-in RAG tool |
| LangGraph | Free | Low | Medium | Best for vendor independence, custom agent loops |
| LangChain Agents | Free | Low | Medium | Mature ecosystem, good for RAG pipelines |
| OpenAI Assistants API | Consumption | High (OpenAI) | Low | Similar to Foundry, no Azure integration |
| Custom agent loop | Free | None | High | Full control, most portable |

## Vector Database / Search
| Option | Cost | Azure-Native | Semantic Ranking | Notes |
|--------|------|-------------|-----------------|-------|
| ✅ **Azure AI Search Basic** | ~$75/month | Yes | Yes | Non-negotiable per brief |
| Azure AI Search Free | $0 | Yes | No | Acceptable fallback, loses reranking quality |
| Qdrant (self-hosted) | Free | No | No | Best vendor-independent alternative |
| pgvector | Included in DB | No | No | Simplest option if eliminating AI Search |
| Weaviate Cloud | Free tier | No | Built-in | Strong alternative with hybrid search |

## LLM
| Option | Cost/1M tokens (in) | Quality | Notes |
|--------|---------------------|---------|-------|
| ✅ **GPT-4o-mini** | $0.15 | Good | Best cost/quality for this use case |
| GPT-4o | $2.50 | Excellent | 17× more expensive — use for complex reasoning |
| GPT-4.1-mini | $0.40 | Very Good | Newer, strong reasoning at low cost |
| Claude 3.5 Haiku | $0.80 | Good | Strong alternative, not Azure-native |
| Llama 3.1 (self-hosted) | Free | Good | Full vendor independence, GPU required |

## Database
| Option | Cost | ORM Support | Notes |
|--------|------|-------------|-------|
| ✅ **Azure PostgreSQL Flexible B1ms** | ~$15/month | Excellent | Native JSONB, arrays, ENUMs |
| Azure SQL Basic | ~$5/month | Good | Cheaper but MSSQL dialect friction |
| Azure Cosmos DB | Free tier | Limited | Flexible schema, no relational integrity |
| Supabase | Free tier | Excellent | PostgreSQL + built-in auth — not Azure-native |

## Frontend Hosting
| Option | Cost | Next.js Support | Notes |
|--------|------|----------------|-------|
| ✅ **Azure Static Web Apps Free** | $0 | Good | Right for showcase |
| Vercel | Free tier | Excellent | Better Next.js support, non-Azure |
| Azure App Service | ~$13/month | Good | Unnecessary cost for static + API routes |

## Memory / Conversation State
| Option | Cost | Complexity | Notes |
|--------|------|-----------|-------|
| ✅ **AI Foundry Memory Store** | TBC (preview) | Low | Primary — native, managed |
| ✅ **PostgreSQL summaries** | Included | Low | Fallback — always implemented |
| mem0 | Free/self-hosted | Medium | Strong open-source alternative, Neo4j support |
| Redis + custom summarisation | ~$15/month | Medium | Full control, no preview risk |

## Email
| Option | Cost | Notes |
|--------|------|-------|
| ✅ **Azure Communication Services** | Free (100/day) | Azure-native, good showcase value |
| SendGrid | Free (100/day) | Better deliverability at scale |
| AWS SES | ~$0.10/1K | Cheapest at volume, not Azure-native |

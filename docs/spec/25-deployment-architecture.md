# 25 — Deployment Architecture

## Azure Services
```
Resource Group: insure-plus-rg

Application:
├── Azure App Service (B1)         FastAPI backend
└── Azure Static Web Apps (Free)   Next.js frontend

AI:
├── Azure AI Foundry               Primary + Analytics agents, Memory Store
├── Azure OpenAI                   gpt-4o-mini, text-embedding-3-small
└── Azure AI Search (Basic)        insurance-knowledge-base index

Data:
├── Azure PostgreSQL Flexible B1ms  Application database
└── Azure Blob Storage (LRS)       Knowledge base documents

Supporting:
├── Azure Communication Services   Policy confirmation emails
└── Azure Application Insights     Monitoring and logs
```

## App Service — Critical Settings
```
HTTP version: HTTP/2
Always On: ON        ← Prevents cold starts dropping SSE connections
ARR Affinity: OFF    ← Stateless backend, not needed
```
SSE requires `X-Accel-Buffering: no` header — disables Nginx proxy buffering. Without this, tokens batch rather than stream.

## Alembic Migrations
Run before app start in CI/CD pipeline:
```bash
alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000
```

## CI/CD — GitHub Actions
```yaml
on: push to main
jobs:
  deploy-backend:
    - Run pytest
    - Run alembic upgrade head
    - Deploy to App Service
  deploy-frontend:
    - npm run build
    - Deploy to Static Web Apps
```

## Project Structure
```
insure-plus/
├── backend/
│   ├── main.py, settings.py, requirements.txt
│   ├── alembic/versions/
│   ├── routers/         auth.py, chat.py, webhooks.py
│   ├── agents/          primary.py, analytics.py, tools/
│   ├── models/          db.py (SQLAlchemy), schemas.py (Pydantic)
│   └── services/        memory.py, quote.py, validation.py
├── frontend/
│   ├── app/             page.tsx, api/auth/, api/chat/
│   ├── components/      Chat.tsx, PaymentForm.tsx, ThreadSidebar.tsx
│   └── hooks/           useChatStream.ts, useAuth.ts
└── knowledge-base/
    ├── generic/, motor/, bike/, life/, device/
```

## Pre-Demo Checklist
```
Infrastructure:
[ ] All Azure services provisioned
[ ] App Service env vars configured
[ ] PostgreSQL accessible from App Service
[ ] Stripe webhook endpoint registered

AI Setup:
[ ] GPT-4o-mini and text-embedding-3-small deployed
[ ] 27 documents uploaded to blob storage
[ ] AI Search index created and verified (80–120 chunks)
[ ] Primary agent configured in portal
[ ] Analytics agent configured in portal
[ ] Memory Store created

Application:
[ ] Alembic migrations run
[ ] Demo user seeded with existing policy
[ ] SSE streaming tested end to end
[ ] Full policy creation flow tested
[ ] Stripe test card payment tested
[ ] Analytics agent trigger verified
```

## Monthly Cost (Showcase)
~$120/month total — see Section 28 for breakdown.

# FTC × n8n — Self-hosted Pipeline Orchestration

n8n is your always-on conductor. It triggers each phase on a schedule, hands
artifacts between agents, and notifies you when a drop is ready to ship.

## 60-second install (any machine with Docker)

```bash
cd ops/n8n
cp .env.example .env
# Open .env and fill: POSTGRES_PASSWORD, N8N_PASSWORD, N8N_ENCRYPTION_KEY,
# plus the provider keys you have (OPENROUTER, FAL, FIRECRAWL, ANTHROPIC).

docker compose up -d
open http://localhost:5678
```

First boot: log in with the `N8N_USER` / `N8N_PASSWORD` you set, then
`Import from File` → `workflows/ftc_pipeline.json`. Activate it.

## What it runs

```
Daily 04:00 (or manual)
   ↓
Phase 1 · Scrape          → artifacts/scrapes/reference_synthesis.json
   ↓
Phase 2 · Test Batch (5)  → kills bad concepts, unlocks Phase 3
   ↓
Phase 3 · Generate 1000   → artifacts/collection_v1/{svg,concepts,catalog.html}
   ↓
Phase 4 · Render (50/day) → photoreal via Fal.ai (rate-limited by your budget)
   ↓
Notify                    → Slack / Discord / email
```

The 50-per-day cap on rendering keeps Fal spend under `FTC_DAILY_BUDGET_USD`
from your `.env`. Bump it once you trust the pipeline.

## Hosting recommendations

| Environment | Cost | Notes |
| :--- | :--- | :--- |
| Your laptop | $0 | fine for dev; shuts off when you do |
| **Hetzner CX22** | **~$4/mo** | recommended; 24/7, fast disks |
| Railway / Render | $7-25/mo | one-click; managed Postgres |
| Fly.io | $5+/mo | global; good for webhooks |
| AWS Lightsail | $5/mo | familiar if you already use AWS |

Put it behind Cloudflare Tunnel or Caddy for HTTPS + Basic auth.

## Where keys live

Keys live in this folder's `.env` (gitignored). When n8n calls a node, it
pulls credentials from container environment variables — they never appear
in the workflow JSON file.

Rotate the n8n encryption key once on first boot, then never share it.

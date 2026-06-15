# Family AI Budget Assistant — Session Handoff

> Last updated: 2026-06-15
> Status: **Phase 1 complete** — Railway deploy 95% done (one step remaining)

---

## What This Project Is

AI-powered family shopping optimizer for the Bulgarian market. The core question it answers:

> "How should my family shop this week to spend the least money, time and effort?"

This is fundamentally different from competitors (Pazarko, Shopko, Veliko) that only do product-level price lookup. We operate at the **basket level** and add route planning, fake promotion detection, predictive needs, and bulk-buying logic.

---

## Current State (as of 2026-06-15)

### Phase 1 — Foundation ✅ COMPLETE + Deployed

All Phase 1 code is committed and pushed to GitHub (`main` branch, 3 commits).

---

## Railway Project: `remarkable-optimism`

**Project ID:** `fd3ea5bf-8079-4232-a1d9-1052f67a899a`

| Service | Status | Domain |
|---------|--------|--------|
| `backend` | GitHub-linked, Root Dir = `backend` | `https://backend-production-3cd8.up.railway.app` |
| `frontend` | GitHub-linked, Root Dir = `frontend` | `https://frontend-production-4b3f.up.railway.app` |
| `Postgres` | ✅ Online (managed, has volume) | `postgres.railway.internal:5432` |
| `Redis` | ✅ Online (managed, has volume) | `redis.railway.internal:6379` |

**Old project `family-budget-assistant`** — ignore/delete. Full of duplicates, never successfully deployed.

---

## ⚠️ Pick up here next session

### Step 1 — Set ANTHROPIC_API_KEY on backend (you must provide the key)
```bash
railway link  # select: remarkable-optimism → production
railway variables --service backend --set "ANTHROPIC_API_KEY=sk-ant-YOUR_KEY"
```

### Step 2 — Push to GitHub to trigger deploys (if not already done)
```bash
git push origin main
```
Railway will auto-deploy both services from GitHub on push.

### Step 3 — Verify backend is live
```bash
curl https://backend-production-3cd8.up.railway.app/health
# expect: {"status": "ok"}
```
The `releaseCommand = "alembic upgrade head"` in `backend/railway.toml` runs migrations automatically before uvicorn starts.

### Step 4 — Run seed data locally against Railway DB
```bash
cd backend
DATABASE_URL=postgresql+asyncpg://postgres:<PG_PASS>@acela.proxy.rlwy.net:<PORT>/railway python -m scraper.seed
```
Get `PG_PASS` and `PORT` from Railway dashboard → Postgres service → Variables → `PGPASSWORD` and `RAILWAY_TCP_PROXY_PORT`.

### Step 5 — Verify full flow
1. Open `https://frontend-production-4b3f.up.railway.app`
2. Register → Login → Dashboard shows seed data
3. Products search → search "мляко" → returns EUR prices

---

## What was fixed during the Railway deploy sessions (2026-06-15)

| Problem | Fix |
|---------|-----|
| Railway using Railpack instead of Dockerfile | Added `backend/Procfile` with uvicorn start command |
| `next@14.2.18` blocked by Railway security scan | Upgraded to `14.2.35` |
| Frontend Docker build failing | Added `frontend/public/.gitkeep` (Docker COPY needs dir to exist) |
| Backend DATABASE_URL pointing to wrong host | Fixed to `postgres.railway.internal` (Postgres service in same project) |
| pgvector not enabled | Ran `CREATE EXTENSION IF NOT EXISTS vector` on new Postgres |
| Old `family-budget-assistant` project | Abandoned — use `remarkable-optimism` |

---

## Environment Variables — `remarkable-optimism` backend service

| Variable | Value |
|----------|-------|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:<pass>@postgres.railway.internal:5432/railway` |
| `REDIS_URL` | `redis://default:<pass>@redis.railway.internal:6379` |
| `SECRET_KEY` | set ✅ |
| `ENCRYPTION_KEY` | set ✅ |
| `ENVIRONMENT` | `production` |
| `ANTHROPIC_API_KEY` | ❌ **NOT SET — required before backend works** |

Frontend has `API_URL=https://backend-production-3cd8.up.railway.app` set ✅

---

## Git State

```
main branch (GitHub: PeterStoyanov83/family-budget-assistant)

0ba781b  fix: add Procfile for Railpack + upgrade Next.js to 14.2.35
9948dae  fix: add public/.gitkeep so Docker COPY step doesn't fail  ← may not be pushed yet
881ee3f  feat: Phase 1 complete — full backend, frontend, scraper + Railway deploy config
d18f7d4  init: Family AI Budget Assistant — project scaffold
```

**Commits that may not be pushed yet:** `9948dae` (public/.gitkeep) and `0ba781b` (Procfile + Next.js).
Run `git status` and `git push origin main` to confirm.

---

## How to Start the App Locally

```bash
cp .env.example .env          # fill in ANTHROPIC_API_KEY etc.
docker compose up
docker compose exec backend alembic upgrade head
docker compose exec -e PYTHONPATH=/scraper:/app backend python /scraper/seed.py

# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# API docs: http://localhost:8000/docs
```

---

## Not yet built (Phase 2+)
- `POST /optimize` — Claude AI basket optimization (Phase 2)
- `GET /route` — Mapbox route optimization (Phase 2)
- Celery task bodies (`score_promotions`, `anonymize_deleted_users` — stubbed)
- Klaviyo onboarding emails (Phase 2)
- Amplitude EU analytics (Phase 2)
- Stripe billing (Phase 3)
- Billa, Fantastico, T-Market, DM, Metro scrapers (Phase 2)
- Tests (none yet)

---

## The Three MVP Phases

### Phase 1 — Foundation ✅ DONE
Auth · product catalog · Lidl+Kaufland scraping · shopping lists · price comparison · dashboard · GDPR soft-delete

### Phase 2 — Intelligence ← NEXT
`POST /optimize` with Claude AI (Master Prompt v2.1) · promotion scoring Celery task · route optimization (Mapbox) · BigQuery price history · +5 chains · Klaviyo · Amplitude EU

### Phase 3 — Growth
Predictive shopping · bulk buying · household analytics · loyalty card pricing · Stripe billing · mobile PWA · B2B

---

## Key Business Rules (non-negotiable)

1. **All prices in EUR** — Bulgaria adopted the Euro; never use BGN/лв.
2. **Basket optimization always** — never optimize individual products in isolation.
3. **Every promotion must be scored** — REAL / AVERAGE / FAKE against 30-day history.
4. **Transport threshold** — only recommend extra stores if net saving > 5 € after fuel + time.
5. **Unit price normalization** — always compare €/kg or €/l, never package price.
6. **GDPR from day one** — soft delete on all models, AES-256 on personal data, Amplitude EU only.

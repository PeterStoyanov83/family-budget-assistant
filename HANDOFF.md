# Family AI Budget Assistant — Session Handoff

> Last updated: 2026-06-16
> Status: **Phase 1 deployed — CORS blocker on backend, root cause = deploy pipeline**

---

## What This Project Is

AI-powered family shopping optimizer for the Bulgarian market. Core question:
> "How should my family shop this week to spend the least money, time and effort?"

---

## Current State (as of 2026-06-16)

### Phase 1 — Foundation ✅ Code complete, Railway deploy PARTIALLY working

Frontend deploys correctly. Backend is online but stuck on old deployment.

---

## Railway Project: `remarkable-optimism`

| Service | Status | Domain |
|---------|--------|--------|
| `backend` | Online but OLD code running | `https://backend-production-3cd8.up.railway.app` |
| `frontend` | ✅ Deploying correctly | `https://frontend-production-4b3f.up.railway.app` |
| `Postgres` | ✅ Online | `postgres.railway.internal:5432` |
| `Redis` | ✅ Online | `redis.railway.internal:6379` |

---

## ⚠️ THE BLOCKER — Pick up here next session

### Root Problem
The backend service is stuck running an OLD Docker image. Every new deployment fails silently. The CORS error in the browser (`No 'Access-Control-Allow-Origin' header`) is a symptom — the real issue is Railway not activating new backend deployments.

### Diagnostic Step 1 — Confirm old code is running
```bash
curl https://backend-production-3cd8.up.railway.app/health
```
- If response has `"build":"cors-v3"` → NEW code is live (CORS fix worked, investigate further)
- If response does NOT have `"build":"cors-v3"` → OLD code confirmed, Railway deploy pipeline broken

### Diagnostic Step 2 — Check deploy logs
Go to Railway dashboard → backend service → **Deployments tab** → click the latest deployment → read the build/deploy logs. Look for errors.

### Most Likely Causes
1. **`alembic upgrade head` was failing as `releaseCommand`** — This blocked every deployment since day 1. Fixed in commit `0fcdad8` (moved to startCommand with `;`).
2. **Docker build failing** — Check Railway build logs for Python package install errors.
3. **Health check failing before app starts** — `healthcheckTimeout = 30` might be too short if alembic takes time.

### Fix Already In Code (commit `0fcdad8`)
`backend/railway.toml` now has:
```toml
startCommand = "alembic upgrade head; uvicorn app.main:app --host 0.0.0.0 --port $PORT"
```
No more `releaseCommand` that blocks deployment.

### If Deploy Still Fails
Try increasing health check timeout in `backend/railway.toml`:
```toml
healthcheckTimeout = 60
```
Or temporarily remove the health check to rule it out.

---

## Architecture — How Frontend Connects to Backend

```
Browser → https://backend-production-3cd8.up.railway.app (direct CORS calls)
```

| Service | Variable | Value | Where set |
|---|---|---|---|
| Frontend | `NEXT_PUBLIC_API_URL` | `https://backend-production-3cd8.up.railway.app` | `frontend/.env.production` (in repo) |
| Backend | `CORS_ORIGINS` | `http://localhost:3000,https://frontend-production-4b3f.up.railway.app` | Railway dashboard + baked in `config.py` default |

### CORS Implementation
`backend/app/main.py` has a custom `@app.middleware("http")` that:
- Handles OPTIONS preflight returning 200 + CORS headers
- Allows any `*.up.railway.app` origin AND explicit `cors_origins` list
- Uses `samesite="none"; secure=True` in production for cross-origin cookies

---

## Environment Variables

### Backend (Railway dashboard)
| Variable | Value | Status |
|----------|-------|--------|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:<pass>@postgres.railway.internal:5432/railway` | ✅ |
| `REDIS_URL` | `redis://default:<pass>@redis.railway.internal:6379` | ✅ |
| `SECRET_KEY` | set | ✅ |
| `ENCRYPTION_KEY` | set | ✅ |
| `ENVIRONMENT` | `production` | ✅ |
| `ANTHROPIC_API_KEY` | set | ✅ |
| `CORS_ORIGINS` | `http://localhost:3000,https://frontend-production-4b3f.up.railway.app` | ✅ |

### Frontend (Railway dashboard)
- `NEXT_PUBLIC_API_URL` should be DELETED from dashboard (now in `frontend/.env.production`)
- If it still exists with a trailing space, delete it

---

## Git State

```
main branch — latest commits:
3c8c629  chore: add build marker to health endpoint for deploy verification
0fcdad8  fix: move alembic out of releaseCommand into startCommand
1f5efc9  config: bake Railway URLs into repo (frontend/.env.production + cors default)
7f5c73e  fix: replace CORSMiddleware with explicit custom CORS middleware
ec0d4f8  fix: drop proxy — browser calls backend directly via NEXT_PUBLIC_API_URL
```

---

## How to Start Locally

```bash
cp .env.example .env          # fill in ANTHROPIC_API_KEY
docker compose up
docker compose exec backend alembic upgrade head
```

Frontend: http://localhost:3000 | Backend: http://localhost:8000

---

## Not Yet Built (Phase 2+)
- `POST /optimize` — Claude AI basket optimization
- `GET /route` — Mapbox route optimization
- Celery task bodies (score_promotions, anonymize_deleted_users — stubbed)
- Klaviyo onboarding emails
- Amplitude EU analytics
- Stripe billing
- Billa, Fantastico, T-Market, DM, Metro scrapers
- Tests

## The Three MVP Phases

### Phase 1 — Foundation (code complete, deploy blocked)
Auth · product catalog · Lidl+Kaufland scraping · shopping lists · price comparison · dashboard · GDPR soft-delete

### Phase 2 — Intelligence ← NEXT after deploy fixed
`POST /optimize` with Claude AI · promotion scoring · route optimization (Mapbox) · BigQuery · +5 chains · Klaviyo · Amplitude EU

### Phase 3 — Growth
Predictive shopping · bulk buying · loyalty cards · Stripe · mobile PWA · B2B

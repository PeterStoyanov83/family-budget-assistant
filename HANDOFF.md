# Family AI Budget Assistant — Session Handoff

> Last updated: 2026-06-16
> Status: **Phase 1 deployed — awaiting confirmation that CORS fix is live**

---

## What This Project Is

AI-powered family shopping optimizer for the Bulgarian market.
> "How should my family shop this week to spend the least money, time and effort?"

---

## Current State (as of 2026-06-16)

### Phase 1 — Foundation ✅ Code complete, Railway deploy unblocked (pending verify)

The root cause of all CORS failures was identified and fixed:
- `alembic upgrade head` ran BEFORE uvicorn in `startCommand`
- It took >30s → health check killed the deployment → Railway rolled back to old image
- Every backend push for the past session was silently reverted

---

## Railway Project: `remarkable-optimism`

| Service | Domain |
|---------|--------|
| `backend` | `https://backend-production-3cd8.up.railway.app` |
| `frontend` | `https://frontend-production-4b3f.up.railway.app` |
| `Postgres` | `postgres.railway.internal:5432` ✅ |
| `Redis` | `redis.railway.internal:6379` ✅ |

---

## ⚠️ Pick up here next session

### Step 1 — Confirm new backend code is live
```bash
curl https://backend-production-3cd8.up.railway.app/health
```
- `"build":"cors-v3"` in response → new code is live ✅
- No `build` field → still old code → check Railway deploy logs again

### Step 2 — Test frontend
Open `https://frontend-production-4b3f.up.railway.app` → Register → Login → Dashboard

### Step 3 — If CORS still fails after new code confirmed live
Check Railway backend → Variables → confirm `CORS_ORIGINS` is set to:
```
http://localhost:3000,https://frontend-production-4b3f.up.railway.app
```
(Already baked as default in `config.py` so this should not be needed)

### Step 4 — Run seed data (once auth works)
```bash
# Get PG connection details from Railway dashboard → Postgres → Variables
DATABASE_URL=postgresql+asyncpg://postgres:<PG_PASS>@<PROXY_HOST>:<PORT>/railway \
  python -m scraper.seed
```

---

## What Was Fixed This Session (2026-06-16)

| Problem | Fix | Commit |
|---------|-----|--------|
| Next.js `rewrites()` read `API_URL` at build time, not runtime | Drop proxy entirely; browser calls backend directly via `NEXT_PUBLIC_API_URL` | `ec0d4f8` |
| `NEXT_PUBLIC_API_URL` not embedded in build | Added `ARG NEXT_PUBLIC_API_URL` to frontend Dockerfile | `ec0d4f8` |
| `NEXT_PUBLIC_API_URL` had trailing space in Railway var | Baked correct URL into `frontend/.env.production` (committed to repo) | `1f5efc9` |
| CORS blocked cross-origin requests | Replaced FastAPI CORSMiddleware with custom `@app.middleware("http")` | `7f5c73e` |
| Backend never deployed new code | `alembic upgrade head` as `releaseCommand` blocked every deploy for >30s | `dde8eea` |
| Health check killed deploys | uvicorn now starts immediately; alembic runs via `startup` event in background | `dde8eea` |
| CORS origins hardcoded to localhost only | `cors_origins` default in `config.py` includes Railway frontend URL | `1f5efc9` |
| Auth cookies blocked cross-origin | `SameSite=None; Secure=True` in production | `ec0d4f8` |

---

## Architecture — How Frontend Connects to Backend

```
Browser
  │  fetch("https://backend-production-3cd8.up.railway.app/auth/login")
  │  NEXT_PUBLIC_API_URL embedded in bundle at build time (frontend/.env.production)
  ▼
Railway Backend (FastAPI)
  │  Custom CORS middleware: allows *.up.railway.app + explicit list
  │  SameSite=None cookies for cross-origin auth
  ▼
Railway Postgres + Redis
```

**No proxy.** Browser calls backend directly. All CORS handled in `backend/app/main.py`.

---

## Key Files Changed This Session

| File | What changed |
|------|-------------|
| `frontend/.env.production` | `NEXT_PUBLIC_API_URL=https://backend-production-3cd8.up.railway.app` |
| `frontend/Dockerfile` | `ARG NEXT_PUBLIC_API_URL` → `ENV` in builder stage |
| `frontend/lib/api.ts` | `API_BASE = process.env.NEXT_PUBLIC_API_URL ?? ""` |
| `frontend/next.config.mjs` | Removed broken `rewrites()` |
| `backend/app/main.py` | Custom CORS middleware + startup migration event |
| `backend/app/core/config.py` | `cors_origins` default includes Railway frontend URL |
| `backend/app/core/security.py` | `SameSite=None` in production for cross-origin cookies |
| `backend/railway.toml` | `startCommand = uvicorn` only; `healthcheckTimeout = 120` |
| `.gitignore` | `.env.production` removed (safe to commit — no secrets) |

---

## Environment Variables

### Backend (Railway dashboard — secrets only)
| Variable | Status |
|----------|--------|
| `DATABASE_URL` | ✅ set |
| `REDIS_URL` | ✅ set |
| `SECRET_KEY` | ✅ set |
| `ENCRYPTION_KEY` | ✅ set |
| `ENVIRONMENT` | ✅ `production` |
| `ANTHROPIC_API_KEY` | ✅ set |
| `CORS_ORIGINS` | ✅ set (also baked in code default) |

### Frontend (Railway dashboard)
- `NEXT_PUBLIC_API_URL` — **delete this if it exists with trailing space**; value now in `frontend/.env.production`

---

## Git State (latest commits)

```
dde8eea  fix: health check was killing deploys before uvicorn could start
ce44c9e  docs: update HANDOFF.md
3c8c629  chore: add build marker to health endpoint for deploy verification
0fcdad8  fix: move alembic out of releaseCommand into startCommand
1f5efc9  config: bake Railway URLs into repo (frontend/.env.production)
7f5c73e  fix: replace CORSMiddleware with explicit custom CORS middleware
ec0d4f8  fix: drop proxy — browser calls backend directly via NEXT_PUBLIC_API_URL
```

---

## How to Start Locally

```bash
cp .env.example .env   # fill in ANTHROPIC_API_KEY and other secrets
docker compose up
# migrations run automatically via startup event
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# API docs: http://localhost:8000/docs
```

---

## Not Yet Built (Phase 2+)

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

### Phase 1 — Foundation (code done, deploy being verified)
Auth · product catalog · Lidl+Kaufland scraping · shopping lists · price comparison · dashboard · GDPR soft-delete

### Phase 2 — Intelligence ← NEXT after Phase 1 verified
`POST /optimize` with Claude AI (Master Prompt v2.1) · promotion scoring Celery task · route optimization (Mapbox) · BigQuery price history · +5 chains · Klaviyo · Amplitude EU

### Phase 3 — Growth
Predictive shopping · bulk buying · household analytics · loyalty card pricing · Stripe billing · mobile PWA · B2B

---

## Key Business Rules (non-negotiable)

1. **All prices in EUR** — Bulgaria adopted the Euro; never use BGN/лв.
2. **Basket optimization always** — never optimize individual products.
3. **Every promotion must be scored** — REAL / AVERAGE / FAKE against 30-day history.
4. **Transport threshold** — only recommend extra stores if net saving > 5 € after fuel + time.
5. **Unit price normalization** — always compare €/kg or €/l, never package price.
6. **GDPR from day one** — soft delete on all models, AES-256 on personal data, Amplitude EU only.

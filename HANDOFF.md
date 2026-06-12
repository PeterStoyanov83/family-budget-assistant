# Family AI Budget Assistant — Session Handoff

> Last updated: 2026-06-12
> Status: **Phase 1 complete** — Deploying to Railway (in progress)

---

## What This Project Is

AI-powered family shopping optimizer for the Bulgarian market. The core question it answers:

> "How should my family shop this week to spend the least money, time and effort?"

This is fundamentally different from competitors (Pazarko, Shopko, Veliko) that only do product-level price lookup. We operate at the **basket level** and add route planning, fake promotion detection, predictive needs, and bulk-buying logic.

---

## Current State (as of 2026-06-12)

### Phase 1 — Foundation ✅ COMPLETE

**Infrastructure**
- `docker-compose.yml` — postgres (pgvector/pgvector:pg16), redis, backend, celery, frontend — one `docker compose up` starts everything
- `backend/Dockerfile` and `frontend/Dockerfile` ready
- `.env.example` at root for API keys

**Backend**
- `backend/app/core/database.py` — async SQLAlchemy engine + session factory
- `backend/app/core/security.py` — JWT in HttpOnly cookies (access 30min, refresh 30d), bcrypt, cookie set/clear helpers
- `backend/app/core/deps.py` — `CurrentUser` FastAPI dependency
- `backend/app/core/config.py` — Pydantic Settings with `encryption_key` field added
- `backend/app/worker.py` — Celery app; `score_promotions` and `anonymize_deleted_users` tasks stubbed
- All models: `User`, `LoyaltyCard`, `Store`, `Product` (pgvector 1536-dim), `Price`, `Promotion`, `PurchaseHistory`, `ShoppingList`, `ListItem`, `BasketOptimization`
- All schemas: auth, product, promotion, shopping_list
- All routers: auth, products, promotions, lists
- `backend/app/main.py` — all routers wired, `/health` and `/metrics`
- Alembic: `alembic.ini`, async `alembic/env.py`, `001_initial_schema.py` migration (pgvector extension + all tables)
- `email-validator` added to `requirements.txt`

**API endpoints implemented**
```
POST   /auth/register
POST   /auth/login
POST   /auth/refresh
POST   /auth/logout
DELETE /auth/account       soft-delete → Celery anonymization
GET    /auth/me
GET    /auth/gdpr/export   full JSON data export

GET    /products/search
GET    /products/{id}/price-history
GET    /products/{id}/alternatives  (pgvector cosine, falls back to category)

GET    /promotions
GET    /promotions/{id}/score

GET    /lists
POST   /lists
GET    /lists/{id}
PATCH  /lists/{id}
DELETE /lists/{id}
POST   /lists/{id}/items
PATCH  /lists/{id}/items/{item_id}
DELETE /lists/{id}/items/{item_id}

GET    /health
GET    /metrics
```

**Scraper**
- `scraper/base.py` — `BaseScraper` ABC, `ScrapedPrice` dataclass, `compute_unit_price`, `score_promotion`
- `scraper/lidl.py` — Playwright scraper for Lidl BG offers page
- `scraper/kaufland.py` — Playwright scraper for Kaufland BG offers, handles member card pricing
- `scraper/seed.py` — seeds 4 stores (Lidl + Kaufland Sofia), 20 products, prices, 5 promotions with realistic EUR data; run with `python -m scraper.seed`

**Frontend (Next.js 14 + TypeScript + Tailwind)**
- `frontend/` fully scaffolded: `package.json`, `tsconfig.json`, `tailwind.config.ts`, `postcss.config.js`, `next.config.ts`
- Design tokens wired (`--color-primary: #2D6A4F`, `--color-real: #52B788`, `--color-fake: #E63946`, `--color-warning: #F4A261`)
- `lib/api.ts` — typed API client for all Phase 1 endpoints, all TypeScript interfaces
- `lib/auth-context.tsx` — `AuthProvider` + `useAuth` hook (checks `/auth/me` on mount)
- `lib/utils.ts` — `cn()`, `formatEur()`, `formatUnitPrice()`
- `components/ui/button.tsx` — CVA button variants (default/outline/ghost/destructive)
- `components/ui/input.tsx` — styled input
- `components/promotion-badge.tsx` — РЕАЛНА/СРЕДНА/ФАЛШИВА badge with design token colors
- `components/nav.tsx` — top nav with Табло / Списъци / Продукти / Изход
- `app/(auth)/login/page.tsx` — login form with zod validation
- `app/(auth)/register/page.tsx` — register form (email, password, name, household size, city, has_car)
- `app/(app)/layout.tsx` — auth guard + nav
- `app/(app)/dashboard/page.tsx` — stats cards, recent lists, real promotions feed
- `app/(app)/lists/page.tsx` — list CRUD with create form
- `app/(app)/lists/[id]/page.tsx` — list detail with item CRUD, check-off, progress bar
- `app/(app)/products/page.tsx` — live search with price comparison table per product

### Not yet built (Phase 2+)
- `POST /optimize` — Claude AI basket optimization (Phase 2)
- `GET /route` — Mapbox route optimization (Phase 2)
- `GET /recommendations/{user_id}` — predictive shopping (Phase 2)
- `GET /budget/analytics` — household analytics (Phase 3)
- BigQuery price history warehouse (Phase 2)
- Celery task bodies (`score_promotions`, `anonymize_deleted_users` — stubbed)
- Klaviyo onboarding emails (Phase 2)
- Amplitude EU analytics (Phase 2)
- Stripe billing (Phase 3)
- Billa, Fantastico, T-Market, DM, Metro scrapers (Phase 2)
- Loyalty card pricing in optimizer (Phase 2)
- Tests (none yet)

---

## How to Start the App

### Local (Docker Compose)
```bash
cp .env.example .env          # fill in ANTHROPIC_API_KEY etc.
docker compose up
docker compose exec backend alembic upgrade head
docker compose exec -e PYTHONPATH=/scraper:/app backend python /scraper/seed.py

# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# API docs: http://localhost:8000/docs
```

Note: `docker-compose.yml` mounts `./scraper:/scraper` in the backend container so the seed script is accessible.

### Production (Railway)
Railway project: **family-budget-assistant**  
Railway project ID: `122eff23-65f6-419a-bd17-a76ea80a4c45`

**Services (after cleanup):**
| Service | Type | Status |
|---------|------|--------|
| backend | Dockerfile from `backend/` | Deploying |
| frontend | Dockerfile from `frontend/` | Deploying |
| Postgres-Oj9V | Railway managed Postgres | Online ✅ |
| Redis | Railway managed Redis (with volume) | Online ✅ |

**⚠️ Remaining deploy steps (pick up here next session):**

1. **Delete duplicate services** in the Railway dashboard — remove `postgres`, `Postgres`, `Postgres-BN0I` (Docker image duplicates), and `redis` (Docker image). Keep `Postgres-Oj9V` and `Redis` (the managed ones with volume icons).

2. **Fix backend DATABASE_URL** — click `Postgres-Oj9V` → Variables → copy its `DATABASE_URL`, then go to backend service → Variables → update `DATABASE_URL` replacing `postgresql://` with `postgresql+asyncpg://`.

3. **Generate backend public domain** — backend → Settings → Networking → Generate Domain.

4. **Set frontend API_URL** — frontend → Variables → add `API_URL=https://<backend-domain>.railway.app`.

5. **Run migration + seed on Railway** (once backend is live):
   ```bash
   railway run --service backend alembic upgrade head
   railway run --service backend python /scraper/seed.py
   ```
   Note: seed won't find `/scraper` on Railway — need to either copy seed data into backend or run via SSH. Simplest: run it locally against the Railway DB by temporarily setting `DATABASE_URL` in your local shell to the Railway postgres URL.

6. **Enable pgvector extension** on Postgres-Oj9V:
   ```bash
   railway connect Postgres-Oj9V
   # then in psql:
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

---

## Repository Layout

```
.planning/
  PROJECT.md              — Vision, personas, MVP phases, success metrics
  TECHNICAL_SPEC.md       — Full stack, API endpoints, DB schema, KPIs
  MASTER_PROMPT.md        — Master Prompt v2.1 (canonical, synced from Full_prompt.md)
  research/
    COMPETITIVE_ANALYSIS.md

Full_prompt.md            — Source of truth for Master Prompt (keep in sync with MASTER_PROMPT.md)

docker-compose.yml
.env.example

backend/
  Dockerfile
  alembic.ini
  alembic/
    env.py
    versions/001_initial_schema.py
  app/
    main.py               — FastAPI app + all routers
    worker.py             — Celery app + task stubs
    core/
      config.py           — Pydantic Settings
      database.py         — async engine + Base
      security.py         — JWT cookies + bcrypt
      deps.py             — CurrentUser dependency
    models/               — SQLAlchemy 2 async models (all tables)
    schemas/              — Pydantic v2 schemas
    routers/              — auth, products, promotions, lists
  requirements.txt

scraper/
  chains.py               — CHAINS config dict (all 7 stores)
  base.py                 — BaseScraper + ScrapedPrice
  lidl.py                 — LidlScraper (Playwright)
  kaufland.py             — KauflandScraper (Playwright)
  seed.py                 — Dev seed data (run once after migration)
  requirements.txt

frontend/
  Dockerfile
  package.json
  tsconfig.json / tailwind.config.ts / next.config.ts
  .env.local.example
  app/
    layout.tsx            — Root layout + AuthProvider
    page.tsx              — Redirects to /dashboard or /login
    (auth)/
      login/page.tsx
      register/page.tsx
    (app)/
      layout.tsx          — Auth guard + Nav
      dashboard/page.tsx
      lists/
        page.tsx          — List CRUD
        [id]/page.tsx     — List detail + item management
      products/page.tsx   — Price comparison search
  components/
    nav.tsx
    promotion-badge.tsx   — РЕАЛНА/СРЕДНА/ФАЛШИВА with design token colors
    ui/button.tsx
    ui/input.tsx
  lib/
    api.ts                — Typed API client + all TypeScript interfaces
    auth-context.tsx      — AuthProvider + useAuth
    utils.ts              — cn(), formatEur(), formatUnitPrice()
```

---

## Architecture at a Glance

| Layer | Technology | Status |
|-------|-----------|--------|
| Frontend | Next.js 14 + TypeScript + Tailwind + shadcn/ui | ✅ Phase 1 done |
| State | Zustand 4 + TanStack Query 5 | Partial (auth context done; TanStack not yet wired) |
| Backend | FastAPI + Python 3.12 | ✅ Phase 1 done |
| Auth | JWT + HttpOnly cookies | ✅ Done |
| Primary DB | PostgreSQL 16 + pgvector | ✅ Schema + migration done |
| Cache | Redis 7 | ✅ In Docker Compose; not yet used in API |
| Queue | Celery + Redis | ✅ Stubbed (tasks not implemented) |
| ORM | SQLAlchemy 2 async + Alembic | ✅ Done |
| AI | claude-sonnet-4-6 via Anthropic SDK | Phase 2 |
| Warehouse | BigQuery (price history) | Phase 2 |
| Scraping | Playwright + BeautifulSoup4 + APScheduler | ✅ Lidl + Kaufland + seed |
| Maps | Mapbox GL JS | Phase 2 |
| Analytics | Amplitude EU | Phase 2 |
| Notifications | Klaviyo | Phase 2 |
| Payments | Stripe (EUR) | Phase 3 |

---

## Key Business Rules (non-negotiable)

1. **All prices in EUR** — Bulgaria adopted the Euro; never use BGN/лв.
2. **Basket optimization always** — never optimize individual products in isolation.
3. **Every promotion must be scored** — REAL / AVERAGE / FAKE against 30-day history.
4. **Transport threshold** — only recommend extra stores if net saving > 5 € after fuel (0.06 €/km) + time (0.50 €/min).
5. **Unit price normalization** — always compare €/kg or €/l, never package price.
6. **GDPR from day one** — soft delete on all models, AES-256 on personal data columns, Amplitude EU only.

---

## Promotion Scoring Logic

```python
real_discount = (hist_avg_30d - promo_price) / hist_avg_30d

if real_discount > 0.10:  score = 'real'
elif real_discount >= 0:  score = 'average'
else:                     score = 'fake'
```

Implemented in: `scraper/base.py:score_promotion()` and `backend/app/routers/promotions.py:compute_promotion_score()`

---

## The Three MVP Phases

### Phase 1 — Foundation ✅ DONE
Auth · product catalog · Lidl+Kaufland scraping · shopping lists · price comparison · dashboard · GDPR soft-delete

### Phase 2 — Intelligence ← NEXT
`POST /optimize` with Claude AI (Master Prompt v2.1 in `.planning/MASTER_PROMPT.md`) · promotion scoring Celery task · unit price normalization · route optimization (Mapbox) · BigQuery price history · +5 chains (Billa, Fantastico, T-Market, DM, Metro) · Klaviyo onboarding · Amplitude EU

### Phase 3 — Growth
Predictive shopping · bulk buying logic · household analytics · loyalty card pricing · Stripe billing (EUR) · mobile PWA · B2B pipeline

---

## Pricing Plans

| Plan | Price |
|------|-------|
| Free | 0 €/month |
| Family | 2.99 €/month |
| Family Plus | 4.99 €/month |
| Premium Household | 7.99 €/month |
| B2B Analytics | on request |

---

## Design Tokens

```
--color-primary:  #2D6A4F
--color-real:     #52B788   (genuine promotion)
--color-fake:     #E63946   (fake promotion)
--color-warning:  #F4A261   (average promotion)
--border-radius:  12px
--tap-target-min: 44px
```

---

## Scraper Schedule

| Chain | Engine | Day | Time |
|-------|--------|-----|------|
| Billa | BeautifulSoup | Monday | 06:00 |
| DM | BeautifulSoup | Monday | 06:00 |
| Metro | Playwright | Tuesday | 06:00 |
| Kaufland | Playwright | Wednesday | 06:00 |
| Fantastico | BeautifulSoup | Wednesday | 06:00 |
| Lidl | Playwright | Thursday | 06:00 |
| T-Market | BeautifulSoup | Thursday | 06:00 |

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Activation rate (register → first optimize) | > 40% |
| D7 retention | > 35% |
| Avg saving / session | > 5 € |
| Fake promotion detection accuracy | > 80% |
| Free → paid conversion | > 8% |
| MRR Month 6 | > 2 500 € |
| API p95 latency | < 300ms |
| AI endpoint p95 | < 3s |

---

## How to Pick Up Work

```bash
# Check current state
/gsd-progress

# Start Phase 2 (Intelligence — Claude AI basket optimization)
/gsd-discuss-phase 2
/gsd-plan-phase 2
/gsd-execute-phase 2
```

The full AI shopping assistant prompt (injected at `POST /optimize`) is in `.planning/MASTER_PROMPT.md`.
`Full_prompt.md` in the project root is the source that was used to sync it — keep the two in lockstep.
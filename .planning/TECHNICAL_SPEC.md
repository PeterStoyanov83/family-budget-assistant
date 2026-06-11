# Family AI Budget Assistant — Technical Specification v1.1

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, TypeScript 5, Tailwind CSS, shadcn/ui |
| State | Zustand 4, TanStack Query 5 |
| Forms | React Hook Form 7, Zod 3 |
| Maps | Mapbox GL JS |
| i18n | next-i18next (Bulgarian default) |
| Backend | FastAPI, Python 3.12 |
| Queue | Celery + Redis 7 |
| ORM | SQLAlchemy 2 async + Alembic |
| Auth | JWT + refresh tokens |
| Validation | Pydantic v2 |
| Primary DB | PostgreSQL 16 + pgvector |
| Cache | Redis 7 |
| Warehouse | BigQuery |
| AI | claude-sonnet-4-6 via Anthropic SDK |
| Embeddings | text-embedding-3-small (product matching) |
| Scraping | Playwright, BeautifulSoup4, APScheduler, Tesseract |
| Analytics | Amplitude EU (GDPR) |
| Notifications | Klaviyo |
| CRM | HubSpot |
| Support | Intercom |
| Project mgmt | Linear + Notion |
| Design | Figma |
| Payments | Stripe (EUR) |
| Hosting | Railway/Render → AWS ECS |
| CDN | Cloudflare |

## Services

```
User Service       — auth, profiles, household data
Product Service    — catalog, search, pgvector matching
Promotion Service  — scraping, scoring, history
Basket Service     — optimization via Claude AI
Route Service      — Mapbox routing, fuel calculation
Budget Service     — spending tracking, forecasts
Recommendation     — predictive shopping, alternatives
Analytics Service  — BigQuery sync, household insights
Notification       — Klaviyo email/push
```

## API Endpoints

```
POST   /auth/register
POST   /auth/login
POST   /auth/refresh
DELETE /auth/account              GDPR: anonymizes in 30 days
GET    /gdpr/export               Returns all user data as JSON

GET    /products/search?q=&store=
GET    /products/{id}/price-history
GET    /products/{id}/alternatives

GET    /promotions?store=&category=&valid=true
GET    /promotions/{id}/score

POST   /lists
GET    /lists/{id}
POST   /lists/{id}/items
DELETE /lists/{id}/items/{item_id}

POST   /optimize                  Main AI endpoint
GET    /route?stores[]=&origin=
GET    /recommendations/{user_id}
GET    /budget/analytics

GET    /health
GET    /metrics
```

## Database Schema (key tables)

```sql
stores          — id, name, chain, city, lat, lng, promo_day
products        — id, canonical_name, brand, category, unit_type,
                  unit_size, embedding (vector 1536)
prices          — product_id, store_id, price EUR, unit_price,
                  currency='EUR', is_member, scraped_at
promotions      — product_id, store_id, promo_price, regular_price,
                  discount_pct, score, hist_avg_30d, hist_avg_90d
users           — id, email, household_size, plan,
                  preferences_enc (AES-256), deleted_at
loyalty_cards   — user_id, chain, active
shopping_lists  — user_id, name, budget EUR, status, deleted_at
basket_optimizations — list_id, variant, total_price EUR,
                       total_minutes, total_km, fuel_cost EUR
purchase_history — user_id, product_id, store_id, price_paid EUR
subscriptions   — user_id, plan, status, price_eur, stripe_sub_id
```

## Promotion Scoring (Celery task)

```python
real_discount = (hist_avg_30d - promo_price) / hist_avg_30d

if real_discount > 0.10:  score = 'real'
elif real_discount >= 0:  score = 'average'
else:                     score = 'fake'
```

## Product Matching (pgvector)

Cosine similarity threshold: 0.92
Embedding: canonical_name + brand + unit_type + unit_size

## Scraper Schedule

| Chain | Engine | Day | Time |
|-------|--------|-----|------|
| Lidl | Playwright | Thursday | 06:00 |
| Kaufland | Playwright | Wednesday | 06:00 |
| Billa | BeautifulSoup | Monday | 06:00 |
| Fantastico | BeautifulSoup | Wednesday | 06:00 |
| T-Market | BeautifulSoup | Thursday | 06:00 |
| DM | BeautifulSoup | Monday | 06:00 |
| Metro | Playwright | Tuesday | 06:00 |

Currency normalization: always store as EUR with 2 decimal places.

## GDPR Requirements

- AES-256 encryption on all personal data columns
- Soft delete everywhere (deleted_at column)
- DELETE /auth/account → Celery task anonymizes within 30 days
- GET /gdpr/export → full JSON data export
- Cookie consent banner on first visit
- Amplitude EU only (EU data residency)
- Klaviyo double opt-in
- Data retention: prices 2 years, personal data 3 years
- Infrastructure: EU region (Frankfurt) for PostgreSQL, BigQuery EU multi-region

## Design Tokens

```
--color-primary:    #2D6A4F
--color-real:       #52B788   (real promotion)
--color-fake:       #E63946   (fake promotion)
--color-warning:    #F4A261   (average promotion)
--font-size-base:   16px
--tap-target-min:   44px
--border-radius:    12px
```

## Pricing Plans

| Plan | Price |
|------|-------|
| Free | 0 €/month |
| Family | 2.99 €/month |
| Family Plus | 4.99 €/month |
| Premium Household | 7.99 €/month |
| B2B Analytics | on request |

## MVP Phases

### Phase 1 — Foundation (4 weeks)
Auth, product catalog, Lidl + Kaufland scraping, shopping lists,
basic price comparison, dashboard, GDPR.

### Phase 2 — Intelligence (4 weeks)
Claude AI basket optimization, promotion scoring, unit price,
route optimization, BigQuery price history, 5 more chains,
Klaviyo onboarding, Intercom tours.

### Phase 3 — Growth (4 weeks)
Predictive shopping, bulk buying, household analytics,
loyalty card pricing, Stripe billing, mobile PWA, B2B pipeline.

## KPIs

| Metric | Target |
|--------|--------|
| API p95 latency | < 300ms |
| AI endpoint p95 | < 3s |
| Scraper success rate | > 95% |
| Uptime | > 99.5% |
| Activation rate | > 40% |
| D7 retention | > 35% |
| Avg saving/session | > 5 € |
| Fake promo accuracy | > 80% |
| Free → paid conversion | > 8% |
| MRR Month 6 | > 2 500 € |
| CAC | < 8 € |
| LTV/CAC | > 5x |

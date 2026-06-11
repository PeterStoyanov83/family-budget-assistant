# Family AI Budget Assistant — Project Guide

## Project

AI платформа за оптимизация на семейното пазаруване в България.
Сравнява цени, открива фалшиви промоции, планира маршрут и предвижда нужди на домакинството.

See `.planning/PROJECT.md` for full project context.
See `.planning/MASTER_PROMPT.md` for the AI shopping assistant prompt.
See `.planning/TECHNICAL_SPEC.md` for the full technical specification.

## GSD Workflow

This project uses the Get Shit Done (GSD) workflow.

```
/gsd-discuss-phase 1   # Gather context and clarify approach
/gsd-plan-phase 1      # Plan a phase
/gsd-execute-phase 1   # Execute a phase plan
/gsd-progress          # Check current state
```

## Stack

- **Frontend:** Next.js 14 + TypeScript + Tailwind CSS + shadcn/ui (in `frontend/`)
- **Backend:** FastAPI Python 3.12 (in `backend/`)
- **Database:** PostgreSQL 16 + SQLAlchemy 2 async + Alembic + pgvector
- **Cache:** Redis 7
- **Queue:** Celery + Redis
- **AI:** Claude claude-sonnet-4-6 via Anthropic SDK (direct, no LangChain)
- **Warehouse:** BigQuery (price history, promotion scoring)
- **Scraping:** Playwright + BeautifulSoup4 + APScheduler (in `scraper/`)
- **Analytics:** Amplitude EU (GDPR-compliant)
- **Notifications:** Klaviyo

## Critical Constraints

1. **All prices in EUR** — Bulgaria adopted the Euro. Never use BGN/лв.
2. **Basket-level optimization** — always optimize the full basket, never individual products
3. **Promotion scoring is mandatory** — every promotion must be scored (real/average/fake) against 30-day price history
4. **Transport threshold** — only recommend extra stores if net saving > 5 € after fuel + time cost
5. **GDPR from day one** — soft delete on all models, AES-256 for personal data, Amplitude EU only
6. **Unit price normalization** — always compare €/kg or €/l, never package price

## Architecture Notes

- AI endpoint: POST /optimize calls claude-sonnet-4-6 with Master Prompt v2.1 from `.planning/MASTER_PROMPT.md`
- Promotion scoring runs as a Celery task on every new price scrape
- pgvector handles product matching across retail chains (cosine similarity > 0.92)
- Scraper schedule: Lidl=Thu, Kaufland=Wed, Billa=Mon, Fantastico=Wed, TMarket=Thu
- BigQuery is the warehouse for price history — PostgreSQL is the operational DB

## Pricing Plans (EUR)

- Free: 0 €/month
- Family: 2.99 €/month
- Family Plus: 4.99 €/month
- Premium: 7.99 €/month

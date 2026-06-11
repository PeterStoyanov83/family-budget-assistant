# Family AI Budget Assistant

AI-powered family shopping optimizer for the Bulgarian market.

## What it does

- Compares prices across Lidl, Kaufland, Billa, Fantastico, T-Market, DM, Metro
- Optimizes the full shopping basket (not just individual products)
- Detects fake promotions using 30/90-day price history
- Plans the cheapest route between stores
- Recommends bulk buying when genuine discounts appear
- Predicts what your household needs based on purchase history
- All prices in EUR

## Three optimization variants

| Variant | Goal |
|---------|------|
| Cheapest | Minimum total spend |
| Fastest | Minimum time and stores |
| Balanced | Best price/time ratio |

## Stack

- **Frontend:** Next.js 14 + TypeScript + Tailwind CSS + shadcn/ui
- **Backend:** FastAPI (Python 3.12) + PostgreSQL 16 + Redis
- **AI:** Claude claude-sonnet-4-6 via Anthropic SDK
- **Data:** BigQuery (price warehouse) + pgvector (product matching)
- **Scraping:** Playwright + BeautifulSoup4 + APScheduler
- **Notifications:** Klaviyo (email + push)
- **Analytics:** Amplitude EU (GDPR-compliant)

## Project structure

```
frontend/          Next.js app
backend/           FastAPI services
scraper/           Retail chain scrapers
tools/             Dev utilities
.planning/         Specs, prompts, research
```

## Getting started

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Competitive positioning

Current market (Pazarko, Shopko) answers: "Where is product X cheapest?"

This app answers: "How should my family shop this week to spend the least money, time and effort?"

Unique features vs all known competitors:
- Basket-level optimization (not product-level)
- Route + fuel cost calculation
- Fake promotion detection
- Bulk buying recommendations
- Predictive shopping based on household history

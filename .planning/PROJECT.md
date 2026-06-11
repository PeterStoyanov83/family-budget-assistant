# Family AI Budget Assistant

## Vision

AI-powered family shopping platform for the Bulgarian market that answers:

> "How should my family shop this week to spend the least money, time and effort?"

Current competitors (Pazarko, Shopko, Veliko) answer: "Where is product X cheapest?"
We answer the harder, more valuable question at the basket level.

## Core Value

Maximum value for the user = saved money + saved time + preserved quality.

## Target User

Bulgarian families (2-6 members), weekly grocery shoppers, smartphone users.
Primary persona: household manager, 28-45 years old, shops at 1-3 supermarket chains weekly.

## Key Differentiators vs Competitors

| Feature | Pazarko | Shopko | Us |
|---------|---------|--------|-----|
| Price comparison | ✅ | ✅ | ✅ |
| Basket optimization | ❌ | ⚠️ | ✅ |
| Route + fuel cost | ❌ | ❌ | ✅ |
| Fake promotion detection | ❌ | ❌ | ✅ |
| Bulk buying recommendations | ❌ | ❌ | ✅ |
| Predictive shopping | ❌ | ❌ | ✅ |
| Family budget planning | ❌ | ❌ | ✅ |

## Retail Chains Covered

Lidl, Kaufland, Billa, Fantastico, T-Market, DM, Metro

## Promotion Scoring Logic

- **REAL**: promo price is below 30-day historical average
- **AVERAGE**: discount is below category average
- **FAKE**: price was inflated before the "promotion"; real discount < 5%

## Transport Decision Rule

Only recommend an extra store if:
net saving > fuel cost (0.06 €/km) + time cost (0.50 €/min) × 2

## MVP Phases

### Phase 1 — Foundation (4 weeks)
Auth, product catalog, price scraping (Lidl + Kaufland), shopping lists,
basic price comparison, dashboard, GDPR compliance.

### Phase 2 — Intelligence (4 weeks)
Basket optimization (Claude AI), promotion scoring, unit price normalization,
route optimization (Mapbox), price history (BigQuery), + 5 more chains,
Klaviyo onboarding, Intercom tours.

### Phase 3 — Growth (4 weeks)
Predictive shopping, bulk buying logic, household analytics, loyalty card pricing,
Stripe billing (EUR), mobile PWA, HubSpot B2B.

## Success Metrics

- Activation rate: > 40% (register → first optimization)
- D7 retention: > 35%
- Average saving per session: > 5 €
- Fake promotion detection accuracy: > 80%
- Conversion free → paid: > 8%
- MRR Month 6: > 2 500 €

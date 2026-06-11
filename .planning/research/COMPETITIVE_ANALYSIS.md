# Competitive Analysis

## Market Summary

The Bulgarian price comparison market is served by Pazarko, Shopko, and Veliko.
All three focus on product-level price lookup. None offer basket optimization,
route planning, fake promotion detection, or household intelligence.

## Competitive Matrix

| Capability | Pazarko | Shopko | Veliko | Us |
|------------|---------|--------|--------|-----|
| Price comparison | ✅ | ✅ | ⚠️ | ✅ |
| Promotions tracking | ✅ | ✅ | ⚠️ | ✅ |
| Shopping lists | ✅ | ✅ | ✅ | ✅ |
| Price history | ✅ | ✅ | ❌ | ✅ |
| Price alerts | ✅ | ✅ | ❌ | ✅ |
| Basket optimization | ❌ | ⚠️ | ⚠️ | ✅ |
| Route optimization | ❌ | ❌ | ❌ | ✅ |
| Fuel cost analysis | ❌ | ❌ | ❌ | ✅ |
| Time optimization | ❌ | ❌ | ❌ | ✅ |
| Family budget planning | ❌ | ❌ | ⚠️ | ✅ |
| Household analytics | ❌ | ❌ | ⚠️ | ✅ |
| AI recommendations | ⚠️ | ⚠️ | ⚠️ | ✅ |
| Promotion scoring (real/fake) | ❌ | ❌ | ❌ | ✅ |
| Predictive shopping | ❌ | ❌ | ❌ | ✅ |
| Bulk buying recommendations | ❌ | ❌ | ❌ | ✅ |

## Pazarko — Architecture Analysis

Pazarko is the closest competitor (~40,000 products, 7 chains, Android app).

**What they do well:**
- Strong price tracking and history
- Large product catalog
- Price drop notifications

**What they lack (our opportunity):**
- No basket-level optimization
- No route planning
- No fake promotion detection
- No family budget layer
- No predictive intelligence

**Likely stack:** Centralized PostgreSQL, scraper ETL pipeline,
mobile app with push notifications, affiliate/freemium monetization.

## Strategic Gap

Current market solves: "Where is product X cheapest?"

Our solution: "How should my family shop this week to spend the least money, time and effort?"

The strongest differentiation is in layers 3-5 where no competitor operates publicly:
- Layer 3: Basket optimization
- Layer 4: Budget intelligence
- Layer 5: Predictive household AI

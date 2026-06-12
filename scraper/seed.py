"""
Seed script — loads realistic Bulgarian grocery data into the DB.
Run: python -m scraper.seed

Populates: stores (Lidl + Kaufland Sofia), products, prices, promotions.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings
from app.models import Product, Price, Promotion, Store

STORES = [
    {"name": "Lidl Люлин", "chain": "lidl", "city": "София", "address": "бул. Царица Йоана 4", "lat": 42.7178, "lng": 23.2700, "promo_day": "thursday"},
    {"name": "Lidl Младост", "chain": "lidl", "city": "София", "address": "ул. Александър Малинов 59", "lat": 42.6483, "lng": 23.3795, "promo_day": "thursday"},
    {"name": "Kaufland Люлин", "chain": "kaufland", "city": "София", "address": "бул. Европа 122", "lat": 42.7230, "lng": 23.2612, "promo_day": "wednesday"},
    {"name": "Kaufland Младост", "chain": "kaufland", "city": "София", "address": "бул. Александър Малинов 89", "lat": 42.6501, "lng": 23.3812, "promo_day": "wednesday"},
]

PRODUCTS = [
    {"canonical_name": "Кисело мляко 2%", "brand": None, "category": "dairy", "unit_type": "kg", "unit_size": 0.4, "unit_size_label": "400г"},
    {"canonical_name": "Кисело мляко 3.6%", "brand": None, "category": "dairy", "unit_type": "kg", "unit_size": 0.4, "unit_size_label": "400г"},
    {"canonical_name": "Пиле цяло охладено", "brand": None, "category": "meat", "unit_type": "kg", "unit_size": 1.0, "unit_size_label": "1кг"},
    {"canonical_name": "Пилешко филе охладено", "brand": None, "category": "meat", "unit_type": "kg", "unit_size": 1.0, "unit_size_label": "1кг"},
    {"canonical_name": "Слънчогледово олио", "brand": None, "category": "oils", "unit_type": "l", "unit_size": 1.0, "unit_size_label": "1л"},
    {"canonical_name": "Кравешко мляко 3.5% UHT", "brand": None, "category": "dairy", "unit_type": "l", "unit_size": 1.0, "unit_size_label": "1л"},
    {"canonical_name": "Хляб Добруджа", "brand": None, "category": "bakery", "unit_type": "kg", "unit_size": 0.8, "unit_size_label": "800г"},
    {"canonical_name": "Яйца L клас", "brand": None, "category": "eggs", "unit_type": "piece", "unit_size": 10.0, "unit_size_label": "10бр"},
    {"canonical_name": "Кашкавал 45%", "brand": None, "category": "dairy", "unit_type": "kg", "unit_size": 0.3, "unit_size_label": "300г"},
    {"canonical_name": "Сирене краве 45%", "brand": None, "category": "dairy", "unit_type": "kg", "unit_size": 0.5, "unit_size_label": "500г"},
    {"canonical_name": "Ориз дългозърнест", "brand": None, "category": "grains", "unit_type": "kg", "unit_size": 1.0, "unit_size_label": "1кг"},
    {"canonical_name": "Паста спагети №5", "brand": None, "category": "grains", "unit_type": "kg", "unit_size": 0.5, "unit_size_label": "500г"},
    {"canonical_name": "Доматена пюре", "brand": None, "category": "canned", "unit_type": "kg", "unit_size": 0.4, "unit_size_label": "400г"},
    {"canonical_name": "Тоалетна хартия 3-пласт", "brand": None, "category": "household", "unit_type": "piece", "unit_size": 8.0, "unit_size_label": "8бр"},
    {"canonical_name": "Прах за пране универсален", "brand": None, "category": "household", "unit_type": "kg", "unit_size": 3.0, "unit_size_label": "3кг"},
    {"canonical_name": "Банани", "brand": None, "category": "fruits", "unit_type": "kg", "unit_size": 1.0, "unit_size_label": "1кг"},
    {"canonical_name": "Домати", "brand": None, "category": "vegetables", "unit_type": "kg", "unit_size": 1.0, "unit_size_label": "1кг"},
    {"canonical_name": "Картофи", "brand": None, "category": "vegetables", "unit_type": "kg", "unit_size": 1.0, "unit_size_label": "1кг"},
    {"canonical_name": "Масло краве 82%", "brand": None, "category": "dairy", "unit_type": "kg", "unit_size": 0.125, "unit_size_label": "125г"},
    {"canonical_name": "Захар кристална", "brand": None, "category": "sugar", "unit_type": "kg", "unit_size": 1.0, "unit_size_label": "1кг"},
]

# Prices: (product_index, store_index, price_eur, is_member)
# Based on realistic Sofia supermarket prices 2026
PRICES = [
    # Кисело мляко 2% — product 0
    (0, 0, 0.49, False),  # Lidl Люлин
    (0, 1, 0.49, False),  # Lidl Младост
    (0, 2, 0.63, False),  # Kaufland Люлин
    (0, 3, 0.63, False),  # Kaufland Младост
    # Кисело мляко 3.6% — product 1
    (1, 0, 0.51, True),   # Lidl Plus price
    (1, 0, 0.59, False),  # Lidl shelf
    (1, 2, 0.66, False),  # Kaufland
    # Пиле цяло — product 2
    (2, 0, 3.89, False),
    (2, 2, 4.29, False),
    # Пилешко филе — product 3
    (3, 0, 5.11, False),
    (3, 2, 5.62, False),
    (3, 3, 5.62, False),
    # Олио 1л — product 4
    (4, 0, 1.53, False),  # Lidl promo
    (4, 2, 1.79, False),  # Kaufland
    # Мляко 1л — product 5
    (5, 0, 1.29, False),
    (5, 2, 1.35, False),
    # Хляб — product 6
    (6, 0, 1.19, False),
    (6, 2, 1.29, False),
    # Яйца 10бр — product 7
    (7, 0, 2.29, False),
    (7, 2, 2.49, False),
    # Кашкавал — product 8
    (8, 0, 3.49, False),
    (8, 2, 3.79, False),
    # Сирене — product 9
    (9, 0, 3.19, False),
    (9, 2, 3.39, False),
    # Ориз — product 10
    (10, 0, 1.29, False),
    (10, 2, 1.49, False),
    # Паста — product 11
    (11, 0, 0.79, False),
    (11, 2, 0.89, False),
    # Доматена пюре — product 12
    (12, 0, 0.59, False),
    (12, 2, 0.69, False),
    # Тоалетна хартия — product 13
    (13, 0, 3.49, False),
    (13, 2, 3.89, False),
    # Прах за пране — product 14
    (14, 0, 6.99, False),
    (14, 2, 7.49, False),
    # Банани — product 15
    (15, 0, 1.09, False),
    (15, 2, 1.19, False),
    # Домати — product 16
    (16, 0, 1.89, False),
    (16, 2, 1.99, False),
    # Картофи — product 17
    (17, 0, 0.79, False),
    (17, 2, 0.89, False),
    # Масло — product 18
    (18, 0, 1.89, False),
    (18, 2, 1.99, False),
    # Захар — product 19
    (19, 0, 1.19, False),
    (19, 2, 1.29, False),
]

# Promotions: (product_index, store_index, promo_price, regular_price, hist_avg_30d)
PROMOTIONS = [
    (4, 0, 1.53, 2.19, 2.10),   # Олио Lidl — РЕАЛНА промоция -27%
    (14, 2, 5.99, 7.49, 7.20),  # Прах Kaufland — РЕАЛНА промоция -17%
    (8, 0, 3.49, 3.99, 3.45),   # Кашкавал Lidl — СРЕДНА промоция (hist_avg ≈ promo)
    (1, 0, 0.51, 0.59, 0.48),   # Кисело мляко Lidl Plus — СРЕДНА (member price)
    (7, 2, 1.99, 2.49, 2.55),   # Яйца Kaufland — РЕАЛНА промоция
]


async def seed():
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        from sqlalchemy import text, select

        # Check if already seeded
        result = await session.execute(select(Store).limit(1))
        if result.scalar_one_or_none():
            print("Database already seeded — skipping.")
            return

        print("Creating stores...")
        store_objs = [Store(**s) for s in STORES]
        session.add_all(store_objs)
        await session.flush()

        print("Creating products...")
        product_objs = [Product(**p) for p in PRODUCTS]
        session.add_all(product_objs)
        await session.flush()

        print("Creating prices...")
        price_objs = []
        for prod_idx, store_idx, price_eur, is_member in PRICES:
            p = product_objs[prod_idx]
            s = store_objs[store_idx]
            unit_price = None
            if p.unit_type and p.unit_size:
                unit_price = round(price_eur / p.unit_size, 4)
            price_objs.append(Price(
                product_id=p.id, store_id=s.id,
                price=price_eur, unit_price=unit_price,
                currency="EUR", is_member=is_member,
            ))
        session.add_all(price_objs)
        await session.flush()

        print("Creating promotions...")
        for prod_idx, store_idx, promo_price, regular_price, hist_avg in PROMOTIONS:
            p = product_objs[prod_idx]
            s = store_objs[store_idx]
            discount_pct = round((regular_price - promo_price) / regular_price * 100, 1)
            real_discount = (hist_avg - promo_price) / hist_avg if hist_avg else 0
            score = "real" if real_discount > 0.10 else ("average" if real_discount >= 0 else "fake")
            session.add(Promotion(
                product_id=p.id, store_id=s.id,
                promo_price=promo_price, regular_price=regular_price,
                discount_pct=discount_pct, score=score,
                hist_avg_30d=hist_avg, is_active=True,
            ))

        await session.commit()
        print(f"Seeded: {len(store_objs)} stores, {len(product_objs)} products, "
              f"{len(price_objs)} prices, {len(PROMOTIONS)} promotions")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())

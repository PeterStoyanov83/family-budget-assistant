from fastapi import APIRouter, Query
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from app.core.deps import CurrentUser, SessionDep
from app.models.product import Product
from app.models.price import Price
from app.models.store import Store
from app.schemas.product import PriceHistoryPoint, ProductOut, ProductWithPricesOut

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/search", response_model=list[ProductWithPricesOut])
async def search_products(
    session: SessionDep,
    current_user: CurrentUser,
    q: str = Query("", min_length=0),
    store: str | None = None,
    category: str | None = None,
    limit: int = Query(20, le=100),
):
    stmt = (
        select(Product)
        .options(selectinload(Product.prices).selectinload(Price.store))
        .limit(limit)
    )
    if q:
        stmt = stmt.where(Product.canonical_name.ilike(f"%{q}%"))
    if category:
        stmt = stmt.where(Product.category == category)
    if store:
        stmt = stmt.join(Price).join(Store).where(Store.chain == store)

    result = await session.execute(stmt)
    return result.scalars().unique().all()


@router.get("/{product_id}/price-history", response_model=list[PriceHistoryPoint])
async def price_history(
    product_id: int,
    session: SessionDep,
    current_user: CurrentUser,
    days: int = Query(30, le=90),
):
    from datetime import datetime, timedelta, timezone
    since = datetime.now(timezone.utc) - timedelta(days=days)

    result = await session.execute(
        select(Price, Store.name.label("store_name"))
        .join(Store)
        .where(Price.product_id == product_id, Price.scraped_at >= since)
        .order_by(desc(Price.scraped_at))
    )
    rows = result.all()
    return [
        PriceHistoryPoint(
            price=row.Price.price,
            unit_price=row.Price.unit_price,
            store_id=row.Price.store_id,
            store_name=row.store_name,
            is_member=row.Price.is_member,
            scraped_at=row.Price.scraped_at,
        )
        for row in rows
    ]


@router.get("/{product_id}/alternatives", response_model=list[ProductWithPricesOut])
async def product_alternatives(
    product_id: int,
    session: SessionDep,
    current_user: CurrentUser,
):
    product = await session.get(Product, product_id)
    if not product:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    # pgvector cosine similarity search — threshold 0.92
    # Falls back to category match when embedding is null (seed data)
    if product.embedding is not None:
        result = await session.execute(
            select(Product)
            .options(selectinload(Product.prices).selectinload(Price.store))
            .where(
                Product.id != product_id,
                Product.embedding.cosine_distance(product.embedding) < 0.08,
            )
            .limit(5)
        )
    else:
        result = await session.execute(
            select(Product)
            .options(selectinload(Product.prices).selectinload(Price.store))
            .where(Product.category == product.category, Product.id != product_id)
            .limit(5)
        )
    return result.scalars().unique().all()

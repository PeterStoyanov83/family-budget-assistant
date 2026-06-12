from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.deps import CurrentUser, SessionDep
from app.models.price import Promotion
from app.schemas.promotion import PromotionOut

router = APIRouter(prefix="/promotions", tags=["promotions"])


@router.get("", response_model=list[PromotionOut])
async def list_promotions(
    session: SessionDep,
    current_user: CurrentUser,
    store: str | None = None,
    category: str | None = None,
    score: str | None = Query(None, pattern="^(real|average|fake)$"),
    valid: bool = True,
    limit: int = Query(50, le=200),
):
    from app.models.store import Store
    from app.models.product import Product

    stmt = (
        select(Promotion)
        .options(selectinload(Promotion.product), selectinload(Promotion.store))
        .limit(limit)
    )
    if valid:
        stmt = stmt.where(Promotion.is_active.is_(True))
    if score:
        stmt = stmt.where(Promotion.score == score)
    if store:
        stmt = stmt.join(Store).where(Store.chain == store)
    if category:
        stmt = stmt.join(Product).where(Product.category == category)

    result = await session.execute(stmt)
    return result.scalars().all()


@router.get("/{promotion_id}/score", response_model=PromotionOut)
async def get_promotion_score(
    promotion_id: int,
    session: SessionDep,
    current_user: CurrentUser,
):
    promo = await session.get(Promotion, promotion_id)
    if not promo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promotion not found")
    return promo


def compute_promotion_score(promo_price: float, hist_avg_30d: float) -> str:
    """Score a promotion against 30-day price history."""
    if hist_avg_30d <= 0:
        return "average"
    real_discount = (hist_avg_30d - promo_price) / hist_avg_30d
    if real_discount > 0.10:
        return "real"
    elif real_discount >= 0:
        return "average"
    return "fake"

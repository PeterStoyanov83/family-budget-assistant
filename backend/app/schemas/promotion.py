from datetime import datetime

from pydantic import BaseModel


class PromotionOut(BaseModel):
    id: int
    product_id: int
    store_id: int
    promo_price: float
    regular_price: float
    discount_pct: float
    score: str | None
    hist_avg_30d: float | None
    hist_avg_90d: float | None
    valid_from: datetime | None
    valid_until: datetime | None
    is_active: bool
    scraped_at: datetime

    model_config = {"from_attributes": True}

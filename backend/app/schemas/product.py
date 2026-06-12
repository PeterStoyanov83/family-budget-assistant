from datetime import datetime

from pydantic import BaseModel


class StoreOut(BaseModel):
    id: int
    name: str
    chain: str
    city: str
    address: str | None
    lat: float | None
    lng: float | None
    promo_day: str | None

    model_config = {"from_attributes": True}


class PriceOut(BaseModel):
    id: int
    store_id: int
    store: StoreOut
    price: float
    unit_price: float | None
    currency: str
    is_member: bool
    scraped_at: datetime

    model_config = {"from_attributes": True}


class ProductOut(BaseModel):
    id: int
    canonical_name: str
    brand: str | None
    category: str | None
    unit_type: str | None
    unit_size: float | None
    unit_size_label: str | None
    image_url: str | None

    model_config = {"from_attributes": True}


class ProductWithPricesOut(ProductOut):
    prices: list[PriceOut] = []


class PriceHistoryPoint(BaseModel):
    price: float
    unit_price: float | None
    store_id: int
    store_name: str
    is_member: bool
    scraped_at: datetime

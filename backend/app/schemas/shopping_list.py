from datetime import datetime

from pydantic import BaseModel


class ListItemCreate(BaseModel):
    name: str
    quantity: float = 1.0
    unit: str | None = None
    preferred_brand: str | None = None
    note: str | None = None
    product_id: int | None = None


class ListItemUpdate(BaseModel):
    name: str | None = None
    quantity: float | None = None
    unit: str | None = None
    preferred_brand: str | None = None
    note: str | None = None
    is_checked: bool | None = None


class ListItemOut(BaseModel):
    id: int
    list_id: int
    product_id: int | None
    name: str
    quantity: float
    unit: str | None
    preferred_brand: str | None
    note: str | None
    is_checked: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ShoppingListCreate(BaseModel):
    name: str
    budget: float | None = None


class ShoppingListUpdate(BaseModel):
    name: str | None = None
    budget: float | None = None
    status: str | None = None


class ShoppingListOut(BaseModel):
    id: int
    user_id: int
    name: str
    budget: float | None
    currency: str
    status: str
    created_at: datetime
    updated_at: datetime
    items: list[ListItemOut] = []

    model_config = {"from_attributes": True}


class ShoppingListSummary(BaseModel):
    id: int
    name: str
    budget: float | None
    status: str
    item_count: int
    created_at: datetime

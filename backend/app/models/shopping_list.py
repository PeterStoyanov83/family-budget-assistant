from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ShoppingList(Base):
    __tablename__ = "shopping_lists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    budget: Mapped[float | None] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    # draft | active | completed
    status: Mapped[str] = mapped_column(String(20), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="shopping_lists")  # noqa: F821
    items: Mapped[list["ListItem"]] = relationship(back_populates="list", cascade="all, delete-orphan")
    optimizations: Mapped[list["BasketOptimization"]] = relationship(back_populates="list", cascade="all, delete-orphan")


class ListItem(Base):
    __tablename__ = "list_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    list_id: Mapped[int] = mapped_column(ForeignKey("shopping_lists.id"), nullable=False, index=True)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"))
    # Free-text name when product is not yet matched to catalog
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, default=1.0)
    unit: Mapped[str | None] = mapped_column(String(20))
    preferred_brand: Mapped[str | None] = mapped_column(String(150))
    note: Mapped[str | None] = mapped_column(String(500))
    is_checked: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    list: Mapped["ShoppingList"] = relationship(back_populates="items")
    product: Mapped["Product | None"] = relationship()  # noqa: F821


class BasketOptimization(Base):
    __tablename__ = "basket_optimizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    list_id: Mapped[int] = mapped_column(ForeignKey("shopping_lists.id"), nullable=False, index=True)
    # cheapest | fastest | balanced
    variant: Mapped[str] = mapped_column(String(20), nullable=False)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)
    total_minutes: Mapped[float | None] = mapped_column(Float)
    total_km: Mapped[float | None] = mapped_column(Float)
    fuel_cost: Mapped[float | None] = mapped_column(Float)
    result_json: Mapped[str | None] = mapped_column(String(65535))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    list: Mapped["ShoppingList"] = relationship(back_populates="optimizations")

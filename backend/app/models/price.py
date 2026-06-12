from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Price(Base):
    __tablename__ = "prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"), nullable=False, index=True)
    # All prices in EUR
    price: Mapped[float] = mapped_column(Float, nullable=False)
    # Normalised price per kg / l / piece
    unit_price: Mapped[float | None] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    is_member: Mapped[bool] = mapped_column(Boolean, default=False)
    scraped_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    product: Mapped["Product"] = relationship(back_populates="prices")  # noqa: F821
    store: Mapped["Store"] = relationship(back_populates="prices")  # noqa: F821


class Promotion(Base):
    __tablename__ = "promotions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"), nullable=False, index=True)
    promo_price: Mapped[float] = mapped_column(Float, nullable=False)
    regular_price: Mapped[float] = mapped_column(Float, nullable=False)
    discount_pct: Mapped[float] = mapped_column(Float, nullable=False)
    # real | average | fake
    score: Mapped[str | None] = mapped_column(String(20), index=True)
    hist_avg_30d: Mapped[float | None] = mapped_column(Float)
    hist_avg_90d: Mapped[float | None] = mapped_column(Float)
    valid_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    scraped_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    product: Mapped["Product"] = relationship(back_populates="promotions")  # noqa: F821
    store: Mapped["Store"] = relationship(back_populates="promotions")  # noqa: F821


class PurchaseHistory(Base):
    __tablename__ = "purchase_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"), nullable=False)
    price_paid: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    quantity: Mapped[float] = mapped_column(Float, default=1.0)
    purchased_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

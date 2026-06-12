from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Store(Base):
    __tablename__ = "stores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    chain: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str | None] = mapped_column(String(500))
    lat: Mapped[float | None] = mapped_column(Float)
    lng: Mapped[float | None] = mapped_column(Float)
    # Day of week promos change: monday, tuesday, wednesday, thursday, friday
    promo_day: Mapped[str | None] = mapped_column(String(20))
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    prices: Mapped[list["Price"]] = relationship(back_populates="store")  # noqa: F821
    promotions: Mapped[list["Promotion"]] = relationship(back_populates="store")  # noqa: F821

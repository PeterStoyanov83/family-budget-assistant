from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    canonical_name: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    brand: Mapped[str | None] = mapped_column(String(150))
    category: Mapped[str | None] = mapped_column(String(100), index=True)
    # unit_type: kg, l, piece, pack
    unit_type: Mapped[str | None] = mapped_column(String(20))
    unit_size: Mapped[float | None] = mapped_column(Float)
    unit_size_label: Mapped[str | None] = mapped_column(String(30))
    image_url: Mapped[str | None] = mapped_column(String(500))
    # pgvector embedding for cross-chain matching (cosine similarity > 0.92)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    prices: Mapped[list["Price"]] = relationship(back_populates="product")  # noqa: F821
    promotions: Mapped[list["Promotion"]] = relationship(back_populates="product")  # noqa: F821

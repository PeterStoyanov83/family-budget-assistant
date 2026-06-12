from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(100))
    household_size: Mapped[int] = mapped_column(Integer, default=1)
    plan: Mapped[str] = mapped_column(String(50), default="free")
    # AES-256 encrypted JSON blob: dietary restrictions, preferences
    preferences_enc: Mapped[str | None] = mapped_column(String(2048))
    has_car: Mapped[bool] = mapped_column(Boolean, default=True)
    city: Mapped[str | None] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    loyalty_cards: Mapped[list["LoyaltyCard"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    shopping_lists: Mapped[list["ShoppingList"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # noqa: F821


class LoyaltyCard(Base):
    __tablename__ = "loyalty_cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    chain: Mapped[str] = mapped_column(String(50), nullable=False)
    card_number: Mapped[str | None] = mapped_column(String(100))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="loyalty_cards")

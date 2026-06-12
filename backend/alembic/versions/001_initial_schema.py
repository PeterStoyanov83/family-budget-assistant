"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-06-12
"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("first_name", sa.String(100)),
        sa.Column("household_size", sa.Integer, nullable=False, server_default="1"),
        sa.Column("plan", sa.String(50), nullable=False, server_default="free"),
        sa.Column("preferences_enc", sa.String(2048)),
        sa.Column("has_car", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("city", sa.String(100)),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "loyalty_cards",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("chain", sa.String(50), nullable=False),
        sa.Column("card_number", sa.String(100)),
        sa.Column("active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "stores",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("chain", sa.String(50), nullable=False),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("address", sa.String(500)),
        sa.Column("lat", sa.Float),
        sa.Column("lng", sa.Float),
        sa.Column("promo_day", sa.String(20)),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_stores_chain", "stores", ["chain"])

    op.create_table(
        "products",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("canonical_name", sa.String(300), nullable=False),
        sa.Column("brand", sa.String(150)),
        sa.Column("category", sa.String(100)),
        sa.Column("unit_type", sa.String(20)),
        sa.Column("unit_size", sa.Float),
        sa.Column("unit_size_label", sa.String(30)),
        sa.Column("image_url", sa.String(500)),
        sa.Column("embedding", Vector(1536)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_products_canonical_name", "products", ["canonical_name"])
    op.create_index("ix_products_category", "products", ["category"])

    op.create_table(
        "prices",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id"), nullable=False),
        sa.Column("store_id", sa.Integer, sa.ForeignKey("stores.id"), nullable=False),
        sa.Column("price", sa.Float, nullable=False),
        sa.Column("unit_price", sa.Float),
        sa.Column("currency", sa.String(3), nullable=False, server_default="EUR"),
        sa.Column("is_member", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("scraped_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_prices_product_id", "prices", ["product_id"])
    op.create_index("ix_prices_store_id", "prices", ["store_id"])
    op.create_index("ix_prices_scraped_at", "prices", ["scraped_at"])

    op.create_table(
        "promotions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id"), nullable=False),
        sa.Column("store_id", sa.Integer, sa.ForeignKey("stores.id"), nullable=False),
        sa.Column("promo_price", sa.Float, nullable=False),
        sa.Column("regular_price", sa.Float, nullable=False),
        sa.Column("discount_pct", sa.Float, nullable=False),
        sa.Column("score", sa.String(20)),
        sa.Column("hist_avg_30d", sa.Float),
        sa.Column("hist_avg_90d", sa.Float),
        sa.Column("valid_from", sa.DateTime(timezone=True)),
        sa.Column("valid_until", sa.DateTime(timezone=True)),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("scraped_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_promotions_product_id", "promotions", ["product_id"])
    op.create_index("ix_promotions_is_active", "promotions", ["is_active"])
    op.create_index("ix_promotions_score", "promotions", ["score"])

    op.create_table(
        "shopping_lists",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("budget", sa.Float),
        sa.Column("currency", sa.String(3), nullable=False, server_default="EUR"),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_shopping_lists_user_id", "shopping_lists", ["user_id"])

    op.create_table(
        "list_items",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("list_id", sa.Integer, sa.ForeignKey("shopping_lists.id"), nullable=False),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id")),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column("quantity", sa.Float, nullable=False, server_default="1"),
        sa.Column("unit", sa.String(20)),
        sa.Column("preferred_brand", sa.String(150)),
        sa.Column("note", sa.String(500)),
        sa.Column("is_checked", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_list_items_list_id", "list_items", ["list_id"])

    op.create_table(
        "basket_optimizations",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("list_id", sa.Integer, sa.ForeignKey("shopping_lists.id"), nullable=False),
        sa.Column("variant", sa.String(20), nullable=False),
        sa.Column("total_price", sa.Float, nullable=False),
        sa.Column("total_minutes", sa.Float),
        sa.Column("total_km", sa.Float),
        sa.Column("fuel_cost", sa.Float),
        sa.Column("result_json", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "purchase_history",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id"), nullable=False),
        sa.Column("store_id", sa.Integer, sa.ForeignKey("stores.id"), nullable=False),
        sa.Column("price_paid", sa.Float, nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="EUR"),
        sa.Column("quantity", sa.Float, nullable=False, server_default="1"),
        sa.Column("purchased_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_purchase_history_user_id", "purchase_history", ["user_id"])


def downgrade() -> None:
    op.drop_table("purchase_history")
    op.drop_table("basket_optimizations")
    op.drop_table("list_items")
    op.drop_table("shopping_lists")
    op.drop_table("promotions")
    op.drop_table("prices")
    op.drop_table("products")
    op.drop_table("stores")
    op.drop_table("loyalty_cards")
    op.drop_table("users")
    op.execute("DROP EXTENSION IF EXISTS vector")

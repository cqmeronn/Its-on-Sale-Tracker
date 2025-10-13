"""Defines SQLAlchemy ORM models for the core database tables."""

from sqlalchemy import (
    Integer, BigInteger, Text, Boolean, Numeric, ForeignKey,
    UniqueConstraint, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import TIMESTAMP
from .db import Base

class Product(Base):
    __tablename__ = "product"
    product_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    site: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[object] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    __table_args__ = (UniqueConstraint("site", "url", name="uq_product_site_url"),)

    prices: Mapped[list["PriceHistory"]] = relationship(back_populates="product")

class PriceHistory(Base):
    __tablename__ = "price_history"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.product_id"), index=True, nullable=False)
    ts_utc: Mapped[object] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), index=True)
    price_numeric: Mapped[float | None] = mapped_column(Numeric(12, 2))
    currency: Mapped[str | None] = mapped_column(Text)
    in_stock_bool: Mapped[bool | None] = mapped_column(Boolean)
    on_sale_bool: Mapped[bool | None] = mapped_column(Boolean)
    source_hash: Mapped[str | None] = mapped_column(Text)

    product: Mapped["Product"] = relationship(back_populates="prices")

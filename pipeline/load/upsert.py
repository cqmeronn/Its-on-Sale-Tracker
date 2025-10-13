"""Handles upserting products and writing price snapshots to the database."""

from sqlalchemy import select
from sqlalchemy.orm import Session
from pipeline.common.db import SessionLocal
from pipeline.common.models import Product, PriceHistory

def get_or_create_product(session: Session, site: str, url: str, name: str | None = None) -> int:
    existing = session.execute(
        select(Product).where(Product.site == site, Product.url == url)
    ).scalar_one_or_none()
    if existing:
        return existing.product_id
    p = Product(site=site, url=url, name=name)
    session.add(p)
    session.flush()
    return p.product_id

def write_price_snapshot(
    session: Session,
    product_id: int,
    price: float | None,
    currency: str | None,
    in_stock: bool | None,
    on_sale: bool | None,
    source_hash: str | None,
):
    session.add(
        PriceHistory(
            product_id=product_id,
            price_numeric=price,
            currency=currency,
            in_stock_bool=in_stock,
            on_sale_bool=on_sale,
            source_hash=source_hash,
        )
    )

def main():
    # currently using hardcoded example data
    site = "example"
    url = "https://example.com/"
    name = "Example Placeholder"
    price = 9.99
    currency = "GBP"
    in_stock = True
    on_sale = False
    source_hash = "example_v1"

    with SessionLocal() as session:
        pid = get_or_create_product(session, site, url, name)
        write_price_snapshot(session, pid, price, currency, in_stock, on_sale, source_hash)
        session.commit()
        print(f"Wrote snapshot for product_id {pid}")

if __name__ == "__main__":
    main()

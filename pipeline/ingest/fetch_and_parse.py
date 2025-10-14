"""Fetch a product page, parse fields, and write a price snapshot."""

from loguru import logger
import requests
import hashlib

from pipeline.ingest.parsers.books_to_scrape import parse_product_page
from pipeline.load.upsert import get_or_create_product, write_price_snapshot
from pipeline.common.db import SessionLocal

PRODUCT_URL = "https://books.toscrape.com/catalogue/william-shakespeares-star-wars-verily-a-new-hope-william-shakespeares-star-wars-4_871/index.html"

def main():
    url = PRODUCT_URL
    r = requests.get(url, timeout=20, headers={"User-Agent": "its-on-sale-tracker/0.1"})
    r.raise_for_status()
    logger.info(f"Fetched {url} with status {r.status_code}")

    parsed = parse_product_page(r.text, url)
    body_hash = hashlib.sha256(r.text.encode("utf-8")).hexdigest()[:16]

    with SessionLocal() as session:
        pid = get_or_create_product(session, site=parsed["site"], url=url, name=parsed["name"])
        write_price_snapshot(
            session,
            product_id=pid,
            price=parsed["price"],
            currency=parsed["currency"],
            in_stock=parsed["in_stock"],
            on_sale=parsed["on_sale"],
            source_hash=body_hash,
        )
        session.commit()
        logger.info(f"Wrote snapshot for product_id={pid} price={parsed['price']} {parsed['currency']}")

if __name__ == "__main__":
    main()

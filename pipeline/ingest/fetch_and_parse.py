"""Fetch a product page, parse fields, and write a price snapshot."""

from loguru import logger
import requests
import hashlib

from pipeline.ingest.parsers.books_to_scrape import parse_product_page
from pipeline.load.upsert import get_or_create_product, write_price_snapshot
from pipeline.common.db import SessionLocal

from pipeline.ingest.parsers import books_to_scrape


URLS = [
    "https://books.toscrape.com/catalogue/william-shakespeares-star-wars-verily-a-new-hope-william-shakespeares-star-wars-4_871/index.html",
    "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
]

PARSERS = {
    "books.toscrape.com": books_to_scrape.parse_product_page,
}

def get_parser(url: str):
    for host, fn in PARSERS.items():
        if host in url:
            return fn
    raise ValueError(f"No parser registered for: {url}")

def main():
    with SessionLocal() as session:
        for url in URLS:
            r = requests.get(url, timeout=20, headers={"User-Agent": "its-on-sale-tracker/0.1"})
            r.encoding = "utf-8"  # ensure proper decoding
            r.raise_for_status()
            logger.info(f"Fetched {url} with status {r.status_code}")
            parse_product_page = get_parser(url)
            parsed = parse_product_page(r.text, url)
            parsed = parse_product_page(r.text, url)
            body_hash = hashlib.sha256(r.text.encode("utf-8")).hexdigest()[:16]

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
        logger.info(f"Wrote snapshots for {len(URLS)} products")


if __name__ == "__main__":
    main()

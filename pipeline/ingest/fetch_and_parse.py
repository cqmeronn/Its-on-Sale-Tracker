"""Fetches a webpage, simulates parsing, and writes a price snapshot to the database."""

from loguru import logger
import requests
import hashlib
from pipeline.load.upsert import get_or_create_product, write_price_snapshot
from pipeline.common.db import SessionLocal

def main():
    url = "https://example.com/"
    site = "example"

    r = requests.get(url, timeout=20)
    logger.info(f"Fetched {url} with status {r.status_code}")

    body_hash = hashlib.sha256(r.text.encode("utf-8")).hexdigest()[:16]

    with SessionLocal() as session:
        pid = get_or_create_product(session, site=site, url=url, name="Example Placeholder")
        write_price_snapshot(
            session,
            product_id=pid,
            price=9.99,
            currency="GBP",
            in_stock=True,
            on_sale=False,
            source_hash=body_hash,
        )
        session.commit()
        logger.info(f"Wrote snapshot for product_id={pid} source_hash={body_hash}")

if __name__ == "__main__":
    main()

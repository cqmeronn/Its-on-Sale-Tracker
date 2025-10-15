"""Seed tracked product URLs into the product table."""

from sqlalchemy import select
from sqlalchemy.orm import Session
from pipeline.common.db import SessionLocal
from pipeline.common.models import Product

SEED = [
    ("books.toscrape.com", "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html", "A Light in the Attic"),
    ("books.toscrape.com", "https://books.toscrape.com/catalogue/william-shakespeares-star-wars-verily-a-new-hope-william-shakespeares-star-wars-4_871/index.html", "William Shakespeare's Star Wars"),
    ("scrapeme.live", "https://scrapeme.live/shop/Poliwhirl", "Poliwhirl"),
    ("scrapeme.live", "https://scrapeme.live/shop/Charmander/", "Charmander"),
    ("scrapeme.live", "https://scrapeme.live/shop/squirtle/", "Squirtle")
]

def upsert_product(session: Session, site: str, url: str, name: str | None):
    exists = session.execute(select(Product).where(Product.site == site, Product.url == url)).scalar_one_or_none()
    if exists:
        return
    session.add(Product(site=site, url=url, name=name))

def main():
    with SessionLocal() as s:
        for site, url, name in SEED:
            upsert_product(s, site, url, name)
        s.commit()
        print(f"Seeded {len(SEED)} products")

if __name__ == "__main__":
    main()

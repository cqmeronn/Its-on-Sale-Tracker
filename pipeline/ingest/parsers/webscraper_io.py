"""Parse a product page on webscraper.io test e-commerce site."""

from bs4 import BeautifulSoup
from urllib.parse import urlparse

def parse_product_page(html: str, url: str) -> dict:
    host = urlparse(url).hostname or "unknown"
    soup = BeautifulSoup(html, "lxml")

    name_el = soup.select_one(".caption h4:nth-of-type(2), .product-title, h1")
    name = name_el.get_text(strip=True) if name_el else None

    price_el = soup.select_one(".price, .price.pull-right, .caption h4.price")
    raw_price = price_el.get_text(strip=True) if price_el else None
    price = None
    currency = "USD"
    if raw_price:
        cleaned = (
            raw_price.replace("£", "")
                     .replace("$", "")
                     .replace("USD", "")
                     .replace(",", "")
                     .replace("Â", "")
                     .strip()
        )
        try:
            price = float(cleaned)
        except ValueError:
            price = None

    in_stock = True

    return {
        "site": host.lower(),
        "url": url,
        "name": name,
        "price": price,
        "currency": currency,
        "in_stock": in_stock,
        "on_sale": False,
    }

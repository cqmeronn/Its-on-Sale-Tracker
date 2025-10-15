"""Parse a Books to Scrape product page into structured fields."""

from bs4 import BeautifulSoup

def parse_product_page(html: str, url: str) -> dict:
    soup = BeautifulSoup(html, "lxml")

    name_el = soup.select_one(".product_main h1")
    price_el = soup.select_one(".product_main .price_color")
    stock_el = soup.select_one(".product_main .availability")

    name = name_el.get_text(strip=True) if name_el else None
    raw_price = price_el.get_text(strip=True) if price_el else None
    currency = "GBP"
    price = None
    if raw_price:
        cleaned = raw_price.replace("£", "").replace("Â", "").strip()
        try:
            price = float(cleaned)
        except ValueError:
            price = None

    in_stock = None
    if stock_el:
        txt = stock_el.get_text(strip=True).lower()
        in_stock = "in stock" in txt

    return {
        "site": "books.toscrape.com",
        "url": url,
        "name": name,
        "price": price,
        "currency": currency,
        "in_stock": in_stock,
        "on_sale": False,
    }
"""Parse a Scrapeme (WooCommerce) product page."""
from bs4 import BeautifulSoup
import re

def _extract_price_text(soup: BeautifulSoup) -> str | None:
    ins = soup.select_one("p.price ins .amount, p.price ins .woocommerce-Price-amount")
    if ins:
        return ins.get_text(strip=True)
    amt = soup.select_one("p.price .amount, p.price .woocommerce-Price-amount")
    return amt.get_text(strip=True) if amt else None

def _to_float(raw: str | None) -> float | None:
    if not raw:
        return None
    cleaned = raw.replace("£", "").replace("$", "").replace("GBP", "")
    cleaned = cleaned.replace(",", "").replace("Â", "").strip()
    m = re.search(r"(\d+(\.\d+)?)", cleaned)
    if not m:
        return None
    try:
        return float(m.group(1))
    except ValueError:
        return None

def parse_product_page(html: str, url: str) -> dict:
    soup = BeautifulSoup(html, "lxml")

    name_el = soup.select_one("h1.product_title, .product_title.entry-title")
    name = name_el.get_text(strip=True) if name_el else None

    raw_price = _extract_price_text(soup)
    price = _to_float(raw_price)

    stock_el = soup.select_one("p.stock")
    in_stock = None
    if stock_el:
        txt = stock_el.get_text(strip=True).lower()
        in_stock = ("in stock" in txt) or ("available" in txt) or ("in-stock" in stock_el.get("class", []))

    return {
        "site": "scrapeme.live",
        "url": url,
        "name": name,
        "price": price,
        "currency": "GBP",
        "in_stock": in_stock,
        "on_sale": False,
    }

"""Streamlit app showing price trends and metrics."""

import os
import pandas as pd
from sqlalchemy import create_engine, text
import streamlit as st

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    st.stop()

engine = create_engine(DATABASE_URL, future=True)

@st.cache_data(ttl=60)
def load_products():
    with engine.connect() as c:
        df = pd.read_sql(text("""
            select product_id, name, site, url
            from public.product
            order by product_id
        """), c)
    return df

@st.cache_data(ttl=60)
def load_price_history(product_id: int):
    with engine.connect() as c:
        df = pd.read_sql(text("""
            select ts_utc, price_numeric as price, currency, in_stock_bool as in_stock
            from public.price_history
            where product_id = :pid
            order by ts_utc
        """), c, params={"pid": product_id})
    return df

st.title("It’s On Sale — Price Tracker")

products = load_products()
if products.empty:
    st.info("No products yet. Run the ingestion pipeline.")
    st.stop()

# Add site filter
site_filter = st.selectbox(
    "Filter by site",
    ["All"] + sorted(products["site"].dropna().unique().tolist()),
)

if site_filter != "All":
    products = products[products["site"] == site_filter]


pid = st.selectbox(
    "Select a product",
    products["product_id"].tolist(),
    format_func=lambda i: products.set_index("product_id").loc[i, "name"],
)

row = products.set_index("product_id").loc[pid]
st.markdown(f"**Site:** {row['site']}  \n**URL:** {row['url']}")

hist = load_price_history(pid)
if hist.empty:
    st.info("No price history yet for this product.")
    st.stop()

hist["ts_utc"] = pd.to_datetime(hist["ts_utc"])
hist = hist.sort_values("ts_utc")

latest_price = hist.iloc[-1]["price"]
currency = hist.iloc[-1]["currency"]

if len(hist) > 1:
    prev_price = hist.iloc[-2]["price"]
    diff = latest_price - prev_price
    pct = (diff / prev_price) * 100 if prev_price else 0
else:
    prev_price, diff, pct = None, None, 0

col1, col2, col3 = st.columns(3)
col1.metric("Latest price", f"{latest_price:.2f} {currency}")
if prev_price:
    col2.metric("Previous price", f"{prev_price:.2f} {currency}")
    col3.metric("Change %", f"{pct:.2f}%", delta=f"{pct:.2f}")

st.line_chart(hist.set_index("ts_utc")["price"])
st.dataframe(hist.tail(20))

"""Simple UI to browse products and view price history."""

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

choice = st.selectbox(
    "Select a product",
    products["product_id"].tolist(),
    format_func=lambda pid: f"{pid} — {products.set_index('product_id').loc[pid, 'name']}",
)

row = products.set_index("product_id").loc[choice]
st.markdown(f"**Site:** {row['site']}  \n**URL:** {row['url']}")

hist = load_price_history(choice)
if hist.empty:
    st.info("No price history yet for this product.")
else:
    st.metric("Latest price", f"{hist.iloc[-1]['price']} {hist.iloc[-1]['currency']}")
    st.line_chart(hist.set_index("ts_utc")["price"])
    st.dataframe(hist.tail(20))

"""Generate a short summary of latest price snapshots."""

import os
import pandas as pd
from sqlalchemy import create_engine, text
import json
import requests

def main():
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url, future=True)

    with engine.connect() as conn:
        df = pd.read_sql(
            text("""
                select p.name, p.site, ph.price_numeric as price, ph.currency, ph.ts_utc
                from public.price_history ph
                join public.product p on p.product_id = ph.product_id
                where ph.ts_utc > now() - interval '1 day'
                order by ph.ts_utc desc
            """),
            conn,
        )

    if df.empty:
        msg = "No new price snapshots in the past 24h."
    else:
        latest = (
            df.groupby(["site", "name"])
            .agg({"price": "last", "currency": "last"})
            .reset_index()
        )
        lines = [f"{row.site} – {row.name}: {row.price:.2f} {row.currency}" for _, row in latest.iterrows()]
        msg = "Latest price summary:\n" + "\n".join(lines)

    print(msg)

    slack_url = os.getenv("SLACK_WEBHOOK_URL")
    if slack_url:
        try:
            requests.post(slack_url, data=json.dumps({"text": msg}), headers={"Content-Type": "application/json"})
            print("Posted summary to Slack.")
        except Exception as e:
            print("Slack post failed:", e)

if __name__ == "__main__":
    main()

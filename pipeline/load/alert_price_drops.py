"""Post Slack alerts for price drops detected in last 12 hours."""

import os, json, requests
import pandas as pd
from sqlalchemy import create_engine, text

def main():
    db_url = os.getenv("DATABASE_URL")
    slack = os.getenv("SLACK_WEBHOOK_URL")
    engine = create_engine(db_url, future=True)

    with engine.connect() as c:
        df = pd.read_sql(text("""
            select e.product_id, p.name, p.site, p.url, e.prev_price, e.new_price, e.drop_pct, e.ts_utc
            from marts.price_events e
            join staging.stg_product p on p.product_id = e.product_id
            where e.event_type = 'DROP' and e.ts_utc > now() - interval '12 hours'
            order by e.ts_utc desc
        """), c)

    if df.empty:
        print("No price drops in the last 12 hours.")
        return

    lines = [
        f"{row.site} – {row.name}: {row.prev_price:.2f} → {row.new_price:.2f} GBP ({row.drop_pct:.2f}%)\n{row.url}"
        for _, row in df.iterrows()
    ]
    text = "Price drops detected:\n" + "\n\n".join(lines)
    print(text)

    if slack:
        try:
            requests.post(slack, data=json.dumps({"text": text}), headers={"Content-Type": "application/json"})
            print("Posted drop alerts to Slack.")
        except Exception as e:
            print("Slack post failed:", e)

if __name__ == "__main__":
    main()

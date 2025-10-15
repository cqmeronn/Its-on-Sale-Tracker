"""Post Slack alerts for price drops detected in last 12 hours."""

import os, json, requests
import pandas as pd
from sqlalchemy import create_engine, text as sql_text

def main():
    db_url = os.getenv("DATABASE_URL")
    slack = os.getenv("SLACK_WEBHOOK_URL")
    engine = create_engine(db_url, future=True)

    with engine.connect() as c:
        df = pd.read_sql(sql_text("""
        with hist as (
          select
            ph.product_id,
            ph.ts_utc,
            ph.price_numeric as curr_price,
            lag(ph.price_numeric) over (
              partition by ph.product_id
              order by ph.ts_utc
            ) as prev_price
          from public.price_history ph
          where ph.price_numeric is not null
        ),
        drops as (
          select
            product_id,
            ts_utc,
            prev_price,
            curr_price,
            case
              when prev_price is not null and curr_price < prev_price
              then round(100.0 * (prev_price - curr_price) / nullif(prev_price, 0), 2)
              else null
            end as drop_pct
          from hist
        )
        select
          p.product_id,
          p.name,
          p.site,
          p.url,
          d.prev_price,
          d.curr_price as new_price,
          d.drop_pct,
          d.ts_utc
        from drops d
        join public.product p
          on p.product_id = d.product_id
        where d.drop_pct is not null
          and d.ts_utc > now() - interval '12 hours'
        order by d.ts_utc desc
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

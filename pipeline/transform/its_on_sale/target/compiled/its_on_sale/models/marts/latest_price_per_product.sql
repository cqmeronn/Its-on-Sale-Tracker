-- Latest price per product

with ranked as (
  select
    ph.product_id,
    ph.ts_utc,
    ph.price,
    ph.currency,
    ph.in_stock,
    row_number() over (partition by ph.product_id order by ph.ts_utc desc) as rn
  from "neondb"."public_staging"."stg_price_history" ph
)
select
  r.product_id,
  r.ts_utc as last_seen_utc,
  r.price,
  r.currency,
  r.in_stock
from ranked r
where r.rn = 1
-- Fact table for price time series

select
  ph.id,
  ph.product_id,
  p.site,
  p.url,
  p.name,
  ph.ts_utc,
  ph.price,
  ph.currency,
  ph.in_stock,
  ph.on_sale
from "neondb"."public_staging"."stg_price_history" ph
join "neondb"."public_staging"."stg_product" p
  on p.product_id = ph.product_id
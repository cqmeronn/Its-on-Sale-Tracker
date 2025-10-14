-- Basic staging view over price_history

select
  id,
  product_id,
  ts_utc,
  cast(price_numeric as numeric(12,2)) as price,
  currency,
  in_stock_bool as in_stock,
  on_sale_bool as on_sale,
  source_hash
from public.price_history

-- Basic staging view over product

select
  product_id,
  site,
  url,
  name,
  created_at
from public.product
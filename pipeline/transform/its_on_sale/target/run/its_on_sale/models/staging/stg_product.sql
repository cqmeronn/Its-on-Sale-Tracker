
  create view "neondb"."public_staging"."stg_product__dbt_tmp"
    
    
  as (
    -- Basic staging view over product

select
  product_id,
  site,
  url,
  name,
  created_at
from public.product
  );
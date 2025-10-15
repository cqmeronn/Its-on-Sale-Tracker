select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      -- fail if any (site, url) appears more than once

select site, url
from "neondb"."public_staging"."stg_product"
group by 1, 2
having count(*) > 1
      
    ) dbt_internal_test
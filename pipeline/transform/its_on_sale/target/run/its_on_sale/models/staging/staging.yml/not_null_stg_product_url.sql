select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select url
from "neondb"."public_staging"."stg_product"
where url is null



      
    ) dbt_internal_test
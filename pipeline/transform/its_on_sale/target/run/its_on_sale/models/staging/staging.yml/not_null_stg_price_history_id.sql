select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select id
from "neondb"."public_staging"."stg_price_history"
where id is null



      
    ) dbt_internal_test
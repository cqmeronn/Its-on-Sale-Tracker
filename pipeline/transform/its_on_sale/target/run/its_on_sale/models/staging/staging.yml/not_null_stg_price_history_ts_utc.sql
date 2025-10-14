select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select ts_utc
from "neondb"."public_staging"."stg_price_history"
where ts_utc is null



      
    ) dbt_internal_test
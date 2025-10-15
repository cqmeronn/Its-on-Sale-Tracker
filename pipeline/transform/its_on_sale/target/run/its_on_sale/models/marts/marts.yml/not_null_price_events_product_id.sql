select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select product_id
from "neondb"."public_marts"."price_events"
where product_id is null



      
    ) dbt_internal_test
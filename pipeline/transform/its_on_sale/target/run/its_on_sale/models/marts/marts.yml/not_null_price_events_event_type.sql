select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select event_type
from "neondb"."public_marts"."price_events"
where event_type is null



      
    ) dbt_internal_test
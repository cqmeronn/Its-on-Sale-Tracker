
    
    

select
    url as unique_field,
    count(*) as n_records

from "neondb"."public_staging"."stg_product"
where url is not null
group by url
having count(*) > 1



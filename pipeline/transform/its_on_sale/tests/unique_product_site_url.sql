-- fail if any (site, url) appears more than once

select site, url
from {{ ref('stg_product') }}
group by 1, 2
having count(*) > 1

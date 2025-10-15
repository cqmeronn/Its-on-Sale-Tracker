-- Price drop/restock events derived from consecutive snapshots

with hist as (
  select
    product_id,
    ts_utc,
    price,
    in_stock,
    lag(price) over (partition by product_id order by ts_utc) as prev_price,
    lag(in_stock) over (partition by product_id order by ts_utc) as prev_stock
  from {{ ref('stg_price_history') }}
),
events as (
  select
    product_id,
    ts_utc,
    prev_price,
    price as new_price,
    case
      when prev_price is not null and price is not null and price < prev_price then 'DROP'
      when prev_stock = false and in_stock = true then 'RESTOCK'
      when prev_stock = true and in_stock = false then 'OOS'
      else null
    end as event_type,
    case
      when prev_price is not null and price is not null and price < prev_price
        then round(100.0*(prev_price - price)/prev_price, 2)
      else null
    end as drop_pct
  from hist
)
select * from events where event_type is not null

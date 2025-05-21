v_stock_prices_last = """
CREATE VIEW v_stock_prices_last AS
--CREATE VIEW IF NOT EXISTS v_stock_prices_last AS
select
 symbol,
 date,
 price,
 price_type,
 updated_date,
 previous_price,
 time as price_time
from (
    SELECT 
        symbol,
        date,
        price,
        price_type,
        updated_date,
        time,
        LAG(price) OVER (PARTITION BY symbol ORDER BY date) AS previous_price,
        rank() OVER (PARTITION BY symbol ORDER BY date DESC) rnk 
    FROM prices
    ) x
where x.rnk = 1
"""

v_trades_pl = """
CREATE VIEW v_trades_pl AS
--CREATE VIEW IF NOT EXISTS v_trades_pl AS
with prep as (
    select 
    t.symbol,
    p.date,
    t.trade_date,
    t.volume,
    t.trade_price,
    p.price,
    COALESCE(lag(p.price) over ( partition by t.id, p.price_type, t.portfolio_id order by p.date), t.trade_price) as prev_price,
    prt.name portfolio,
    t.id,
    prt.id as portfolio_id,
    prt.user_id
    from trades t
    join portfolio prt
        on prt.id = t.portfolio_id
    join prices p
        on p.symbol = t.symbol
        and p.date >= t.trade_date
    where 0=0
    order by 3 asc
    )
, pl as (
    select 
    t.*,
    t.price - t.trade_price as price_change_total,
    t.price - t.prev_price as price_change_day,
    t.volume*(t.price - t.prev_price) as pl
    from prep t
    )
select 
t.symbol,
t.date,
to_char(date, 'YYYY-MM') AS month_end,
t.trade_date,
t.trade_price,
t.price,
t.prev_price,
t.price_change_day,
t.price_change_total,
t.pl,
sum(t.pl) over (partition by t.symbol, t.trade_date, t.id order by  date rows between unbounded preceding and current row) as pl_cum,
t.portfolio,
t.portfolio_id,
t.user_id
from pl t
where 0=0
"""

v_portfolio_overview="""
CREATE VIEW v_portfolio_overview AS
--CREATE VIEW IF NOT EXISTS v_portfolio_overview AS
SELECT 
 t.symbol,
 i.name,
 t.trade_price,
 t.volume,
 t.trade_date,
 p.price,
 case 
     when date(t.trade_date) = date('now') then (p.price-t.trade_price)*t.volume
     when p.date = date('now') then (p.price - p.previous_price)*t.volume
     else 0
 end as day_profit,
 case 
     when date(t.trade_date) = date('now') then (p.price-t.trade_price)/t.trade_price
     when p.date = date('now') then (p.price - p.previous_price)/p.previous_price
     else 0
 end as day_change,
 (p.price - t.trade_price)*t.volume as profit,
 p.price*t.volume as value,
 CASE 
    WHEN p.date = CURRENT_DATE THEN to_char(p.price_time AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Prague', 'HH24:MI:SS') 
    ELSE p.date::text 
 END AS price_time,
 prt.name as portfolio,
 prt.id as portfolio_id,
 prt.user_id,
 t.id as trade_id 
FROM trades t
join v_stock_prices_last p
    on t.symbol = p.symbol
join instruments i
    on i.symbol = t.symbol 
join portfolio prt 
    on prt.id = t.portfolio_id
"""
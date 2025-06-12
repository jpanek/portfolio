sql_stocks = """
select 
 t.symbol as Symbol,
 t.name as Name,
 p.price as Price,
 p.date as "Price Date",
 TO_CHAR(p.price_time, 'HH24:MI:SS') as "Price Time",
 TO_CHAR(p.updated_date AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Prague', 'YYYY-MM-DD HH24:MI:SS') as "Updated time"
from instruments t
left join v_stock_prices_last p
    on p.symbol = t.symbol
where 0=0
and   t.category = 'EQUITY'
"""

sql_ccy = """
select 
 t.symbol as Symbol,
 t.name as Name,
 p.price as Price,
 p.date as "Price Date",
 TO_CHAR(p.updated_date AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Prague', 'YYYY-MM-DD HH24:MI:SS') as "Updated time"
from instruments t
left join v_stock_prices_last p
    on p.symbol = t.symbol
where 0=0
and  t.symbol like '%=X'
"""

sql_trades_detail = """
with portfolio as (
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
)
select 
 --cast(trade_id as text) as id,
 symbol as "Symbol", 
 replace(name,'VII PLC ISHRS ','') as "Name", 
 trade_price as "Trade Price", 
 date(trade_date) as "Trade Date",
 --volume as "Volume", 
 CASE
    WHEN volume = floor(volume) THEN round(volume)
    ELSE volume
 END AS Volume,
 price as "Price", 
 day_change*100 as "Day pct",
 day_profit as "Day Profit", profit as "Profit", value as "Value", price_time as "Price time"
--from v_portfolio_overview 
from portfolio
where portfolio_id = %s
order by trade_date
"""

sql_trades = """
with portfolio as (
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
)
select 
 date('now') as Date,
 sum(volume*trade_price) as Investment,
 sum(volume*price) as Value,
 sum(day_profit)/sum(value)*100 as "Day pct",
 sum(day_profit) as "Day Profit",
 (sum(volume*price)/sum(volume*trade_price)-1)*100   as "Overall pct",
 sum(profit)    as "Profit"
--from v_portfolio_overview
from portfolio
where portfolio_id = %s
"""

sql_history = """
select 
  t.symbol, 
  to_char(t.date,'YYYY-MM-DD') as date, 
  t.price,
  t.price_type
from prices t
where 0=0
and   symbol = %s
and   date >= %s
and   date <= %s
"""

sql_pl = """
with prep as (
select 
 symbol,
 date as date,
 sum(pl) as pl
from v_trades_pl t
where 0=0
and   user_id = %s
and   symbol = %s
and   date >= %s
and   date <= %s
group by 
 symbol,
 date
order by 2 asc
           )
select 
t.*, 
sum(t.pl) over (partition by 1 order by date) as "PL Period"
from prep t
"""

sql_pl_month = """
with prep as (
select 
 symbol,
 month_end as date,
 sum(pl) as pl
from v_trades_pl
where 0=0
and   user_id = %s
and   symbol = %s
and   date >= %s
and   date <= %s
group by 
 symbol,
 month_end
order by 2 asc
           )
select 
t.*, 
sum(t.pl) over (partition by 1 order by date) as "PL Period"
from prep t
"""

sql_pl_all_start="""
select 
{place_holder} as "Date",
sum(pl) as "PL Daily",
SUM(SUM(pl)) OVER (ORDER BY {place_holder}) AS "PL Period",
sum(pl_cum) as "PL Total"
from v_trades_pl
where 0=0
and    date >= %s
and    date <= %s
and    user_id = %s 
"""

sql_pl_all_end="""
group by 
{place_holder}
order by 1 asc 
"""

sql_portfolio="""
select 
 cast(p.id as text) as id,
 p.name as "Portfolio name",
 u.name as "User name",
 sum(t.trade_price*t.volume) as Investment,
 sum(ov.value) as Value,
 sum(ov.profit) as Profit,
 sum(caSE when t.id is not null then 1 end) as Deals,
 date(p.created_date) as Created
from users u
join portfolio p
     on p.user_id = u.id
left join trades t
    on t.portfolio_id = p.id
left join v_portfolio_overview ov
    on ov.trade_id = t.id
where 0=0
and   u.id = %s
group by
p.name, u.name, p.id
order by p.id
"""

def modify_query(query, value):
    return query.format(place_holder=value)
--ATTACH DATABASE '/Users/jurajpanek/Documents/code/playground/api_testing/DB/portfolio_db.db' AS old_portfolio;
--DETACH DATABASE old_portfolio;


-- move the instruments
insert into portfolio.instruments (symbol,name,updated_date,type)
SELECT 
 t.symbol,
 t.name,
 datetime('now') updated_date, 
 case when t.symbol like '%=X' then 'CCY' else 'EQT' end type
FROM old_portfolio.stocks t
;

-- move prices
insert into portfolio.prices
SELECT * FROM old_portfolio.stock_prices
;

-- insert portfolio
INSERT INTO portfolio (name, user_id)
VALUES ('xtb_usd', 1),
       ('xtb_eur', 1);
;

-- move trades:
insert into portfolio.trades (symbol,trade_date,volume,trade_price,trade_type,currency,portfolio_id,updated_date)
SELECT 
 t.symbol,
 t.trade_date,
 t.volume,
 t.trade_price,
 t.trade_type,
 t.currency,
 p.id, -- portfolio_id,
 datetime('now') datetime
FROM old_portfolio.trades t
left join portfolio p
    on p.name = t.portfolio
WHERE 0=0
--and   t.id = 57
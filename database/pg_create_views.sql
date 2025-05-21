BEGIN;

CREATE VIEW v_trades_pl AS
WITH prep AS (
    SELECT 
        t.symbol,
        p.date,
        t.trade_date,
        t.volume,
        t.trade_price,
        p.price,
        COALESCE(LAG(p.price) OVER (PARTITION BY t.id, p.price_type, t.portfolio_id ORDER BY p.date), t.trade_price) AS prev_price,
        prt.name AS portfolio,
        t.id,
        prt.id AS portfolio_id,
        prt.user_id
    FROM trades t
    JOIN portfolio prt ON prt.id = t.portfolio_id
    JOIN prices p ON p.symbol = t.symbol AND p.date >= t.trade_date
    ORDER BY t.trade_date ASC
),
pl AS (
    SELECT 
        prep.*,
        prep.price - prep.trade_price AS price_change_total,
        prep.price - prep.prev_price AS price_change_day,
        prep.volume * (prep.price - prep.prev_price) AS pl
    FROM prep
)
SELECT 
    pl.symbol,
    pl.date,
    TO_CHAR(pl.date, 'YYYY-MM') AS month_end,
    pl.trade_date,
    pl.trade_price,
    pl.price,
    pl.prev_price,
    pl.price_change_day,
    pl.price_change_total,
    pl.pl,
    SUM(pl.pl) OVER (PARTITION BY pl.symbol, pl.trade_date, pl.id ORDER BY pl.date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS pl_cum,
    pl.portfolio,
    pl.portfolio_id,
    pl.user_id
FROM pl
WHERE TRUE;

CREATE VIEW v_stock_prices_last AS
SELECT
    symbol,
    date,
    price,
    price_type,
    updated_date,
    previous_price,
    time AS price_time
FROM (
    SELECT 
        symbol,
        date,
        price,
        price_type,
        updated_date,
        time,
        LAG(price) OVER (PARTITION BY symbol ORDER BY date) AS previous_price,
        RANK() OVER (PARTITION BY symbol ORDER BY date DESC) AS rnk
    FROM prices
) sub
WHERE rnk = 1;

CREATE VIEW v_portfolio_overview AS
SELECT 
    t.symbol,
    i.name,
    t.trade_price,
    t.volume,
    t.trade_date,
    p.price,
    CASE 
        WHEN t.trade_date::date = CURRENT_DATE THEN (p.price - t.trade_price) * t.volume
        WHEN p.date = CURRENT_DATE THEN (p.price - p.previous_price) * t.volume
        ELSE 0
    END AS day_profit,
    CASE 
        WHEN t.trade_date::date = CURRENT_DATE THEN (p.price - t.trade_price) / t.trade_price
        WHEN p.date = CURRENT_DATE THEN (p.price - p.previous_price) / p.previous_price
        ELSE 0
    END AS day_change,
    (p.price - t.trade_price) * t.volume AS profit,
    p.price * t.volume AS value,
    CASE WHEN p.date = CURRENT_DATE THEN p.price_time ELSE p.date END AS price_time,
    prt.name AS portfolio,
    prt.id AS portfolio_id,
    prt.user_id,
    t.id AS trade_id
FROM trades t
JOIN v_stock_prices_last p ON t.symbol = p.symbol
JOIN instruments i ON i.symbol = t.symbol
JOIN portfolio prt ON prt.id = t.portfolio_id;

COMMIT;

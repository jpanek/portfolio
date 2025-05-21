BEGIN;

CREATE TABLE users (
  id INTEGER NOT NULL PRIMARY KEY,
  username TEXT NOT NULL UNIQUE,
  name     TEXT NOT NULL,
  password TEXT NOT NULL,
  role     TEXT NOT NULL,
  updated_date TIMESTAMP
);

CREATE TABLE IF NOT EXISTS instruments (
  symbol       TEXT NOT NULL PRIMARY KEY,
  name         TEXT,
  updated_date TIMESTAMP,
  category     TEXT
);

CREATE TABLE prices (
  id           INTEGER   NOT NULL PRIMARY KEY,
  symbol       TEXT      NOT NULL,
  date         DATE      NOT NULL,
  price        FLOAT     NOT NULL,
  price_type   TEXT,
  updated_date TIMESTAMP,
  time         TIMESTAMP,
  CONSTRAINT prices_symbol_date_type_uc UNIQUE (symbol, date, price_type),
  FOREIGN KEY(symbol) REFERENCES instruments(symbol)
);

-- define portfolio before trades
CREATE TABLE IF NOT EXISTS portfolio (
  id           INTEGER   NOT NULL PRIMARY KEY,
  name         TEXT      NOT NULL,
  user_id      INTEGER   NOT NULL,
  created_date TIMESTAMP,
  CONSTRAINT uq_portfolio_name_user UNIQUE(name, user_id),
  FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE trades (
  id           INTEGER   NOT NULL PRIMARY KEY,
  symbol       TEXT      NOT NULL,
  trade_date   TIMESTAMP NOT NULL,
  volume       INTEGER   NOT NULL,
  trade_price  FLOAT     NOT NULL,
  trade_type   TEXT      NOT NULL,
  currency     TEXT      NOT NULL,
  portfolio_id INTEGER   NOT NULL,
  updated_date TIMESTAMP,
  FOREIGN KEY(symbol)       REFERENCES instruments(symbol),
  FOREIGN KEY(portfolio_id) REFERENCES portfolio(id)
);

COMMIT;

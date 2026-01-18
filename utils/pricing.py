# pricing.py

import pandas as pd
import yfinance as yf
import time
from utils.db import get_db_connection, get_sqlalchemy_engine
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(BASE_DIR, 'logs', 'cron_log.log')

""" Main class to handle the Market Position and use Yahoo Finance package 
--------------------------------------------------------------------- """
class position:
    def __init__(self, ticker, open_price=0, open_date=None, vol=0, portfolio=None):
        self.ticker = ticker
        self.open_price = open_price
        self.open_date = open_date
        self.volume = vol
        self.investment = vol*open_price
        self.portfolio = portfolio
        
        #Initation functions:
        self.get_info()
        self.get_price()
        #self.get_daily_history()
        #self.get_monthly_history()
        self.handle = yf.Ticker(self.ticker)

    def get_info(self):
        yf_handle = yf.Ticker(self.ticker)
        self.symbol = yf_handle.info['symbol']
        self.name = yf_handle.info['shortName']
        self.category = yf_handle.info['quoteType']

    def get_price(self):
        yf_handle = yf.Ticker(self.ticker)

        data = yf_handle.history(period="1d",interval='1m')

        if data.empty:  # Check if history is empty
            print(f"Warning: No price data found for {self.ticker}. It might be delisted or market is closed.")
            self.price = None
            return None

        self.price = data['Close'].iloc[-1]
        self.price_time = data['Close'].index[-1]
        self.value = self.price * self.volume
        self.total_pl = (self.price - self.open_price)*self.volume
        return self.price
        
    def get_daily_prices(self,start_date=None,price_type="Close"):
        yf_handle = yf.Ticker(self.ticker)
        if start_date is None:
            start_date = self.open_date
        prices = yf_handle.history(start=start_date)[price_type]
        self.daily_prices = prices
        return prices
        
    def get_monthly_prices(self, price_type="Close"):
        today = pd.Timestamp.today()#.normalize()
        data = yf.download(self.ticker,start = self.open_date, end = today)
        eom_prices = data[price_type].resample('ME').last()
        eom_prices = eom_prices[self.ticker]
        eom_prices.name = 'EOM Prices'
        
        #add today's price
        if eom_prices.index[-1] != data.index[-1]:
            eom_prices = eom_prices.rename(index={eom_prices.index[-1]: data.index[-1]})
        
        self.eom_prices = eom_prices
        return eom_prices
    
    def calculate_pl(self,prices):
        previous = self.open_price
        stock_pl = prices.copy()
        stock_pl_cum = prices.copy()
        stock_pl.name = 'EOM PL'
        stock_pl_cum.name = 'EOM PL Cumulative'
    
        for i,price in enumerate(prices):
            pl = (price-previous)*self.volume
            stock_pl.values[i] = pl
            if i==0:
                stock_pl_cum.values[i] = pl
            else:
                stock_pl_cum.values[i] = pl + stock_pl_cum.values[i-1]
            previous = price
        return stock_pl, stock_pl_cum

    def print_info(self):
        print(f"-----------------------------------------------")
        print(f"Name: {self.name}")
        print(f"Ticker/Symbol: {self.ticker}")
        print(f"Category: {self.category}")
        print(f"Volume: {self.volume}")
        print(f"Purchase price: {self.open_price:.2f}")
        print(f"Current price: {self.price:.2f}")

        print(f"Purchase date: {self.open_date}")
        
        print(f"Initial investment: {self.investment:.2f}")
        print(f"Current investment value: {self.value:.2f}")
        print(f"Total position PL: {self.total_pl:.2f}")
        print(f"-----------------------------------------------")


""" Function to refresh prices in Database
--------------------------------------------------------------------- """
def refresh_prices(history_days=3,symbol=None):
    with open(LOG_FILE, "a") as f:
            
        start_time = time.time()
        print(f"--------------------------------------------------------------------------", file=f, flush=True)
        print(f"\n--- [MANUAL] Loading of prices started at {pd.Timestamp.today()} ---", file=f, flush=True)

        prices_start_date = (pd.Timestamp.today() - pd.Timedelta(days=history_days)).date()
        
        conn = get_db_connection()
        cur = conn.cursor()

        sqlalchemy_engine = get_sqlalchemy_engine()

        try:
            query = "SELECT * FROM instruments"
            if symbol:
                query += " where symbol= '"+str(symbol)+"'"

            df = pd.read_sql_query(query, sqlalchemy_engine)
            i = 0

            for index, row in df.iterrows():
                try:
                    handle = position(ticker=row.symbol)

                    print(f"Loading prices for {row.symbol} starting from date: {prices_start_date}")
                    print(f"Loading prices for {row.symbol} starting from date: {prices_start_date}", file=f, flush=True)

                    if handle.price is None:
                        print(f"Skipping {row.symbol} due to missing price data.")
                        print(f"Skipping {row.symbol} due to missing price data.", file=f, flush=True)
                        continue

                    prices = handle.get_daily_prices(prices_start_date)

                    if prices.empty:
                        print(f"No historical prices found for {handle.ticker}. Skipping...")
                        print(f"No historical prices found for {handle.ticker}. Skipping...", file=f, flush=True)
                        continue

                    # Load the prices into DB
                    j = 0
                    for date, price in prices.items():
                        if j == len(prices)-1:
                            cur.execute("""
                                INSERT INTO prices (symbol, date, price, price_type, updated_date, time)
                                VALUES (%s, %s, %s, 'Close', CURRENT_TIMESTAMP, %s)
                                ON CONFLICT (symbol, date, price_type)
                                DO UPDATE SET 
                                    price = EXCLUDED.price,
                                    updated_date = CURRENT_TIMESTAMP,
                                    time = EXCLUDED.time;
                            """, (handle.ticker, date.strftime("%Y-%m-%d"), float(handle.price), handle.price_time.to_pydatetime()))
                        else:
                            cur.execute("""
                                INSERT INTO prices (symbol, date, price, price_type, updated_date)
                                VALUES (%s, %s, %s, 'Close', CURRENT_TIMESTAMP)
                                ON CONFLICT (symbol, date, price_type)
                                DO UPDATE SET 
                                    price = EXCLUDED.price,
                                    updated_date = CURRENT_TIMESTAMP;
                            """, (handle.ticker, date.strftime("%Y-%m-%d"), float(price)))

                        i, j = i + 1, j + 1
                    print(f"Loaded {j} prices for ticker {handle.ticker}")
                    print(f"Loaded {j} prices for ticker {handle.ticker}", file=f, flush=True)

                except Exception as e:
                    print(f"Unexpected error for {row.symbol}: {e}")
                    print(f"Unexpected error for {row.symbol}: {e}", file=f, flush=True)

            print(f"Loaded overall {i} records")
            print(f"Loaded overall {i} records", file=f, flush=True)
            conn.commit()

        except Exception as e:
            print(f"Database operation failed: {e}")
            print(f"Database operation failed: {e}", file=f, flush=True)
            conn.rollback()

        finally:
            conn.close()  # Always closes connection
            end_time = time.time()
            run_time = round(end_time - start_time)
            print(f"Execution time: {run_time} seconds")
            print(f"Execution time: {run_time} seconds", file=f, flush=True)
            print(f"\n--- [MANUAL] Finished at {pd.Timestamp.today()} ---", file=f, flush=True)


    return run_time

import sys
from pathlib import Path
from datetime import datetime

# Get the parent folder (one level up)
parent_dir = Path(__file__).resolve().parent.parent
print(parent_dir)
sys.path.insert(0, str(parent_dir))

from pricing import refresh_prices

history = 3

print(f"--------------------------------------------------------------------------")
time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print(f"Loading of prices started at {time_now} \n")

#refresh_prices(history,symbol='CSPX.L')
refresh_prices(history)

time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print(f"\nFinished at {time_now}")

#*/30 9-19 * * 1-5 /Users/jurajpanek/Documents/code/portfolio_app/venv/bin/python /Users/jurajpanek/Documents/code/portfolio_app/utils/load_prices.py >> /Users/jurajpanek/Documents/code/portfolio_app/logs/cron_log.log 2>&1